#!/usr/bin/env python3
"""EPIC-01: read a gate_probe.py run folder. Prints the breakpoint hits with
their dumps, in order, and writes the traced instruction windows (cpu_disasm
and I/O lines) to <run>/windows.txt.

Usage: read_probe.py <run folder>
"""

import re
import sys
from pathlib import Path

TRACE = re.compile(r"^(GEMDOS|BIOS|XBIOS|HDC|Gemdos_Boot)|repeats of: ")
NOISE = re.compile(r"^(Reading debugger|Changed (to|back)|Removed CPU|-> |\(PC\)$|CPU condition breakpoint|> b )")
WINDOW = re.compile(r"^(\$[0-9a-f]{8} :|[0-9a-f]{8} [0-9a-f]{4} |IO (read|write)\.)")


def main() -> int:
    run = Path(sys.argv[1])
    out = run / "windows.txt"
    chain, windows, hits = [], [], 0
    started = False
    for line in (run / "hatari.out").read_text(errors="replace").splitlines():
        if "breakpoint condition(s) matched" in line:
            started = True
            hits += 1
            chain.append(f"--- hit {hits}")
            continue
        if not started or TRACE.search(line) or NOISE.match(line):
            continue
        if WINDOW.match(line) or line.startswith("$"):
            windows.append(line)
            continue
        chain.append(line.rstrip())
    out.write_text("\n".join(windows) + "\n")
    print("\n".join(chain))
    print(f"[{len(windows)} traced lines in {out}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
