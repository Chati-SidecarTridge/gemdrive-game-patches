#!/usr/bin/env python3
"""tools/dev/mksource.py: a labelled vasm source for one launcher stage, from its
bytes and a map of what is known about it (EPIC-02 STORY-04).

Usage: tools/dev/mksource.py [--report] <stage.map> <out.s>

The map (one directive per line, `;` starts a comment):

    binary <path>              the bytes the source must give back (relative to the repository);
                               for `format tos`, a GEMDOS program (header, text, relocations)
    format bin|tos             raw binary at `origin`, or a GEMDOS program (text at 0, BSS after)
    origin <addr>              where the bytes run (bin)
    include <file>             an include file for the source (system names, tools/dev/../)
    title <text>               a line of the header comment
    code <addr> [name] [; c]   an entry point: traced through every static branch and call
    data <start> <end> [name]  never code, even if referred to as code
    name <addr> <name> [; c]   a label's name, and the comment above it
    pointers <start> <count> <stride>   a table of code addresses: the long at start +
                               i * stride, for i < count, is traced like a `code` entry and
                               written as dc.l <label>
    executed <path>            addresses Hatari ran (src/probes/epic02/profile_addrs.py), one per
                               line: traced like `code` entries, without becoming labels
    run <start> <end> <addr> <name>   (tos) text start..end is copied to and runs at addr: its
                               absolute references to its own run addresses become
                               `name_run+(label-name)` expressions

Code is what a trace from the `code` entries reaches (tools/dev/m68k.py); the rest is
data. Every branch target, PC-relative operand and, for `tos`, every relocated long
becomes a label; for `bin`, so does every absolute address inside the stage. The
instruction text comes from objdump (tools/dev/disasm.sh) on a copy of the bytes
with the data replaced by NOPs, converted by tools/dev/listing2vasm.py's rules. The
source is then assembled until every line gives back its own bytes; a line that
cannot becomes dc.w with its disassembly in the comment. With --report, prints the
references into the stage that the trace did not reach, to be read and added to the
map as `code` or `data`.
"""

from __future__ import annotations

import re
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
import listing2vasm as l2v  # noqa: E402
import m68k  # noqa: E402

WORK = HERE / "builds" / "mksource"
MAX_PASSES = 40
NUM = r"\$[0-9a-f]+|-?\d+"


def num(s: str) -> int:
    s = s.strip()
    return int(s[1:], 16) if s.startswith("$") else int(s, 0)


class Map:
    def __init__(self, path: Path):
        self.path = path
        self.format, self.origin, self.binary = "bin", 0, None
        self.includes, self.titles = [], []
        self.entries: list[int] = []
        self.roots: list[int] = []
        self.pointer_tables: list[tuple[int, int, int]] = []
        self.data: list[tuple[int, int]] = []
        self.names: dict[int, str] = {}
        self.comments: dict[int, str] = {}
        self.runs: list[tuple[int, int, int, str]] = []
        for n, raw in enumerate(path.read_text().splitlines(), 1):
            body, _, comment = raw.partition(";")
            words = body.split()
            if not words:
                continue
            key, args, comment = words[0], words[1:], comment.strip()
            try:
                if key == "binary":
                    self.binary = REPO / args[0]
                elif key == "format":
                    self.format = args[0]
                elif key == "origin":
                    self.origin = num(args[0])
                elif key == "include":
                    self.includes.append(args[0])
                elif key == "title":
                    self.titles.append(raw.split(None, 1)[1] if len(raw.split(None, 1)) > 1 else "")
                elif key in ("code", "name"):
                    addr = num(args[0])
                    if key == "code":
                        self.entries.append(addr)
                    if len(args) > 1:
                        self.names[addr] = args[1]
                    if comment:
                        self.comments[addr] = comment
                elif key == "data":
                    self.data.append((num(args[0]), num(args[1])))
                    if len(args) > 2:
                        self.names[num(args[0])] = args[2]
                    if comment:
                        self.comments[num(args[0])] = comment
                elif key == "pointers":
                    self.pointer_tables.append((num(args[0]), num(args[1]), num(args[2])))
                    if comment:
                        self.comments[num(args[0])] = comment
                elif key == "executed":
                    f = REPO / args[0]
                    self.roots += [num(x) for x in f.read_text().split()] if f.exists() else []
                elif key == "run":
                    self.runs.append((num(args[0]), num(args[1]), num(args[2]), args[3]))
                    self.names.setdefault(num(args[0]), args[3])
                else:
                    raise ValueError(key)
            except (IndexError, ValueError) as e:
                sys.exit(f"error: {path}:{n}: {raw.strip()} ({e})")
        if self.binary is None:
            sys.exit(f"error: {path}: no binary")


