#!/usr/bin/env python3
"""Turn an objdump listing (tools/dev/disasm.sh) into a vasm source that
reassembles to the same bytes.

Usage: tools/dev/listing2vasm.py [--verbose] <listing> <bin> <out.s>

The listing (from tools/dev/disasm.sh) gives the instructions; the binary it
was made from gives the bytes, which the listing cannot always show (a last
instruction cut short by the end of the file has none), and is what the
result must reassemble to.

Each objdump line becomes one source line in Motorola syntax, with its address
in a comment. Where the line does not give back the original bytes, it becomes
`dc.w` with the disassembly kept in the comment. That happens when vasm rejects
it, when the bytes are not a 68000 instruction, or when the assembler picks
another encoding. Absolute operands are tried as `.w`, then as `.l`. The
converter assembles in the pinned toolchain (tools/dev/asm.sh) until every
line matches, so the result is mechanical: no labels and no comments of
substance. Standard library only.

Lines whose bytes depend on their own address (branches, PC-relative
operands) are first held as data, so a line that assembles to another length
cannot shift them out of range. They are brought back once every other line
matches and every address is right.
"""

from __future__ import annotations

import itertools
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE / "builds" / "listing2vasm"
MAX_PASSES = 40

SIZED = {
    "move", "movea", "movem", "movep", "add", "adda", "addi", "addq", "addx", "sub", "suba",
    "subi", "subq", "subx", "and", "andi", "or", "ori", "eor", "eori", "cmp", "cmpa", "cmpi",
    "cmpm", "clr", "neg", "negx", "not", "tst", "ext", "asl", "asr", "lsl", "lsr", "rol",
    "ror", "roxl", "roxr", "mulu", "muls", "divu", "divs", "chk", "link",
}
CONDITIONS = ("hi", "ls", "cc", "cs", "ne", "eq", "vc", "vs", "pl", "mi", "ge", "lt", "gt", "le")
BRANCHES = {"bra", "bsr"} | {"b" + c for c in CONDITIONS}
SIZED |= BRANCHES
# Mnemonics objdump prints that no 68000 has: kept as data without asking vasm.
NOT_68000 = re.compile(r"^(chkl|linkl|extbl|bkpt|rtd|movec|moves|cas|callm|rtm|pack|unpk|"
                       r"cmp2|chk2|bf|p(?!ea$)[a-z]|f[a-z]|cp|trap(?!v?$)|mul[su]l|div[su]l)")

INSN = re.compile(r"^\s*([0-9a-f]+):\t([0-9a-f ]+?)\s*\t(.*)$")
CONT = re.compile(r"^\s*([0-9a-f]+):\t([0-9a-f ]+?)\s*$")
LST = re.compile(r"^[0-9A-F]{2}:([0-9A-F]{8}) (?:[0-9A-F]+|\*) *(?:\t *(\d+):)?")
ERR = re.compile(r"error \d+ in line (\d+) of")


class Unsupported(Exception):
    pass


ZERO_RUN = 8  # bytes of zeros from which a run becomes one dcb.b line


def parse_listing(text: str, binary: bytes) -> list[dict]:
    insns = []
    for line in text.splitlines():
        m = INSN.match(line)
        if m:
            insns.append(dict(addr=int(m[1], 16), data=bytes.fromhex(m[2]), text=m[3].strip()))
            continue
        m = CONT.match(line)
        if m and insns:
            insns[-1]["data"] += bytes.fromhex(m[2])
    if not insns:
        sys.exit("error: no instructions in the listing")
    vma = insns[0]["addr"]
    for a, b in zip(insns, insns[1:]):
        if a["addr"] + len(a["data"]) != b["addr"]:
            sys.exit(f"error: bytes missing after ${a['addr']:x}: was the listing made "
                     "with tools/dev/disasm.sh (objdump -z)?")
    for insn in insns:
        off = insn["addr"] - vma
        if binary[off:off + len(insn["data"])] != insn["data"]:
            sys.exit(f"error: the listing and the binary differ at ${insn['addr']:x}")
    end = insns[-1]["addr"] + len(insns[-1]["data"])
    if end - vma < len(binary):  # objdump stops at an instruction cut short by the end
        insns.append(dict(addr=end, data=binary[end - vma:], text=".tail"))
    # Runs of zero bytes (objdump shows them as ori.b #0,d0) become one data line.
    folded, run = [], []
    for insn in insns + [None]:
        if insn is not None and not any(insn["data"]):
            run.append(insn)
            continue
        if sum(len(r["data"]) for r in run) >= ZERO_RUN:
            folded.append(dict(addr=run[0]["addr"], data=b"".join(r["data"] for r in run),
                               text=".zero"))
        else:
            folded.extend(run)
        run = []
        if insn is not None:
            folded.append(insn)
    return folded


