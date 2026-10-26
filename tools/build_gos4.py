#!/usr/bin/env python3
"""tools/build_gos4.py: a GOS4 game's START.TOS for a GEMDOS drive, built from its original by
signature, as tools/build_gos5.py builds a GOS5 game's.

Usage: build_gos4.py <START.TOS> <out START.TOS> [--info] [--floppy]

The launcher program packed in <START.TOS> (tools/unpack.py) gets src/gemdrive/gos4_patch.s's block
at the front of its text, as build_gos5.py does with gos5_patch.s, and its PPHD check becomes a
bra.w to the block's gd_check. The block's branches and parameters come from the launcher, by
signature:
  the check     movea.l $472.w,a1 / cmpi.l #'PPHD',-8(a1) / bne: PP's path after it, PP's
                fallback at the bne's target
  the table     in PP's path, lea table,a6 / move.l a6,pointer: where PP's path writes the driver
                table GOS takes, and the long GOS takes it from ($C00E0 and $C0030 in 110 launchers,
                $1C00E0 and $1C0030 in the 2 MB ones, $C0098 and $5FA in Defender 2's)
  where PP's    the bra.w or bra.s that ends PP's path (clr.l (a1)+ / move.l d3,(a1)+ / clr.l (a1)+ /
  path goes on  clr.l (a1)+ / move.l a2,(a1) / bra), whose target leads to the jump into GOS
  GOS           the one jmp $C0100 (or $1C0100): GOS's text, which the block searches at run time for
                the move.l #trap1,$84.w of the GOS build the game carries
  the info      show_info and its call after Vsync, as in build_gos5.py: our line under PP's, and
  screen        with --floppy "Insert any floppy disk in drive A"
The result is packed with the original's own stub (tools/pack.py); a launcher that is not packed
(Herman's, Hoog's, Ranx's, Grandad's) is written back unpacked. With --info it only prints what it
found. It writes nothing on an original it does not know. Prints both files' SHA-256.
"""

from __future__ import annotations

import hashlib
import re
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import build_gos5 as b5  # noqa: E402
import pack  # noqa: E402
import unpack  # noqa: E402

PATCH_SRC = REPO / "src" / "gemdrive" / "gos4_patch.s"
PATCH_BIN = REPO / "tools" / "dev" / "builds" / "gos4" / "gos4_patch.bin"
END = re.compile(rb"\x42\x99\x22\xc3\x42\x99\x42\x99\x22\x8a\x60(?:\x00(..)|([^\x00]))", re.S)
TABLE = re.compile(rb"\x4d\xf9(....)(?:\x23\xce(....)|\x21\xce(..))", re.S)
JMP = re.compile(rb"\x4e\xf9(\x00[\x0c\x1c]\x01\x00)")


def find(text: bytes) -> dict:
    checks = b5.even(b5.CHECK, text)
    if len(checks) != 1:
        b5.fail(f"{len(checks)} PPHD checks, not one")
    m = checks[0]
    short = m.group(1) != b"\0"
    end = m.start() + 14 if short else m.start() + 16
    disp = struct.unpack(">b", m.group(1))[0] if short else struct.unpack(">h", m.group(2))[0]
    found = {"check": m.start(), "check_end": end, "pp": end, "no_pp": m.start() + 14 + disp}
    ends = [e for e in b5.even(END, text) if e.start() > end]
    if not ends:
        b5.fail("the end of PP's path: none after the check")
    e = ends[0]
    found["gos_start"] = e.start() + 12 + (struct.unpack(">h", e.group(1))[0] if e.group(1)
                                           else struct.unpack(">b", e.group(2))[0])
    tables = [t for t in b5.even(TABLE, text) if end <= t.start() < e.start()]
    if len(tables) != 1:
        b5.fail(f"the driver table in PP's path: {len(tables)}, not one")
    t = tables[0]
    found["table"] = struct.unpack(">I", t.group(1))[0]
    found["table_ptr"] = struct.unpack(">I", t.group(2))[0] if t.group(2) else struct.unpack(">H", t.group(3))[0]
    jmps = b5.even(JMP, text)
    if len(jmps) != 1 or jmps[0].start() < found["gos_start"]:
        b5.fail(f"the jump into GOS: {len(jmps)}, not one after PP's path")
    found["gos"] = struct.unpack(">I", jmps[0].group(1))[0]
    found["info"], found["info_call"] = b5.info_screen(text)
    if found["gos"] not in b5.AREAS:
        b5.fail(f"GOS at ${found['gos']:X}: no place known for the forwarder")
    found["run"], found["md_stack"] = b5.AREAS[found["gos"]]
    return found


def main() -> int:
    args = [a for a in sys.argv[1:] if a not in ("--info", "--floppy")]
    if len(args) != (1 if "--info" in sys.argv else 2):
        sys.exit(__doc__)
    original = Path(args[0]).read_bytes()
    prog, packed = b5.launcher(original)
    tlen = struct.unpack(">I", prog[2:6])[0]
    f = find(prog[28:28 + tlen])
    print(f"{args[0]}: PPHD check +${f['check']:X}, PP's path +${f['pp']:X}, fallback +${f['no_pp']:X}, "
          f"on to GOS +${f['gos_start']:X}, GOS ${f['gos']:X}, driver table ${f['table']:X} at "
          f"${f['table_ptr']:X}, forwarder ${f['run']:X}, stack ${f['md_stack']:X}, info screen "
          f"+${f['info']:X} called at +${f['info_call']:X}"
          + (", needs a disk in drive A" if "--floppy" in sys.argv else ""))
    if "--info" in sys.argv:
        return 0
    block = b5.patch_block(PATCH_SRC, PATCH_BIN)
    new = b5.build(prog, block, f, "--floppy" in sys.argv,
                   (f["gos"], f["table"], f["table_ptr"], f["run"], f["md_stack"]))
    out = pack.build_start(new, original, raise_top=True) if packed else new
    if packed and unpack.unpack_start(out) != new:
        b5.fail("the packed result does not unpack to the patched program")
    Path(args[1]).write_bytes(out)
    for name, data in ((args[0], original), (args[1], out)):
        print(f"  {hashlib.sha256(data).hexdigest()}  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
