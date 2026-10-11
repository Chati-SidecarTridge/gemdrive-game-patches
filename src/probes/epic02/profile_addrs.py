#!/usr/bin/env python3
"""EPIC-02 STORY-04: the executed addresses of a profile_probe.py run, sorted by
stage, as lists tools/dev/mksource.py reads (`executed <file>` in a map).

Usage: profile_addrs.py <profile run> <chain run>

<chain run> is a chain_probe.py run of the same setup: its dumps are each stage's
bytes at its entry. An executed address counts for a stage when the opcode word
Hatari ran there (as shown in the profile, from memory at the time it was saved)
equals the stage's own word at that address; the others are listed apart, as
code that changed between load and run (decrypted, patched or overwritten).
LEMLD2's addresses are taken from the "lemld2" profile only (other code runs
where LEMLD2 was once it has jumped to the block) and are written as text offsets, like the block's and the
loader's, whose run addresses are mapped back to LEMLD2's text.

Writes tools/dev/builds/epic02/executed/<stage>.txt and prints a summary.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
LINE = re.compile(r"^([0-9a-f]{8}) ((?:[0-9a-f]{4} ?)+)\s")
BASES = {"st-104": 0x17A88, "ste-162": 0x17A68, "ste-206": 0x1D2E4}
TLEN = 34910


def profiles(text: str) -> dict[str, dict[int, str]]:
    """{profile name: {address: first opcode word}} from hatari.out."""
    out, name = {}, None
    for line in text.splitlines():
        m = re.match(r"> profile save (\w+)\.txt", line)
        if m:
            name = m[1]
            out[name] = {}
            continue
        if line.startswith("Disassembled"):
            name = None
            continue
        if name:
            m = LINE.match(line)
            if m:
                out[name][int(m[1], 16)] = m[2].split()[0]
    return out


def main() -> int:
    if len(sys.argv) != 3:
        sys.exit(__doc__.split("\n\n")[1])
    prof_run, chain_run = Path(sys.argv[1]), Path(sys.argv[2])
    setup = next(s for s in BASES if f"-{s}-" in prof_run.name)
    base = BASES[setup]
    profs = profiles((prof_run / "hatari.out").read_text(errors="replace"))
    dump = lambda f: (chain_run / f).read_bytes()  # noqa: E731
    lem = dump("lemld2.bin")[28:]
    stages = {  # name: (run start, length, bytes at entry, text offset of the run start or None)
        "ls2dd": (0x70000, 7168, dump("ls2dd.bin"), None),
        "d15r": (0xC0100, 91460, dump("d15r.bin"), None),
        "block": (0x80100, 1600, dump("block.bin"), 0x604),
        "loader": (0x85000, 818, dump("loader.bin"), 0x912),
    }
    outdir = REPO / "tools" / "dev" / "builds" / "epic02" / "executed"
    outdir.mkdir(parents=True, exist_ok=True)
    found: dict[str, set[int]] = {"lemld2": set()}
    changed: dict[str, set[int]] = {}
    for a in profs.get("lemld2", {}):
        if base <= a < base + TLEN:
            found["lemld2"].add(a - base)
    for pname, addrs in profs.items():
        for a, word in addrs.items():
            for name, (start, length, data, text) in stages.items():
                if start <= a < start + length:
                    o = a - start
                    same = data[o:o + 2].hex() == word
                    key = "lemld2" if text is not None else name
                    where = text + o if text is not None else a
                    (found if same else changed).setdefault(key, set()).add(where)
    for name, addrs in sorted(found.items()):
        (outdir / f"{name}.txt").write_text("".join(f"${a:x}\n" for a in sorted(addrs)))
    for name, addrs in sorted(changed.items()):
        (outdir / f"{name}-changed.txt").write_text("".join(f"${a:x}\n" for a in sorted(addrs)))
    print(f"profiles: " + ", ".join(f"{k} {len(v)} addresses" for k, v in profs.items()))
    for name in sorted(set(found) | set(changed)):
        print(f"  {name:7} executed as loaded: {len(found.get(name, ())):5}   "
              f"changed since loaded: {len(changed.get(name, ())):5}")
    print(f"wrote {outdir.relative_to(REPO)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
