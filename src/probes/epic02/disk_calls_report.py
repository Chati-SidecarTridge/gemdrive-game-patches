#!/usr/bin/env python3
"""EPIC-02 STORY-05: the calls disk_calls_probe.py logged, in order, as a table.

Usage: disk_calls_report.py <run folder>

For the loader: the file name (at a0), the destination (a1); for file_io: its parameters
($C0730: +4 drive, +6 offset, +$A length, +$E buffer, +$12 "Wr", +$22 name); for the driver
copy's hdv_rw: rwflag, buffer, count, recno, drive from the stack. Consecutive hdv_mediach
calls are counted, not listed.
"""

import re
import struct
import sys
from pathlib import Path

HIT = re.compile(r"^\tpc = \$([0-9a-f]+) ")
MEM = re.compile(r"^([0-9A-Fa-f]{8}): ((?:[0-9A-Fa-f]{2} ){1,16})")
REG = re.compile(r"\b([AD][0-7]) ([0-9A-F]{8})")
NAMES = {"85000": "loader", "c0170": "file_io", "c02ca": "file_io_2",
         "b718c": "hdv_bpb", "b71c2": "hdv_rw", "b75be": "hdv_mediach"}


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(__doc__.split("\n\n")[1])
    lines = (Path(sys.argv[1]) / "hatari.out").read_text(errors="replace").splitlines()
    events, cur, matched = [], None, False
    for line in lines:
        if "condition(s) matched" in line:
            matched = True
            continue
        m = HIT.search(line)
        if m and matched:
            matched = False
            if m[1] not in NAMES:  # another breakpoint (the hand-over's)
                cur = None
                continue
            cur = dict(kind=NAMES[m[1]], mem=b"", regs={})
            events.append(cur)
            continue
        if cur is None:
            continue
        m = MEM.match(line)
        if m:
            cur["mem"] += bytes.fromhex(m[2].replace(" ", ""))
        for r, v in REG.findall(line):
            cur["regs"].setdefault(r, int(v, 16))
    media = 0
    for e in events:
        if e["kind"] == "hdv_mediach":
            media += 1
            continue
        if media:
            print(f"  hdv_mediach x{media}")
            media = 0
        mem = e["mem"]
        if e["kind"] == "loader":
            name = mem.split(b"\0")[0].decode("latin-1", "replace")
            print(f"loader      name {name!r:16} to ${e['regs'].get('A1', 0):x}, d1 = {e['regs'].get('D1', 0)}")
        elif e["kind"].startswith("file_io") and len(mem) >= 0x30:
            drive, off, length, buf = struct.unpack(">HIII", mem[4:18])
            wr = mem[0x12:0x14] == b"Wr"
            name = mem[0x22:0x30].split(b"\0")[0].decode("latin-1", "replace")
            print(f"{e['kind']:11} {'write' if wr else 'read'} {name!r:16} offset {off}, length {length}, to ${buf:x}, drive {drive}")
        elif e["kind"] == "hdv_rw" and len(mem) >= 16:
            _ret, flag, buf, count, rec, dev = struct.unpack(">IHIHHH", mem[:16])
            print(f"  hdv_rw    {'write' if flag & 1 else 'read'} record {rec} x{count} to ${buf:x}, drive {dev}")
        else:
            print(f"  {e['kind']}")
    if media:
        print(f"  hdv_mediach x{media}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
