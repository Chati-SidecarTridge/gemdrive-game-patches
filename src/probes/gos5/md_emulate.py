#!/usr/bin/env python3
"""Hatari made to act, at each call gd_forward hands on, like the SidecarTridge
Multidevice's GEMDRIVE (../md-drives-emulator/target/atarist/src/gemdrive.s), which Hatari's
GEMDOS drive is not: a test build only.

Usage: md_emulate.py [--setup ste-162] [--memsize 4] [--stack] [--dgetdrv] [--dskbuf] [--delay N]
                     [--expect <file>]

The launcher of tools/build_gemdrive.sh, with gd_forward replaced by one that, before handing the
call to Hatari's TRAP #1, does what GEMDRIVE does for a call it serves:
  --stack    switch to its own stack at $B7100 (md_move_stack's), keeping registers there
  --dgetdrv  a nested Dgetdrv through TRAP #1 (GOS's image sends it to gd_forward, then GOS),
             as detect_emulated_drive for Dsetpath and Fopen; with the stack, on it
  --dskbuf   ILLEGAL over the $114 bytes from _dskbufp: send_sync's wait code and Fread's
             registers at +$100
  --delay N  a busy loop run N times (about 18 cycles each), an SD card's latency
and gemdrive-first-level.exp runs it on the GEMDOS drive. Builds in a new folder
tools/dev/builds/gos5/mdemu-<date>-<time>/ each run (nothing is deleted).
"""

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

EMULATION = """\
gd_to_machine:
	move.w	(a1),d0
	move.l	a6,-(sp)
	movea.l	sp,a6
	ifne	MD_STACK
	lea	($b7100).l,a6
	endif
	move.l	sp,-(a6)
	movea.l	a6,sp
	movem.l	d0-d7/a0-a5,-(sp)
	ifne	MD_DSKBUF
	movea.l	($4c6).w,a5
	move.w	#$114/2-1,d7
md_fill:
	move.w	#$4afc,(a5)+
	dbf	d7,md_fill
	endif
	ifne	MD_DGETDRV
	cmpi.w	#$3b,d0
	beq.s	md_dgetdrv
	cmpi.w	#$3d,d0
	bne.s	md_no_dgetdrv
md_dgetdrv:
	move.w	#$19,-(sp)
	trap	#1
	addq.l	#2,sp
md_no_dgetdrv:
	endif
	ifne	MD_DELAY
	move.l	#MD_DELAY,d7
md_delay:
	subq.l	#1,d7
	bne.s	md_delay
	endif
	movem.l	(sp)+,d0-d7/a0-a5
	movea.l	(sp),sp
	move.l	(sp)+,a6
	move.l	gd_machine(pc),-(sp)
	rts
"""

ORIGINAL = """\
gd_to_machine:
	move.l	gd_machine(pc),-(sp)
	rts
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--setup", default="ste-162", choices=("st-104", "ste-162", "ste-206"))
    ap.add_argument("--memsize", type=int, default=4)
    ap.add_argument("--stack", action="store_true")
    ap.add_argument("--dgetdrv", action="store_true")
    ap.add_argument("--dskbuf", action="store_true")
    ap.add_argument("--delay", type=int, default=0)
    ap.add_argument("--expect", type=Path,
                    default=REPO / "tools" / "dev" / "expect" / "gemdrive-first-level.exp")
    a = ap.parse_args()
    out = REPO / "tools" / "dev" / "builds" / "gos5" / time.strftime("mdemu-%Y%m%d-%H%M%S")
    gemdrive = REPO / "tools" / "dev" / "builds" / "gemdrive"
    subprocess.run([str(REPO / "tools" / "build_gemdrive.sh"), str(gemdrive)], check=True,
                   stdout=subprocess.DEVNULL)
    shutil.copytree(gemdrive / "src", out / "src")
    lemld2 = out / "src" / "lemld2" / "lemld2.s"
    s = lemld2.read_text()
    if s.count(ORIGINAL) != 1:
        sys.exit("error: gd_forward is not the one this emulation was written for")
    flags = (f"MD_STACK equ {int(a.stack)}\nMD_DGETDRV equ {int(a.dgetdrv)}\n"
             f"MD_DSKBUF equ {int(a.dskbuf)}\nMD_DELAY equ {a.delay}\n")
    s = s.replace(ORIGINAL, EMULATION).replace("\tbeq.s\tgd_to_gos\n", "\tbeq.w\tgd_to_gos\n")
    lemld2.write_text(flags + s)
    subprocess.run([str(REPO / "tools" / "build_launcher.sh"), "--allow-longer", str(out / "src"),
                    str(out / "build")], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([str(REPO / "tools" / "dev" / "make_disks.sh"), str(out / "build" / "LEMMINGS"),
                    str(out / "disks")], check=True, stdout=subprocess.DEVNULL)
    name = "mdemu" + "".join(f"-{k}" for k in ("stack", "dgetdrv", "dskbuf") if getattr(a, k))
    name += f"-delay{a.delay}" if a.delay else ""
    cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"),
           "--setup", a.setup, "--disk", "gemdrive", "--drive", str(out / "disks" / "gemdrive"),
           "--memsize", str(a.memsize), "--expect", str(a.expect), "--name", name]
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
