#!/usr/bin/env python3
"""EPIC-09 STORY-02: every archive of the mirror, and what the patcher page does with it (D-22).

Usage: patch_table.py

Writes src/survey/patches.tsv, one line per ZIP under the mirror's site/ (MIRROR in tools/dev/dev.cfg):

  archive        its path in site/ (LEMMINGS.ZIP, ASTGA/I/IRONLORF.ZIP)
  bytes, sha256  the file as downloaded: the page knows a ZIP by these
  rows           the rows of src/survey/migration.csv whose download it is, or that list it as another
  start          the game's program to start, its path in the ZIP (run_all.py's plan), for the page to say
  action         none (the game runs as it is), gos5, gos4, gdbpb, fastload, rody2 (a fix the page
                 applies), refuse (no file: the reason says why), other (another download of a game,
                 not the one its verdict is from), notgame (no game of the list)
  options        the build tool's options (--floppy)
  target         for a fix, the file the page writes, its path in the ZIP
  target_sha256  that file in the original ZIP (empty: the page adds it)
  result_sha256  that file as the page must write it: the card builder's result
  needs, needs_sha256, add   a second download the user gives (D-23), its SHA-256, and the files taken
                 from it (name=sha256, ...)
  reason         in plain words, for the page

A fix's result is computed by tools/survey/sdcard.py's own build (built(), and the files ports.tsv adds)
on a copy of the unpacked download (tools/dev/builds/survey/games/, unpack_games.py), so the page's file
equals the card's. The table holds names, sizes and hashes only: no byte of the adaptations (D-11).
"""

from __future__ import annotations

import csv
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_all  # noqa: E402
import sdcard  # noqa: E402

OUT = REPO / "src" / "survey" / "patches.tsv"
FIELDS = ["archive", "bytes", "sha256", "rows", "action", "start", "options", "target", "target_sha256",
          "result_sha256", "needs", "needs_sha256", "add", "reason"]


def mirror() -> Path:
    for line in (REPO / "tools" / "dev" / "dev.cfg").read_text().splitlines():
        if line.startswith("MIRROR="):
            return Path(line.split("=", 1)[1].strip()) / "site"
    sys.exit("error: MIRROR not set in tools/dev/dev.cfg")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fix(g: dict, port: dict, p: dict, site: Path) -> dict:
    """The fix's target and result, from sdcard.py's own build on a copy of the unpacked download."""
    base = run_all.SURVEY / "games" / Path(g["download"]).with_suffix("")
    options = port["options"].split()
    with tempfile.TemporaryDirectory(dir=run_all.SURVEY) as tmp:
        if p is None:  # the whole download, as sdcard.py copies it (Rody and Mastico 2)
            inner = [e for e in base.iterdir() if e.name != ".DS_Store"]
            folder = inner[0] if len(inner) == 1 and inner[0].is_dir() else base
            start = ""
        else:
            folder, start = p["folder"], p["start"]
        work = Path(tmp) / "game"
        shutil.copytree(folder, work)
        prefix = folder.relative_to(base).as_posix()
        prefix = "" if prefix == "." else prefix + "/"
        row = {"options": " ".join(o for o in options if o.startswith("--"))}
        if g["strategy"] in ("Gamex + GOS4", "Gamex + GOS5"):
            row["action"] = "gos4" if g["strategy"] == "Gamex + GOS4" else "gos5"
            row["target"] = prefix + start
            row["target_sha256"] = sha(folder / start)
            sdcard.built(work / start, options, g["strategy"])
            row["result_sha256"] = sha(work / start)
        elif "gdbpb" in options:
            row["action"], row["target"] = "gdbpb", prefix + "GDBPB.PRG"
            sdcard.built(work / start, options, g["strategy"])
            row["result_sha256"] = sha(work / "GDBPB.PRG")
        elif "fastload" in options:
            known = [f for f in folder.rglob("*") if f.name.upper() in sdcard.set_fastload.PROGRAMS]
            row["action"], row["target"] = "fastload", prefix + known[0].relative_to(folder).as_posix()
            row["target_sha256"] = sha(known[0])
            sdcard.built(work / start, options, g["strategy"])
            row["result_sha256"] = sha(work / known[0].relative_to(folder))
        if port["add"]:
            needs = port["from"]
            row["needs"], row["needs_sha256"] = needs, sha(site / needs)
            row["add"] = ",".join(f"{prefix}{n}={sha(sdcard.found(needs, n))}" for n in port["add"].split())
            if "action" not in row:  # the added program is the whole fix (Rody and Mastico 2)
                row["action"] = "rody2" if g["download"].upper() == "RODYM2.ZIP" else "add"
                row["start"] = row["add"].split("=")[0]
    return row


