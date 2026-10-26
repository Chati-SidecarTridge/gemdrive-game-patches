#!/usr/bin/env python3
"""tools/survey/watch.py: what changed on the 8bitchip.info website's list since the survey's tables.

Usage: watch.py [--head] [--report <file.md>]

Reads the live list page (fromhd3.php), one request, and compares it with
src/survey/catalogue.csv: records added or removed, and records whose cells
changed (the Date column is the upload or last change of the adaptation). For
every added or changed record it reads the game page and fetches its downloads,
and compares each one's size and SHA-256 with src/survey/patches.tsv: a new
archive, or one that is no longer the file the patcher knows.

--head also asks the server for the size of every archive of patches.tsv, one
request a second without downloading it (about 35 minutes), and fetches only
the archives whose size changed or that are gone. Meant for once a week.

What it finds is kept in tools/dev/builds/watch/state.json until the tables
agree with the website again, so a change seen by a --head run stays in the
next runs' reports. With --report the findings are written as Markdown to the
file, which is removed when there are none; without it they are printed.
Standard library only; never writes the tables.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalogue  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
SURVEY = REPO / "src" / "survey"
STATE = REPO / "tools" / "dev" / "builds" / "watch" / "state.json"
SITE = catalogue.SITE_URL
PAUSE = 1.0
RETRIES = (5, 15, 45)


def get(url: str, head: bool = False) -> tuple[int, bytes, str]:
    """(status, body, final url) of url, after the retries; status 0 when the server never answered."""
    for wait in (*RETRIES, None):
        time.sleep(PAUSE)
        try:
            request = urllib.request.Request(url, method="HEAD" if head else "GET")
            with urllib.request.urlopen(request, timeout=120) as response:
                body = b"" if head else response.read()
                size = response.headers.get("content-length", "") if head else str(len(body))
                return response.status, body, size
        except urllib.error.HTTPError as error:
            if error.code == 404 or wait is None:
                return error.code, b"", ""
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            print(f"  {url}: {error}", file=sys.stderr, flush=True)
            if wait is None:
                return 0, b"", ""
        time.sleep(wait)
    return 0, b"", ""


def archive_url(name: str) -> str:
    """A download as the site serves it: dwnld.php?get=NAME sends to NAME, at the top of the site."""
    return SITE + name


def fetch_archive(name: str) -> dict:
    status, body, _ = get(archive_url(name))
    if status != 200:
        return {"status": status}
    return {"status": 200, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}


def live_records() -> list[tuple[str, str, list[str]]]:
    status, body, _ = get(SITE + "fromhd3.php")
    if status != 200:
        sys.exit(f"error: the list page answered {status}")
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "fromhd3.php").write_bytes(body)
        return catalogue.read_list(Path(tmp))


def page_downloads(page: str) -> list[str] | None:
    """The downloads a game page offers, as catalogue.py reads them; None when the page is gone."""
    status, body, _ = get(SITE + page)
    if status != 200:
        return None
    raw = body.decode("latin-1")
    links = catalogue.downloads_of(raw, page)
    if not links:  # the page sends its download to the game archive (ASTGA/)
        m = re.search(r'href="\.\./(ASTGA/[^"]+)"', raw)
        if m:
            status, body, _ = get(SITE + m.group(1))
            if status == 200:
                links = catalogue.downloads_of(body.decode("latin-1"), m.group(1))
    return [d[0] for d in links]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--head", action="store_true", help="also check the size of every archive of patches.tsv")
    ap.add_argument("--report", type=Path, help="write the findings to this Markdown file")
    args = ap.parse_args()

    known = {r["archive"]: r for r in csv.DictReader((SURVEY / "patches.tsv").open(), delimiter="\t")}
    rows = list(csv.DictReader((SURVEY / "catalogue.csv").open()))
    state = json.loads(STATE.read_text()) if STATE.is_file() else {"archives": {}, "last_head": ""}
    flagged: dict[str, dict] = state["archives"]  # archive -> what the website serves now

    # 1. The list, against catalogue.csv: a record is its name and page.
    live = live_records()
    ours = {(r["name"], r["page"]): r for r in rows}
    theirs = {(name, page): dict(zip(catalogue.LIST_COLUMNS, cells)) for name, page, cells in live}
    added = [k for k in theirs if k not in ours]
    removed = [k for k in ours if k not in theirs]
    changed = {k: [c for c in catalogue.LIST_COLUMNS if theirs[k][c] != ours[k][c]]
               for k in theirs if k in ours}
    changed = {k: cols for k, cols in changed.items() if cols}

    # 2. The downloads of every added or changed record.
    pages: dict[tuple[str, str], list[str] | None] = {}
    for key in added + list(changed):
        pages[key] = page_downloads(key[1])
        for name in pages[key] or []:
            entry = flagged.get(name)
            if not entry or entry.get("date") != theirs[key]["date"]:
                flagged[name] = {**fetch_archive(name), "date": theirs[key]["date"]}

    # 3. Once a week: the size of every archive the patcher knows.
    if args.head:
        for i, (name, row) in enumerate(known.items(), 1):
            status, _, size = get(archive_url(name), head=True)
            if status == 200 and size == row["bytes"]:
                continue
            print(f"  {i}/{len(known)} {name}: {status} {size or '-'} bytes, the table says {row['bytes']}",
                  file=sys.stderr, flush=True)
            flagged[name] = {**(fetch_archive(name) if status == 200 else {"status": status}),
                             "date": flagged.get(name, {}).get("date", "")}
        state["last_head"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # An archive stays flagged until patches.tsv knows the file the website serves.
    def agrees(name: str, entry: dict) -> bool:
        row = known.get(name)
        return bool(row) and entry.get("status") == 200 and entry.get("sha256") == row["sha256"]
    for name in [n for n, e in flagged.items() if agrees(n, e)]:
        del flagged[name]
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")

    report = render(added, removed, changed, theirs, ours, pages, flagged, known, state["last_head"])
    if args.report:
        if report:
            args.report.write_text(report)
        elif args.report.is_file():
            args.report.unlink()
    print(report or "no changes", end="" if report else "\n")
    return 0


def render(added, removed, changed, theirs, ours, pages, flagged, known, last_head) -> str:
    if not (added or removed or changed or flagged):
        return ""
    out = ["# Changes on the 8bitchip.info website's list", "",
           "Written by `tools/survey/watch.py`: the live list and its downloads against "
           "`src/survey/catalogue.csv` and `src/survey/patches.tsv`."
           + (f" Sizes of every archive last checked {last_head}." if last_head else ""), ""]

    def game(key) -> str:
        return f"[{key[0]}]({SITE}{key[1]})"

    if added:
        out += ["## Records added", "", "| game | date | downloads |", "| --- | --- | --- |"]
        out += [f"| {game(k)} | {theirs[k]['date']} | {', '.join(f'`{d}`' for d in pages.get(k) or []) or '-'} |"
                for k in added]
        out += [""]
    if removed:
        out += ["## Records removed", "", "| game | row | downloads |", "| --- | --- | --- |"]
        out += [f"| {game(k)} | {ours[k]['row']} | {', '.join(f'`{d}`' for d in ours[k]['page_downloads'].split(';') if d) or '-'} |"
                for k in removed]
        out += [""]
    if changed:
        out += ["## Records changed", "", "| game | row | what changed |", "| --- | --- | --- |"]
        for k, cols in changed.items():
            what = "; ".join(f"{c}: {ours[k][c] or '(empty)'} → {theirs[k][c] or '(empty)'}" for c in cols)
            downloads = pages.get(k)
            was = [d for d in ours[k]["page_downloads"].split(";") if d]
            if downloads is None:
                what += "; the game page did not answer"
            elif downloads != was:
                what += f"; downloads: {', '.join(was) or '(none)'} → {', '.join(downloads) or '(none)'}"
            out.append(f"| {game(k)} | {ours[k]['row']} | {what} |")
        out += [""]
    if flagged:
        out += ["## Archives that are not the files in patches.tsv", "",
                "| archive | in patches.tsv | on the website | action |", "| --- | --- | --- | --- |"]
        for name, e in sorted(flagged.items()):
            row = known.get(name)
            table = f"{row['bytes']} bytes, `{row['sha256'][:16]}`" if row else "not there"
            site = (f"{e['bytes']} bytes, `{e['sha256'][:16]}`" if e.get("status") == 200
                    else f"HTTP {e.get('status')}")
            out.append(f"| `{name}` | {table} | {site} | {row['action'] if row else '-'} |")
        out += [""]

    out += ["## What to do", ""]
    if added or changed or flagged:
        out.append("- Refresh the mirror and the survey for these games: `tools/survey/mirror.py`, "
                   "`catalogue.py`, `unpack_games.py`, `inventory.py`, `classify.py`, then "
                   "`run_all.py --only <name>` and `verdicts.py`.")
    fixed = sorted(n for n in flagged if n in known and known[n]["action"] not in ("none", "notgame", "other", "refuse"))
    if fixed:
        out.append(f"- These archives have a fix ({', '.join(f'`{n}`' for n in fixed)}): the patcher checks the "
                   "download by SHA-256 and refuses the new file. Rebuild and test the fix on the new download.")
    if flagged:
        out.append("- Then `tools/survey/patch_table.py` and `tools/site/build_site.py --check`, so the "
                   "patcher's table knows the new files.")
    if removed:
        out.append("- Records removed from the list: decide whether the catalogue keeps them.")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.exit(main())
