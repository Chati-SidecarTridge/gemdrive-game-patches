#!/usr/bin/env python3
"""The patcher page's code (tools/site/patcher.js) run in headless Chrome on
the mirror's archives, and every ZIP it writes checked here.

Usage: patch_test.py [--only ARCHIVE ...] [--sample N]

Builds nothing: it uses the site as tools/site/build_site.py left it (tools/dev/builds/site/, with
patcher.js and patch-data.js). A local server (127.0.0.1, a secure context for crypto.subtle) serves the
site, the mirror's site/ (MIRROR, read only) and a test page; Chrome runs the page, which gives every
archive with a fix, and N of each other action (default 5), to the patcher, and posts back each patched
ZIP and its results. Then each patched ZIP is checked with zipfile against its original: every entry the
same but the fix's file, which must be the table's result, and the added files, which must be the
table's. Also: a ZIP the table does not know, and a damaged one, must be refused. Writes the ZIPs and
results.json into tools/dev/builds/patcher/test-<time>/ and prints a summary.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import http.server
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SITE = REPO / "tools" / "dev" / "builds" / "site"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FIXES = ("gos5", "gos4", "gdbpb", "fastload", "rody2")

PAGE = """<!doctype html><meta charset="utf-8"><title>patch test</title>
<script src="/site/patcher.js"></script><script src="/site/patch-data.js"></script>
<script>
(async () => {
  const todo = %s, results = [];
  const get = async (p) => new Uint8Array(await (await fetch('/mirror/' + p)).arrayBuffer());
  for (const name of todo) {
    const r = { archive: name };
    const t0 = performance.now();
    try {
      const zip = await get(name);
      const { row } = await Patcher.identify(zip);
      r.known = !!row; r.action = row && row.action;
      if (row && %s.includes(row.action)) {
        const second = row.needs ? await get(row.needs) : null;
        const out = await Patcher.patch(zip, row, second);
        await fetch('/zip/' + encodeURIComponent(name), { method: 'POST', body: out });
        r.bytes = out.length;
      }
    } catch (e) { r.error = String(e.message || e); }
    r.ms = Math.round(performance.now() - t0);
    results.push(r);
  }
  for (const [label, make] of [['unknown', (z) => { const c = z.slice(); c[c.length - 30] ^= 1; return c; }],
                                ['damaged', (z) => z.slice(0, z.length - 100)]]) {
    const z = make(await get(todo[0]));
    const r = { archive: label };
    try { const { row } = await Patcher.identify(z); r.known = !!row; if (!row) Patcher.readZip(z); }
    catch (e) { r.error = String(e.message || e); }
    results.push(r);
  }
  await fetch('/result', { method: 'POST', body: JSON.stringify(results) });
})();
</script>"""


def mirror() -> Path:
    for line in (REPO / "tools" / "dev" / "dev.cfg").read_text().splitlines():
        if line.startswith("MIRROR="):
            return Path(line.split("=", 1)[1].strip()) / "site"
    sys.exit("error: MIRROR not set")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--sample", type=int, default=5)
    a = ap.parse_args()
    site_mirror = mirror()
    rows = list(csv.DictReader((REPO / "src" / "survey" / "patches.tsv").open(), delimiter="\t"))
    table = {r["archive"]: r for r in rows}
    if a.only:
        todo = a.only
    else:
        todo = [r["archive"] for r in rows if r["action"] in FIXES]
        for action in sorted({r["action"] for r in rows} - set(FIXES)):
            todo += [r["archive"] for r in rows if r["action"] == action][:a.sample]
    work = REPO / "tools" / "dev" / "builds" / "patcher" / time.strftime("test-%Y%m%d-%H%M%S")
    (work / "zips").mkdir(parents=True)
    page = PAGE % (json.dumps(todo), json.dumps(list(FIXES)))
    done = threading.Event()
    results: list = []

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def translate_path(self, path):
            path = path.split("?")[0]
            from urllib.parse import unquote
            path = unquote(path)
            if path.startswith("/site/"):
                return str(SITE / path[6:])
            if path.startswith("/mirror/"):
                return str(site_mirror / path[8:])
            return str(work / "page.html")

        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"]))
            from urllib.parse import unquote
            if self.path.startswith("/zip/"):
                name = unquote(self.path[5:]).replace("/", "__")
                (work / "zips" / name).write_bytes(body)
            elif self.path == "/result":
                results.extend(json.loads(body))
                done.set()
            self.send_response(204)
            self.end_headers()

    (work / "page.html").write_text(page)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    profile = tempfile.mkdtemp(prefix="chrome-", dir=work)
    chrome = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={profile}",
                               "--no-first-run", f"http://127.0.0.1:{server.server_address[1]}/test.html"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    started = time.time()
    ok = done.wait(timeout=3600)
    chrome.terminate()
    chrome.wait()
    server.shutdown()
    shutil.rmtree(profile, ignore_errors=True)
    if not ok:
        print("error: the page did not finish within an hour")
        return 1
    (work / "results.json").write_text(json.dumps(results, indent=1))
    problems = []
    for r in results:
        row = table.get(r["archive"])
        if r["archive"] == "unknown":
            if r.get("known"):
                problems.append("unknown: taken as known")
            continue
        if r["archive"] == "damaged":
            if r.get("known") or not r.get("error"):
                problems.append(f"damaged: not refused ({r})")
            continue
        if not r.get("known"):
            problems.append(f"{r['archive']}: not recognised ({r.get('error')})")
            continue
        if row["action"] not in FIXES:
            continue
        if r.get("error"):
            problems.append(f"{r['archive']}: {r['error']}")
            continue
        problems += check_zip(site_mirror / r["archive"], work / "zips" / r["archive"].replace("/", "__"), row, site_mirror)
    fixes = [r for r in results if (table.get(r["archive"]) or {}).get("action") in FIXES]
    slow = max(fixes, key=lambda r: r["ms"]) if fixes else None
    print(f"{work.relative_to(REPO)}: {len(results)} archives in {time.time() - started:.0f} s, {len(fixes)} patched"
          + (f", the slowest {slow['archive']} {slow['ms']} ms" if slow else "") + f", {len(problems)} problem(s)")
    for p in problems[:40]:
        print("  " + p)
    return 1 if problems else 0


def check_zip(original: Path, patched: Path, row: dict, site: Path) -> list[str]:
    """The patched ZIP: the original's entries, the same bytes but the fix's file, plus the added files."""
    out = []
    name = row["archive"]
    zo, zp = zipfile.ZipFile(original), zipfile.ZipFile(patched)
    if zp.testzip() is not None:
        return [f"{name}: a damaged entry in the patched ZIP"]
    po = {i.filename: i for i in zo.infolist()}
    pp = {i.filename: i for i in zp.infolist()}
    want = {}
    if row["target"]:
        want[row["target"].upper()] = row["result_sha256"]
    for item in filter(None, row["add"].split(",")):
        path, digest = item.split("=")
        want[path.upper()] = digest
    for fn in po:
        if fn not in pp:
            out.append(f"{name}: {fn} missing")
        elif fn.upper() not in want and zo.read(fn) != zp.read(fn):
            out.append(f"{name}: {fn} changed")
    for fn in pp:
        if fn not in po and fn.upper() not in want:
            out.append(f"{name}: {fn} added")
    for path, digest in want.items():
        fn = next((f for f in pp if f.upper() == path), None)
        if fn is None:
            out.append(f"{name}: {path} not in the patched ZIP")
        elif hashlib.sha256(zp.read(fn)).hexdigest() != digest:
            out.append(f"{name}: {path} is not our build")
    return out


if __name__ == "__main__":
    sys.exit(main())
