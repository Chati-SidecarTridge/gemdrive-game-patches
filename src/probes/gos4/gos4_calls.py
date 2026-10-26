#!/usr/bin/env python3
"""The GEMDOS calls a GOS4 game makes, logged at GOS's own GEMDOS.

Usage: gos4_calls.py <ZIP folder name> [--setup st-104|ste-162|ste-206] [--seconds N]
       gos4_calls.py --report <run folder>

Hatari's GEMDOS trace sees only the calls that reach its own hook, and under GOS4 the game's
calls go to GOS (D15R_HH4, TOS 1.04's GEMDOS at $C0100, $1C0100 for a 2 MB game). So the game's folder, as the card lays it
out (unpacked download, tools/survey/sdcard.py's plan), is copied into a new folder under
tools/dev/builds/gos4/, its D15R_HH4.FIC unpacked, and GOS's GEMDOS dispatcher found by
signature (`movea.l (8,a6),a0 / move.w (a0),(-26,a6) / cmpi.w #87,(-26,a6)`): a :trace breakpoint
just after the movea dumps the call's parameters (a0) and the memory at the two longs that may
point to a name, at every call. The game runs from the PPDRIVER image (its original START.TOS: the
reference), at the RAM of its run, for N seconds (default 120): screenshots, the space bar, Return,
a click. Then the report: every call in order (consecutive Fread/Fwrite/Fseek on one handle
counted, and any call repeated), and the functions with their counts. Nothing is deleted.
"""

from __future__ import annotations

import argparse
import collections
import re
import struct
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src" / "probes" / "gos5"))
import gos5_run  # noqa: E402

DISPATCH = bytes.fromhex("206E00083D50FFE60C6E0057FFE6")
# GOS4's text, as the launcher relocates D15R_HH4, by the game's RAM (runs 20261016-171229, Operation
# Stealth: TRAP #1 = $C0100 + $8F1C; 20261016-172301, Grandad: the dispatcher at $1C0100 + its offset)
BASE = {1: 0xC0100, 2: 0x1C0100}
HIT = re.compile(r"^\tpc = \$([0-9a-f]+) ")
MEM = re.compile(r"^([0-9A-Fa-f]{8}): ((?:[0-9A-Fa-f]{2} ){1,16})")
NAMES = {0x00: "Pterm0", 0x01: "Cconin", 0x02: "Cconout", 0x06: "Crawio", 0x07: "Crawcin", 0x08: "Cnecin",
         0x09: "Cconws", 0x0A: "Cconrs", 0x0B: "Cconis", 0x0E: "Dsetdrv", 0x19: "Dgetdrv", 0x1A: "Fsetdta",
         0x20: "Super", 0x2A: "Tgetdate", 0x2B: "Tsetdate", 0x2C: "Tgettime", 0x2D: "Tsettime",
         0x2F: "Fgetdta", 0x30: "Sversion", 0x31: "Ptermres", 0x36: "Dfree", 0x39: "Dcreate", 0x3A: "Ddelete",
         0x3B: "Dsetpath", 0x3C: "Fcreate", 0x3D: "Fopen", 0x3E: "Fclose", 0x3F: "Fread", 0x40: "Fwrite",
         0x41: "Fdelete", 0x42: "Fseek", 0x43: "Fattrib", 0x45: "Fdup", 0x46: "Fforce", 0x47: "Dgetpath",
         0x48: "Malloc", 0x49: "Mfree", 0x4A: "Mshrink", 0x4B: "Pexec", 0x4C: "Pterm", 0x4E: "Fsfirst",
         0x4F: "Fsnext", 0x56: "Frename", 0x57: "Fdatime"}
NAMED = {0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x41, 0x43, 0x4E}  # a name at +2


def text(mem: bytes) -> str:
    return mem.split(b"\0")[0].decode("latin-1", "replace")


def describe(f: int, p: bytes, at2: bytes, at4: bytes) -> str:
    w = lambda o: struct.unpack(">h", p[o:o + 2])[0]  # noqa: E731
    l = lambda o: struct.unpack(">I", p[o:o + 4])[0]  # noqa: E731
    if f in NAMED:
        extra = {0x3C: f", attr {w(6)}", 0x3D: f", mode {w(6)}", 0x43: f", {w(6)}, {w(8)}",
                 0x4E: f", attr ${w(6) & 0xFFFF:x}"}.get(f, "")
        return f'"{text(at2)}"{extra}'
    if f in (0x3F, 0x40):
        return f"handle {w(2)}, {l(4)} bytes, to ${l(8):x}"
    if f == 0x42:
        return f"{struct.unpack('>i', p[2:6])[0]}, handle {w(6)}, mode {w(8)}"
    if f in (0x3E, 0x45):
        return f"handle {w(2)}"
    if f == 0x4B:
        return f'mode {w(2)}, "{text(at4)}"'
    if f == 0x56:
        return f"${l(4):x}, ${l(8):x}"
    if f in (0x1A, 0x20, 0x48, 0x49):
        return f"${l(2):x}"
    if f == 0x4A:
        return f"${l(4):x}, ${l(8):x}"
    if f in (0x0E, 0x4C):
        return f"{w(2)}"
    if f in (0x47, 0x36):
        return f"${l(2):x}, drive {w(6)}"
    return ""


