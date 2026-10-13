#!/usr/bin/env python3
"""EPIC-03 STORY-07: is a clone of this repository ready to go public (D-15)?

Usage: check_public.py [<clone>]

Checks a clone (by default a fresh clone of this repository, made in a temporary folder, with every
branch) against docs/publication/remove.txt: no entry may match a file of the clone or a path in any
commit of its history; no binary file the list does not name may be left in its history; no commit
message may carry an AI co-author trailer or a "Generated with" line (CLAUDE.md); and the site must
build from the clone (tools/site/build_site.py --no-snapshots --check). Prints what it finds and
exits 0 only when the clone is ready. Standard library only.
"""

from __future__ import annotations

import collections
import fnmatch
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LIST = REPO / "docs" / "publication" / "remove.txt"


def git(clone: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(clone), *args], capture_output=True, check=True).stdout


def entries() -> list[tuple[str, str, str]]:
    out = []
    for line in LIST.read_text().splitlines():
        m = re.match(r"(must|review)\s+(\S+)\s*(?:#\s*(.*))?$", line)
        if m:
            out.append(m.groups())
    return out


def matches(path: str, pattern: str) -> bool:
    return path.startswith(pattern) if pattern.endswith("/") else fnmatch.fnmatchcase(path, pattern)


def check(clone: Path) -> int:
    problems = 0
    files = git(clone, "ls-files", "-z").decode().split("\0")[:-1]
    history = collections.defaultdict(set)  # every path any commit of any branch touched -> its blob ids
    parts = git(clone, "log", "--all", "-m", "--raw", "-z", "--no-abbrev", "--no-renames", "--format=").decode().split("\0")
    for meta, path in zip(parts, parts[1:]):
        if meta.strip("\n").startswith(":"):
            oid = meta.split()[3]
            history[path].update({oid} - {"0" * len(oid)})
    print(f"{clone}: {len(files)} files, {len(history)} paths in the history of every branch")

    listed = entries()
    for kind, pattern, why in listed:
        now = [f for f in files if matches(f, pattern)]
        ever = [p for p in history if matches(p, pattern)]
        if now or ever:
            problems += 1
            print(f"  {kind:6} {pattern}: {len(now)} files, {len(ever)} paths in history ({why})")

    binaries = []
    for path, oids in sorted(history.items()):
        if any(matches(path, p) for _, p, _ in listed):
            continue
        for oid in oids:
            if b"\0" in git(clone, "cat-file", "blob", oid)[:8000]:
                binaries.append(path)
                break
    if binaries:
        problems += 1
        print(f"  binary files the list does not name: {len(binaries)}: {', '.join(binaries[:10])}")

    log = git(clone, "log", "--all", "--format=%h %B%x00").decode()
    trailers = [c.split(" ", 1)[0] for c in log.split("\0") if re.search(r"(?im)^co-authored-by:|generated with", c)]
    if trailers:
        problems += 1
        print(f"  commits with a co-author trailer or a \"Generated with\" line: {', '.join(trailers)}")

    with tempfile.TemporaryDirectory() as out:
        site = subprocess.run([sys.executable, "-I", str(clone / "tools" / "site" / "build_site.py"), "--out",
                               str(Path(out) / "site"), "--no-snapshots", "--check"], capture_output=True, text=True)
    print("  site: " + (site.stdout.strip().splitlines() or [site.stderr.strip()[-200:]])[-1])
    problems += site.returncode != 0

    print("ready to go public" if not problems else f"not ready: {problems} problem(s)")
    return 1 if problems else 0


def main() -> int:
    if len(sys.argv) > 1:
        return check(Path(sys.argv[1]).resolve())
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "clone"
        subprocess.run(["git", "clone", "-q", "--no-local", str(REPO), str(clone)], check=True)
        return check(clone)


if __name__ == "__main__":
    sys.exit(main())
