#!/usr/bin/env python3
"""EPIC-09 STORY-04: a ZIP the patcher page wrote, unpacked onto Hatari's GEMDOS drive and run as a user
would run it.

Usage: run_patched.py <patched ZIP> <archive> [--setup st-104|ste-162|ste-206] [--keys K,K,...]

<archive> is its line in src/survey/patches.tsv (LEMMINGS.ZIP), which gives the program to start and the
fix. The ZIP is unpacked into a new folder under tools/dev/builds/epic09/ (zipfile, every entry checked to
stay inside it), which becomes drive C:. A gdbpb fix's GDBPB.PRG is copied into C:\\AUTO\\, the way a user
runs it before the game (Hatari's harness starts one program). The run, at the RAM of the game's survey
or build run, with tools/survey/run_all.py's expectation (--keys: 12 s, then each key), goes to
tools/dev/logs/; prints run_all's analysis.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools" / "survey"))
import run_all  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("zip", type=Path)
    ap.add_argument("archive")
    ap.add_argument("--setup", default="st-104")
    ap.add_argument("--keys")
    a = ap.parse_args()
    row = next(r for r in csv.DictReader((REPO / "src" / "survey" / "patches.tsv").open(), delimiter="\t")
               if r["archive"] == a.archive)
    game_rows = row["rows"].split(";")
    runs = {r["row"]: r for r in csv.DictReader((run_all.SURVEY / "runs.tsv").open(), delimiter="\t")}
    ports = {r["row"]: r for r in csv.DictReader((REPO / "src" / "survey" / "ports.tsv").open(), delimiter="\t")}
    memsize = 1
    for r in game_rows:
        for src in (ports.get(r, {}), runs.get(r, {})):
            run = src.get("run", "")
            m = re.search(r"--memsize (\d)", (REPO / "tools" / "dev" / "logs" / run / "command.txt").read_text()) \
                if run and (REPO / "tools" / "dev" / "logs" / run / "command.txt").exists() else None
            if m:
                memsize = max(memsize, int(m.group(1)))
        memsize = max(memsize, int(runs.get(r, {}).get("memsize") or 1))
    work = REPO / "tools" / "dev" / "builds" / "epic09" / time.strftime(f"run-{Path(a.archive).stem}-%Y%m%d-%H%M%S")
    drive = work / "drive"
    drive.mkdir(parents=True)
    with zipfile.ZipFile(a.zip) as z:
        for info in z.infolist():
            path = PurePosixPath(info.filename)
            if path.is_absolute() or ".." in path.parts:
                sys.exit(f"error: {info.filename}: outside the folder")
            if not info.is_dir():
                (drive / path).parent.mkdir(parents=True, exist_ok=True)
                (drive / path).write_bytes(z.read(info))
    if row["action"] == "gdbpb":
        (drive / "AUTO").mkdir()
        shutil.copy(drive / row["target"], drive / "AUTO" / "GDBPB.PRG")
    start = "C:\\" + row["start"].replace("/", "\\")
    exp = work / "game.exp"
    folder, program = start.rsplit("\\", 1)
    exp.write_text("\n".join([
        f'expect start Pexec\\(0, "{re.escape(start)}"', "sleep 12", "shot s12"]
        + ([x for n, k in enumerate(a.keys.split(","), 1) for x in (f"key {k}", "sleep 10", f"shot k{n}")]
           if a.keys else ["key space", "sleep 8", "shot s20", "key return", "sleep 8", "shot s28", "key f1",
                           "sleep 6", "shot s34", "sleep 4", "shot s38"]) + [""]))
    (work / "exits.dbg").write_text("\n".join(run_all.EXITS) + "\n")
    (work / "exit.ini").write_text("info basepage\n")
    cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"), "--setup", a.setup, "--disk", "gemdrive",
           "--drive", str(drive), "--start", start, "--expect", str(exp), "--name", f"patched-{Path(a.archive).stem.lower()}",
           "--memsize", str(memsize), "--step-time", "30", "--parse", str(work / "exits.dbg")]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    found = re.findall(r"run folder (\S+)", out)
    if not found:
        print(out)
        return 1
    run = Path(found[0]) if Path(found[0]).is_absolute() else REPO / found[0]
    games = {g["row"]: g for g in csv.DictReader((REPO / "src" / "survey" / "migration.csv").open())}
    an = run_all.analyse(run, games[game_rows[0]]["strategy"])
    print(f"run      {run.relative_to(REPO)}  ({memsize} MB, start {start})")
    for k in ("result", "opened", "missing", "sectors_c", "screen", "halt", "faults", "proposal", "reason"):
        print(f"{k:9}{an.get(k, '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
