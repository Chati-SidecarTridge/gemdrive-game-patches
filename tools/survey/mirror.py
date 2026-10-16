#!/usr/bin/env python3
"""tools/survey/mirror.py: a local copy of the 8bitchip.info website's hard-disk adaptation pages
(EPIC-03 STORY-02, D-11, D-12).

    python3 tools/survey/mirror.py

Copies into MIRROR (tools/dev/dev.cfg, outside the repository, never
committed): the list page fromhd3.php, every game page it links (SCRSH/), every
download those pages offer (dwnld.php?get=NAME, saved under its own name, or an
archive linked directly), the game-archive pages (ASTGA/) a game page sends its
download to and their downloads, PP's documentation pages and the archives they
link, then the images of every page saved. One request at a time with a pause; a file already on disk is not
fetched again, so a stopped run resumes. Every fetch is a line of
MIRROR/manifest.tsv: time, url, final url, path, status, bytes, sha256.
"""

from __future__ import annotations

import hashlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dev"))
from devcfg import cfg  # noqa: E402

SITE = "https://atari.8bitchip.info/"
LIST = "fromhd3.php"
DOCS = [
    "fromhd.php", "fromhd2.php", "fromh.css", "pp100best.html", "playfhd.html",
    "plafh.html", "GamexUsage.html", "GAMEXdoc.html", "astopensw.php",
    "GamexLSrc.html", "GamexLSrc2.html", "GamexLSrc3.html", "imgrun.php",
    "floimgd.php", "agcat.html", "flashest.php", "monocg.html", "drimus.php",
    "drimlus.php", "atricl.php", "ikbdbatt.html",
]
ARCHIVE = re.compile(r"\.(zip|7z|rar|lzh|lha|tos|prg|st|msa)$", re.I)
PAUSE = 1.0
RETRIES = (5, 15, 45)

MIRROR = Path(cfg("MIRROR"))
ROOT = MIRROR / "site"
MANIFEST = MIRROR / "manifest.tsv"


def local(url: str) -> Path:
    """Where url is kept: its path under ROOT."""
    path = urllib.parse.unquote(urllib.parse.urlsplit(url).path).lstrip("/")
    return ROOT / path


def fetch(url: str, path: Path | None = None) -> Path | None:
    """Fetch url into path (or where its final url says), unless already on
    disk. Returns the path, or None after the retries fail."""
    if path is not None and path.is_file():
        return path
    for wait in (*RETRIES, None):
        time.sleep(PAUSE)
        status, final, data = 0, url, b""
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                status, final, data = response.status, response.geturl(), response.read()
        except urllib.error.HTTPError as error:
            status = error.code
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            print(f"  {url}: {error}", flush=True)
        if status == 200:
            break
        if status == 404 or wait is None:
            record(url, final, None, status, b"")
            print(f"FAIL {status} {url}", flush=True)
            return None
        time.sleep(wait)
    target = path or local(final)
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + ".part")
    part.write_bytes(data)
    part.replace(target)  # a stopped run leaves no short file behind
    record(url, final, target, status, data)
    print(f"ok {len(data):>9} {target.relative_to(ROOT)}", flush=True)
    return target


def record(url: str, final: str, path: Path | None, status: int, data: bytes) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    where = path.relative_to(MIRROR) if path else "-"
    digest = hashlib.sha256(data).hexdigest() if data else "-"
    with MANIFEST.open("a") as out:
        out.write(f"{stamp}\t{url}\t{final}\t{where}\t{status}\t{len(data)}\t{digest}\n")


def links(page: Path, base: str) -> list[str]:
    """The same-site href targets of a saved page, as absolute urls."""
    text = page.read_text(encoding="latin-1")
    found = []
    for href in re.findall(r'href="([^"#]+)', text, re.I):
        url = urllib.parse.urljoin(base, href.strip())
        if url.startswith(SITE) and url not in found:
            found.append(url)
    return found


def images(page: Path, base: str) -> list[str]:
    text = page.read_text(encoding="latin-1")
    found = []
    for src in re.findall(r'<img[^>]*\ssrc="([^"]+)"', text, re.I):
        url = urllib.parse.urljoin(base, src.strip())
        if url.startswith(SITE) and url not in found:
            found.append(url)
    return found


def download_path(url: str) -> Path | None:
    """dwnld.php?get=NAME is kept as NAME, next to the list page."""
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    name = query.get("get", [""])[0]
    return ROOT / name if name and "/" not in name else None


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    pages: list[tuple[Path, str]] = []

    listing = fetch(SITE + LIST, ROOT / LIST)
    if listing is None:
        sys.exit("error: the list page could not be fetched")
    pages.append((listing, SITE + LIST))
    games = [u for u in links(listing, SITE + LIST) if "/SCRSH/" in u]
    print(f"{len(games)} game pages", flush=True)

    downloads: list[str] = []
    archive_pages: list[str] = []

    def offered(page: Path, url: str) -> None:
        for u in links(page, url):
            if u in downloads:
                continue
            if "dwnld.php" in u or ARCHIVE.search(urllib.parse.urlsplit(u).path):
                downloads.append(u)
            elif "/ASTGA/" in u and "/ASTGA/" not in url and u not in archive_pages:
                archive_pages.append(u)

    for url in games:
        page = fetch(url, local(url))
        if page is None:
            continue
        pages.append((page, url))
        offered(page, url)
    for url in archive_pages:  # where some game pages send their download
        page = fetch(url, local(url))
        if page is not None:
            pages.append((page, url))
            offered(page, url)
    print(f"{len(downloads)} game downloads, {len(archive_pages)} game-archive pages", flush=True)
    for url in downloads:
        fetch(url, download_path(url) if "dwnld.php" in url else local(url))

    for name in DOCS:
        page = fetch(SITE + name, ROOT / name)
        if page is None or not name.endswith((".php", ".html")):
            continue
        pages.append((page, SITE + name))
        for url in links(page, SITE + name):
            if "dwnld.php" in url:
                fetch(url, download_path(url))
            elif ARCHIVE.search(urllib.parse.urlsplit(url).path):
                fetch(url, local(url))

    for page, base in pages:
        for url in images(page, base):
            fetch(url, local(url))
    print("done", flush=True)


if __name__ == "__main__":
    main()
