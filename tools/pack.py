#!/usr/bin/env python3
"""tools/pack.py: the Gamex launcher's packer, rebuilt (EPIC-02 STORY-03).

    pack.py fic <in.bin> <out.FIC> <like.FIC> [--pad]
        a .FIC with <like.FIC>'s name and +10 field
    pack.py start <LEMLD2.TOS> <out.TOS> <like.TOS> [--stub <stub.bin>] [--pad]
        START.TOS: the stub (<like.TOS>'s, or the 230 bytes assembled from src/start/start.s),
        its size constants set for the new payload, <like.TOS>'s header otherwise

--pad fills the file with zeros up to <like>'s length, so that a rebuilt launcher takes the
same clusters on a disk as PP's and the reference's record numbers stay put (EPIC-02 STORY-06);
the unpacking code stops at the stream's end byte and never sees them.

The stream format is tools/unpack.py's (src/notes/launcher-formats.md). PP's packer is unknown,
so the output is not byte-identical to his; it is an optimal parse of the same format, never
longer than his for the launcher's files, which matters: LEMLD2 reads LS2DD.FIC with a fixed
count of 4,929 bytes and D15R_*.FIC into a 51,000-byte buffer.
"""

from __future__ import annotations

import os
import struct
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import unpack  # noqa: E402

MAX_LIT, SHORT_DIST, LONG_DIST = 127, 255, 65535
SHORT_MAX, LONG_MAX = 0x3F + 3, 0x3F + 4
CHAIN = 512  # candidates tried per position

# START.TOS's stub (src/notes/launcher-formats.md): file offsets of the longs it computes with.
STUB_TEXT_DATA = 28 + 0x08  # adda.l #text+data,a0: end of the packed stream
STUB_TOP = 28 + 0x10        # adda.l #$8D40,a6: where the stream is copied down to
STUB_LONGS = 28 + 0x18      # move.l #2203,d2: longs copied


def matches(data: bytes) -> list[tuple[int, int, int, int]]:
    """Per position: the longest match within SHORT_DIST and the longest within LONG_DIST, as
    (short length, short distance, long length, long distance); lengths below the minimum are 0."""
    n = len(data)
    heads: dict[bytes, list[int]] = {}
    found = []
    for i in range(n):
        key = data[i:i + 3]
        cands = heads.setdefault(key, []) if len(key) == 3 else []
        s_len = s_dist = l_len = l_dist = 0
        limit_s, limit_l = min(SHORT_MAX, n - i), min(LONG_MAX, n - i)
        target = data[i:i + limit_l]
        for j in reversed(cands[-CHAIN:]):
            dist = i - j
            if dist > LONG_DIST:
                break
            length = len(os.path.commonprefix([data[j:j + limit_l], target]))
            if dist <= SHORT_DIST and length > s_len:
                s_len, s_dist = min(length, limit_s), dist
            if length > l_len:
                l_len, l_dist = length, dist
            if l_len == limit_l and (s_len == limit_s or dist > SHORT_DIST):
                break
        found.append((s_len if s_len >= 3 else 0, s_dist, l_len if l_len >= 4 else 0, l_dist))
        if len(key) == 3:
            cands.append(i)
    return found


def pack(data: bytes) -> bytes:
    """The shortest stream of this format that unpacks to data, end byte included."""
    n = len(data)
    found = matches(data)
    INF = 1 << 60
    cost = [INF] * (n + 1)
    step: list[tuple] = [()] * (n + 1)
    cost[n] = 1  # the end byte
    window: deque[int] = deque()  # positions j > i ordered by cost[j] + j, for literal runs
    for i in range(n - 1, -1, -1):
        j = i + 1
        while window and cost[window[-1]] + window[-1] >= cost[j] + j:
            window.pop()
        window.append(j)
        while window[0] > i + MAX_LIT:
            window.popleft()
        best, how = cost[window[0]] + window[0] - i + 1, ("lit", window[0] - i)
        s_len, s_dist, l_len, l_dist = found[i]
        for length in range(3, s_len + 1):
            if cost[i + length] + 2 < best:
                best, how = cost[i + length] + 2, ("short", length, s_dist)
        for length in range(4, l_len + 1):
            if cost[i + length] + 3 < best:
                best, how = cost[i + length] + 3, ("long", length, l_dist)
        cost[i], step[i] = best, how
    out = bytearray()
    i = 0
    while i < n:
        how = step[i]
        if how[0] == "lit":
            out.append(how[1])
            out += data[i:i + how[1]]
            i += how[1]
        elif how[0] == "short":
            out += bytes((0x80 | (how[1] - 3), how[2]))
            i += how[1]
        else:
            out += bytes((0xC0 | (how[1] - 4), how[2] >> 8, how[2] & 0xFF))
            i += how[1]
    out.append(0)
    if len(out) != cost[0] or unpack.depack(bytes(out)) != data:
        sys.exit("error: internal: the stream does not unpack to its input")
    return bytes(out)


