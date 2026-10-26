#!/usr/bin/env python3
"""tools/rody2_runme.py: solution S4 (src/notes/solutions.md §3.4, §4, EPIC-06 STORY-03): Rody and
Mastico 2 started with Rody and Mastico 4's RUNME.TOS.

Usage: rody2_runme.py <RODYM4 folder> <RODYM2 folder>

The two folders are the unpacked downloads RODYM4.ZIP and RODYM2.ZIP from the 8bitchip.info website
(each a folder holding RUNME.TOS or not, HAGE, FILES\\R.ST). Rody and Mastico 2's download has no
RUNME.TOS; its HAGE module is the one Rody and Mastico 4's RUNME.TOS starts. The tool checks both by
SHA-256 and copies RUNME.TOS into the RODYM2 folder; one already there and the same is left as it is,
any other file refuses and nothing is written. Prints the copy's SHA-256.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

RUNME4 = "b7c667cff31895c9f3d5e2aad987f3bac79b51e85cb5e829f2155a6151e2e572"
RODY2 = {"HAGE": "7c1cba215f9e1b5a2878bafc5f8e9ae2db759f78f82f60efca6ef1607313c589",
         "FILES/R.ST": "f586314936db4a3a2f2f0d86be4578d9e28d119d51adcd339909c37614016ed9"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    m4, m2 = Path(sys.argv[1]), Path(sys.argv[2])
    if not (m4 / "RUNME.TOS").is_file() or sha(m4 / "RUNME.TOS") != RUNME4:
        sys.exit(f"error: {m4}: not Rody and Mastico 4's folder (its RUNME.TOS); nothing written")
    for name, digest in RODY2.items():
        if not (m2 / name).is_file() or sha(m2 / name) != digest:
            sys.exit(f"error: {m2}: not Rody and Mastico 2's folder ({name}); nothing written")
    target = m2 / "RUNME.TOS"
    if target.exists():
        if sha(target) != RUNME4:
            sys.exit(f"error: {target}: another RUNME.TOS is there; nothing written")
        print(f"{target}: there already")
    else:
        target.write_bytes((m4 / "RUNME.TOS").read_bytes())
        print(f"{target}: copied from {m4}")
    print(f"  {sha(target)}  {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