def split_operands(s: str) -> list[str]:
    ops, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            ops.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        ops.append(cur)
    return ops


def reg(r: str) -> str:
    r = r.lstrip("%")
    return {"fp": "a6"}.get(r, r)


def number(n: str) -> str:
    if re.fullmatch(r"[0-9a-f]{16}", n):  # objdump's form for an index displacement
        v = int(n, 16)
        return str(v - (1 << 64) if v >= 1 << 63 else v)
    return "$" + n[2:] if n.startswith("0x") else n


def index(x: str) -> str:
    parts = x.split(":")
    if len(parts) != 2:  # a scale factor: 68020 and later
        raise Unsupported(x)
    return f"{reg(parts[0])}.{parts[1]}"


def operand(op: str, branch: bool) -> tuple[str, bool]:
    """Motorola form of one operand; the flag says it is an absolute address."""
    if "@(" in op and ")@" in op:
        raise Unsupported(op)  # memory indirect: 68020 and later
    if op.startswith("#"):
        return "#" + number(op[1:]), False
    if re.fullmatch(r"0x[0-9a-f]+", op):
        return number(op), not branch
    if re.fullmatch(r"-?\d+", op):
        return op, not branch
    m = re.fullmatch(r"%(\w+)@(\+|-)?", op)
    if m:
        r = reg(m[1])
        return {"+": f"({r})+", "-": f"-({r})", None: f"({r})"}[m[2]], False
    m = re.fullmatch(r"%(\w+)@\(([^,]+)(?:,([^)]+))?\)", op)
    if m:
        base, disp = reg(m[1]), number(m[2])
        inner = f"{disp},{base}" + (f",{index(m[3])}" if m[3] else "")
        return f"({inner})", False
    if re.fullmatch(r"%\w+", op):
        return reg(op), False
    if re.fullmatch(r"(%\w+(-%\w+)?)(/%\w+(-%\w+)?)*", op):
        return "/".join("-".join(reg(r) for r in part.split("-")) for part in op.split("/")), False
    raise Unsupported(op)


def convert(text: str) -> tuple[str, list[str], list[int], bool]:
    """(mnemonic, operands, indices of absolute operands, whether the bytes depend
    on the line's own address) in Motorola syntax."""
    mnem, _, rest = text.partition(" ")
    if mnem.startswith(".") or NOT_68000.match(mnem):
        raise Unsupported(mnem)
    if mnem[-1] in "bwls" and mnem[:-1] in SIZED:
        base, size = mnem[:-1], mnem[-1]
        mnem = f"{base}.{size}"
    else:
        base = mnem
    branch = base in BRANCHES or (base.startswith("db") and base[2:] in CONDITIONS + ("f", "t", "ra"))
    ops, absolute = [], []
    for i, op in enumerate(split_operands(rest) if rest else []):
        s, is_abs = operand(op.strip(), branch)
        ops.append(s)
        if is_abs:
            absolute.append(i)
    return mnem, ops, absolute, branch or any(o.endswith(",pc)") or ",pc," in o for o in ops)


def data_line(insn: dict) -> str:
    d = insn["data"]
    if insn["text"] == ".zero":
        return f"dcb.b\t{len(d)},0"
    words = [f"${int.from_bytes(d[i:i + 2], 'big'):04x}" for i in range(0, len(d) - 1, 2)]
    parts = []
    if words:
        parts.append("dc.w\t" + ",".join(words))
    if len(d) % 2:
        parts.append(f"dc.b\t${d[-1]:02x}")
    return "\n\t".join(parts)


def code_line(conv: tuple, sizes: tuple) -> str:
    mnem, ops, absolute, _ = conv
    ops = list(ops)
    for i, size in zip(absolute, sizes):
        ops[i] = f"({ops[i]}).{size}"
    return f"{mnem}\t{','.join(ops)}" if ops else mnem


def size_combos(conv: tuple) -> list[tuple]:
    """The size choices for the absolute operands, in the order they are tried:
    .w first where the address fits in a sign-extended word, else only .l."""
    choices = []
    for i in conv[2]:
        v = int(conv[1][i].lstrip("$"), 16) if conv[1][i].startswith("$") else int(conv[1][i])
        choices.append("wl" if v <= 0x7FFF or v >= 0xFFFF8000 else "l")
    return list(itertools.product(*choices))


def next_attempt(st: dict) -> None:
    """The next size choice for a line, or data when there is none left."""
    if st["code"] is not None and st["attempt"] + 1 < len(st["combos"]):
        st["attempt"] += 1
    else:
        st["code"], st["attempt"], st["combos"] = None, 0, [()]


