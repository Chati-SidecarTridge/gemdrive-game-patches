#!/usr/bin/env python3
"""One game of the survey run with the small fixes, from Hatari's GEMDOS drive or PPDRIVER.

Usage: fix_run.py <row> [--setup st-104|ste-162|ste-206] [--disk gemdrive|ppdriver] [--bpb]
                  [--fastload] [--rody2] [--auto PRG] [--keys K,K,... | --steps FILE] [--memsize N]

<row> is the game's row in src/survey/migration.csv (1698, Crystals of Arborea), or its name when
only one row has it. Its folder, as tools/survey/run_all.py finds it, is copied into a folder under
tools/dev/builds/small-fixes/ (what its download keeps beside it, into the drive's root), and changed:
  --bpb       GDBPB.PRG (src/gemdrive/gdbpb.s, S2) in C:\\AUTO\\, the GEMDOS drive only
  --fastload  tools/set_fastload.py on the program it knows in the folder (S3)
  --auto PRG  another program in C:\\AUTO\\, the GEMDOS drive only (a test's: one that keeps low RAM)
  --rody2     tools/rody2_runme.py: Rody and Mastico 4's RUNME.TOS into Rody and Mastico 2's folder,
              which has no program to start without it (S4)
The run is at the RAM of the game's survey run (runs.tsv: run_all gives a game more RAM while its run
ends in trouble; Stormlord 4 MB), with run_all's expectation (--keys: 12 s, then each key, the
harness's names or scancodes, 0x03 for 2, or event:EVENT for a Hatari event such as event:doubleclick,
with a screenshot 10 s after it; --steps: the harness's steps in FILE after the start's 12 s), into tools/dev/logs/.
From PPDRIVER the folder is C:\\LEMMINGS on make_disks.sh's image. Prints the run, run_all's analysis
(files opened, Rwabs on C:, the screen, the verdict), Getbpb calls per drive, the Pexec calls and
whether GDBPB.PRG stayed resident.
"""

from __future__ import annotations

import argparse
import collections
import csv
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools" / "survey"))
sys.path.insert(0, str(REPO / "tools"))
import run_all  # noqa: E402
import set_fastload  # noqa: E402

