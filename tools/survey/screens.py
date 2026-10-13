#!/usr/bin/env python3
"""EPIC-03 STORY-05: is this Hatari screenshot the TOS desktop?

Usage: screens.py <png> ...                  the verdict and the score for each screenshot
       screens.py --learn <name> <png>       keep that screenshot's menu bar as a desktop's

The desktop is told by its menu bar ("Desk File View Options"), not by its colours: a game or
PP's TOS in RAM may leave other colours in the palette. Hatari saves palette PNGs; the menu bar is
the top 20 lines of the ST screen (from line 58 in an 832x552 screenshot with borders, from line 0
in a 640x400 one), and its mask is every pixel whose palette index is not the band's most common
one: the text, whatever its colour (a palette index, or an RGB value when Hatari saved one). A screenshot is the desktop when its mask overlaps one of the
learned desktop masks (tools/survey/desktops.txt, one per resolution: low, medium, high) by at
least MATCH (common ink over all ink, the best within a few pixels of shift). A GEM program's own
menu bar ("Desk Spiel Voreinstellung …") does not. Standard library only.
"""

from __future__ import annotations

import collections
import struct
import sys
import zlib
from pathlib import Path

LEARNED = Path(__file__).with_name("desktops.txt")
BAND = 20
MATCH = 0.85  # common ink over all ink, against a learned desktop menu bar
SHIFT = 4      # pixels of shift tried each way


def read_png(path: Path) -> tuple[int, int, list[list[bytes]]]:
    """Width, height and rows of pixels (each pixel the bytes of its value: a palette index, or
    RGB/RGBA) of an 8-bit PNG, the kinds Hatari saves."""
    data = path.read_bytes()
    pos, idat, size = 8, b"", None
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            size = struct.unpack(">IIBB", body[:10])
        elif kind == b"IDAT":
            idat += body
    w, h, depth, ctype = size
    bpp = {3: 1, 0: 1, 2: 3, 6: 4, 4: 2}.get(ctype)
    if depth != 8 or bpp is None:
        raise ValueError(f"{path}: an {depth}-bit PNG of colour type {ctype}")
    stride = w * bpp
    raw, rows, prev, i = zlib.decompress(idat), [], bytearray(stride), 0
    for _ in range(h):
        kind, line = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if kind == 1:
                line[x] = (line[x] + a) & 255
            elif kind == 2:
                line[x] = (line[x] + b) & 255
            elif kind == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif kind == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append([bytes(line[x:x + bpp]) for x in range(0, stride, bpp)])
        prev = line
    return w, h, rows


def menu_mask(path: Path) -> str:
    """The menu bar's mask as a string of 0 and 1, with the screenshot's size in front."""
    w, h, rows = read_png(path)
    x0, y0 = ((w - 640) // 2, 58) if (w, h) == (832, 552) else (0, 0)
    band = [r[x0:x0 + 640] for r in rows[y0:y0 + BAND]]
    background = collections.Counter(v for r in band for v in r).most_common(1)[0][0]
    return f"{w}x{h}:" + "".join("1" if v != background else "0" for r in band for v in r)


def learned() -> dict[str, str]:
    if not LEARNED.exists():
        return {}
    return dict(line.split(" ", 1) for line in LEARNED.read_text().splitlines() if line.strip())


def ink(mask: str) -> set[tuple[int, int]]:
    return {(i % 640, i // 640) for i, bit in enumerate(mask.split(":")[1]) if bit == "1"}


def score(path: Path) -> tuple[float, str]:
    """The best overlap with a learned desktop menu bar (common ink over all ink, within SHIFT
    pixels of shift), and which one."""
    mask = menu_mask(path)
    here = ink(mask)
    best = (0.0, "")
    for name, ref in learned().items():
        if ref.split(":")[0] != mask.split(":")[0] or not here:
            continue
        there = ink(ref)
        for dx in range(-SHIFT, SHIFT + 1):
            for dy in range(-SHIFT, SHIFT + 1):
                moved = {(x + dx, y + dy) for x, y in here}
                best = max(best, (len(moved & there) / len(moved | there), name))
    return best


def is_desktop(path: Path) -> bool:
    return score(path)[0] >= MATCH


def blank(path: Path) -> bool:
    """Is the ST screen (inside the borders) one colour, nothing on it?"""
    w, h, rows = read_png(path)
    x0, y0 = ((w - 640) // 2, 58) if (w, h) == (832, 552) else (0, 0)
    return len({v for r in rows[y0:y0 + 400] for v in r[x0:x0 + 640]}) == 1


def desktop_items(path: Path) -> int:
    """How much stands out on the desktop under its menu bar: the pixels that differ from the one
    two rows up and from the one two columns left (the desktop's background is a pattern that
    repeats every two pixels). An empty desktop (no drive icon, no window) leaves only the mouse
    pointer's few hundred; a desktop with its drives or a window open leaves thousands."""
    w, h, rows = read_png(path)
    x0, y0 = ((w - 640) // 2, 58) if (w, h) == (832, 552) else (0, 0)
    count = 0
    for y in range(y0 + BAND + 4, y0 + 400):
        r, up = rows[y], rows[y - 2]
        for x in range(x0 + 2, x0 + 640):
            if r[x] != up[x] and r[x] != r[x - 2]:
                count += 1
    return count


def main() -> int:
    if sys.argv[1:2] == ["--learn"]:
        name, png = sys.argv[2], Path(sys.argv[3])
        table = learned()
        table[name] = menu_mask(png)
        LEARNED.write_text("".join(f"{k} {v}\n" for k, v in sorted(table.items())))
        print(f"learned {name} from {png}")
        return 0
    for png in sys.argv[1:]:
        agree, name = score(Path(png))
        print(f"{'desktop' if agree >= MATCH else 'not desktop':12} {agree:.4f} {name:14} {png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
