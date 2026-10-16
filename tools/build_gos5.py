#!/usr/bin/env python3
"""tools/build_gos5.py: a GOS5 game's START.TOS for a GEMDOS drive, built from its original by
signature (EPIC-04 STORY-04; the change is STORY-01's and STORY-02's).

Usage: build_gos5.py <START.TOS> <out START.TOS> [--info] [--floppy]

The launcher program packed in <START.TOS> (tools/unpack.py) gets src/gemdrive/gos5_patch.s's block
at the front of its text: its first instruction branches over the block, every relocation moves by
the block's size (no PC-relative reference changes: the whole text moves), and the launcher's PPHD
check becomes a bra.w to the block's gd_check. The block's branches and parameters come from the
launcher's own code, found by signature:
  the check     movea.l $472.w,a1 / cmpi.l #'PPHD',-8(a1) / bne: PP's path after it, PP's
                fallback at the bne's target
  the image     movea.l (img).l,a6 / adda.l #img_add,a6 (reuse_pp_driver's): GOS at img_add - $700
  GOS's start   where PP's two paths meet: family A (Lemmings), the bra.w that ends set_buffers
                (clr.l (a1)+ / move.l d3,(a1)+ / clr.l (a1)+ / clr.l (a1)+ / move.l a2,(a1) / bra.w;
                Lemmings' goes to start_d15r, Jetsons' first to more setup); family B, after the
                check, lea gos,a0 / ... move.w 12(a0),d0 ... jsr (a0) / bra.w
  the info      show_info, the routine that starts with lea of the string ESC E ESC Y '0' ' ', and
  screen        its one call, a bsr.w after Vsync: turned to the block's gd_info, which adds our
                line under PP's ("Patched for GEMDRIVE HD by SidecarTridge"), and with --floppy
                "Insert any floppy disk in drive A" (a game that waits for the drive's motor to
                stop, which an empty drive never lets it do: Pit Fighter)
The result is packed with the original's own stub (tools/pack.py); a launcher that is not packed
(Indigo's START.TOS is the program itself) is written back unpacked. With --info it only prints
what it found. It writes nothing on an original it does not know. Prints both files' SHA-256.
"""

from __future__ import annotations

import hashlib
import re
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import pack  # noqa: E402
import unpack  # noqa: E402

PATCH_SRC = REPO / "src" / "gemdrive" / "gos5_patch.s"
PATCH_BIN = REPO / "tools" / "dev" / "builds" / "gos5" / "gos5_patch.bin"
GD_CHECK = 46                       # gos5_patch.s: x_pp +4, x_no_pp +8, x_gos +12, x_info +16,
GD_INFO = 20                        # gd_info's bra.w +20, p_* +24..+40, p_floppy +44
CHECK = re.compile(rb"\x22\x78\x04\x72\x0c\xa9PPHD\xff\xf8\x66(.)(..)?", re.S)
IMAGE = re.compile(rb"\x2c\x79(....)\xdd\xfc(....)", re.S)
CLEAR = b"\x1bE\x1bY0 \x00"         # show_info's first string
VSYNC = b"\x3f\x3c\x00\x25\x4e\x4e\x54\x8f"
END_A = re.compile(rb"\x42\x99\x22\xc3\x42\x99\x42\x99\x22\x8a\x60\x00(..)", re.S)
AFTER_B = re.compile(rb"\x41\xf9(....)\x70\x00\x30\x28\x00\x0c\xd1\xc0\x4e\x90\x60\x00(..)", re.S)
# where gd_forward's block and GEMDRIVE's stack go, by GOS's base: PP's driver copy (GOS - $8F80 in
# every family A launcher) and the top of his GEMDOS buffers below it (EPIC-04 STORY-01, STORY-02)
AREAS = {0xC0100: (0xB7180, 0xB7100), 0x1A0100: (0x197180, 0x197100), 0x1C0100: (0x1B7180, 0x1B7100)}


