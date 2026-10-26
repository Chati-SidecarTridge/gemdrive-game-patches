#!/usr/bin/env python3
"""tools/set_fastload.py: solution S3 (src/notes/solutions.md §3.3, §4) for Spy vs Spy 2, Strike Force
Harrier and Aquanaut: the fastload bit set in the program each one's start program
runs.

Usage: set_fastload.py <program> <out>

Their start program shrinks its memory with its stack still at the top of RAM, then starts the game.
Hatari's GEMDOS drive clears a program's free memory when its fastload bit (bit 0 of header byte 25)
is clear, the caller's stack with it, and TOS ends the caller. With the bit set the memory stays as
it is. The tool knows each program by its SHA-256: an original gets the bit, a program that has it
already is written as it is (run twice, nothing changes), any other file is refused and nothing is
written. Prints both files' SHA-256.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

# name: (original's SHA-256, with the bit set)
PROGRAMS = {
    "SPY2.BOY": ("1e40edf55f4e6dbfe1f63bfb068403cac4f36900377380113f9ecb6fe7cac742",
                 "96dc8c43efca18ed7b7de56b3d8e066fce2c110bcbbe6079caec2b220effe864"),
    "HARRIER.TOS": ("aa15233b6dfec7df2c56edd92cfba4992095598712d08ae49aef59c5a7711376",
                    "1ecf0199707b32af67ec3c8b8dcd70e05c6cb6eaaf47ea89f578da73bf4e6a93"),
    "AQUANAUT.EXE": ("24bc7d8bf2eff4dbb234bd5583fc5ff0a685576faeb099197a0b6b4e67087dbd",
                     "9b9bfb5774088019d1dce3e056fcdc1ecfb95c4756eb08296620479e98ea5d35"),
}


def main() -> int:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    data = bytearray(src.read_bytes())
    digest = hashlib.sha256(data).hexdigest()
    name = next((n for n, h in PROGRAMS.items() if digest in h), None)
    if name is None:
        sys.exit(f"error: {src}: not {', '.join(PROGRAMS)} as this tool knows them; nothing written")
    if digest == PROGRAMS[name][0]:
        data[25] |= 1
        if hashlib.sha256(data).hexdigest() != PROGRAMS[name][1]:
            sys.exit(f"error: {src}: the result is not the expected {name}; nothing written")
        print(f"{src}: {name}, the fastload bit set")
    else:
        print(f"{src}: {name}, the fastload bit already set")
    out.write_bytes(data)
    for path, d in ((src, src.read_bytes()), (out, bytes(data))):
        print(f"  {hashlib.sha256(d).hexdigest()}  {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