def main() -> int:
    site = mirror()
    games = list(csv.DictReader((REPO / "src" / "survey" / "migration.csv").open()))
    files: dict[str, list[dict]] = {}
    for f in csv.DictReader((REPO / "src" / "survey" / "files.csv").open()):
        files.setdefault(f["archive"], []).append(f)
    records = {r["row"]: r for r in csv.DictReader((REPO / "src" / "survey" / "catalogue.csv").open())}
    ports = {r["row"]: r for r in csv.DictReader((REPO / "src" / "survey" / "ports.tsv").open(), delimiter="\t")}
    primary: dict[str, list[dict]] = {}
    other: dict[str, list[dict]] = {}
    for g in games:
        primary.setdefault(g["download"].upper(), []).append(g)
        for o in filter(None, (x.split(":")[0].strip() for x in g["other_downloads"].split(";"))):
            other.setdefault(o.upper(), []).append(g)
    lines = []
    for z in sorted(p for p in site.rglob("*") if p.is_file() and p.suffix.upper() == ".ZIP"):
        name = z.relative_to(site).as_posix()
        row = {"archive": name, "bytes": z.stat().st_size, "sha256": sha(z)}
        mine = primary.get(name.upper(), [])
        if mine:
            row["rows"] = ";".join(g["row"] for g in mine)
            p0 = run_all.plan(mine[0], files.get(mine[0]["download"], []), records.get(mine[0]["row"], {}))
            if p0 is not None:
                base = run_all.SURVEY / "games" / Path(mine[0]["download"]).with_suffix("")
                row["start"] = (p0["folder"] / p0["start"]).relative_to(base).as_posix()
            fixes = [g for g in mine if g["verdict"] == "fix" and ports.get(g["row"], {}).get("result") == "runs"]
            if fixes:
                g = fixes[0]
                p = run_all.plan(g, files.get(g["download"], []), records.get(g["row"], {}))
                row.update(fix(g, ports[g["row"]], p, site))
                row["reason"] = g["solution"]
            elif all(g["verdict"] == "as it is" for g in mine):
                row["action"], row["reason"] = "none", "runs from GEMDOS and GEMDRIVE as it is"
            else:
                g = next(g for g in mine if g["verdict"] != "as it is")
                port = ports.get(g["row"], {})
                why = {"fix": "a fix is planned but not built yet", "not feasible": "not feasible",
                       "unsure": "unsure"}[g["verdict"]]
                if port.get("result") == "fails":
                    why = "built, but it still fails"
                row["action"], row["reason"] = "refuse", f"{why}: {g['reason']}"
        elif name.upper() in other:
            gs = other[name.upper()]
            row["rows"] = ";".join(g["row"] for g in gs)
            row["action"] = "other"
            row["reason"] = (f"another download of {gs[0]['name']}; its verdict is from {gs[0]['download']}, "
                             f"the one the page patches")
        else:
            row["action"], row["reason"] = "notgame", "not a game of the list (a tool or a document)"
        lines.append(row)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, FIELDS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for row in lines:
            w.writerow({k: row.get(k, "") for k in FIELDS})
    count: dict[str, int] = {}
    for row in lines:
        count[row["action"]] = count.get(row["action"], 0) + 1
    print(f"{OUT.relative_to(REPO)}: {len(lines)} archives, " + ", ".join(f"{k} {v}" for k, v in sorted(count.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