def render(insns, states, vma) -> tuple[str, dict[int, int]]:
    """The source text and, for each source line number, the instruction index."""
    lines = [
        "; Generated by tools/dev/listing2vasm.py from an objdump listing. Mechanical: no",
        "; labels or comments yet. A dc.w line with a disassembly in its comment is a line",
        "; that did not reassemble to the original bytes as an instruction.",
        f"\torg\t${vma:x}",
    ]
    owner = {}
    for i, (insn, st) in enumerate(zip(insns, states)):
        if st["code"] is None or st["held"]:
            note = "" if insn["text"].startswith(".") else f"  {insn['text']}"
            body = data_line(insn)
        else:
            body, note = code_line(st["code"], st["combos"][st["attempt"]]), ""
        first = len(lines) + 1
        for j, part in enumerate(body.split("\n\t")):
            comment = f"; ${insn['addr']:06x}{note}" if j == 0 else ""
            lines.append(f"\t{part}\t{comment}".rstrip())
            owner[first + j] = i
    return "\n".join(lines) + "\n", owner


def assemble(src_text: str) -> tuple[int, str, str, bytes]:
    WORK.mkdir(parents=True, exist_ok=True)
    src, out, lst = WORK / "pass.s", WORK / "pass.bin", WORK / "pass.lst"
    src.write_text(src_text)
    for f in (out, lst):
        f.unlink(missing_ok=True)
    r = subprocess.run([str(HERE / "asm.sh"), str(src), str(out), str(lst)],
                       capture_output=True, text=True)
    return (r.returncode, r.stdout + r.stderr, lst.read_text() if lst.exists() else "",
            out.read_bytes() if out.exists() else b"")


def assembled_bytes(listing: str, binary: bytes, vma: int) -> dict[int, bytes]:
    """The bytes each source line produced: the listing gives where each line
    starts, the binary what is there up to where the next line starts."""
    starts = [(int(m[1], 16), int(m[2])) for m in map(LST.match, listing.splitlines())
              if m and m[2]]
    ends = [a for a, _ in starts[1:]] + [vma + len(binary)]
    return {line: binary[a - vma:e - vma] for (a, line), e in zip(starts, ends)}


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--verbose"]
    verbose = len(args) != len(sys.argv) - 1
    if len(args) != 3:
        sys.exit(f"usage: {sys.argv[0]} [--verbose] <listing> <bin> <out.s>")
    original = Path(args[1]).read_bytes()
    insns = parse_listing(Path(args[0]).read_text(), original)

    def report(what: str, idx, got=None) -> None:
        for i in sorted(idx):
            extra = ""
            if got is not None:
                extra = f" (original {insns[i]['data'][:8].hex()}, assembled {got.get(i, b'')[:8].hex()})"
            print(f"  ${insns[i]['addr']:06x} {what}: {insns[i]['text']}{extra}")
    vma = insns[0]["addr"]

    states = []
    for insn in insns:
        try:
            conv = convert(insn["text"])
            states.append(dict(code=conv, combos=size_combos(conv), attempt=0, held=conv[3]))
        except Unsupported:
            states.append(dict(code=None, combos=[()], attempt=0, held=False))

    for npass in range(1, MAX_PASSES + 1):
        text, owner = render(insns, states, vma)
        rc, msgs, listing, binary = assemble(text)
        if rc != 0:
            bad = {owner[int(n)] for n in ERR.findall(msgs) if int(n) in owner}
            if not bad:
                sys.exit(f"error: vasm failed on a line that is not an instruction:\n{msgs}")
            if verbose:
                report("rejected", bad)
            for i in bad:
                next_attempt(states[i])
            print(f"pass {npass}: {len(bad)} line(s) rejected by vasm, retried")
            continue
        got = assembled_bytes(listing, binary, vma)
        per_insn: dict[int, bytes] = {}
        for line, data in got.items():
            if line in owner:
                per_insn[owner[line]] = per_insn.get(owner[line], b"") + data
        wrong = [i for i, insn in enumerate(insns) if per_insn.get(i, b"") != insn["data"]]
        if not wrong and any(s["held"] for s in states):
            for s in states:
                s["held"] = False
            print(f"pass {npass}: every address fixed; branches and PC-relative lines back")
            continue
        if not wrong:
            if binary != original:
                sys.exit("error: every line matches but the whole does not; a bug here")
            Path(args[2]).write_text(text)
            ndata = sum(1 for s in states if s["code"] is None)
            print(f"pass {npass}: all {len(insns)} lines match; "
                  f"{len(insns) - ndata} as instructions, {ndata} as data; wrote {args[2]}")
            return 0
        if verbose:
            report("other bytes", wrong, per_insn)
        for i in wrong:
            next_attempt(states[i])
        print(f"pass {npass}: {len(wrong)} line(s) gave other bytes, retried")
    sys.exit(f"error: no match after {MAX_PASSES} passes")


if __name__ == "__main__":
    sys.exit(main())
