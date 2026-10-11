#!/usr/bin/env python3
"""EPIC-03 STORY-04: every game's strategy, from its files.

Usage: classify.py [<out.csv>]        (default src/survey/migration.csv)

Reads src/survey/catalogue.csv (the records and their downloads), src/survey/files.csv (every file
of every download) and the unpacked downloads in tools/dev/builds/survey/games/. For every download
it scans the program the user starts (PP's self-unpacking stub unpacked first, tools/unpack.py)
for the signatures of disk access, and gives the download one strategy from its files and those
signatures (src/notes/strategies.md defines them):

  HAGA, HAGE, HAG2              the module of that name in the game's folder
  Gamex + GOS4, Gamex + GOS5    START.TOS with a D15R_HH4/F4, or D15R_H5/F5/H15/F15/5H/5F file
  Gamex + GOS 1.00              START.TOS with D15R_NG1/F1
  Gamex + GOS (iTOS)            D15RI.FIC: PP's own TOS
  FWRD RAM disk                 an FWRD file: every game file in one, read into RAM
  Gamex                         GXUTnnn.PRG and PP's START stub, no GOS
  PP launcher                   PP's START stub without GXUT
  plain                         the game's own program(s); "+ HOLE" or "AUTO" when those are there
  floppy image                  only floppy images (for the Image Runner, or a floppy)
  original disk image           only STX images: PP's copies of the original disks (ASTGA/)

and "unclassified" with the reason when none fits. "access" is the strongest disk access the start
programs show: registers (ACSI or floppy controller), sectors (XBIOS Floprd or DMAread, BIOS
Rwabs), files (GEMDOS file calls only), or nothing seen. "inner_evidence" lists the sector and
register signatures in the download's PP-packed files (unpacked; D15R and T14 left out, being
TOS's own code): what the game's own stages contain, which PP's launcher may patch at run time. A game (one record of the list) gets the
strategy of its first download that is a hard-disk adaptation (else its first floppy image); the
others are listed too. The verdict
columns stay empty for STORY-05. Standard library only.
"""

from __future__ import annotations

import collections
import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
import unpack  # noqa: E402

GAMES = REPO / "tools" / "dev" / "builds" / "survey" / "games"

# Disk-access signatures (src/notes/launcher-signatures.md, src/notes/strategies.md)
SIGNATURES = {
    "PPHD": rb"\x22\x78\x04\x72\x0c\xa9PPHD\xff\xf8",                  # PP-driver check on hdv_bpb
    "DMAread": rb"\x3f\x3c\x00\x2a\x4e\x4e",                            # XBIOS 42
    "DMAr": rb"\x26\x3c\x44\x4d\x41\x72",                               # move.l #'DMAr',d3
    "Floprd": rb"\x3f\x3c\x00\x08\x4e\x4e",                             # XBIOS 8
    "Rwabs": rb"\x3f\x3c\x00\x04\x4e\x4d",                              # BIOS 4
    "FDC/ACSI": rb"\xff\xff\x86[\x04-\x0d]|[\x41\x43\x45\x47\x49\x4b]\xf8\x86[\x04\x06]|\x31\xfc..\x86[\x04\x06]",
    "GEMDOS file": rb"\x3f\x3c\x00[\x3d\x3f\x4b]\x4e\x41|\x70[\x3d\x3f]\x3f\x00\x4e\x41",
}
GOS = [(r"^D15R_(NG1|F1)\.FIC$", "Gamex + GOS 1.00"), (r"^D15R_(HH4|F4)\.FIC$", "Gamex + GOS4"),
       (r"^D15R_(H5|F5|H15|F15|5H|5F)\.FIC$", "Gamex + GOS5"), (r"^D15RI\.FIC$", "Gamex + GOS (iTOS)")]
NOT_ADAPTATION = ("original disk image", "manual", "not in the mirror")


def scan(path: Path) -> list[str]:
    """The signatures in a program's text section, at even offsets (where 68000 instructions
    start), PP's stub unpacked first."""
    data = path.read_bytes()
    try:
        if data[28:36] == bytes.fromhex("4BFAFFFE204DD1FC"):
            data = unpack.unpack_start(data)
    except SystemExit:
        pass
    text = data[28:28 + int.from_bytes(data[2:6], "big")] if data[:2] == b"\x60\x1a" else data
    return [k for k, pat in SIGNATURES.items()
            if any(m.start() % 2 == 0 for m in re.finditer(pat, text, re.S))]