def fail(msg: str) -> None:
    sys.exit(f"error: {msg}")


def even(pattern: re.Pattern, data: bytes) -> list[re.Match]:
    return [m for m in pattern.finditer(data) if m.start() % 2 == 0]


def patch_block() -> bytes:
    if not PATCH_BIN.exists() or PATCH_BIN.stat().st_mtime < PATCH_SRC.stat().st_mtime:
        PATCH_BIN.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(REPO / "tools" / "dev" / "asm.sh"), str(PATCH_SRC), str(PATCH_BIN)],
                       check=True, stdout=subprocess.DEVNULL)
    block = PATCH_BIN.read_bytes()
    if block[GD_CHECK:GD_CHECK + 4] != b"\x22\x78\x04\x72" or block[GD_INFO:GD_INFO + 2] != b"\x60\x00" \
            or len(block) % 2:
        fail(f"{PATCH_BIN}: not the block this tool was written for")
    return block


def relocations(prog: bytes, tlen: int, dlen: int, slen: int) -> list[int]:
    table = 28 + tlen + dlen + slen
    first = struct.unpack(">I", prog[table:table + 4])[0]
    if not first:
        return []
    out, pos, i = [first], first, table + 4
    while True:
        step = prog[i]
        i += 1
        if step == 0:
            return out
        if step == 1:
            pos += 254
            continue
        pos += step
        out.append(pos)


def encode(positions: list[int]) -> bytes:
    if not positions:
        return b"\0\0\0\0"
    out = bytearray(struct.pack(">I", positions[0]))
    for a, b in zip(positions, positions[1:]):
        step = b - a
        while step > 254:
            out.append(1)
            step -= 254
        out.append(step)
    out.append(0)
    return bytes(out)


def find(text: bytes) -> dict:
    checks = even(CHECK, text)
    if len(checks) != 1:
        fail(f"{len(checks)} PPHD checks, not one")
    m = checks[0]
    short = m.group(1) != b"\0"
    end = m.start() + 14 if short else m.start() + 16
    disp = struct.unpack(">b", m.group(1))[0] if short else struct.unpack(">h", m.group(2))[0]
    found = {"check": m.start(), "check_end": end, "pp": end, "no_pp": m.start() + 14 + disp if short
             else m.start() + 14 + disp}
    images = {(struct.unpack(">I", i.group(1))[0], struct.unpack(">I", i.group(2))[0])
              for i in even(IMAGE, text)}
    images = {(a, b) for a, b in images if b - a == 0x1A}
    if len(images) != 1:
        fail(f"GOS's image pointer: {sorted(images)}, not one")
    found["img"], found["img_add"] = images.pop()
    found["gos"] = found["img_add"] - 0x700
    after = AFTER_B.match(text, end)
    if after and struct.unpack(">I", after.group(1))[0] == found["gos"]:
        found["family"] = "B"
        found["gos_start"] = end + 18 + struct.unpack(">h", after.group(2))[0]  # bra.w at end+16
    else:
        ends = [e for e in even(END_A, text) if e.start() > end]
        if not ends:
            fail("GOS's start: no end of set_buffers after the check")
        found["family"] = "A"
        found["gos_start"] = ends[0].start() + 12 + struct.unpack(">h", ends[0].group(1))[0]
    def target(at: int) -> int:
        return at + 2 + struct.unpack(">h", text[at + 2:at + 4])[0]

    strings = [s.start() for s in re.finditer(re.escape(CLEAR), text)]
    infos = [k for k in range(0, len(text) - 4, 2) if text[k:k + 2] == b"\x41\xfa" and target(k) in strings]
    calls = [k for k in range(8, len(text) - 4, 2) if text[k:k + 2] == b"\x61\x00" and target(k) in infos
             and text[k - 8:k] == VSYNC]
    if len(infos) != 1 or len(calls) != 1:
        fail(f"the info screen: {len(infos)} show_info, {len(calls)} calls, not one")
    found["info"], found["info_call"] = infos[0], calls[0]
    if found["gos"] not in AREAS:
        fail(f"GOS at ${found['gos']:X}: no place known for the forwarder")
    found["run"], found["md_stack"] = AREAS[found["gos"]]
    return found


