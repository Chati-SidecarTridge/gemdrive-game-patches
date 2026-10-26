#!/usr/bin/env python3
"""gos4_selftest.s, the forwarder's test, run under GOS4 from Hatari's GEMDOS drive.

Usage: gos4_selftest.py [--setup st-104|ste-162|ste-206] [--game HERMAN] [--program FILES/HERL]

The game's folder (default Herman's, whose launcher starts FILES\\HERL) is copied from its download
into a new folder under tools/dev/builds/gos4/, the program its launcher starts replaced by
gos4_selftest.s assembled as a GEMDOS program, its START.TOS built by tools/build_gos4.py, and the
copy run from the GEMDOS drive for 20 s. Prints the test's line (RESULT.OUT, as the run left it on
the drive), what TEST.OUT holds, and the run. Nothing is deleted.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src" / "probes" / "gos5"))
import gos5_run  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--setup", default="st-104")
    ap.add_argument("--game", default="HERMAN")
    ap.add_argument("--program", default="FILES/HERL")
    a = ap.parse_args()
    work = REPO / "tools" / "dev" / "builds" / "gos4" / time.strftime(f"selftest-{a.game}-%Y%m%d-%H%M%S")
    game = work / a.game
    start, memsize = gos5_run.original(a.game, game)
    target = game / a.program
    if not target.is_file():
        sys.exit(f"error: {target}: no such program")
    subprocess.run([str(REPO / "tools" / "dev" / "asm.sh"), "--tos", str(Path(__file__).with_name("gos4_selftest.s")),
                    str(target)], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, "-I", str(REPO / "tools" / "build_gos4.py"), str(game / start), str(game / start)],
                   check=True, stdout=subprocess.DEVNULL)
    subprocess.run([str(REPO / "tools" / "dev" / "make_disks.sh"), str(game), str(work / "disks")],
                   check=True, stdout=subprocess.DEVNULL)
    exp = work / "selftest.exp"
    exp.write_text(f'expect start Pexec\\(0, "C:\\\\LEMMINGS\\\\{re.escape(start)}"\nsleep 20\nshot result\n')
    done = subprocess.run([sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"), "--setup", a.setup,
                           "--disk", "gemdrive", "--drive", str(work / "disks" / "gemdrive"), "--start",
                           f"C:\\LEMMINGS\\{start}", "--expect", str(exp), "--name", f"gos4-selftest-{a.game.lower()}",
                           "--memsize", str(memsize)], capture_output=True, text=True)
    runs = re.findall(r"tools/dev/logs/\S+", done.stdout)
    if not runs:
        print(done.stdout, done.stderr)
        return 1
    run = REPO / runs[-1]
    folder = run / "drive" / "LEMMINGS" / Path(a.program).parent
    for name in ("RESULT.OUT", "TEST.OUT"):
        f = folder / name
        print(f"{name:10} {f.read_bytes()!r}" if f.is_file() else f"{name:10} (none)")
    print(f"TEST2.OUT  {'there' if (folder / 'TEST2.OUT').exists() else 'deleted'}")
    print(f"run        {runs[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
