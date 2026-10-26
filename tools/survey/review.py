#!/usr/bin/env python3
"""EPIC-03 STORY-05: the human review of the runs, one click per game.

Usage: review.py [--port 8642] [--host 127.0.0.1]   then open http://localhost:8642 on this Mac
       (--host 0.0.0.0: also from the local network, http://<this Mac's address>:8642)

A page per batch of games, from tools/dev/builds/survey/runs.tsv: each game's snapshot (the screen
just before its run ended; a click shows it large, another click closes it), its strategy, run_all.py's proposal and reason, and three buttons:
OK (the game works from the GEMDOS drive), Broken (it does not), Not sure, with a note. A click is
written at once to src/survey/review.tsv (time, row, name, verdict, note, the run looked at and the
proposal it had); the last answer for a game counts. A game run from PPDRIVER too shows that run's
snapshot under its own. Filters: what is not reviewed yet (with the games whose answer was given on
a run since replaced, verdicts.py's stale.txt), what migration.csv still calls unsure ("to
settle"), by proposal, by strategy. It listens on 127.0.0.1 unless --host says otherwise. Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SURVEY = REPO / "tools" / "dev" / "builds" / "survey"
REVIEW = REPO / "src" / "survey" / "review.tsv"
MIGRATION = REPO / "src" / "survey" / "migration.csv"
FIELDS = ["time", "row", "name", "verdict", "note", "run", "proposal"]
PAGE = 60
VERDICTS = {"ok": ("OK", "#2e7d32"), "broken": ("Broken", "#c62828"), "unsure": ("Not sure", "#ef6c00")}
# the tile's colour is the proposal's (Diego, 2026-10-12): as it is white, broken light red
TILES = {"as it is": "#ffffff", "broken": "#ff9e9e", "fix": "#ffbe6b", "unsure": "#ffe866"}


def runs() -> list[dict]:
    return list(csv.DictReader((SURVEY / "runs.tsv").open(), delimiter="\t")) if (SURVEY / "runs.tsv").exists() else []


def answers() -> dict[str, dict]:
    if not REVIEW.exists():
        return {}
    return {r["row"]: r for r in csv.DictReader(REVIEW.open(), delimiter="\t")}


def page(query: dict) -> str:
    show = query.get("show", ["todo"])[0]
    strategy = query.get("strategy", [""])[0]
    start = int(query.get("from", ["0"])[0])
    done = answers()
    every = runs()
    rows = sorted((r for r in every if r.get("snapshot") and (r["setup"], r["disk"]) == ("st-104", "gemdrive")),
                  key=lambda r: int(r["row"]))  # the GEMDOS-drive runs; PPDRIVER and STE runs are references
    reference = {r["row"]: r for r in every if r.get("snapshot") and (r["setup"], r["disk"]) == ("st-104", "ppdriver")}
    strategies = sorted({r["strategy"] for r in rows})
    # an answer given on a run since replaced by one that ends otherwise (verdicts.py) is asked again
    stale = set((SURVEY / "stale.txt").read_text().split()) if (SURVEY / "stale.txt").exists() else set()
    if show == "todo":
        rows = [r for r in rows if r["row"] not in done or r["row"] in stale and done[r["row"]]["run"] != r["run"]]
    elif show in ("as it is", "fix", "broken", "unsure"):
        rows = [r for r in rows if r["proposal"] == show]
    elif show == "settle":  # the games migration.csv still calls unsure (verdicts.py)
        unsure = {g["row"] for g in csv.DictReader(MIGRATION.open()) if g["verdict"] == "unsure"}
        rows = [r for r in rows if r["row"] in unsure]
    elif show.startswith("mine-"):
        rows = [r for r in rows if done.get(r["row"], {}).get("verdict") == show[5:]]
    if strategy:
        rows = [r for r in rows if r["strategy"] == strategy]
    total = len(rows)
    rows = rows[start:start + PAGE]
    counts = {k: sum(1 for a in done.values() if a["verdict"] == k) for k in VERDICTS}

    def link(label: str, **kw: str) -> str:
        q = {"show": show, "strategy": strategy, "from": "0"}
        q.update(kw)
        return f'<a href="/?{urllib.parse.urlencode(q)}">{html.escape(label)}</a>'

    cards = []
    for r in rows:
        mine = done.get(r["row"], {})
        buttons = "".join(
            f'<button data-v="{k}" class="{"on" if mine.get("verdict") == k else ""}" style="--c:{c}">{lab}</button>'
            for k, (lab, c) in VERDICTS.items())
        cards.append(
            f'<figure data-row="{r["row"]}" data-name="{html.escape(r["name"])}" data-run="{html.escape(r["run"])}" '
            f'data-proposal="{html.escape(r["proposal"])}" style="background:{TILES.get(r["proposal"], "#e8e8e8")}">'
            f'<img loading="lazy" src="/snap/{urllib.parse.quote(r["snapshot"])}" alt="">'
            + (f'<div class="ref"><img loading="lazy" src="/snap/{urllib.parse.quote(reference[r["row"]]["snapshot"])}" '
               f'alt=""><span>from PPDRIVER: {html.escape(reference[r["row"]]["proposal"])} '
               f'{html.escape(reference[r["row"]]["reason"])}</span></div>' if r["row"] in reference else "") +
            f'<figcaption><b>{int(r["row"])}</b> {html.escape(r["name"])}<br>'
            f'<span class="s">{html.escape(r["strategy"])} · {r["memsize"]} MB{" · mono" if r["monitor"] else ""}</span><br>'
            f'<span class="p {r["proposal"].replace(" ", "")}">{html.escape(r["proposal"])}</span> '
            f'<span class="s">{html.escape(r["reason"])}</span>'
            f'<div class="b">{buttons}</div>'
            f'<input placeholder="note (optional)" value="{html.escape(mine.get("note", ""))}"></figcaption></figure>')
    nav = " · ".join(link(lab, show=key) for key, lab in (("todo", "not reviewed"), ("settle", "to settle"), ("all", "all"),
                     ("unsure", "proposed unsure"), ("broken", "proposed broken"), ("fix", "proposed fix"),
                     ("as it is", "proposed as it is"),
                     ("mine-ok", "my OK"), ("mine-broken", "my Broken"), ("mine-unsure", "my Not sure")))
    nav += " | strategy: " + " ".join(link(s or "all", strategy=s) for s in [""] + strategies)
    more = ""
    if start + PAGE < total:
        more = link(f"next {PAGE} →", **{"from": str(start + PAGE)})
    return f"""<!doctype html><meta charset="utf-8"><title>Review the runs</title>
