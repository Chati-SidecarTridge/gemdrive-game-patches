#!/usr/bin/env python3
"""EPIC-03 STORY-06: the other downloads of the games to fix, run from Hatari's GEMDOS drive.

Usage: run_other.py [--jobs N] [--disk gemdrive|ppdriver] [--only ZIP ...] [--list]

For every GOS4/GOS5 game of src/survey/migration.csv, and Great Giana Sisters STE, each of its
other downloads (other_downloads) whose strategy runs from a GEMDOS drive (HAGA, HAGE, HAG2, plain,
Gamex, launcher without Gamex, FWRD RAM disk…) is run as run_all.py runs a game's main download: the same
program choice, RAM, monitor, analysis and escalation, on ST TOS 1.04 (Giana on STE TOS 1.62). A
download whose README fixes its folder gets that name too (COMP.ZIP: C:\\COMP). Lines go to
tools/dev/builds/survey/runs-other.tsv (run_all's columns, the download and the main download's
strategy; one per game, download and disk), snapshots to tools/dev/builds/survey/snapshots-other/;
verdicts.py names the ones that run as it is beside the game's solution. Standard library only.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_all  # noqa: E402

REPO = run_all.REPO
TSV = run_all.SURVEY / "runs-other.tsv"
FIELDS = run_all.FIELDS + ["download", "main_strategy"]
KEEP = {"HAGA", "HAG2", "HAGE", "plain", "plain + HOLE", "Gamex", "Gamex + GOS 1.00", "launcher without Gamex", "FWRD RAM disk"}
GIANA = "1112"
FOLDERS = {"COMP.ZIP": ("COMP",)}  # its README and .RDF files name C:\COMP
LOCK = threading.Lock()


def items() -> list[tuple[dict, str, str, str]]:
    """(game, download, its strategy, setup) for every download to run."""
    out = []
    for g in csv.DictReader((REPO / "src" / "survey" / "migration.csv").open()):
        if g["strategy"] not in ("Gamex + GOS4", "Gamex + GOS5") and g["row"] != GIANA:
            continue
        for part in g["other_downloads"].split(";"):
            if ":" in part:
                zip_, strategy = (x.strip() for x in part.split(":", 1))
                if strategy in KEEP:
                    out.append((g, zip_, strategy, "ste-162" if g["row"] == GIANA else "st-104"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=5)
    ap.add_argument("--disk", default="gemdrive", choices=("gemdrive", "ppdriver"))
    ap.add_argument("--only", nargs="+", default=[])
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    run_all.SNAPSHOTS = run_all.SURVEY / "snapshots-other"
    files: dict[str, list[dict]] = {}
    for f in csv.DictReader((REPO / "src" / "survey" / "files.csv").open()):
        files.setdefault(f["archive"], []).append(f)
    records = {r["row"]: r for r in csv.DictReader((REPO / "src" / "survey" / "catalogue.csv").open())}
    todo = items()
    if args.list:
        for g, zip_, strategy, setup in todo:
            print(g["row"], g["name"], g["strategy"], zip_, strategy, setup)
        print(len(todo), "downloads,", len({g["row"] for g, *_ in todo}), "games")
        return 0
    if not TSV.exists():
        TSV.write_text("\t".join(FIELDS) + "\n")
    done = {(r["row"], r["download"], r["disk"]) for r in csv.DictReader(TSV.open(), delimiter="\t")}
    todo = [t for t in todo if (t[0]["row"], t[1], args.disk) not in done and (not args.only or t[1] in args.only)]
    print(f"{len(todo)} downloads to run", flush=True)
    started = time.time()

    def work(t: tuple[dict, str, str, str]) -> dict:
        g, zip_, strategy, setup = t
        game = dict(g, download=zip_, strategy=strategy, name=f"{Path(zip_).stem} {g['name']}")
        p = run_all.plan(game, files.get(zip_, []), records.get(g["row"], {}))
        if p is None:
            row = {"row": g["row"], "setup": setup, "disk": args.disk, "proposal": "unsure",
                   "reason": "no program to start in the download"}
        else:
            row = run_all.run_game(game, p, setup, args.disk, FOLDERS.get(zip_, ()))
        row.update(name=g["name"], strategy=strategy, download=zip_, main_strategy=g["strategy"])
        line = "\t".join(str(row.get(k, "")).replace("\t", " ") for k in FIELDS) + "\n"
        key = (row["row"], zip_, row["disk"])
        with LOCK:  # one line per game, download and disk
            lines = TSV.read_text().splitlines(keepends=True)
            kept = [l for l in lines[1:] if (l.split("\t")[0], l.split("\t")[FIELDS.index("download")],
                                            l.split("\t")[4]) != key]
            TSV.write_text(lines[0] + "".join(kept) + line)
        return row

    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        for n, row in enumerate(pool.map(work, todo), 1):
            print(f"{n:4}/{len(todo)} {time.time() - started:6.0f}s {row['proposal']:9} {row['strategy']:12} "
                  f"{row['download']:14} {row['name'][:28]:28} {row.get('reason', '')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
