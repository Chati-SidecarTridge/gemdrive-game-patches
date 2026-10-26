#!/usr/bin/env python3
"""D15R against the TOS 1.04 ROM it was made from.

Usage: d15r_vs_tos.py [H5|F5]

Aligns D15R (unpacked, at $C0100) with TOS_ST_104 (tools/dev/dev.cfg; TOS 1.04 UK, at $FC0000)
and classifies every byte of D15R:

  same        the ROM's byte at the aligned place
  relocated   part of a long that is a ROM address in the ROM and the corresponding D15R
              address in D15R (the copy was relocated from $FC0000 to around $C0100), or an
              address in TOS's RAM (below $10000) in the ROM and that address + $D0528 in
              D15R (D15R keeps TOS's RAM in its own image there; swap_low_ram swaps $8-$7FF)
  other       neither: PP's own code and data, or his changes to TOS's

The alignment comes from 16-byte runs found in both (anchors); between anchors the last
offset holds. Prints the totals and every run of "other" bytes of 8 bytes or more, with the
labels of src/d15r/d15r_<build>.s that fall in it. Standard library only.
"""

import re
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools" / "dev"))
from devcfg import cfg  # noqa: E402

ORG, ROM_BASE, K = 0xC0100, 0xFC0000, 16
RAM_IMAGE = 0xD0528  # D15R's image of TOS's low RAM: TOS's address + this


def main() -> int:
    build = (sys.argv[1] if len(sys.argv) > 1 else "H5").upper()
    d = (REPO / "tools" / "dev" / "builds" / "stages" / "unpacked" / f"D15R_{build}.bin").read_bytes()
    rom = Path(cfg("TOS_ST_104")).read_bytes()
    idx: dict[bytes, int] = {}
    for i in range(0, len(rom) - K, 2):
        idx.setdefault(rom[i:i + K], i)
    # anchors: D15R offset -> ROM offset - D15R offset
    delta_at = [None] * len(d)
    for i in range(0, len(d) - K, 2):
        w = d[i:i + K]
        j = idx.get(w)
        if j is not None and len(set(w)) > 3:
            for k in range(K):
                delta_at[i + k] = j - i
    last = None
    for i in range(len(d)):  # carry the last offset forward between anchors
        if delta_at[i] is None:
            delta_at[i] = last
        else:
            last = delta_at[i]
    deltas = {x for x in delta_at if x is not None}
    kind = ["other"] * len(d)
    for i in range(len(d)):
        dl = delta_at[i]
        if dl is not None and 0 <= i + dl < len(rom) and d[i] == rom[i + dl]:
            kind[i] = "same"
    for i in range(0, len(d) - 3, 2):  # relocated longs
        if all(kind[i + k] == "same" for k in range(4)):
            continue
        dl = delta_at[i]
        if dl is None or not 0 <= i + dl <= len(rom) - 4:
            continue
        vd = struct.unpack(">I", d[i:i + 4])[0]
        vr = struct.unpack(">I", rom[i + dl:i + dl + 4])[0]
        rom_ref = ORG <= vd < ORG + len(d) and ROM_BASE <= vr < ROM_BASE + len(rom) \
            and (vr - ROM_BASE) - (vd - ORG) in deltas
        ram_ref = vr < 0x10000 and vd == vr + RAM_IMAGE
        if rom_ref or ram_ref:
            for k in range(4):
                kind[i + k] = "relocated"
    total = {k: kind.count(k) for k in ("same", "relocated", "other")}
    print(f"D15R_{build}: {len(d)} bytes; TOS 1.04 ({Path(cfg('TOS_ST_104')).name})")
    for k, v in total.items():
        print(f"  {k:9} {v:6} bytes ({100 * v / len(d):.1f}%)")
    labels = {}
    src = REPO / "src" / "d15r" / f"d15r_{build.lower()}.s"
    if src.exists():
        cur = None
        for line in src.read_text().splitlines():
            m = re.match(r"^([A-Za-z_]\w*):", line)
            if m:
                cur = m[1]
            m = re.search(r"; \$([0-9a-f]{6})", line)
            if m and cur:
                labels.setdefault(cur, int(m[1], 16))
    by_addr = sorted((a, n) for n, a in labels.items() if not n.startswith("L_"))
    print("  runs of other bytes (8 or more):")
    i = 0
    while i < len(d):
        if kind[i] != "other":
            i += 1
            continue
        j = i
        while j < len(d) and kind[j] == "other":
            j += 1
        if j - i >= 8:
            a, b = ORG + i, ORG + j
            inside = [n for x, n in by_addr if a <= x < b]
            before = [n for x, n in by_addr if x <= a][-1:] if not inside else []
            zero = " (zeros)" if not any(d[i:j]) else ""
            print(f"    ${a:06x}-${b - 1:06x} {j - i:6} bytes{zero}  {', '.join(inside[:6] or ['in ' + x for x in before])}")
        i = j
    return 0


if __name__ == "__main__":
    sys.exit(main())