def header(packed: int, unpacked: int, like: bytes) -> bytes:
    """A "C3" header with the sizes of this stream and like's +10 field and name."""
    return b"C3" + struct.pack(">II", packed, unpacked) + like[10:32]


def in_place_margin(stream: bytes, top: int, out_start: int = -28) -> int:
    """The stub unpacks in place: the stream ends at text+top and the output starts at
    text-28. The smallest gap between the next byte to read and the next byte to write."""
    read, write, i, margin = top - len(stream), out_start, 0, top
    while True:
        c = stream[i]
        size = 1 if c == 0 else 1 + c if c < 0x80 else 3 if c & 0x40 else 2
        produced = 0 if c == 0 else c if c < 0x80 else (c & 0x3F) + (4 if c & 0x40 else 3)
        read, write, i = read + size, write + produced, i + size
        margin = min(margin, read - write)
        if c == 0:
            return margin


def build_start(prog: bytes, like: bytes, stub_text: bytes | None = None,
                raise_top: bool = False) -> bytes:
    stream = pack(prog)
    payload_header = bytearray(header(len(stream), len(prog), like[28 + 230:28 + 230 + 32]))
    payload_header[10:14] = prog[10:14]  # +10: the program's BSS size, from its own header
    data = bytes(payload_header) + stream
    data += b"\0" * (-(len(data) - 32) % 4)  # the stub copies the stream as longs
    stub = bytearray(like[:28] + (stub_text if stub_text is not None else like[28:28 + 230]))
    if len(stub) != 28 + 230:
        sys.exit("error: the stub must be 230 bytes")
    top = struct.unpack(">I", stub[STUB_TOP:STUB_TOP + 4])[0]
    margin = in_place_margin(data[32:], top)
    if margin < 0 and raise_top:  # a longer program: copy the stream higher (EPIC-04 STORY-04)
        top += (-margin + 3) & ~3
        struct.pack_into(">I", stub, STUB_TOP, top)
        margin = in_place_margin(data[32:], top)
    if margin < 0:
        sys.exit(f"error: the stream would overwrite itself while unpacking (margin {margin})")
    struct.pack_into(">I", stub, 6, len(data))                       # header: data size
    struct.pack_into(">I", stub, STUB_TEXT_DATA, 230 + len(data))
    struct.pack_into(">I", stub, STUB_LONGS, (len(data) - 32) // 4)
    return bytes(stub) + data + b"\0\0\0\0"                          # no relocations


def main() -> None:
    args = sys.argv[1:]
    pad = "--pad" in args
    args = [a for a in args if a != "--pad"]
    stub = None
    if "--stub" in args:
        i = args.index("--stub")
        stub = Path(args[i + 1]).read_bytes()
        del args[i:i + 2]
    if len(args) != 4 or args[0] not in ("fic", "start") or (stub and args[0] != "start"):
        sys.exit(__doc__.split("\n\n")[1] + "\n" + __doc__.split("\n\n")[2])
    data, like = Path(args[1]).read_bytes(), Path(args[3]).read_bytes()
    if args[0] == "fic":
        stream = pack(data)
        out = header(len(stream), len(data), like) + stream
    else:
        out = build_start(data, like, stub)
    if pad:
        if len(out) > len(like):
            sys.exit(f"error: {len(out)} bytes, longer than {Path(args[3]).name} ({len(like)}): cannot pad")
        out += bytes(len(like) - len(out))
    Path(args[2]).write_bytes(out)
    print(f"{args[2]}: {len(out)} bytes ({Path(args[3]).name}: {len(like)})")


if __name__ == "__main__":
    main()
