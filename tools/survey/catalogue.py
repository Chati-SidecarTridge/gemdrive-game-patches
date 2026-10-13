#!/usr/bin/env python3
"""EPIC-03 STORY-02: PP's list of hard-disk adaptations as a table.

Usage: catalogue.py [<out.csv>]        (default src/survey/catalogue.csv)

Reads the mirror (MIRROR in tools/dev/dev.cfg, D-12), never the site: the list
(site/fromhd3.php), every game's page (site/SCRSH/*.html) and PP's categories
(site/agcat.html). Writes one row per record of the list, in the list's order.

PP's text stays in the mirror (D-11): a row keeps the list's own cells, the
download names, and what is read from the page with STORY-01's glossary
(src/notes/pp-modes.md): the category code and its parts, the TOS dependence,
the source PP started from, the adaptation terms, and the mode the page names.
Every row carries its page's URL.

Prints the checks: the record count against the list, and the category codes
counted by PP's six categories against agcat.html's totals. Standard library only.
"""

from __future__ import annotations

import collections
import csv
import html
import posixpath
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SITE_URL = "https://atari.8bitchip.info/"
LIST_COLUMNS = ["min_ram", "gx", "tos104", "tos206", "mste16", "falcon", "tt", "note", "date", "val"]
AGCAT_TOTALS = {"1": 40, "2": 130, "3": 104, "4": 61, "5": 6, "6": 107}  # agcat.html, "Total overvieew"

# STORY-01's glossary: term -> pattern on the page's text (lower case)
TERMS = {
    "gamex": r"\bgamex\b", "haga": r"\bhaga\b", "hage": r"\bhage\b", "hag2": r"\bhag2\b",
    "gos": r"\bgos\b", "tos 1.04 in ram": r"tos 1\.04 in ram", "singleparted": r"singlepart",
    "filed": r"\bfiled\b", "ramdisk": r"ram ?disk", "redirect to hard disk": r"redirect(ed)? to hard dis",
    "xbios to image": r"xbios loads directed", "deprotected": r"deprot", "crack": r"\bcrk\b",
    "statesave": r"state ?saves?|savestates?", "exit to desktop": r"exit to desktop",
    "hole": r"\bhole\b", "auto folder": r"auto folder", "image runner": r"image runner|imgrun",
    "itos": r"\bitos\b", "done by jy": r"done by jy", "cheats": r"unlimited|unlim\.|trainer",
}


def mirror() -> Path:
    for line in (REPO / "tools" / "dev" / "dev.cfg").read_text().splitlines():
        if line.startswith("MIRROR="):
            return Path(line.split("=", 1)[1].strip())
    sys.exit("error: no MIRROR in tools/dev/dev.cfg")


def text(fragment: str) -> str:
    fragment = re.sub(r"<(script|style).*?</\1>", " ", fragment, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def read_list(site: Path) -> list[tuple[str, str, list[str]]]:
    """(name, page, the list's cells) for every record: a row with a link to a game page.
    Every row of the table's 11 columns must be one."""
    t = (site / "fromhd3.php").read_text(encoding="latin-1")
    out, eleven = [], 0
    for row in re.findall(r"<tr.*?</tr>", t, re.S | re.I):
        cells = [text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S | re.I)]
        if len(cells) == 11 and cells[0] != "Name , screenshots, DL":
            eleven += 1
        m = re.search(r'href="(SCRSH/[^"]+)"', row)
        if not m:
            continue
        if len(cells) != 11:
            sys.exit(f"error: a record with {len(cells)} cells: {cells[:2]}")
        out.append((cells[0], m.group(1), cells[1:]))
    if eleven != len(out):
        sys.exit(f"error: {eleven} rows in the table, {len(out)} with a game page")
    return out


def read_agcat(site: Path) -> dict[str, str]:
    """Normalised game name -> PP's category (1-6), from the lists in agcat.html."""
    t = (site / "agcat.html").read_text(encoding="latin-1")
    t = re.sub(r"<(script|style).*?</\1>", " ", t, flags=re.S | re.I)
    lines = [text(l) for l in re.split(r"<br[^>]*>", t, flags=re.I)]
    names, sec, state = {}, None, None
    for line in lines:
        m = re.match(r"^(\d)\.\s", line + " ")
        if m and int(m.group(1)) <= 6 and (len(line) < 4 or "Games" in line):
            sec, state = m.group(1), "prose"
        elif line.startswith("Total overv"):
            sec = None
        elif sec and "Cat abbrev" in line:
            state = "code"
        elif sec and state == "code" and not line:
            state = "names"
        elif sec and state == "names" and line and not line.startswith("*") and not line.endswith(":") \
                and line != "etc.":
            name = re.sub(r"\s*(\*|- but .*)$", "", line).strip()
            names.setdefault(norm(name), sec)
    return names


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower().replace("&", "and"))