def inner(files: list[dict], folder: Path) -> str:
    """The disk-access signatures in a download's PP-packed files (not D15R, T14: TOS's own code),
    unpacked: the stages tools/unpack.py can open."""
    found = []
    for f in files:
        if f["kind"] != "PP packed" or f["family"] in ("D15R", "T14"):
            continue
        try:
            data = unpack.unpack_fic((folder / f["path"]).read_bytes())
        except (SystemExit, IndexError, ValueError):
            continue
        hits = [k for k, pat in SIGNATURES.items() if k not in ("GEMDOS file", "PPHD", "DMAr")
                and any(m.start() % 2 == 0 for m in re.finditer(pat, data, re.S))]
        found += [f"{f['path'].rsplit('/', 1)[-1]}: {h}" for h in hits]
    return "; ".join(found)


def strategy(files: list[dict], folder: Path) -> tuple[str, str]:
    """(strategy, evidence) for one download from its inventory rows."""
    names = {f["path"].rsplit("/", 1)[-1].upper(): f for f in files}
    starts = [f for f in files if f["start"]]
    found = []
    for f in starts:
        if f["kind"] == "program":
            found += [f"{f['path'].rsplit('/', 1)[-1]}: {s}" for s in scan(folder / f["path"])]
    evidence = "; ".join(found)
    kinds = collections.Counter(f["kind"] for f in files)
    for module in ("HAG2", "HAGE", "HAGA"):
        if module in names:
            gos = sorted(n for n in names if n.startswith("D15R") or n.startswith("T14"))
            return module, f"{module}{' + ' + ','.join(gos) if gos else ''}; {evidence}".strip("; ")
    for pattern, name in GOS:
        hit = [n for n in names if re.match(pattern, n)]
        if hit:
            return name, f"{','.join(sorted(hit))}; {evidence}".strip("; ")
    if kinds["FWRD"]:
        return "FWRD RAM disk", f"FWRD; {evidence}".strip("; ")
    stub = [f for f in starts if "PP stub" in f["detail"]]
    if any(f["family"] == "GXUT" for f in files) and stub:
        return "Gamex", f"GXUT, PP stub; {evidence}".strip("; ")
    if stub:
        return "PP launcher", f"PP stub; {evidence}".strip("; ")
    if starts:
        extra = " + HOLE" if any(f["family"] == "HOLE" for f in files) else ""
        name = "AUTO" if any(f["family"] == "AUTO" for f in starts) else "plain" + extra
        return name, f"{','.join(f['path'].rsplit('/', 1)[-1] for f in starts)}; {evidence}".strip("; ")
    if kinds["STX image"] and not kinds["ST image"] + kinds["MSA image"]:
        return "original disk image", "STX only"
    if kinds["ST image"] + kinds["MSA image"]:
        return "floppy image", f"{kinds['ST image'] + kinds['MSA image']} images"
    if files and all(f["path"].lower().endswith(".pdf") for f in files):
        return "manual", "PDF only"
    return "unclassified", "no program, no image: " + ",".join(sorted(names)[:5])


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "src" / "survey" / "migration.csv"
    records = list(csv.DictReader((REPO / "src" / "survey" / "catalogue.csv").open()))
    by_archive = collections.defaultdict(list)
    for f in csv.DictReader((REPO / "src" / "survey" / "files.csv").open()):
        by_archive[f["archive"]].append(f)
    cache: dict[str, tuple[str, str]] = {}
    rows = []
    for rec in records:
        downloads = [d for d in rec["page_downloads"].split(";") if d]
        result = []
        for d in downloads:
            if d not in cache:
                folder = GAMES / Path(d).with_suffix("")
                cache[d] = (*strategy(by_archive[d], folder), inner(by_archive[d], folder)) \
                    if d in by_archive else ("not in the mirror", "404", "")
            result.append((d, *cache[d]))
        main_ = next((r for r in result if r[1] not in NOT_ADAPTATION + ("floppy image",)),
                     next((r for r in result if r[1] == "floppy image"), result[0] if result else ("", "", "", "")))
        ev = main_[2]
        access = "registers" if "FDC/ACSI" in ev else "sectors" if re.search(r"Floprd|Rwabs|DMAread", ev) \
            else "files" if "GEMDOS file" in ev else ""
        rows.append({"row": rec["row"], "name": rec["name"], "url": rec["url"], "download": main_[0],
                     "strategy": main_[1], "access": access, "evidence": ev, "inner_evidence": main_[3],
                     "other_downloads": "; ".join(f"{d}: {s}" for d, s, _, _ in result if d != main_[0]),
                     "cat_code": rec["cat_code"], "code_category": rec["code_category"],
                     "page_mode": rec["page_mode"], "min_ram": rec["min_ram"], "monitor": rec["page_monitor"],
                     "verdict": "", "run": "", "reason": "", "solution": ""})
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{out.relative_to(REPO)}: {len(rows)} games")
    counts = collections.Counter(r["strategy"] for r in rows)
    for s, n in counts.most_common():
        print(f"  {n:5}  {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
