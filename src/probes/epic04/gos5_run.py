#!/usr/bin/env python3
"""EPIC-04 STORY-04: one of the card's FIXGOS5 games, its START.TOS built by tools/build_gos5.py,
run from Hatari's GEMDOS drive.

Usage: gos5_run.py <ZIP folder name> [--setup st-104|ste-162|ste-206] [--disk gemdrive|ppdriver]

The game's folder as the card lays it out (tools/survey/sdcard.py), from its unpacked download, is
copied into a new folder under tools/dev/builds/gos5/, its START.TOS built there with
src/survey/ports.tsv's options and its added files, the disks made from the copy (make_disks.sh: it
becomes C:\\LEMMINGS) and the harness runs it with EPIC-03's generic expectation
(src/probes/epic03/mode_probe.py: the start, screenshots at 10 s and 30 s, the space bar, a
screenshot 15 s later), at the RAM of the game's run. Prints mode_probe's report and the crashes
(TOS's Pterm(-1)). Nothing is deleted.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src" / "probes" / "epic03"))
import mode_probe  # noqa: E402
sys.path.insert(0, str(REPO / "tools" / "survey"))
import run_all  # noqa: E402
import sdcard  # noqa: E402


def original(game: str, dest: Path) -> tuple[str, int]:
    """The game's folder, as the card has it before the build, copied to dest; its program to start and RAM."""
    survey = REPO / "src" / "survey"
    rows = [g for g in csv.DictReader((survey / "migration.csv").open()) if Path(g["download"]).stem.upper() == game]
    if len(rows) != 1:
        sys.exit(f"error: {game}: {len(rows)} downloads")
    g = rows[0]
    files = [f for f in csv.DictReader((survey / "files.csv").open()) if f["archive"] == g["download"]]
    record = next((r for r in csv.DictReader((survey / "catalogue.csv").open()) if r["row"] == g["row"]), {})
    run = next((r for r in csv.DictReader((run_all.SURVEY / "runs.tsv").open(), delimiter="\t")
                if r["run"] == g["run"]), {})
    p = run_all.plan(g, files, record)
    sdcard.copy(p["folder"], dest)
    for e in p["extra"]:
        if not (dest / e.name).exists():
            sdcard.copy(e, dest / e.name)
    ram = run.get("memsize") or run_all.megabytes(record.get("min_ram", ""), record.get("gx", ""),
                                                  record.get("page_min_ram", ""))
    return p["start"], int(ram)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("game")
    ap.add_argument("--setup", default="st-104")
    ap.add_argument("--disk", default="gemdrive", choices=("gemdrive", "ppdriver"))
    a = ap.parse_args()
    work = REPO / "tools" / "dev" / "builds" / "gos5" / time.strftime(f"{a.game}-%Y%m%d-%H%M%S")
    game = work / a.game
    start, memsize = original(a.game, game)
    port = next((r for r in csv.DictReader((REPO / "src" / "survey" / "ports.tsv").open(), delimiter="\t")
                 if Path(r["download"]).stem.upper() == a.game), None)
    subprocess.run([sys.executable, "-I", str(REPO / "tools" / "build_gos5.py"), str(game / start),
                    str(game / start)] + (port["options"].split() if port else []), check=True)
    for name in port["add"].split() if port else []:
        sdcard.copy(sdcard.found(port["from"], name), game / name)
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