def parse_code(code: str) -> dict[str, str]:
    """PP's category code (agcat.html): part, RAM, then letters; and the category it implies."""
    parts = {"code_part": "", "code_ram": "", "code_tos": "", "code_aes": "", "code_tpa": "",
             "code_filesys": "", "code_floppy": "", "code_xbios": "", "code_rest": "", "code_category": ""}
    if not code:
        return parts
    rest = code
    if rest[0] in "MS" and not rest.startswith("MS"):
        parts["code_part"] = {"M": "multipart", "S": "singleparted"}[rest[0]]
        rest = rest[1:]
    if rest[:1] in ("5", "1", "2"):
        parts["code_ram"] = {"5": "512K", "1": "1M", "2": "2M"}[rest[0]]
        rest = rest[1:]
    for token, key, value in (("DFC", "code_floppy", "DFC"), ("FDC", "code_floppy", "FDC"),
                              ("XB8", "code_xbios", "XB8"), ("X8", "code_xbios", "X8")):
        if token in rest:
            parts[key] = value
            rest = rest.replace(token, "", 1)
    for letter, key, value in (("T", "code_tos", "T"), ("I", "code_tos", "I"), ("O", "code_tos", "O"),
                               ("A", "code_aes", "A"), ("E", "code_aes", "E"), ("P", "code_tpa", "P"),
                               ("L", "code_filesys", "L"), ("F", "code_floppy", "F"), ("X", "code_xbios", "X")):
        if letter in rest and not parts[key]:
            parts[key] = value
            rest = rest.replace(letter, "", 1)
    parts["code_rest"] = rest
    part, floppy, xbios = parts["code_part"], parts["code_floppy"], parts["code_xbios"]
    if rest or not part or floppy == "DFC":
        cat = "?"
    elif part == "singleparted":
        cat = "3"
    elif floppy:
        cat = "6"
    elif xbios or (parts["code_tos"] == "O" and not parts["code_filesys"]):
        cat = "5"
    elif parts["code_filesys"] and parts["code_tpa"]:
        cat = "1-2"
    elif parts["code_filesys"]:
        cat = "4"
    else:
        cat = "?"
    parts["code_category"] = cat
    return parts


def downloads_of(raw: str, page: str) -> list[tuple[str, str, str, str]]:
    """(archive, RAM, version, machines) for every download page offers (dwnld.php?get=NAME or an
    archive linked directly); the archive as its path in the mirror's site/, the last three as its
    label, up to the line's end, names them."""
    out = []
    for href, after in re.findall(r'href="([^"]*?\.(?:zip|7z|rar|lzh))"[^>]*>(.*?)(?=href="|$)', raw, re.S | re.I):
        if not text(after.split("</a>", 1)[0]) and not re.search(r"<img", after.split("</a>", 1)[0], re.I):
            continue  # a link with nothing to click: a leftover in PP's page (COLBEQ.ZIP on ten pages)
        if "dwnld.php?get=" in href:
            name = href.split("dwnld.php?get=", 1)[1]
        else:
            name = posixpath.normpath(posixpath.join(posixpath.dirname(page), href))
        label = text(re.split(r"<br|</p|</td|</tr", after, maxsplit=1, flags=re.I)[0]).lower()
        m = re.search(r"(\d)\s*mb|512\s*k", label)
        ram = (m.group(1) + "M" if m.group(1) else "512K") if m else ""
        kind = next((v for k, v in (("hag2", "HAG2"), ("hage", "HAGE"), ("haga", "HAGA"), ("gamex", "Gamex"),
                                    ("floppy", "floppy"), ("normal", "normal")) if re.search(rf"\b{k}\b", label)), "")
        names = {"mega st(e)": "Mega ST(E)", "mega ste": "Mega STE", "mega st": "Mega ST", "st(e)": "ST(E)",
                 "ste": "STE", "st": "ST", "falcon": "Falcon", "tt": "TT"}
        machines = ",".join(("not " if neg else "only " if only else "") + names[mach] for neg, only, mach in
                            re.findall(r"(not for\s+)?(only\s+)?\b(mega st\(e\)|mega ste|mega st|st\(e\)|ste|st|"
                                       r"falcon|tt)(?![a-z])", label))
        out.append((name, ram, kind, machines))
    return out


