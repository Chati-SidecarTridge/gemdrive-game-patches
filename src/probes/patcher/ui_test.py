#!/usr/bin/env python3
"""The patcher page (tools/dev/builds/site/patch.html) used as a user would, in headless
Chrome: a ZIP from the mirror given to its file input, the page's answer read, a patched ZIP downloaded
from its link and checked.

Usage: ui_test.py

Cases: a fix (LEMMINGS.ZIP), one with GDBPB.PRG (ARBOTARG.ZIP), a second download (RODYM2.ZIP, then
RODYM4.ZIP), nothing to patch (10THFRAM.ZIP), no fix (AQUAN.ZIP), another download (the first "other" of
src/survey/patches.tsv), not a game (the first "notgame") and an unknown ZIP (LEMMINGS.ZIP with one byte
changed). Prints each answer's text and, for a patch, the downloaded file's name and whether it is the
page's patched ZIP (SHA-256 against what the patcher returns for the same input).
"""

from __future__ import annotations

import csv
import http.server
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[3]
SITE = REPO / "tools" / "dev" / "builds" / "site"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PAGE = """<!doctype html><meta charset="utf-8"><title>ui test</title>
<iframe id="f" src="/site/patch.html" style="width:1200px;height:900px"></iframe>
<script>
const cases = %s;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const log = (m) => fetch('/log', { method: 'POST', body: String(m) });
window.onerror = (m) => log('error: ' + m);
window.onunhandledrejection = (e) => log('rejection: ' + (e.reason && e.reason.message || e.reason));
const get = async (p) => new Uint8Array(await (await fetch('/mirror/' + p)).arrayBuffer());
const give = (doc, sel, bytes, name) => {
  const dt = new DataTransfer();
  dt.items.add(new File([bytes], name, { type: 'application/zip' }));
  const input = doc.querySelector(sel);
  input.files = dt.files;
  input.dispatchEvent(new Event('change', { bubbles: true }));
};
const settle = async (out) => {
  for (let k = 0; k < 200; k++) {
    await sleep(100);
    const t = out.textContent;
    if (t && !/Checking|Patching/.test(t)) return t;
  }
  return out.textContent;
};
window.onload = async () => {
  const f = document.getElementById('f');
  await new Promise((r) => (f.contentDocument.readyState === 'complete' ? r() : f.onload = r));
  const results = [];
  for (const c of cases) {
    log('case ' + c.label);
    f.contentWindow.location.reload();
    await new Promise((r) => (f.onload = r));
    const doc = f.contentDocument, out = doc.querySelector('.patch-result');
    log('reloaded, result box ' + !!out + ', input ' + !!doc.querySelector('#patch-zip'));
    let zip = await get(c.archive);
    if (c.flip) { zip = zip.slice(); zip[zip.length - 30] ^= 1; }
    give(doc, '#patch-zip', zip, c.archive.split('/').pop());
    const r = { label: c.label, text: await settle(out) };
    if (c.second) {
      give(doc, '#patch-second', await get(c.second), c.second);
      await sleep(200);
      r.text = await settle(out);
    }
    const link = out.querySelector('a[download]');
    if (link) {
      r.download = link.getAttribute('download');
      const got = new Uint8Array(await (await fetch(link.href)).arrayBuffer());
      r.sha = await f.contentWindow.Patcher.sha256(got);
      const row = f.contentWindow.PATCHES.find((x) => x.archive === c.archive);
      const second = c.second ? await get(c.second) : null;
      r.expected = await f.contentWindow.Patcher.sha256(await f.contentWindow.Patcher.patch(zip, row, second));
    }
    results.push(r);
  }
  await fetch('/result', { method: 'POST', body: JSON.stringify(results) });
};
</script>"""


def main() -> int:
    site_mirror = Path(next(l.split("=", 1)[1].strip() for l in (REPO / "tools" / "dev" / "dev.cfg").read_text().splitlines()
                            if l.startswith("MIRROR="))) / "site"
    rows = list(csv.DictReader((REPO / "src" / "survey" / "patches.tsv").open(), delimiter="\t"))
    first = {a: next(r["archive"] for r in rows if r["action"] == a) for a in ("other", "notgame")}
    cases = [{"label": "fix", "archive": "LEMMINGS.ZIP"}, {"label": "gdbpb", "archive": "ARBOTARG.ZIP"},
             {"label": "second download", "archive": "RODYM2.ZIP", "second": "RODYM4.ZIP"},
             {"label": "as it is", "archive": "10THFRAM.ZIP"}, {"label": "no fix", "archive": "AQUAN.ZIP"},
             {"label": "other download", "archive": first["other"]}, {"label": "not a game", "archive": first["notgame"]},
             {"label": "unknown", "archive": "LEMMINGS.ZIP", "flip": True}]
    work = Path(tempfile.mkdtemp(prefix="ui-", dir=REPO / "tools" / "dev" / "builds" / "patcher"))
    (work / "page.html").write_text(PAGE % json.dumps(cases))
    done, results = threading.Event(), []

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def translate_path(self, path):
            path = unquote(path.split("?")[0])
            if path.startswith("/site/"):
                return str(SITE / path[6:])
            if path.startswith("/mirror/"):
                return str(site_mirror / path[8:])
            return str(work / "page.html")

        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"]))
            if self.path == "/log":
                print("  page:", body.decode(errors="replace")[:200], flush=True)
            else:
                results.extend(json.loads(body))
                done.set()
            self.send_response(204)
            self.end_headers()

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    chrome = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={work / 'profile'}",
                               "--no-first-run", f"http://127.0.0.1:{server.server_address[1]}/test.html"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ok = done.wait(timeout=int(sys.argv[1]) if len(sys.argv) > 1 else 600)
    chrome.terminate()
    chrome.wait()
    server.shutdown()
    shutil.rmtree(work, ignore_errors=True)
    if not ok:
        print("error: the page did not answer in time")
        return 1
    bad = 0
    for r in results:
        line = " ".join(r["text"].split())
        extra = ""
        if "download" in r:
            same = r["sha"] == r["expected"]
            bad += not same
            extra = f"  [download {r['download']}: {'the patched ZIP' if same else 'NOT the patched ZIP'}]"
        print(f"{r['label']:16} {line[:230]}{extra}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