def report(run: Path) -> int:
    calls, cur, matched = [], None, False
    for line in (run / "hatari.out").read_text(errors="replace").splitlines():
        if "condition(s) matched" in line:
            matched = True
            continue
        m = HIT.search(line)
        if m and matched:
            matched = False
            cur = []
            calls.append(cur)
            continue
        m = MEM.match(line)
        if m and cur is not None:
            cur.append(bytes.fromhex(m[2].replace(" ", "")))
    count, lines, last = collections.Counter(), [], None
    for c in calls:
        if len(c) < 5:
            continue
        p, at2, at4 = c[0], c[1] + c[2], c[3] + c[4]
        f = struct.unpack(">H", p[:2])[0]
        name = NAMES.get(f, f"${f:02x}")
        count[name] += 1
        args = describe(f, p, at2, at4)
        key = (name, args.split(",")[0]) if f in (0x3F, 0x40, 0x42) else None
        if key and last and last[0] == key:
            last[1] += 1
            lines[-1] = f"{name:9} {args.split(',')[0]} x{last[1]}"
            continue
        last = [key, 1] if key else None
        line = f"{name:9} {args}".rstrip()
        m = re.fullmatch(r"(.*?)(?: x(\d+))?", lines[-1]) if lines else None
        if m and m[1] == line:  # the same call again: counted
            lines[-1] = f"{line} x{int(m[2] or 1) + 1}"
            continue
        lines.append(line)
    print(f"{run.name}: {sum(count.values())} calls to GOS's GEMDOS")
    print("\n".join(lines))
    print("\nfunctions: " + ", ".join(f"{k} {v}" for k, v in count.most_common()))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("game", nargs="?")
    ap.add_argument("--setup", default="st-104")
    ap.add_argument("--seconds", type=int, default=120)
    ap.add_argument("--report", type=Path)
    a = ap.parse_args()
    if a.report:
        return report(a.report)
    if not a.game:
        ap.error("a game or --report")
    work = REPO / "tools" / "dev" / "builds" / "gos4" / time.strftime(f"{a.game}-%Y%m%d-%H%M%S")
    game = work / a.game
    start, memsize = gos5_run.original(a.game, game)
    gos = [f for f in game.rglob("*") if f.name.upper() == "D15R_HH4.FIC"]
    if len(gos) != 1:
        sys.exit(f"error: {a.game}: {len(gos)} D15R_HH4.FIC")
    unpacked = work / "d15r_hh4.bin"
    subprocess.run([sys.executable, "-I", str(REPO / "tools" / "unpack.py"), "fic", str(gos[0]), str(unpacked)],
                   check=True, stdout=subprocess.DEVNULL)
    body = unpacked.read_bytes()
    hits = [m.start() for m in re.finditer(re.escape(DISPATCH), body)]
    if body[:2] != b"\x60\x1a" or len(hits) != 1:
        sys.exit(f"error: {gos[0]}: not a GEMDOS program, or {len(hits)} dispatchers")
    bp = BASE[memsize] + hits[0] - 0x1C + 4  # after movea.l (8,a6),a0
    (work / "call.ini").write_text('m a0 16\nm "(a0+2)" 32\nm "(a0+4)" 32\n')
    (work / "calls.dbg").write_text(f"b pc = ${bp:x} :trace :file {work / 'call.ini'}\n")
    steps = [f'expect start Pexec\\(0, "C:\\\\LEMMINGS\\\\{re.escape(start)}"',
             "sleep 10", "shot s10", "sleep 20", "shot s30", "key space", "sleep 15", "shot s45",
             "key return", "sleep 15", "shot s60", "mouse 160 100", "sleep 0.5", "event doubleclick"]
    rest = max(a.seconds - 60, 5)
    steps += [x for i in range(0, rest, 20) for x in ("sleep %d" % min(20, rest - i), f"shot s{60 + i + min(20, rest - i)}",
                                                    "key space")]
    (work / "calls.exp").write_text("\n".join(steps) + "\n")
    subprocess.run([str(REPO / "tools" / "dev" / "make_disks.sh"), str(game), str(work / "disks")],
                   check=True, stdout=subprocess.DEVNULL)
    print(f"{a.game}: {start}, {memsize} MB, GOS's GEMDOS dispatcher at ${bp - 4:x}")
    cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"), "--setup", a.setup,
           "--disk", "ppdriver", "--image", str(work / "disks" / "ppdriver.img"), "--start",
           f"C:\\LEMMINGS\\{start}", "--expect", str(work / "calls.exp"), "--parse", str(work / "calls.dbg"),
           "--name", f"gos4-calls-{a.game.lower()}", "--memsize", str(memsize)]
    done = subprocess.run(cmd, capture_output=True, text=True)
    runs = re.findall(r"tools/dev/logs/\S+", done.stdout)
    if not runs:
        print(done.stdout, done.stderr)
        return 1
    print(done.stdout.strip().splitlines()[-2])
    return report(REPO / runs[-1])


if __name__ == "__main__":
    sys.exit(main())