def read_page(site: Path, page: str) -> dict[str, str]:
    raw = (site / page).read_text(encoding="latin-1")
    t = text(raw)
    low = t.lower()
    links = downloads_of(raw, page)
    archive_page = ""
    if not links:  # some pages send their download to PP's game archive (ASTGA/)
        m = re.search(r'href="\.\./(ASTGA/[^"]+)"', raw)
        if m and (site / m.group(1)).is_file():
            archive_page = m.group(1)
            links = downloads_of((site / archive_page).read_text(encoding="latin-1"), archive_page)
    downloads = [d[0] for d in links]
    m = re.search(r"Cat\s*:\s*([A-Za-z0-9/]+)", t)
    code = m.group(1).upper().replace("/", "") if m else ""
    tos = ""
    for pat, value in ((r"stos dep", "STOS"), (r"aes dep", "TOS+AES"), (r"little tos dep", "little"),
                       (r"tos indep", "independent"), (r"tos dep", "dependent")):
        if re.search(pat, low):
            tos = value
            break
    m = re.search(r"\b(stx|st|msa)\s*(?:/\s*(?:stx|st|msa)\s*)?imgs?\.?\s*(?:of|ot)\s*([a-z]+)", low)
    source = f"{m.group(1).upper()} {dict(org='original', crk='crack').get(m.group(2), m.group(2))}" if m else ""
    if re.search(r"colou?r\s*(and|or|&)\s*mono|mono\w*\s*(and|or)\s*colou?r|mono\w* mode too|all 3 res|"
                 r"any resolution|all resolutions", low):
        monitor = "colour and mono"
    elif re.search(r"needs monochrome|only for monochrome|monochrome mode only|monochrome (game|version|v\b|"
                   r"variant|video mode)|for monochrome (mode|lovers|monitor)|(works|run) in monochrome|"
                   r"high-res \(monochrome\)", low):
        monitor = "mono only"
    else:
        monitor = ""
    m = re.search(r"min\.?\s*(?:ram\s*)?(\d)\s*mb|(\d)\s*mb\s*ram\s*min", low)
    terms = [k for k, pat in TERMS.items() if re.search(pat, low)]
    return {"page_downloads": ";".join(downloads), "page_download_ram": ";".join(d[1] for d in links),
            "page_download_version": ";".join(d[2] for d in links),
            "page_download_machines": ";".join(d[3] for d in links),
            "page_archive": archive_page, "cat_code": code,
            "page_tos": tos, "page_source": source, "page_monitor": monitor,
            "page_min_ram": (m.group(1) or m.group(2)) + "M" if m else "", "page_terms": ";".join(terms)}


def page_mode(terms: set[str], note: str) -> str:
    """The mode the page (or the list's note) names, STORY-01's modes; '' when it names none."""
    note = note.lower()
    for mode, keys in (("HAG2", ("hag2",)), ("HAGE", ("hage",)), ("HAGA", ("haga",)),
                       ("Gamex + GOS", ("gos", "tos 1.04 in ram")), ("Gamex", ("gamex",))):
        if any(k in terms or re.search(rf"\b{re.escape(k)}\b", note) for k in keys):
            return mode
    if re.fullmatch(r"h\.?", note.strip()):
        return "HAGA"
    if re.search(r"\bgx\b", note):
        return "Gamex"
    return ""


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "src" / "survey" / "catalogue.csv"
    m = mirror()
    site = m / "site"
    records = read_list(site)
    agcat = read_agcat(site)
    stamp = next((l.split("\t")[0] for l in (m / "manifest.tsv").read_text().splitlines()
                  if l.split("\t")[1] == SITE_URL + "fromhd3.php"), "?")
    rows = []
    for i, (name, page, cells) in enumerate(records, 1):
        row = {"row": str(i), "name": name, "page": page, "url": SITE_URL + page}
        row.update(dict(zip(LIST_COLUMNS, cells)))
        row.update(read_page(site, page))
        row.update(parse_code(row["cat_code"]))
        row["agcat_category"] = agcat.get(norm(name), "")
        row["page_mode"] = page_mode(set(row["page_terms"].split(";")), row["note"])
        rows.append(row)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    pages = {r["page"] for r in rows}
    print(f"{out.relative_to(REPO)}: {len(rows)} records, {len(pages)} pages; the list fetched {stamp}")
    print(f"  downloads: {sum(len(r['page_downloads'].split(';')) for r in rows if r['page_downloads'])} "
          f"({sum(1 for r in rows if r['page_archive'])} records through a game-archive page); "
          f"records without one: {sum(1 for r in rows if not r['page_downloads'])}")
    coded = [r for r in rows if r["cat_code"]]
    print(f"  category code on {len(coded)} records; parsed into a category: "
          f"{sum(1 for r in coded if r['code_category'] != '?')}")
    cats = collections.Counter(r["code_category"] for r in coded)
    ag = collections.Counter(r["agcat_category"] for r in rows if r["agcat_category"])
    print("  category  | from the codes | agcat.html's total (of 450) | catalogue games in agcat's lists")
    for c in ("1-2", "3", "4", "5", "6", "?"):
        total = AGCAT_TOTALS["1"] + AGCAT_TOTALS["2"] if c == "1-2" else AGCAT_TOTALS.get(c, "")
        listed = ag["1"] + ag["2"] if c == "1-2" else ag.get(c, "")
        print(f"  {c:9} | {cats.get(c, 0):14} | {total!s:27} | {listed}")
    both = [r for r in rows if r["agcat_category"] and r["code_category"] not in ("", "?")]
    agree = sum(1 for r in both if r["code_category"] == r["agcat_category"]
                or (r["code_category"] == "1-2" and r["agcat_category"] in "12"))
    print(f"  games with both a parsed code and an agcat category: {len(both)}, agreeing: {agree}")
    print(f"  page modes: {dict(collections.Counter(r['page_mode'] or '(none)' for r in rows))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