def build(prog: bytes, block: bytes, f: dict, floppy: bool) -> bytes:
    magic, tlen, dlen, blen, slen = struct.unpack(">HIIII", prog[:18])
    relocs = relocations(prog, tlen, dlen, slen)
    if any(f["check"] <= p < f["check_end"] or f["info_call"] - 3 <= p < f["info_call"] + 4 for p in relocs):
        fail("a relocation inside the PPHD check or the info screen's call")
    d = len(block)
    body = bytearray(block) + bytearray(prog[28:28 + tlen + dlen])

    def branch(at: int, target: int) -> None:
        disp = target - (at + 2)
        if not -0x8000 <= disp < 0x8000:
            fail(f"a branch from +{at:X} to +{target:X} is out of reach")
        body[at:at + 4] = b"\x60\x00" + struct.pack(">h", disp)

    branch(0, d)
    branch(4, f["pp"] + d)
    branch(8, f["no_pp"] + d)
    branch(12, f["gos_start"] + d)
    branch(16, f["info"] + d)
    struct.pack_into(">IIIIIH", body, 24, f["gos"], f["img"], f["img_add"], f["run"], f["md_stack"], floppy)
    call = f["info_call"] + d
    body[call + 2:call + 4] = struct.pack(">h", GD_INFO - (call + 2))     # bsr.w gd_info
    site = f["check"] + d
    branch(site, GD_CHECK)
    for at in range(site + 4, f["check_end"] + d, 2):
        body[at:at + 2] = b"\x4e\x71"                    # nop
    moved = [p + d for p in relocs]
    for p in moved:
        struct.pack_into(">I", body, p, struct.unpack(">I", body[p:p + 4])[0] + d)
    header = bytearray(prog[:28])
    struct.pack_into(">I", header, 2, tlen + d)
    symbols = prog[28 + tlen + dlen:28 + tlen + dlen + slen]
    return bytes(header) + bytes(body) + symbols + encode(moved)


def launcher(original: bytes) -> tuple[bytes, bool]:
    """The launcher program, and whether <START.TOS> packs it."""
    try:
        return unpack.unpack_start(original), True
    except SystemExit:
        if original[:2] == b"\x60\x1a" and CHECK.search(original):
            return original, False
        raise


def main() -> int:
    args = [a for a in sys.argv[1:] if a not in ("--info", "--floppy")]
    if len(args) != (1 if "--info" in sys.argv else 2):
        sys.exit(__doc__)
    original = Path(args[0]).read_bytes()
    prog, packed = launcher(original)
    tlen = struct.unpack(">I", prog[2:6])[0]
    f = find(prog[28:28 + tlen])
    print(f"{args[0]}: family {f['family']}, PPHD check +${f['check']:X}, PP's path +${f['pp']:X}, "
          f"fallback +${f['no_pp']:X}, GOS's start +${f['gos_start']:X}, GOS ${f['gos']:X}, "
          f"image (${f['img']:X})+${f['img_add']:X}, forwarder ${f['run']:X}, stack ${f['md_stack']:X}, "
          f"info screen +${f['info']:X} called at +${f['info_call']:X}"
          + (", needs a disk in drive A" if "--floppy" in sys.argv else ""))
    if "--info" in sys.argv:
        return 0
    new = build(prog, patch_block(), f, "--floppy" in sys.argv)
    out = pack.build_start(new, original, raise_top=True) if packed else new
    if packed and unpack.unpack_start(out) != new:
        fail("the packed result does not unpack to the patched program")
    Path(args[1]).write_bytes(out)
    for name, data in ((args[0], original), (args[1], out)):
        print(f"  {hashlib.sha256(data).hexdigest()}  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