class Stage:
    """The bytes to give back, where they run, and their relocations."""

    def __init__(self, m: Map):
        raw = m.binary.read_bytes()
        self.raw, self.relocs, self.bss = raw, set(), 0
        if m.format == "tos":
            magic, tlen, dlen, blen, slen = struct.unpack(">HIIII", raw[:18])
            self.image = raw[28:28 + tlen + dlen]
            self.base, self.bss = 0, blen
            table = 28 + tlen + dlen + slen
            pos = struct.unpack(">I", raw[table:table + 4])[0]
            i = table + 4
            if pos:
                self.relocs.add(pos)
                while raw[i]:
                    pos += 254 if raw[i] == 1 else raw[i]
                    if raw[i] != 1:
                        self.relocs.add(pos)
                    i += 1
        else:
            self.image, self.base = raw, m.origin
        self.end = self.base + len(self.image)
        self.pointers = {s + i * k for s, n, k in m.pointer_tables for i in range(n)}

    def long(self, addr: int) -> int:
        o = addr - self.base
        return struct.unpack(">I", self.image[o:o + 4])[0]


def trace(st: Stage, m: Map) -> tuple[dict[int, m68k.Insn], set[int], list[str]]:
    """Instructions reached from the entries, labels needed, and problems met."""
    forced = lambda a: any(s <= a < e for s, e in m.data)  # noqa: E731
    insns: dict[int, m68k.Insn] = {}
    covered: dict[int, int] = {}
    targets = [st.long(p) for p in sorted(st.pointers)]
    labels: set[int] = set(m.entries) | {x for x in targets if st.base <= x < st.end}
    problems = []
    work = list(m.roots) + list(m.entries) + [x for x in targets if st.base <= x < st.end]
    while work:
        a = work.pop()
        while a not in insns:
            if not st.base <= a < st.end or forced(a):
                problems.append(f"${a:x}: code expected here, but it is outside or marked data")
                break
            if a in covered:
                problems.append(f"${a:x}: inside the instruction at ${covered[a]:x}")
                break
            ins = m68k.decode(st.image, st.base, a)
            if ins is None:
                problems.append(f"${a:x}: not an instruction")
                break
            insns[a] = ins
            for k in range(1, ins.length):
                covered[a + k] = a
            nxt = a + ins.length
            tgt = to_text(ins.target, m) if ins.target is not None else None
            o = a - st.base
            absolute_jump = (st.image[o] << 8 | st.image[o + 1]) & 0xFF80 == 0x4E80 and not ins.pcrel
            if (tgt is not None and absolute_jump and m.format == "tos" and tgt == ins.target
                    and not any(a < r < a + ins.length for r in st.relocs)):
                tgt = None  # a JMP/JSR to a fixed address outside the program (the game's $400)
            if tgt is not None and ins.kind in ("branch", "call", "jump"):
                if st.base <= tgt < st.end:
                    labels.add(tgt)
                    work.append(tgt)
            if ins.kind in ("jump", "stop"):
                break
            a = nxt
    return insns, labels, problems


def to_text(addr: int, m: Map) -> int:
    """An address as the stage sees it: a run address back to its text address."""
    for start, end, run, _ in m.runs:
        if run <= addr < run + (end - start):
            return start + (addr - run)
    return addr


