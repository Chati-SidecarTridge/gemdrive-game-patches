#!/usr/bin/env python3
"""tools/dev/shiftcheck.py: does a source still say the same thing when its code moves?
(EPIC-02 STORY-04).

Usage: tools/dev/shiftcheck.py [--tos] <source.s> <origin>

Assembles the source as it is and with a `nop` inserted before the instruction in
the middle of it, then decodes every instruction of both (tools/dev/m68k.py) and
checks that each branch target, PC-relative operand and absolute long that pointed
into the stage before points to the same place after: the same address if it was
before the nop, two bytes on if it was after. For --tos the relocation tables are
compared the same way. An address written as a number instead of a label shows up
here: it stays put while its target moves. Exit 0 when nothing stayed put.
"""

from __future__ import annotations

import re
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import m68k  # noqa: E402

WORK = HERE / "builds" / "shiftcheck"
LST = re.compile(r"^[0-9A-F]{2}:([0-9A-F]{8}) [0-9A-F]+\s+\t\s*(\d+): \t(\S+)")


def assemble(text: str, name: str, tos: bool) -> tuple[bytes, set[int], dict[int, int]]:
    """(text and data, relocation offsets, {source line: address of its instruction})."""
    WORK.mkdir(parents=True, exist_ok=True)
    src, out, lst = WORK / f"{name}.s", WORK / f"{name}.bin", WORK / f"{name}.lst"
    src.write_text(text)
    cmd = [str(HERE / "asm.sh")] + (["--tos"] if tos else []) + [str(src), str(out), str(lst)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"error: {name} does not assemble:\n{r.stdout}{r.stderr}")
    raw, relocs = out.read_bytes(), set()
    if tos:
        _, tlen, dlen, _, slen = struct.unpack(">HIIII", raw[:18])
        table = 28 + tlen + dlen + slen
        pos, i = struct.unpack(">I", raw[table:table + 4])[0], table + 4
        if pos:
            relocs.add(pos)
            while raw[i]:
                pos += 254 if raw[i] == 1 else raw[i]
                if raw[i] != 1:
                    relocs.add(pos)
                i += 1
        raw = raw[28:28 + tlen + dlen]
    lines = {}
    for line in lst.read_text().splitlines():
        m = LST.match(line)
        if m and not m[3].startswith("dc") and not m[3].startswith("dcb"):
            lines.setdefault(int(m[2]), int(m[1], 16))
    return raw, relocs, lines


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--tos"]
    tos = len(args) != len(sys.argv) - 1
    if len(args) != 2:
        sys.exit(__doc__.split("\n\n")[1])
    text = Path(args[0]).read_text()
    origin = int(args[1].lstrip("$"), 16) if args[1].startswith("$") else int(args[1], 0)
    a_bin, a_rel, a_lines = assemble(text, "before", tos)
    code_lines = sorted(a_lines)
    at_line = code_lines[len(code_lines) // 2]
    at_addr = a_lines[at_line]
    src = text.splitlines()
    src.insert(at_line - 1, "\tnop\t; shiftcheck")
    b_bin, b_rel, b_lines = assemble("\n".join(src) + "\n", "after", tos)
    end = origin + len(a_bin)
    move = lambda x: x + 2 if at_addr <= x < end + 0x100000 else x  # noqa: E731
    bad, checked = [], 0
    for line, a in a_lines.items():
        b = b_lines.get(line + (1 if line >= at_line else 0))
        if b is None:
            continue
        ia, ib = m68k.decode(a_bin, origin, a), m68k.decode(b_bin, origin, b)
        if ia is None or ib is None:
            continue
        checked += 1
        # In a GEMDOS program only relocated longs are addresses (checked below), so
        # its absolute operands are not followed here.
        ra, rb = (ia.pcrel, ib.pcrel) if tos else (ia.refs, ib.refs)
        before = [x for x in ([ia.target] if ia.target is not None else []) + ra
                  if origin <= x < end]
        after = [x for x in ([ib.target] if ib.target is not None else []) + rb]
        for x in before:
            # A label right at the nop may name the nop or the instruction after it.
            if move(x) not in after and not (x == at_addr and x in after):
                bad.append(f"line {line} (${a:x}): ${x:x} should be ${move(x):x}, is {[hex(y) for y in after]}")
    if tos:
        want = {move(r) for r in a_rel}
        if want != b_rel:
            bad.append(f"relocations: {len(want - b_rel)} expected missing, {len(b_rel - want)} unexpected")
        for r in a_rel:
            va = struct.unpack(">I", a_bin[r:r + 4])[0]
            vb = struct.unpack(">I", b_bin[move(r):move(r) + 4])[0]
            if move(va) != vb:
                bad.append(f"relocated long at ${r:x}: ${va:x} became ${vb:x}, expected ${move(va):x}")
    print(f"nop before line {at_line} (${at_addr:x}): {checked} instructions checked, "
          f"{len(bad)} reference(s) that did not move")
    for b in bad[:30]:
        print("  " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
