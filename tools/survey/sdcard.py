#!/usr/bin/env python3
"""EPIC-03 STORY-08: every game laid out for a microSD card, to test from the SidecarTridge Multidevice's
GEMDRIVE.

Usage: sdcard.py [--out DIR]

Writes into DIR (default tools/dev/builds/sdcard/), to copy to the card as it is, one folder per download
of src/survey/migration.csv, from tools/dev/builds/survey/games/ (unpack_games.py):

  <verdict>\\<RAM>\\<group>\\<ZIP's name>\\
  WORKS      as it is from Hatari's GEMDOS drive
  FIXGOS4    a fix, by strategy: FIXGOS4 and FIXGOS5 (Gamex + GOS4, GOS5), FIXHAGE, FIXPLAIN, FIXHOLE
  UNSURE     unsure;  NOFIX: not feasible
  STILLNOT   ported, and still not working: the games of src/survey/ports.tsv whose build fails
  1MB 2MB 4MB  the RAM of the run that gave the verdict (runs.tsv: run_all.py adds RAM to the list's
             figure while a run ends in trouble), the list's figure when there was no run
  10T-AST    at most 80 games, in alphabetical order, named after the first three characters of its
             first and last: a folder with more exhausts the machine's memory (Diego, 2026-10-13); a
             RAM folder is cut into the fewest groups, of even size, and has one at least

The game's folder holds what Hatari's runs had in C:\\GAME\\ (run_all.plan: the folder of the program
started), and beside it what the download keeps next to that folder, unless the folder has its own of that
name (Zero-5's README.TXT); a file the run opened at the drive's root (Maddog Williams' C:\\PABISYS.FIL)
goes to the card's root. A game with no program to start gets its whole download. A ported game
(src/survey/ports.tsv) gets its program to start built for a GEMDOS drive (tools/build_gos5.py or, for a
GOS4 game, build_gos4.py, with the table's options) and the files the table adds from another download (Forgotten Worlds' GOS, D-19: what
the instructions have a user do). INDEX.TXT, at the root,
gives each game's program to start. DIR is emptied first if it holds an INDEX.TXT from this script, and
must otherwise be empty. PP's files: never committed (D-11).
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_all  # noqa: E402

TOPS = {"as it is": "WORKS", "unsure": "UNSURE", "not feasible": "NOFIX"}
FIXES = {"Gamex + GOS4": "FIXGOS4", "Gamex + GOS5": "FIXGOS5", "HAGE": "FIXHAGE", "plain": "FIXPLAIN",
         "plain + HOLE": "FIXHOLE"}
GROUP = 80


def copy(src: Path, dest: Path) -> int:
    """src (a file or a folder) to dest, data only, without .DS_Store; the bytes copied."""
    if src.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        return src.stat().st_size
    dest.mkdir(parents=True, exist_ok=True)
    return sum(copy(e, dest / e.name) for e in sorted(src.iterdir()) if e.name != ".DS_Store")


def groups(stems: set[str]) -> dict[str, str]:
    """Each stem's group: the fewest groups of at most GROUP, of even size, named after their first and
    last stems (10T-AST)."""
    stems = sorted(stems)
    size = math.ceil(len(stems) / math.ceil(len(stems) / GROUP))
    chunks = [stems[i:i + size] for i in range(0, len(stems), size)]
    names = [f"{c[0][:3]}-{c[-1][:3]}" for c in chunks]
    if len(set(names)) < len(names):
        sys.exit(f"error: two groups named alike: {names}")
    return {stem: name for chunk, name in zip(chunks, names) for stem in chunk}


def built(start: Path, options: list[str], strategy: str) -> None:
    """A ported game's program to start, the download's copy at start, built for a GEMDOS drive in its place
    (tools/build_gos4.py for a GOS4 game, build_gos5.py for a GOS5 one)."""
    tool = "build_gos4.py" if strategy == "Gamex + GOS4" else "build_gos5.py"
    done = subprocess.run([sys.executable, "-I", str(REPO / "tools" / tool), str(start), str(start)]
                          + options, capture_output=True, text=True)
    if done.returncode:
        sys.exit(f"error: {start}: {done.stdout}{done.stderr}")


def found(download: str, name: str) -> Path:
    """The one file called name in an unpacked download."""
    hits = [f for f in (run_all.SURVEY / "games" / Path(download).with_suffix("")).rglob(name) if f.is_file()]
    if len(hits) != 1:
        sys.exit(f"error: {name} in {download}: {len(hits)} files")
    return hits[0]


def empty(out: Path) -> None:
    """out emptied (if this script wrote it) or made; refused if it holds anything else."""
    out.mkdir(parents=True, exist_ok=True)
    entries = [e for e in out.iterdir() if e.name != ".DS_Store"]
    if entries and not (out / "INDEX.TXT").is_file():
        sys.exit(f"error: {out} holds files and no INDEX.TXT of this script: not touched")
    for e in entries:
        shutil.rmtree(e, onexc=finder) if e.is_dir() and not e.is_symlink() else e.unlink()


def finder(func, path, exc) -> None:
    """rmtree's errors: a folder open in Finder gets a new .DS_Store while it is deleted; remove it, again."""
    if func is not os.rmdir:
        raise exc
    Path(path, ".DS_Store").unlink(missing_ok=True)
    os.rmdir(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=REPO / "tools" / "dev" / "builds" / "sdcard")
    out = ap.parse_args().out.resolve()
    games = list(csv.DictReader((REPO / "src" / "survey" / "migration.csv").open()))
    files: dict[str, list[dict]] = {}
    for f in csv.DictReader((REPO / "src" / "survey" / "files.csv").open()):
        files.setdefault(f["archive"], []).append(f)
    records = {r["row"]: r for r in csv.DictReader((REPO / "src" / "survey" / "catalogue.csv").open())}
    runs = {r["run"]: r for r in csv.DictReader((run_all.SURVEY / "runs.tsv").open(), delimiter="\t")}
    ports = {r["row"]: r for r in csv.DictReader((REPO / "src" / "survey" / "ports.tsv").open(), delimiter="\t")}
    places = []  # each game's verdict and RAM folders, and its plan
    for g in games:
        run = runs.get(g["run"], {})
        record = records.get(g["row"], {})
        port = ports.get(g["row"])
        top = "STILLNOT" if port and port["result"] == "fails" else \
            FIXES[g["strategy"]] if g["verdict"] == "fix" else TOPS[g["verdict"]]
        ram = run.get("memsize") or run_all.megabytes(record.get("min_ram", ""), record.get("gx", ""),
                                                      record.get("page_min_ram", ""))
        places.append((g, run, top, f"{ram}MB", run_all.plan(g, files.get(g["download"], []), record)))
    stems: dict[tuple[str, str], set[str]] = {}
    for g, run, top, ram, p in places:
        stems.setdefault((top, ram), set()).add(Path(g["download"]).stem.upper())
    group = {key: groups(names) for key, names in stems.items()}
    empty(out)
    folders: dict[str, Path] = {}  # download: its folder on the card
    index, total = [], 0
    for g, run, top, ram, p in places:
        stem = Path(g["download"]).stem.upper()
        dest = out / top / ram / group[(top, ram)][stem] / stem
        if g["download"] not in folders:
            if stem in {f.name for f in folders.values()}:
                sys.exit(f"error: two downloads named {stem}")
            folders[g["download"]] = dest
            if p is None:  # the whole download, without its single top folder
                base = run_all.SURVEY / "games" / Path(g["download"]).with_suffix("")
                inner = [e for e in base.iterdir() if e.name != ".DS_Store"]
                total += copy(inner[0] if len(inner) == 1 and inner[0].is_dir() else base, dest)
            else:
                total += copy(p["folder"], dest)
                log = run_all.RUNS / g["run"] / "hatari.out"
                text = log.read_text(errors="replace").upper() if p["extra"] and log.is_file() else ""
                for e in p["extra"]:
                    if f'"C:\\{e.name.upper()}"' in text:
                        total += copy(e, out / e.name)
                    elif not (dest / e.name).exists():
                        total += copy(e, dest / e.name)
                port = ports.get(g["row"])
                if port:
                    built(dest / p["start"], port["options"].split(), g["strategy"])
                    for name in port["add"].split():
                        total += copy(found(port["from"], name), dest / name)
        elif folders[g["download"]] != dest:
            sys.exit(f"error: {g['download']} in {folders[g['download']]} and {dest}")
        where = folders[g["download"]].relative_to(out)
        start = p["start"].replace("/", "\\") if p else ""
        note = "mono" if run.get("monitor") == "mono" else "" if p else "no program to start"
        note += ("; " if note else "") + (g["solution"] if g["verdict"] == "fix" else
                                          g["reason"] if g["verdict"] != "as it is" else "")
        index.append(f"{where}\\{start}  {g['name']}" + (f" ({note})" if note else ""))
    text = ("PP's hard-disk adaptations from the SidecarTridge Multidevice's GEMDRIVE: "
            f"{len(games)} games, {len(folders)} folders (EPIC-03 STORY-08).\r\n"
            "VERDICT\\RAM\\GROUP\\ZIP\\: WORKS as it is from Hatari's GEMDOS drive; FIX*: a fix, by "
            "strategy (FIXGOS4, FIXGOS5: built for the GEMDOS drive, EPIC-04, EPIC-05); STILLNOT: built, still not working; "
            "UNSURE; NOFIX: not feasible. RAM: what its run needed. GROUP: at most 80 games, "
            "from the first to the last.\r\n\r\n"
            + "".join(line.replace("/", "\\") + "\r\n" for line in sorted(index)))
    (out / "INDEX.TXT").write_bytes(text.encode("ascii", "replace"))
    for (top, ram), names in sorted(stems.items()):
        print(f"{top:9} {ram:4} {len(names):5} in {', '.join(sorted(set(group[(top, ram)].values())))}")
    print(f"{out}: {len(games)} games, {len(folders)} folders, {total / 1e6:.0f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
