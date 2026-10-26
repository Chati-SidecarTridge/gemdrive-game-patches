#!/usr/bin/env python3
"""A contact sheet of run_all.py's snapshots, to look the runs over.

Usage: sheet.py [--all]

Writes tools/dev/builds/survey/sheets/sheet-NNN.html, one self-contained page (the snapshots
embedded) with every run not on an earlier sheet (--all: every run; a game run again comes
back), in the list's order: the record's row, the game, its strategy, and run_all.py's proposal
with its reason.
Prints the page's path, or nothing when there is nothing new. Standard library only.
"""

from __future__ import annotations

import base64
import csv
import html
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SURVEY = REPO / "tools" / "dev" / "builds" / "survey"
SHEETS = SURVEY / "sheets"
COLOURS = {"as it is": "#2e7d32", "fix": "#c62828", "broken": "#6a1b9a", "unsure": "#ef6c00"}


def main() -> int:
    rows = [r for r in csv.DictReader((SURVEY / "runs.tsv").open(), delimiter="\t") if r.get("snapshot")]
    SHEETS.mkdir(parents=True, exist_ok=True)
    shown_file = SHEETS / "shown.txt"
    shown = set() if "--all" in sys.argv or not shown_file.exists() else set(shown_file.read_text().split())
    new = sorted((r for r in rows if r["run"] not in shown), key=lambda r: int(r["row"]))
    if not new:
        return 0
    number = len(list(SHEETS.glob("sheet-*.html"))) + 1
    counts = {k: sum(1 for r in rows if r["proposal"] == k) for k in COLOURS}
    cards = []
    for r in new:
        data = base64.b64encode((SURVEY / "snapshots" / r["snapshot"]).read_bytes()).decode()
        colour = COLOURS.get(r["proposal"], "#555")
        reason = f" — {html.escape(r['reason'])}" if r["reason"] else ""
        cards.append(
            f'<figure><img src="data:image/png;base64,{data}" alt="{html.escape(r["name"])}">'
            f'<figcaption><b>{int(r["row"])}</b> {html.escape(r["name"])}<br>'
            f'<span class="s">{html.escape(r["strategy"])}{" · " + r["memsize"] + " MB" if r["memsize"] == "2" else ""}'
            f'{" · mono" if r["monitor"] else ""}</span><br>'
            f'<span style="color:{colour}"><b>{html.escape(r["proposal"])}</b>{reason}</span></figcaption></figure>')
    page = f"""<!doctype html><meta charset="utf-8"><title>Runs, sheet {number}</title>
<style>
body {{ font: 13px -apple-system, Helvetica, sans-serif; margin: 16px; background: #fafafa; }}
h1 {{ font-size: 18px; margin: 0 0 4px; }} p {{ margin: 0 0 12px; color: #444; }}
main {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }}
figure {{ margin: 0; background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 6px; }}
img {{ width: 100%; image-rendering: pixelated; display: block; }}
figcaption {{ margin-top: 4px; line-height: 1.35; }} .s {{ color: #666; }}
</style>
<h1>Hatari GEMDOS drive, ST TOS 1.04 — sheet {number}: {len(new)} games</h1>
<p>Each picture is the screen just before the run ended. Proposals so far ({len(rows)} games): as it is
{counts["as it is"]}, fix {counts["fix"]}, broken {counts["broken"]}, unsure {counts["unsure"]}. Rows are the list's records (catalogue.csv).</p>
<main>{"".join(cards)}</main>
"""
    out = SHEETS / f"sheet-{number:03d}.html"
    out.write_text(page)
    shown_file.write_text("\n".join(sorted(shown | {r["run"] for r in new})) + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