def later_cpu(st: Stage, ins: m68k.Insn) -> str | None:
    """The name of a 68010/68030 instruction vasm -m68000 cannot take, else None."""
    o = ins.addr - st.base
    op = st.image[o] << 8 | st.image[o + 1]
    if op in (0x4E7A, 0x4E7B):
        return "movec (68010 and later)"
    if (op & 0xFFC0) == 0xF000:
        return "pmove (68030 MMU)"
    return None


def masked(st: Stage, insns: dict[int, m68k.Insn]) -> bytes:
    """The image with everything that is not traced 68000 code replaced by NOPs, so
    that objdump's linear disassembly stays on the traced instructions."""
    out = bytearray(b"\x4e\x71" * ((len(st.image) + 1) // 2))[:len(st.image)]
    for a, ins in insns.items():
        if later_cpu(st, ins) is None:
            o = a - st.base
            out[o:o + ins.length] = st.image[o:o + ins.length]
    return bytes(out)


def objdump_text(st: Stage, insns: dict[int, m68k.Insn]) -> dict[int, str]:
    WORK.mkdir(parents=True, exist_ok=True)
    binf, lst = WORK / "masked.bin", WORK / "masked.lst"
    binf.write_bytes(masked(st, insns))
    subprocess.run([str(HERE / "disasm.sh"), str(binf), hex(st.base), str(lst)],
                   check=True, capture_output=True)
    text = {}
    for line in lst.read_text().splitlines():
        mm = l2v.INSN.match(line)
        if mm and int(mm[1], 16) in insns:
            text[int(mm[1], 16)] = mm[3].strip()
    return text


class Symbols:
    def __init__(self, st: Stage, m: Map, labels: set[int], insns: dict[int, m68k.Insn]):
        self.st, self.m = st, m
        self.labels = set(labels)
        self.system: dict[int, str] = {}  # the include files' equates, for absolute operands
        for inc in m.includes:
            for line in (REPO / inc).read_text().splitlines():
                mm = re.match(r"(\w+)\s+equ\s+\$([0-9a-f]+)", line)
                if mm:
                    self.system.setdefault(int(mm[2], 16), mm[1])
        self.inside: dict[int, int] = {}  # label address -> instruction it falls in
        for a, ins in insns.items():
            for k in range(1, ins.length):
                self.inside[a + k] = a

    def name(self, addr: int) -> str:
        return self.m.names.get(addr) or (f"L_{addr:x}" if addr < self.st.end else f"B_{addr:x}")

    def reloc(self, value: int) -> str:
        """A relocated long: a label, or past the program's end an offset from the end
        of its BSS (LEMLD2 has one: a buffer in the free memory after it)."""
        top = self.st.end + self.st.bss
        if value >= top or value < self.st.base:
            return f"end_of_bss+${value - top:x}" if self.st.bss and value >= top else f"${value:x}"
        return self.ref(value, run_ok=False) or f"{self.name(self.st.base)}+${value - self.st.base:x}"

    def ref(self, value: int, run_ok: bool = True) -> str | None:
        """The symbol for an address the stage refers to, or None."""
        st, m = self.st, self.m
        if run_ok:
            for start, end, run, rname in m.runs:
                if run <= value < run + (end - start):
                    t = start + (value - run)
                    self.labels.add(t)
                    return f"{rname}_run" if t == start else f"{rname}_run+({self.name(t)}-{rname})"
        if st.base <= value < st.end + st.bss:
            self.labels.add(value)
            return self.name(value)
        return None


def readable(op: str, m: re.Match) -> str:
    """An immediate as objdump gives it (decimal) made readable: four printable bytes
    as characters ("PPHD"), other values above 255 in hex. The same bytes either way."""
    if not m[1] or m[2].startswith("$"):
        return op
    v = int(m[2])
    if v < 0 or v <= 255:
        return op
    b = v.to_bytes(4, "big") if v <= 0xFFFFFFFF else b""
    if len(b) == 4 and all(0x20 < c < 0x7F and c not in b"'\\" for c in b):
        return f"#'{b.decode()}'"
    return f"#${v:x}"


def operand_symbol(op: str, sym: Symbols, conv_abs: bool, reloc_vals: set[int] | None,
                   is_branch: bool, is_jump: bool = False) -> str:
    """Replace the number in one Motorola operand by a symbol where it is an address."""
    st = sym.st
    m = re.fullmatch(rf"\(({NUM}),pc(,.*)?\)", op)
    if m:  # PC-relative: the number is the target address
        s = sym.ref(num(m[1]), run_ok=False) or m[1]
        return f"({s},pc{m[2] or ''})"
    m = re.fullmatch(rf"(#)?({NUM})", op)
    if not m:
        return op
    value = num(m[2]) & 0xFFFFFFFF
    op = readable(op, m)
    if is_branch:
        return sym.ref(value, run_ok=False) or m[2]
    if reloc_vals is not None:  # tos: only relocated longs are addresses inside
        if conv_abs and value not in reloc_vals and value in sym.system and not is_jump:
            return sym.system[value]
        if value in reloc_vals:
            return f"{m[1] or ''}{sym.reloc(value)}"
        s = sym.ref(value) if any(r <= value < r + (e - b) for b, e, r, _ in sym.m.runs) else None
        return f"{m[1] or ''}{s}" if s else op
    if m[1] and len(m[2]) <= 5:  # a small immediate: a number, not an address
        return op
    s = sym.ref(value)
    if s is None and conv_abs and not is_jump:  # $400 jumped to is code, not etv_timer
        s = sym.system.get(value) or sym.system.get(value | 0xFF000000)
    return f"{m[1] or ''}{s}" if s else op


def build(m: Map, report: bool) -> tuple[str, list[str]]:
    st = Stage(m)
    insns, labels, problems = trace(st, m)
    texts = objdump_text(st, insns)
    sym = Symbols(st, m, labels, insns)
    for a in m.names:
        sym.labels.add(a)

    # Per instruction: converted form and the symbolised operands.
    lines: dict[int, dict] = {}
    for a, ins in sorted(insns.items()):
        text = None if later_cpu(st, ins) else texts.get(a)
        entry = dict(addr=a, data=st.image[a - st.base:a - st.base + ins.length],
                     text=later_cpu(st, ins) or text or "?")
        try:
            if text is None:
                raise l2v.Unsupported("no objdump line")
            mnem, ops, absolute, pcdep = l2v.convert(text)
            reloc_vals = None
            if m.format == "tos":
                reloc_vals = {st.long(r) for r in st.relocs if a <= r < a + ins.length}
            branch = mnem.split(".")[0] in l2v.BRANCHES or mnem.startswith("db")
            if not absolute:
                entry["combos"] = [()]
            elif len(ins.abs_sizes) == len(absolute):  # the sizes the bytes were encoded with
                entry["combos"] = [tuple(ins.abs_sizes)]
            else:
                entry["combos"] = l2v.size_combos((mnem, ops, absolute, pcdep))
            jump = mnem in ("jmp", "jsr")
            ops = [operand_symbol(o, sym, i in absolute, reloc_vals, branch, jump)
                   for i, o in enumerate(ops)]
            entry["code"] = (mnem, ops, absolute, pcdep or branch)
        except l2v.Unsupported:
            entry["code"] = None
        lines[a] = entry
    # Relocated longs inside data (tos), and absolute in-stage longs where the map says so.
    data_relocs = {r for r in st.relocs | st.pointers
                   if not any(a <= r < a + i.length for a, i in insns.items())}
    for r in data_relocs:
        sym.reloc(st.long(r))

    if report:
        reached = set(insns)
        refs = set()
        for ins in insns.values():
            for r in ins.refs:
                t = to_text(r, m)
                if st.base <= t < st.end and t not in reached:
                    refs.add(t)
        for r in data_relocs:
            t = st.long(r)
            if st.base <= t < st.end and t not in reached:
                refs.add(t)
        problems += [f"${t:x}: referred to, not traced" for t in sorted(refs)
                     if not any(s <= t < e for s, e in m.data)]
    return render_all(st, m, sym, lines, data_relocs), problems


def data_chunks(st: Stage, start: int, end: int, cut: set[int], relocs: set[int], sym: Symbols):
    """Source lines for the data bytes start..end, split at labels."""
    out = []
    a = start
    while a < end:
        nxt = min([c for c in cut if a < c < end] + [end])
        b = st.image[a - st.base:nxt - st.base]
        i = 0
        while i < len(b):
            p = a + i
            if p in relocs and i + 4 <= len(b):
                out.append((p, f"dc.l\t{sym.reloc(st.long(p))}"))
                i += 4
                continue
            z = 0
            while i + z < len(b) and b[i + z] == 0 and p + z not in relocs:
                z += 1
            if z >= 8:
                out.append((p, f"dcb.b\t{z},0"))
                i += z
                continue
            t = 0
            while i + t < len(b) and 0x20 <= b[i + t] < 0x7F and b[i + t] != 0x22 and p + t not in relocs:
                t += 1
            if t >= 4:
                out.append((p, f'dc.b\t"{b[i:i + t].decode()}"'))
                i += t
                continue
            n = 1
            while i + n < len(b) and n < 16 and (a + i + n) not in relocs:
                n += 1
            out.append((p, "dc.b\t" + ",".join(f"${x:02x}" for x in b[i:i + n])))
            i += n
        a = nxt
    return out


def render_all(st, m, sym, lines, data_relocs):
    return dict(st=st, m=m, sym=sym, lines=lines, relocs=data_relocs)


def render(ctx, states) -> tuple[str, dict[int, int]]:
    st, m, sym, lines = ctx["st"], ctx["m"], ctx["sym"], ctx["lines"]
    out = [f"; {t}" for t in m.titles] + [
        f"; Source made by tools/dev/mksource.py from {m.path.relative_to(REPO)}; reassembles",
        "; to the original bytes (tools/dev/roundtrip.sh). A dc.w line with a disassembly in",
        "; its comment is an instruction that does not reassemble as written.", ""]
    out += [f'\tinclude\t"{inc}"' for inc in m.includes]
    for start, end, run, rname in m.runs:
        out.append(f"{rname}_run\tequ\t${run:x}")
    if m.format == "tos":
        out.append("\tsection\ttext")
    else:
        out.append(f"\torg\t${st.base:x}")
    owner: dict[int, int] = {}
    code_addrs = sorted(lines)
    cut = set(sym.labels) | set(code_addrs) | {st.end}
    for s, e in m.data:
        cut |= {s, e}
    equs = []
    a = st.base
    while a < st.end:
        if a in lines and any(a + k in sym.labels for k in range(1, len(lines[a]["data"]))):
            sym.labels.add(a)  # a label inside this instruction is defined from its start
        if a in sym.labels and a not in sym.inside:
            if a in m.comments:
                out.append(f"; {m.comments[a]}")
            out.append(f"{sym.name(a)}:")
        if a in lines:
            e = lines[a]
            stt = states[a]
            if stt["code"] is None or stt["held"]:
                note = "" if e["text"].startswith(".") else f"  {e['text']}"
                body = l2v.data_line(dict(data=e["data"], text=e["text"]))
            else:
                body, note = l2v.code_line(stt["code"], stt["combos"][stt["attempt"]]), ""
            first = len(out) + 1
            for j, part in enumerate(body.split("\n\t")):
                c = f"; ${a:06x}{note}" if j == 0 else ""
                out.append(f"\t{part}\t{c}".rstrip())
                owner[first + j] = a
            for k in range(1, len(e["data"])):
                if a + k in sym.labels:
                    equs.append(f"{sym.name(a + k)}\tequ\t{sym.name(a)}+{k}")
            a += len(e["data"])
            continue
        nxt = min([c for c in cut if c > a])
        for p, text in data_chunks(st, a, nxt, cut, ctx["relocs"], sym):
            out.append(f"\t{text}\t; ${p:06x}")
        a = nxt
    if st.bss:
        out.append("\tsection\tbss")
        b = st.end
        for lab in sorted(x for x in sym.labels if x >= st.end):
            if lab > b:
                out.append(f"\tds.b\t{lab - b}")
            out.append(f"{sym.name(lab)}:")
            b = lab
        if st.end + st.bss > b:
            out.append(f"\tds.b\t{st.end + st.bss - b}")
        out.append("end_of_bss:")
    out += equs
    return "\n".join(out) + "\n", owner


def assemble(src_text: str, tos: bool):
    WORK.mkdir(parents=True, exist_ok=True)
    src, outf, lst = WORK / "pass.s", WORK / "pass.bin", WORK / "pass.lst"
    src.write_text(src_text)
    for f in (outf, lst):
        f.unlink(missing_ok=True)
    cmd = [str(HERE / "asm.sh")] + (["--tos"] if tos else []) + [str(src), str(outf), str(lst)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return (r.returncode, r.stdout + r.stderr, lst.read_text() if lst.exists() else "",
            outf.read_bytes() if outf.exists() else b"")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--report"]
    report = len(args) != len(sys.argv) - 1
    if len(args) != 2:
        sys.exit(__doc__.split("\n\n")[1])
    m = Map(Path(args[0]).resolve())
    ctx, problems = build(m, report)
    for p in problems:
        print("  " + p)
    st, lines = ctx["st"], ctx["lines"]
    tos = m.format == "tos"
    states = {}
    for a, e in lines.items():
        conv = e["code"]
        if conv is None:
            states[a] = dict(code=None, combos=[()], attempt=0, held=False)
        else:
            states[a] = dict(code=conv, combos=e["combos"], attempt=0, held=conv[3])
    for npass in range(1, MAX_PASSES + 1):
        text, owner = render(ctx, states)
        rc, msgs, listing, binary = assemble(text, tos)
        if rc != 0:
            bad = {owner[int(n)] for n in l2v.ERR.findall(msgs) if int(n) in owner}
            if not bad:
                Path(args[1]).write_text(text)
                sys.exit(f"error: vasm failed outside the instructions (source left in {args[1]}):\n{msgs[:3000]}")
            for a in bad:
                l2v.next_attempt(states[a])
            print(f"pass {npass}: {len(bad)} line(s) rejected by vasm, retried")
            continue
        image = binary[28:28 + len(st.image)] if tos else binary
        starts = [(int(mm[1], 16), int(mm[2])) for mm in map(l2v.LST.match, listing.splitlines())
                  if mm and mm[2]]
        got: dict[int, bytes] = {}
        ends = [x for x, _ in starts[1:]] + [st.base + len(image)]
        for (addr, line), end in zip(starts, ends):
            if line in owner:
                a = owner[line]
                got[a] = got.get(a, b"") + image[addr - st.base:end - st.base]
        wrong = [a for a, e in lines.items() if got.get(a, b"") != e["data"]]
        if not wrong and any(s["held"] for s in states.values()):
            for s in states.values():
                s["held"] = False
            print(f"pass {npass}: every address fixed; branches and PC-relative lines back")
            continue
        if not wrong:
            whole = binary if tos else binary
            ok = whole == st.raw
            Path(args[1]).write_text(text)
            ndata = sum(1 for s in states.values() if s["code"] is None)
            print(f"pass {npass}: {len(lines)} instructions, {len(lines) - ndata} as code, "
                  f"{ndata} as dc.w; whole file {'matches' if ok else 'DIFFERS'}; wrote {args[1]}")
            return 0 if ok else 1
        for a in wrong:
            l2v.next_attempt(states[a])
        print(f"pass {npass}: {len(wrong)} line(s) gave other bytes, retried")
    sys.exit(f"error: no match after {MAX_PASSES} passes")


if __name__ == "__main__":
    sys.exit(main())
