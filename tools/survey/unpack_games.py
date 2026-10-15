#!/usr/bin/env python3
"""EPIC-03 STORY-03: every archive in the mirror, unpacked.

Usage: unpack_games.py

Every .zip, .rar, .7z and .lzh under the mirror's site/ (MIRROR in tools/dev/dev.cfg) is unpacked
into tools/dev/builds/survey/games/<its path in site/, without the extension>/, emptied first:
LEMMINGS.ZIP into games/LEMMINGS/, ASTGA/I/IRONLORF.ZIP into games/ASTGA/I/IRONLORF/. These are
untrusted data: only their bytes are written, nothing from them runs, and an entry whose path
would leave its folder (absolute, or with ..) is refused. ZIP archives are read with zipfile; the
others are listed and extracted by bsdtar, which keeps entries inside the folder. A ZIP inside an
archive is unpacked once more, next to itself (X.ZIP into X/), with the same checks.

Writes tools/dev/builds/survey/unpacked.tsv: archive, folder, files, bytes, and "ok" or the reason
it was not (fully) unpacked. Standard library, and bsdtar for the non-ZIP formats.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "tools" / "dev" / "builds" / "survey"
FORMATS = (".zip", ".rar", ".7z", ".lzh")


def mirror() -> Path:
    for line in (REPO / "tools" / "dev" / "dev.cfg").read_text().splitlines():
        if line.startswith("MIRROR="):
            return Path(line.split("=", 1)[1].strip())
    sys.exit("error: no MIRROR in tools/dev/dev.cfg")


def safe(name: str) -> PurePosixPath | None:
    """The entry's path inside its folder, or None if it would leave it."""
    p = PurePosixPath(name.replace("\\", "/"))
    if p.is_absolute() or ".." in p.parts or not p.parts:
        return None
    return p


def unpack_zip(archive: Path, dest: Path) -> list[str]:
    problems = []
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            rel = safe(info.filename)
            if rel is None:
                problems.append(f"refused {info.filename}")
                continue
            target = dest.joinpath(*rel.parts)
            if target.exists():  # the Mac's file system ignores case: A/x and a/X collide
                problems.append(f"same name twice {info.filename}")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(info))
    return problems


def unpack_other(archive: Path, dest: Path) -> list[str]:
    listing = subprocess.run(["bsdtar", "-tf", str(archive)], capture_output=True, text=True)
    if listing.returncode:
        return [f"bsdtar cannot list it: {listing.stderr.strip()[:80]}"]
    bad = [n for n in listing.stdout.splitlines() if safe(n) is None]
    if bad:
        return [f"refused {n}" for n in bad]
    dest.mkdir(parents=True, exist_ok=True)
    run = subprocess.run(["bsdtar", "-xf", str(archive), "-C", str(dest), "--no-same-owner",
                          "--no-same-permissions"], capture_output=True, text=True)
    return [f"bsdtar: {run.stderr.strip()[:80]}"] if run.returncode else []


def main() -> int:
    site = mirror() / "site"
    games = OUT / "games"
    shutil.rmtree(games, ignore_errors=True)
    games.mkdir(parents=True)
    archives = sorted(p for p in site.rglob("*") if p.is_file() and p.suffix.lower() in FORMATS)
    rows, failed = [], 0
    for archive in archives:
        rel = archive.relative_to(site)
        dest = games / rel.with_suffix("")
        dest.mkdir(parents=True, exist_ok=True)
        try:
            problems = (unpack_zip if archive.suffix.lower() == ".zip" else unpack_other)(archive, dest)
            for inner in sorted(f for f in dest.rglob("*") if f.is_file() and f.suffix.lower() == ".zip"):
                inner_dest = inner.with_suffix("")
                if inner_dest.exists():
                    problems.append(f"no room to unpack {inner.relative_to(dest)}")
                else:
                    problems += [f"{inner.name}: {p}" for p in unpack_zip(inner, inner_dest)]
        except (zipfile.BadZipFile, OSError, RuntimeError, NotImplementedError) as error:
            problems = [f"{type(error).__name__}: {error}"[:100]]
        files = [f for f in dest.rglob("*") if f.is_file()]
        status = "ok" if not problems else " ".join("; ".join(problems).split())
        failed += bool(problems)
        rows.append(f"{rel}\t{dest.relative_to(games)}\t{len(files)}\t{sum(f.stat().st_size for f in files)}\t{status}")
    (OUT / "unpacked.tsv").write_text("archive\tfolder\tfiles\tbytes\tstatus\n" + "\n".join(rows) + "\n")
    total = sum(int(r.split("\t")[3]) for r in rows)
    print(f"{len(archives)} archives into {games.relative_to(REPO)}: {total / 1e9:.2f} GB; "
          f"{failed} with problems (tools/dev/builds/survey/unpacked.tsv)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