WORK = REPO / "tools" / "dev" / "builds" / "small-fixes"
PRG = WORK / "GDBPB.PRG"
SRC = REPO / "src" / "gemdrive" / "gdbpb.s"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("game")
    ap.add_argument("--setup", default="st-104")
    ap.add_argument("--disk", default="gemdrive", choices=("gemdrive", "ppdriver"))
    ap.add_argument("--bpb", action="store_true")
    ap.add_argument("--fastload", action="store_true")
    ap.add_argument("--rody2", action="store_true")
    ap.add_argument("--auto", type=Path)
    ap.add_argument("--keys", help="keys to press, comma-separated, instead of run_all's")
    ap.add_argument("--steps", type=Path, help="harness steps after the start's 12 s, instead of run_all's")
    ap.add_argument("--memsize", type=int, help="RAM in MB, instead of the game's run's")
    a = ap.parse_args()
    games = [g for g in csv.DictReader((REPO / "src" / "survey" / "migration.csv").open())
             if a.game in (g["row"], g["name"])]
    if len(games) != 1:
        sys.exit(f"error: {a.game}: " + (", ".join(f"row {g['row']} {g['download']} {g['strategy']}" for g in games)
                                         or "not in migration.csv"))
    game = games[0]
    files = [f for f in csv.DictReader((REPO / "src" / "survey" / "files.csv").open())
             if f["archive"] == game["download"]]
    record = next((r for r in csv.DictReader((REPO / "src" / "survey" / "catalogue.csv").open())
                   if r["row"] == game["row"]), {})
    p = run_all.plan(game, files, record)
    if p is None and a.rody2:  # the download's one folder, started from the RUNME.TOS the tool adds
        p = {"folder": next((run_all.SURVEY / "games" / "RODYM2").iterdir()), "start": "RUNME.TOS",
             "memsize": 1, "monitor": "", "extra": []}
    if p is None:
        sys.exit(f"error: {a.game}: no program to start")
    run = next((r for r in csv.DictReader((run_all.SURVEY / "runs.tsv").open(), delimiter="\t")
                if r["run"] == game["run"]), {})
    p["memsize"] = a.memsize or int(run.get("memsize") or p["memsize"])
    if a.bpb and (not PRG.exists() or PRG.stat().st_mtime < SRC.stat().st_mtime):
        PRG.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(REPO / "tools" / "dev" / "asm.sh"), "--tos", str(SRC), str(PRG)],
                       check=True, stdout=subprocess.DEVNULL)
    fixes = [f for f, on in (("bpb", a.bpb), ("fastload", a.fastload), ("rody2", a.rody2)) if on] or ["none"]
    label = re.sub(r"[^a-z0-9]+", "-", game["name"].lower()).strip("-")[:30] + "-" + "-".join(fixes) + \
        (f"-{a.auto.stem.lower()}" if a.auto else "")
    WORK.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=WORK) as stage:
        stage = Path(stage)
        drive = stage / "drive"
        drive.mkdir()
        folder = drive / "GAME"
        shutil.copytree(p["folder"], folder)
        for e in p.get("extra", []):
            if e.name.upper() not in ("GAME", "AUTO"):
                (shutil.copytree if e.is_dir() else shutil.copy)(e, drive / e.name)
        if a.fastload:
            known = [f for f in folder.rglob("*") if f.name.upper() in set_fastload.PROGRAMS]
            if len(known) != 1:
                sys.exit(f"error: {a.game}: {len(known)} programs set_fastload.py knows")
            subprocess.run([sys.executable, "-I", str(REPO / "tools" / "set_fastload.py"), str(known[0]),
                            str(known[0])], check=True, stdout=subprocess.DEVNULL)
        if a.rody2:
            subprocess.run([sys.executable, "-I", str(REPO / "tools" / "rody2_runme.py"),
                            str(next((run_all.SURVEY / "games" / "RODYM4").iterdir())), str(folder)],
                           check=True, stdout=subprocess.DEVNULL)
        if a.auto:
            (drive / "AUTO").mkdir(exist_ok=True)
            shutil.copy(a.auto, drive / "AUTO" / a.auto.name)
        if a.bpb:
            (drive / "AUTO").mkdir(exist_ok=True)
            shutil.copy(PRG, drive / "AUTO" / "GDBPB.PRG")
        start = p["start"].replace("/", "\\")
        home = "GAME" if a.disk == "gemdrive" else "LEMMINGS"
        exp = stage / "game.exp"
        run_all.expectation(p["start"], exp)
        exp.write_text(exp.read_text().replace("GAME", home))
        if a.keys:
            steps = exp.read_text().splitlines()[:3]
            for n, k in enumerate(a.keys.split(","), 1):
                step = f"event {k[6:]}" if k.startswith("event:") else f"key {k}"
                steps += [step, "sleep 10", f"shot k{n}"]
            exp.write_text("\n".join(steps) + "\n")
        if a.steps:
            exp.write_text("\n".join(exp.read_text().splitlines()[:3]) + "\n" + a.steps.read_text())
        (stage / "exits.dbg").write_text("\n".join(run_all.EXITS) + "\n")
        (stage / "exit.ini").write_text("info basepage\n")
        cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"), "--setup", a.setup,
               "--disk", a.disk, "--start", f"C:\\{home}\\{start}", "--expect", str(exp),
               "--name", f"fix-{label}", "--memsize", str(p["memsize"]), "--step-time", "30",
               "--parse", str(stage / "exits.dbg")]
        if a.disk == "gemdrive":
            cmd += ["--drive", str(drive)]
        else:
            subprocess.run([str(REPO / "tools" / "dev" / "make_disks.sh"), str(folder), str(stage / "disks")],
                           check=True, capture_output=True)
            cmd += ["--image", str(stage / "disks" / "ppdriver.img")]
        if p["monitor"]:
            cmd += ["--monitor", p["monitor"]]
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
    runs = re.findall(r"run folder (\S+)", out)
    if not runs:
        print(out)
        return 1
    run = Path(runs[0]) if Path(runs[0]).is_absolute() else REPO / runs[0]
    row = run_all.analyse(run, game["strategy"], run_all.SURVEY / "games" / Path(game["download"]).with_suffix(""))
    text = (run / "hatari.out").read_text(errors="replace")
    bpb = collections.Counter()
    for n, d in re.findall(r"(?:(\d+) repeats of: )?BIOS 0x07 Getbpb\(0x([0-9A-F]+)\)", text, re.I):
        bpb["ABCDEFGHIJKLMNOP"[int(d, 16)] + ":"] += int(n or 1)
    print(f"run      {run.relative_to(REPO)}")
    for k in ("result", "opened", "missing", "sectors_c", "floppy", "screen", "halt", "faults", "proposal", "reason"):
        print(f"{k:9}{row.get(k, '')}")
    print(f"getbpb   {dict(bpb) or '-'}")
    print(f"pexec    {', '.join(re.findall(r'Pexec[(]0, \"([^\"]*)\"', text)) or '-'}")
    if a.bpb:
        print(f"gdbpb    {'resident' if 'Ptermres' in text else 'not resident'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
