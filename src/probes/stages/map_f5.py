#!/usr/bin/env python3
"""D15R_F5's likely code addresses, from D15R_H5's executed ones.

Usage: map_f5.py

No ST or STE runs D15R_F5 (the Falcon build), so it has no profile of
its own. Each address Hatari ran in D15R_H5 is carried over to D15R_F5 when the
16 bytes from there occur exactly once in D15R_F5. Writes
tools/dev/builds/stages/executed/d15r_f5.txt (addresses at $C0100).
"""

from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
W = REPO / "tools" / "dev" / "builds" / "stages"
K, ORG = 16, 0xC0100

h5 = (W / "unpacked" / "D15R_H5.bin").read_bytes()
f5 = (W / "unpacked" / "D15R_F5.bin").read_bytes()
seen: dict[bytes, int] = {}
for i in range(0, len(f5) - K + 1, 2):
    w = f5[i:i + K]
    seen[w] = -1 if w in seen else i
out, missed = [], 0
for line in (W / "executed" / "d15r.txt").read_text().split():
    o = int(line[1:], 16) - ORG
    j = seen.get(h5[o:o + K], -1)
    if j >= 0:
        out.append(ORG + j)
    else:
        missed += 1
(W / "executed" / "d15r_f5.txt").write_text("".join(f"${a:x}\n" for a in sorted(set(out))))
print(f"{len(set(out))} addresses carried over to D15R_F5, {missed} without a unique match")
