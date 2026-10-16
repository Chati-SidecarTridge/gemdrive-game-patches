#!/usr/bin/env python3
"""EPIC-04 STORY-04: one of the card's FIXGOS5 games, its START.TOS built by tools/build_gos5.py,
run from Hatari's GEMDOS drive.

Usage: gos5_run.py <ZIP folder name> [--setup st-104|ste-162|ste-206] [--disk gemdrive|ppdriver]

The game's folder in tools/dev/builds/sdcard/FIXGOS5/ is copied into a new folder under
tools/dev/builds/gos5/, its START.TOS rebuilt there, the disks made from the copy (make_disks.sh:
it becomes C:\\LEMMINGS) and the harness runs it with EPIC-03's generic expectation
(src/probes/epic03/mode_probe.py: the start, screenshots at 10 s and 30 s, the space bar, a
screenshot 15 s later), at the card's RAM (its 1MB or 2MB folder). Prints mode_probe's report and
the crashes (TOS's Pterm(-1)). Nothing is deleted.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src" / "probes" / "epic03"))
import mode_probe  # noqa: E402

CARD = REPO / "tools" / "dev" / "builds" / "sdcard" / "FIXGOS5"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("game")
    ap.add_argument("--setup", default="st-104")
    ap.add_argument("--disk", default="gemdrive", choices=("gemdrive", "ppdriver"))
    a = ap.parse_args()
    found = [p for p in CARD.glob(f"*/*/{a.game}") if p.is_dir()]
    if len(found) != 1:
        sys.exit(f"error: {a.game}: {len(found)} folders in {CARD}")
    src = found[0]
    memsize = int(src.parent.parent.name.rstrip("MB"))
    index = (REPO / "tools" / "dev" / "builds" / "sdcard" / "INDEX.TXT").read_text(encoding="latin-1")
    start = next(l.split("  ")[0].split("\\")[-1] for l in index.splitlines()
                 if l.startswith("FIXGOS5\\") and l.split("  ")[0].split("\\")[3] == a.game)
    work = REPO / "tools" / "dev" / "builds" / "gos5" / time.strftime(f"{a.game}-%Y%m%d-%H%M%S")
    game = work / a.game
    shutil.copytree(src, game)
    subprocess.run([sys.executable, "-I", str(REPO / "tools" / "build_gos5.py"), str(src / start),
                    str(game / start)], check=True)
    disks = work / "disks"
    subprocess.run([str(REPO / "tools" / "dev" / "make_disks.sh"), str(game), str(disks)],
                   check=True, stdout=subprocess.DEVNULL)
    exp = work / "generic.exp"
    exp.write_text("\n".join([
        f'expect start Pexec\\(0, "C:\\\\LEMMINGS\\\\{re.escape(start)}"',
        "sleep 10", "shot s10", "sleep 20", "shot s30", "key space", "sleep 15", "shot s45", ""]))
    cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"),
           "--setup", a.setup, "--disk", a.disk, "--start", f"C:\\LEMMINGS\\{start}",
           "--expect", str(exp), "--name", f"gos5-{a.game.lower()}", "--memsize", str(memsize),
           ] + (["--drive", str(disks / "gemdrive")] if a.disk == "gemdrive"
                else ["--image", str(disks / "ppdriver.img")])
    done = subprocess.run(cmd, capture_output=True, text=True)
    runs = re.findall(r"tools/dev/logs/\S+", done.stdout)
    if not runs:
        print(done.stdout, done.stderr)
        return 1
    run = REPO / runs[-1]
    print(mode_probe.report(run.resolve()))
    print(f"crashes  {(run / 'hatari.out').read_text(errors='replace').count('Pterm(-1)')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
