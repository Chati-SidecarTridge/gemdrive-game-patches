#!/usr/bin/env python3
"""EPIC-03 STORY-03: what every adaptation contains, file by file.

Usage: inventory.py [<out.csv>]        (default src/survey/files.csv)

Reads the archives unpack_games.py left in tools/dev/builds/survey/games/ and writes one row per
file: the archive (its path in the mirror's site/), the file's path in it, size, the first 16 hex
digits of its SHA-256, and what it is:

  start     "yes" for the program the user runs: the shallowest RUNME*.TOS, START*.TOS or
            START*.PRG; without one, the only program (.TOS, .PRG, .APP, .TTP) at the shallowest
            level holding programs, or "choice" for each when there are several
  family    PP's file-name families (src/notes/modes.md): D15R, T14, HAGA module, GXUT, PCH,
            state save (GSxx.TOS), floppy image, AUTO, HOLE, text
  kind      from the first bytes: program (0x601A), PP packed (the "C3" header), ICE, ATM5, FWRD
            (PP's file-wise RAM disk), zip, MSA image, STX image, ST image (by name, whole
            sectors), text, data
  detail    program: text+data+bss and "PP stub" for PP's self-unpacking START.TOS stub;
            PP packed: the name in its header and its unpacked size; ICE: its unpacked size
  marks     byte patterns from src/notes/launcher-signatures.md found in the file as it is:
            PPGX, PPHD (the driver check), unpacker (PP's unpack routine)

Prints the check of STORY-03's acceptance: every record of src/survey/catalogue.csv has its
downloads unpacked, or the reason it has not. Standard library only.
"""

from __future__ import annotations

import collections
import csv
import hashlib
import re
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SURVEY = REPO / "tools" / "dev" / "builds" / "survey"
START = re.compile(r"^(RUNME|START)[^/]*\.(TOS|PRG)$", re.I)
STUB = bytes.fromhex("4BFAFFFE204DD1FC")                       # START.TOS's stub (launcher-signatures.md)
MARKS = {"PPGX": b"PPGX", "PPHD": bytes.fromhex("22780472 0CA9 50504844 FFF8".replace(" ", "")),
         "unpacker": bytes.fromhex("428078067A3F42401019")}


def family(path: str) -> str:
    name = path.rsplit("/", 1)[-1].upper()
    for pattern, fam in ((r"^D15R.*\.FIC$", "D15R"), (r"^T14.*\.FIC$", "T14"), (r"^HAG[AE2]$", "HAGA module"),
                         (r"^GXUT.*\.PRG$", "GXUT"), (r"\.PCH$", "PCH"), (r"^GS\w\w\.TOS$", "state save"),
                         (r"\.(ST|MSA|STX|STT)$", "floppy image"), (r"HOLE.*\.PRG$", "HOLE"),
                         (r"\.(TXT|DOC|NFO)$", "text")):
        if re.search(pattern, name):
            return fam
    return "AUTO" if re.search(r"(^|/)AUTO/", path, re.I) else ""


def describe(path: str, data: bytes) -> tuple[str, str]:
    """(kind, detail) from the file's first bytes."""
    if len(data) >= 28 and data[:2] == b"\x60\x1a":
        text, dat, bss = struct.unpack(">III", data[2:14])
        return "program", f"{text}+{dat}+{bss}" + (" PP stub" if data[28:36] == STUB else "")
    if len(data) >= 32 and data[:2] == b"C3" and data[2] == 0:
        packed, unpacked = struct.unpack(">II", data[2:10])
        name = data[16:32].split(b"\0")[0].decode("latin-1")
        if 32 + packed <= len(data) + 4 and re.fullmatch(r"[ -~]*", name):
            return "PP packed", f"{name} {unpacked}"
    if data[:4] in (b"ICE!", b"Ice!"):
        return "ICE", str(struct.unpack(">I", data[8:12])[0]) if len(data) >= 12 else ""
    if data[:4] == b"ATM5":
        return "ATM5", ""
    if data[:4] == b"FWRD":  # PP's "filewise ramdisk": every file of the game in one (EPIC-03 STORY-03)
        return "FWRD", str(struct.unpack(">H", data[4:6])[0]) + " files"
    if data[:4] == b"PK\x03\x04":
        return "zip", ""
    if data[:2] == b"\x0e\x0f":
        return "MSA image", ""
    if data[:4] == b"RSY\x00":
        return "STX image", ""
    if re.search(r"\.(ST|STT)$", path, re.I) and data and len(data) % 512 == 0:
        return "ST image", f"{len(data) // 512} sectors"
    if data and all(b in b"\t\n\r\x1a" or 32 <= b < 127 or b >= 128 for b in data[:512]) \
            and sum(32 <= b < 127 for b in data[:512]) > 0.8 * min(len(data), 512):
        return "text", ""
    return "data", ""


def starts(files: list[str]) -> dict[str, str]:
    """path -> "yes" or "choice" for the program(s) the user starts."""
    named = [f for f in files if START.match(f.rsplit("/", 1)[-1])]
    if named:
        top = min(f.count("/") for f in named)
        return {f: "yes" for f in named if f.count("/") == top}
    progs = [f for f in files if re.search(r"\.(TOS|PRG|APP|TTP)$", f, re.I)]
    if not progs:
        return {}
    top = min(f.count("/") for f in progs)
    progs = [f for f in progs if f.count("/") == top]
    return {f: "yes" if len(progs) == 1 else "choice" for f in progs}


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "src" / "survey" / "files.csv"
    unpacked = list(csv.DictReader((SURVEY / "unpacked.tsv").open(), delimiter="\t"))
    games = SURVEY / "games"
    rows = []
    for u in unpacked:
        folder = games / u["folder"]
        files = sorted(str(f.relative_to(folder)) for f in folder.rglob("*") if f.is_file())
        start = starts(files)
        for rel in files:
            data = (folder / rel).read_bytes()
            kind, detail = describe(rel, data)
            rows.append({"archive": u["archive"], "path": rel, "size": len(data),
                         "sha256": hashlib.sha256(data).hexdigest()[:16],
                         "start": start.get(rel, ""),
                         "family": family(rel), "kind": kind, "detail": detail,
                         "marks": ";".join(k for k, v in MARKS.items() if v in data)})
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{out.relative_to(REPO)}: {len(rows)} files in {len(unpacked)} archives")
    print("  kinds:", dict(collections.Counter(r["kind"] for r in rows).most_common()))
    print("  families:", dict(collections.Counter(r["family"] for r in rows if r["family"]).most_common()))

    # STORY-03's acceptance: every record's downloads are unpacked, or the reason they are not
    status = {u["archive"]: u["status"] for u in unpacked}
    started = collections.Counter(r["archive"] for r in rows if r["start"])
    records = list(csv.DictReader((REPO / "src" / "survey" / "catalogue.csv").open()))
    none, missing, nostart = [], collections.Counter(), []
    for rec in records:
        downloads = [d for d in rec["page_downloads"].split(";") if d]
        ok = [d for d in downloads if status.get(d) == "ok"]
        for d in downloads:
            if d not in status:
                missing[d] += 1
        if not ok:
            none.append(f"{rec['name']} ({', '.join(f'{d}: {status.get(d, 404)}' for d in downloads)})")
        elif not any(started[d] for d in ok):
            nostart.append(rec["name"])
    print(f"  records: {len(records)}; with a download unpacked: {len(records) - len(none)}; without: {none}")
    print(f"  downloads not in the mirror (PP's site answered 404): {len(missing)}")
    print(f"  records whose downloads have no program to start: {len(nostart)} {nostart[:10]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