<style>
body {{ font: 13px -apple-system, Helvetica, sans-serif; margin: 16px; background: #fafafa; }}
h1 {{ font-size: 18px; margin: 0 0 6px; }} nav {{ margin: 0 0 12px; line-height: 1.8; }}
main {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; }}
figure {{ margin: 0; border: 1px solid #ccc; border-radius: 6px; padding: 6px; }}
figure.saved {{ border-color: #999; }}
.legend span {{ border: 1px solid #ccc; padding: 1px 8px; margin-right: 4px; border-radius: 3px; }} img {{ width: 100%; image-rendering: pixelated; display: block; }}
.s {{ color: #666; }} .p {{ font-weight: bold; }} .asitis {{ color: #2e7d32; }} .fix {{ color: #c62828; }}
.unsure {{ color: #ef6c00; }} .broken {{ color: #6a1b9a; }} .b {{ margin: 6px 0 4px; display: flex; gap: 6px; }}
button {{ flex: 1; padding: 6px; border: 2px solid var(--c); background: #fff; color: var(--c); border-radius: 4px;
  font-weight: bold; cursor: pointer; }} button.on {{ background: var(--c); color: #fff; }}
input {{ width: 100%; box-sizing: border-box; }}
figure img {{ cursor: zoom-in; }}
.ref {{ display: flex; gap: 6px; align-items: center; margin-top: 4px; }} .ref img {{ width: 45%; }}
.ref span {{ color: #666; font-size: 12px; }}
#zoom {{ position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 10; display: none;
  cursor: zoom-out; background: #fff; padding: 6px; border: 1px solid #888; border-radius: 6px;
  box-shadow: 0 8px 30px rgba(0,0,0,.35); }}
#zoom img {{ width: min(1248px, 92vw, calc(92vh * 832 / 552)); }}
#zoom div {{ font-weight: bold; margin-top: 4px; }}
</style>
<div id="zoom"><img alt=""><div></div></div>
<h1>Review: {total} games here · answered: OK {counts["ok"]}, Broken {counts["broken"]}, Not sure {counts["unsure"]}</h1>
<nav>{nav}</nav>
<p class="legend">Tiles: <span style="background:#ffffff">as it is</span> <span style="background:#ff9e9e">broken</span>
<span style="background:#ffbe6b">fix</span> <span style="background:#ffe866">unsure</span></p>
<main>{"".join(cards)}</main>
<p>{more}</p>
<script>
async function send(fig, verdict) {{
  const body = {{row: fig.dataset.row, name: fig.dataset.name, run: fig.dataset.run, proposal: fig.dataset.proposal,
                verdict, note: fig.querySelector("input").value}};
  const r = await fetch("/feedback", {{method: "POST", body: JSON.stringify(body)}});
  if (r.ok) {{ fig.querySelectorAll("button").forEach(b => b.classList.toggle("on", b.dataset.v === verdict));
              fig.classList.add("saved"); }}
}}
const zoom = document.getElementById("zoom");
document.querySelectorAll("figure img").forEach(img => {{
  img.onclick = () => {{
    const same = zoom.style.display === "block" && zoom.querySelector("img").src === img.src;
    if (same) {{ zoom.style.display = "none"; return; }}
    zoom.querySelector("img").src = img.src;
    zoom.querySelector("div").textContent = img.closest("figure").querySelector("figcaption").firstChild.textContent
      + " " + img.closest("figure").dataset.name;
    zoom.style.display = "block"; }};
}});
zoom.onclick = () => {{ zoom.style.display = "none"; }};
document.addEventListener("keydown", e => {{ if (e.key === "Escape") zoom.style.display = "none"; }});
document.querySelectorAll("figure").forEach(fig => {{
  fig.querySelectorAll("button").forEach(b => b.onclick = () => send(fig, b.dataset.v));
  fig.querySelector("input").onchange = () => {{ const on = fig.querySelector("button.on");
                                                if (on) send(fig, on.dataset.v); }};
}});
</script>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args) -> None:
        pass

    def reply(self, code: int, body: bytes, kind: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        url = urllib.parse.urlsplit(self.path)
        if url.path.startswith("/snap/"):
            name = Path(urllib.parse.unquote(url.path[6:])).name
            path = SURVEY / "snapshots" / name
            if path.is_file():
                return self.reply(200, path.read_bytes(), "image/png")
            return self.reply(404, b"no such snapshot", "text/plain")
        if url.path == "/":
            return self.reply(200, page(urllib.parse.parse_qs(url.query)).encode(), "text/html; charset=utf-8")
        self.reply(404, b"not found", "text/plain")

    def do_POST(self) -> None:
        if self.path != "/feedback":
            return self.reply(404, b"not found", "text/plain")
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        if data.get("verdict") not in VERDICTS or not str(data.get("row", "")).isdigit():
            return self.reply(400, b"bad answer", "text/plain")
        row = {k: " ".join(str(data.get(k, "")).split()) for k in FIELDS}
        row["time"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        new = not REVIEW.exists()
        with REVIEW.open("a") as out:
            if new:
                out.write("\t".join(FIELDS) + "\n")
            out.write("\t".join(row[k] for k in FIELDS) + "\n")
        self.reply(200, b"saved", "text/plain")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8642)
    ap.add_argument("--host", default="127.0.0.1", help="0.0.0.0 to answer the local network too")
    args = ap.parse_args()
    print(f"review page: http://localhost:{args.port}  (answers in {REVIEW.relative_to(REPO)})", flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
