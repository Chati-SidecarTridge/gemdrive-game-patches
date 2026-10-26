#!/usr/bin/env python3
"""EPIC-03 STORY-07: the project's website, built from what the repository holds.

Usage: build_site.py [--out DIR] [--no-snapshots] [--check]

Builds a static site into tools/dev/builds/site/ (git-ignored), or DIR: the project and where it
stands, the notes (src/notes/*.md) as pages, the catalogue of the 8bitchip.info website's list with every
game's strategy, verdict, reason and solution (src/survey/migration.csv, catalogue.csv) and the
tools (tools/dev/README.md and the survey scripts' docstrings). The style and the catalogue's
filters are tools/site/site.css and site.js, copied beside the pages. Nothing is fetched: the site
works from its folder and from GitHub Pages alike.

The 8bitchip.info website's pages are linked, never copied (D-11): a note's `agcat.html` links to it
there, and every game links to its page there. The snapshots, this project's own Hatari screenshots of each
game's run (tools/dev/builds/survey/snapshots/, STORY-05), are copied when they are there, unless
--no-snapshots; whether they are published is Diego's call (D-15). A built game's snapshot is the
last screen of its build's run (src/survey/ports.tsv), kept beside the others as port-<row>.png.

The site speaks to its readers, never to the backlog (D-20): --check fails on a page that refers to
docs/epics/ or what is in it (an epic, a story, a decision, ITERATIONS.md). Nor does it name the
adaptations' author (D-21): --check fails on PP, PPera or Putnik in a page's prose (code, as a quoted
string or a driver's name, may), and on a link to the 8bitchip.info website's home page rather than a
game's page or a technical one, or on such a link without rel=nofollow.

--check, after the build: every internal link and anchor resolves, every game of migration.csv
has its row, and no page loads anything from another site. Standard library only.
"""

from __future__ import annotations

import argparse
import collections
import csv
import html
import html.parser
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = REPO / "tools" / "dev" / "builds" / "site"
SNAPSHOTS = REPO / "tools" / "dev" / "builds" / "survey" / "snapshots"
LOGS = REPO / "tools" / "dev" / "logs"
PP = "https://atari.8bitchip.info/"
SITE = "Atari ST hard-disk adaptations, from a GEMDOS drive"

# The notes, by section, in reading order: (file stem, short title)
SECTIONS = [
    ("index", "The project", []),
    ("findings", "Findings", [("gemdrive-failure", "Why Lemmings fails"), ("launch-chain", "The launch chain"),
                              ("disk-layer", "The disk layer"), ("launcher-formats", "The file formats"),
                              ("launcher-signatures", "The launcher's signatures")]),
    ("modes", "The modes", [("modes", "The modes")]),
    ("strategies", "Strategies and solutions", [("hd-strategies", "Verdicts and solutions"),
                                                ("strategies", "The strategies, from the files"),
                                                ("gos5-gemdrive", "The GOS5 games, built"),
                                                ("gos4-gemdrive", "The GOS4 games, built")]),
    ("catalogue", "Catalogue", []),
    ("tools", "Tools", []),
]
VERDICTS = [("as it is", "ok", "runs from the GEMDOS drive unchanged"),
            ("fix", "fix", "runs once one of the four solutions is applied"),
            ("not feasible", "no", "would need the game itself rewritten"),
            ("unsure", "unsure", "its runs did not settle it")]
BY = {"run": "from its run", "Diego": "Diego's review", "ppdriver": "against the PPDRIVER run",
      "trace": "from a trace or a trial"}
CATEGORIES = {"1-2": "1 or 2: the regular file system", "3": "3: loaded whole, no floppy after the start",
              "4": "4: the file system, in low RAM", "5": "5: XBIOS floppy loads",
              "6": "6: the floppy controller during play", "?": "a code the categories do not cover",
              "": "no code on its page"}
MACHINES = [("tos104", "TOS 1.04"), ("tos206", "TOS 2.06"), ("mste16", "Mega STE"), ("falcon", "Falcon"), ("tt", "TT")]


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", s).lower()).strip("-") or "section"


# --- Markdown, the subset the notes use -----------------------------------------------------------

NOTES = {stem for _, _, pages in SECTIONS for stem, _ in pages}
LIST = re.compile(r"^( *)([-*]|\d+\.) +(.*)$")
BACKLOG = re.compile(r"\b(?:EPIC|STORY)-\d+\b|\b[DCH]-\d\d\b|(?:ITERATIONS|DECISIONS|STATUS)\.md|docs/epics"
                     r"|\b[Ii]terations?\b|\b[Ee]pics?\b")
AUTHOR = re.compile(r"\bPP\b|PPera|Putnik", re.I)


def link(url: str, text: str) -> str:
    """A link; one to the 8bitchip.info website is rel=nofollow (Diego, 2026-10-16)."""
    rel = ' rel="nofollow"' if urllib.parse.urlsplit(url).netloc.endswith("8bitchip.info") else ""
    return f'<a href="{url}"{rel}>{text}</a>'


def code_span(text: str) -> str:
    """Inline code; a note's file name links to its page, a page of the 8bitchip.info website's to it."""
    c = f"<code>{esc(text)}</code>"
    if text.endswith(".md") and text[:-3] in NOTES:
        return f'<a href="{text[:-3]}.html">{c}</a>'
    if re.fullmatch(r"[A-Za-z0-9_]+\.(html|php)", text):
        return link(PP + text, c)
    return c


def inline(text: str) -> str:
    codes = []

    def keep(m: re.Match) -> str:
        codes.append(code_span(m.group(1)))
        return f"\x00{len(codes) - 1}\x00"

    def keep_char(c: str) -> str:  # a backslash escape: the character itself, never markup
        codes.append(esc(c))
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]*)`", keep, text)
    text = esc(re.sub(r"\\([\\|*_`\[\]()#])", lambda m: keep_char(m.group(1)), text))
    text = re.sub(r"&lt;(https?://[^&\s]+)&gt;", lambda m: link(m.group(1), m.group(1)), text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: link(m.group(2), m.group(1)), text)
    text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![\w*])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def cells(line: str) -> list[str]:
    """A table line's cells, split on the pipes outside code spans."""
    parts, cur, code = [], "", False
    line = line.strip()
    line = line[1:] if line.startswith("|") else line
    line = line[:-1] if line.endswith("|") and not line.endswith("\\|") else line
    for i, ch in enumerate(line):
        if ch == "`":
            code = not code
        if ch == "|" and not code and (i == 0 or line[i - 1] != "\\"):
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    return parts + [cur.strip()]


class Doc:
    """One note rendered: its title, its body and its headings (level, id, text)."""

    def __init__(self, text: str):
        self.title, self.toc, self.ids = "", [], collections.Counter()
        self.body = self.blocks(text.splitlines(), top=True)

    def anchor(self, text: str) -> str:
        base = slug(text)
        self.ids[base] += 1
        return base if self.ids[base] == 1 else f"{base}-{self.ids[base]}"

    def blocks(self, lines: list[str], top: bool = False) -> str:
        out, i = [], 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
            elif line.startswith("```"):
                j = i + 1
                while j < len(lines) and not lines[j].startswith("```"):
                    j += 1
                out.append(f"<pre><code>{esc(chr(10).join(lines[i + 1:j]))}</code></pre>")
                i = j + 1
            elif m := re.match(r"(#{1,6}) +(.*)", line):
                level, text = len(m.group(1)), inline(m.group(2).strip())
                if level == 1 and top and not self.title:
                    self.title = text
                else:
                    a = self.anchor(text)
                    if top and level in (2, 3):
                        self.toc.append((level, a, text))
                    out.append(f'<h{level} id="{a}">{text}</h{level}>')
                i += 1
            elif line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"\s*\|?\s*:?-{3,}", lines[i + 1]):
                head, align = cells(line), cells(lines[i + 1])
                align = [' class="num"' if a.endswith(":") else "" for a in align]
                rows, j = [], i + 2
                while j < len(lines) and lines[j].lstrip().startswith("|"):
                    rows.append(cells(lines[j]))
                    j += 1
                th = "".join(f"<th{align[k] if k < len(align) else ''}>{inline(c)}</th>" for k, c in enumerate(head))
                trs = "".join("<tr>" + "".join(f"<td{align[k] if k < len(align) else ''}>{inline(c)}</td>"
                                               for k, c in enumerate(r)) + "</tr>" for r in rows)
                out.append(f'<div class="table"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
                i = j
            elif LIST.match(line):
                html_, i = self.list_(lines, i)
                out.append(html_)
            else:
                para = []
                while i < len(lines) and lines[i].strip() and not LIST.match(lines[i]) \
                        and not re.match(r"#{1,6} |```", lines[i]) and not lines[i].lstrip().startswith("|"):
                    para.append(lines[i].strip())
                    i += 1
                out.append(f"<p>{inline(' '.join(para))}</p>")
        return "\n".join(out)

    def list_(self, lines: list[str], i: int) -> tuple[str, int]:
        m = LIST.match(lines[i])
        base, ordered = len(m.group(1)), m.group(2)[0].isdigit()
        start = int(m.group(2)[:-1]) if ordered else 1
        items = []
        while i < len(lines):
            m = LIST.match(lines[i])
            if not m or len(m.group(1)) != base or m.group(2)[0].isdigit() != ordered:
                break
            indent = len(m.group(1)) + len(m.group(2)) + 1
            body, i = [m.group(3)], i + 1
            while i < len(lines):
                line = lines[i]
                if not line.strip():
                    nxt = next((l for l in lines[i + 1:] if l.strip()), "")
                    if len(nxt) - len(nxt.lstrip()) <= base:
                        break
                    body.append("")
                elif len(line) - len(line.lstrip()) > base:
                    body.append(line[min(indent, len(line) - len(line.lstrip())):])
                else:
                    break
                i += 1
            inner = self.blocks(body)
            inner = re.sub(r"^<p>(.*?)</p>", r"\1", inner, count=1, flags=re.S)
            items.append(f"<li>{inner}</li>")
            while i < len(lines) and not lines[i].strip():
                nxt = next((l for l in lines[i:] if l.strip()), "")
                n = LIST.match(nxt)
                if not n or len(n.group(1)) != base:
                    break
                i += 1
        tag = "ol" if ordered else "ul"
        attr = f' start="{start}"' if ordered and start != 1 else ""
        return f"<{tag}{attr}>{''.join(items)}</{tag}>", i


# --- Pages ----------------------------------------------------------------------------------------

def section_of(page: str) -> str:
    for key, _, pages in SECTIONS:
        if page == key or page in (p for p, _ in pages):
            return key
    return ""


def page(name: str, title: str, main: str, rail: str = "", kind: str = "doc", lead: str = "") -> str:
    current = section_of(name)
    nav = "".join(
        f'<li><a href="{(pages[0][0] if pages else key)}.html"{" aria-current=page" if key == current else ""}>{label}</a></li>'
        for key, label, pages in SECTIONS)
    head_title = SITE if name == "index" else f"{title} | {SITE}"
    rail = f'<nav class="rail" aria-label="In this section">{rail}</nav>' if rail else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{re.sub(r"<[^>]+>", "", head_title)}</title>
<meta name="description" content="{esc(lead or SITE)}">
<link rel="stylesheet" href="site.css">
</head>
<body class="{kind}">
<a class="skip" href="#main">Skip to the content</a>
<header class="bar">
<a class="mark" href="index.html">Atari ST hard-disk adaptations<span>, from a GEMDOS drive</span></a>
<nav aria-label="Sections"><ul>{nav}</ul></nav>
</header>
<div class="frame">
{rail}
<main id="main">
{main}
</main>
</div>
<footer class="credits">
<p>The adaptations, their list and their documentation come from the 8bitchip.info website. This
site links to its pages and copies none of its files.
Every run was made in <a href="https://www.hatari-emu.org/">Hatari</a> 2.6.1. Atari, ST, STE, TT,
Falcon and TOS are Atari's names.</p>
</footer>
<script src="site.js"></script>
</body>
</html>
"""


def rail_for(name: str, doc: Doc | None = None) -> str:
    key = section_of(name)
    pages = next(p for k, _, p in SECTIONS if k == key)
    out = []
    if len(pages) > 1:
        out.append("<ul class=pages>" + "".join(
            f'<li><a href="{p}.html"{" aria-current=page" if p == name else ""}>{t}</a></li>' for p, t in pages) + "</ul>")
    if doc and doc.toc:
        items, open_ = [], False
        for level, a, text in doc.toc:
            if level == 2:
                items.append(("</ul></li>" if open_ else "") + f'<li><a href="#{a}">{text}</a>')
                open_ = False
            else:
                items.append(("" if open_ else "<ul>") + f'<li><a href="#{a}">{text}</a></li>')
                open_ = True
        items.append("</ul></li>" if open_ else "</li>")
        out.append('<details class="toc" open><summary>On this page</summary><ul>' + "".join(items) + "</ul></details>")
    return "\n".join(out)


def read_csv(path: Path, delimiter: str = ",") -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter=delimiter))


def n(x: int) -> str:
    return f"{x:,}"


# --- The project ----------------------------------------------------------------------------------

def built() -> set[str]:
    """The rows of the games a port built and that run with their build (src/survey/ports.tsv)."""
    return {r["row"] for r in read_csv(REPO / "src" / "survey" / "ports.tsv", "\t") if r["result"] == "runs"}


def strategy_order(games: list[dict]) -> list[str]:
    return [s for s, _ in collections.Counter(g["strategy"] for g in games).most_common()]


def index(games: list[dict]) -> str:
    count = collections.Counter(g["verdict"] for g in games)
    rank = {v: k for k, (v, _, _) in enumerate(VERDICTS)}
    bands, ported = [], built()
    for b, s in enumerate(strategy_order(games)):
        members = sorted((g for g in games if g["strategy"] == s), key=lambda g: (rank[g["verdict"]], int(g["row"])))
        squares = "".join(
            f'<a class="{dict((v, c) for v, c, _ in VERDICTS)[g["verdict"]]}{" built" if g["row"] in ported else ""}" '
            f'href="catalogue.html#g-{int(g["row"]):04d}" tabindex="-1" '
            f'title="{esc(g["name"])}: {g["verdict"]}{", built: runs" if g["row"] in ported else ""}"></a>' for g in members)
        bands.append(f'<div class="band" style="--b:{b}"><a class="label" href="catalogue.html#s={urllib.parse.quote(s, safe="")}">'
                     f'<span>{esc(s)}</span> <span class="count">{n(len(members))}</span></a>'
                     f'<div class="squares">{squares}</div></div>')
    items = [f'<li><i class="{c}"></i><span class="count">{n(count[v])}</span><span><a href="catalogue.html#v='
             f'{urllib.parse.quote(v, safe="")}">{v}</a>: {what}</span></li>' for v, c, what in VERDICTS]
    items.insert(2, f'<li><i class="fix built"></i><span class="count">{n(len(ported))}</span><span>of them '
                    f'<a href="hd-strategies.html">built</a>, and running from the GEMDOS drive</span></li>')
    legend = "".join(items)
    solutions = collections.Counter(g["solution"].split(":")[0] for g in games if g["verdict"] == "fix")
    names = {}
    for s in read_csv(REPO / "src" / "survey" / "solutions.tsv", "\t"):
        names.setdefault(s["solution"].split(":")[0], s["solution"].split(": ", 1)[1].split(" (")[0])
    sol_rows = "".join(f'<tr><td>{k}</td><td>{esc(names[k])}</td><td class="num">{n(solutions[k])}</td></tr>'
                       for k in sorted(names))
    gos = sum(1 for g in games if g["strategy"] in ("Gamex + GOS4", "Gamex + GOS5"))
    gos5, gos4 = ({g["row"] for g in games if g["strategy"] == s} for s in ("Gamex + GOS5", "Gamex + GOS4"))
    lead = (f"The 8bitchip.info website lists {n(len(games))} Atari ST games adapted to start from a hard disk. "
            f"This project ran every one of them in the Hatari emulator from its GEMDOS drive: a folder of the "
            f"computer it runs on, served as drive C: file by file, with no disk sectors behind it.")
    main = f"""
<section class="hero" aria-labelledby="hero-title">
<h1 id="hero-title">Which of {n(len(games))} Atari ST <span class="nb">hard-disk</span> adaptations run from a GEMDOS drive</h1>
<p class="lead">{lead}</p>
<div class="map">
<div class="bands" role="img" aria-label="{n(count['as it is'])} games run as they are, {n(count['fix'])} need a fix ({n(len(ported))} of them built and running), {n(count['not feasible'])} not feasible, {n(count['unsure'])} unsure, by strategy">
{''.join(bands)}
</div>
<ul class="legend">{legend}</ul>
</div>
<p class="readout" aria-live="polite">Each square is one game, grouped by the way its adaptation reaches its files. Point at a square to see the game; select it to open its row in the catalogue.</p>
</section>

<section class="prose">
<h2 id="why">Why some do not</h2>
<p>Ten of the twelve ways the adaptations reach their files go through GEMDOS by name, and a
GEMDOS drive serves those. The other two, Gamex launchers with GOS4 or GOS5, bring their own
GEMDOS, a copy of TOS 1.04's running from RAM, which reads the disk by sectors through a
hard-disk driver. A GEMDOS drive has neither the driver nor the sectors: those {gos} games, Lemmings
among them, are most of the fixes. <a href="gemdrive-failure.html">Why Lemmings fails</a> shows it
step by step; <a href="hd-strategies.html">Verdicts and solutions</a> has every strategy's count.</p>

<h2 id="solutions">The solutions</h2>
<p>Four solutions make the {n(count['fix'])} games to fix run, each on the Atari side, with the
emulator unchanged. S2, S3 and S4 were shown in trial runs. S1 is built for the {n(len(gos5))} GOS5
games and the {n(len(gos4))} GOS4 games, and {n(len(ported))} of them run from the GEMDOS drive with
their start program built for it: {n(len(ported & gos5))} GOS5 games in Hatari and on an STE with the
SidecarTridge Multidevice's GEMDRIVE (<a href="gos5-gemdrive.html">the GOS5 games, built</a>), and
{n(len(ported & gos4))} GOS4 games in Hatari (<a href="gos4-gemdrive.html">the GOS4 games,
built</a>). The smaller fixes are next.</p>
<div class="table"><table>
<thead><tr><th></th><th>solution</th><th class="num">games</th></tr></thead>
<tbody>{sol_rows}</tbody></table></div>
<p><a href="hd-strategies.html#4-the-solutions-proposed">What each one changes, costs and risks</a>.</p>

<h2 id="project">The project</h2>
<p>It started with one game: the 2011 hard-disk adaptation of Lemmings, whose launcher stops at
once from a GEMDOS drive. The work has two parts. The first understood and classified: why
Lemmings fails, the launcher rebuilt from sources that reassemble to the original bytes, and every
adaptation in the 8bitchip.info website's list given a verdict. The second, under way, builds the solutions one group of games at a
time: the GOS5 and GOS4 games first, {n(len(ported))} of them running now, then the smaller
fixes and the games still unsure; then a check with acsi2stm's GemDrive, the other
GEMDRIVE, and a program that installs the builds on a user's own copies. Each build is tested in
Hatari's GEMDOS drive and on the SidecarTridge Multidevice's GEMDRIVE, which serves an ST's drive
the same way from an SD card.</p>
<p>The findings, in the order they were made: <a href="gemdrive-failure.html">why Lemmings fails</a>,
<a href="launch-chain.html">the launch chain</a>, <a href="disk-layer.html">the disk layer</a>,
<a href="launcher-formats.html">the file formats</a>, <a href="launcher-signatures.html">the
launcher's signatures</a>, <a href="modes.html">the modes</a>, <a href="strategies.html">the
strategies</a> and <a href="hd-strategies.html">the verdicts and solutions</a>.</p>
</section>
"""
    return page("index", SITE, main, kind="home", lead=lead)


# --- The catalogue --------------------------------------------------------------------------------

def ram_of(g: dict) -> str:
    m = re.match(r"(512K|1M|2M)", g["min_ram"])
    return m.group(1) if m else ""


def catalogue(games: list[dict], records: dict, shots: dict) -> str:
    strategies, ported = strategy_order(games), built()
    count = collections.Counter(g["verdict"] for g in games)
    rows = []
    for g in games:
        r = records.get(g["row"], {})
        machines = [label for key, label in MACHINES if r.get(key, "") not in ("", "-", "?")]
        cls = dict((v, c) for v, c, _ in VERDICTS)[g["verdict"]]
        rid = f"g-{int(g['row']):04d}"
        shot = shots.get(g["row"])
        img = (f'<button class="shot" type="button" data-src="snapshots/{shot}" aria-label="Enlarge {esc(g["name"])}\'s screenshot">'
               f'<img src="snapshots/{shot}" alt="" loading="lazy" width="208" height="138"></button>') if shot else ""
        notes = [f'{esc(g["download"])}' + (f': {esc(g["reason"])}' if g["reason"] else "")]
        if g["solution"]:
            notes.append(f'<span class="sol">{esc(g["solution"])}</span>')
        rows.append(
            f'<tr id="{rid}" data-v="{esc(g["verdict"])}" data-s="{esc(g["strategy"])}" data-c="{esc(g["code_category"])}" '
            f'data-r="{ram_of(g)}" data-m="{esc("|".join(machines))}" data-n="{esc(g["name"].lower())}">'
            f'<td class="pic">{img}</td>'
            f'<td class="game">{link(esc(g["url"]), esc(g["name"]))}<p>{" ".join(notes)}</p></td>'
            f'<td>{esc(g["strategy"])}</td>'
            f'<td><span title="{esc(CATEGORIES.get(g["code_category"], ""))}">{esc(g["cat_code"] or "none")}</span>'
            f'<br><small>{esc(g["code_category"] and "cat. " + g["code_category"])}</small></td>'
            f'<td>{esc(g["min_ram"])}</td>'
            f'<td><small>{", ".join(machines)}</small></td>'
            f'<td class="verdict"><i class="{cls}{" built" if g["row"] in ported else ""}"></i>{esc(g["verdict"])}<br>'
            f'<small>{"built: runs" if g["row"] in ported else BY.get(g["by"], "")}</small></td></tr>')

    def options(values, labels=None):
        return "".join(f'<option value="{esc(v)}">{esc((labels or {}).get(v, v))}</option>' for v in values)

    verdict_radios = "".join(
        f'<label><input type="radio" name="v" value="{esc(v)}"><i class="{c}"></i>{v} <span class="count">{n(count[v])}</span></label>'
        for v, c, _ in VERDICTS)
    cats = [c for c in CATEGORIES if any(g["code_category"] == c for g in games)]
    main = f"""
<h1>The catalogue</h1>
<p class="lead">Every game of the 8bitchip.info website's list of hard-disk adaptations
({link(PP + "fromhd3.php", "fromhd3.php")}, read on 2026-10-11), with the way its adaptation
reaches its files and its verdict from Hatari's GEMDOS drive. The name opens the game's page on
the 8bitchip.info website, where its download is; how the original used the floppy and the
machines it runs on are the ones that page gives.{" The picture is the last screen of its run, on an ST with TOS 1.04 (STE games: TOS 1.62); for a game built for the GEMDOS drive, of its build's run." if shots else ""}</p>
<form class="filters" role="search" aria-label="Filter the games">
<label class="search">Name <input type="search" name="q" autocomplete="off" placeholder="Lemmings"></label>
<fieldset class="verdicts"><legend>Verdict</legend>
<label><input type="radio" name="v" value="" checked>all <span class="count">{n(len(games))}</span></label>{verdict_radios}
</fieldset>
<label>Strategy <select name="s"><option value="">all</option>{options(strategies)}</select></label>
<label>Floppy use <select name="c"><option value="">all</option>{options(cats, CATEGORIES)}</select></label>
<label>RAM <select name="r"><option value="">all</option>{options(["512K", "1M", "2M"])}</select></label>
<label>Runs on <select name="m"><option value="">all</option>{options([l for _, l in MACHINES])}</select></label>
<p class="shown" aria-live="polite"><span id="shown">{n(len(games))}</span> of {n(len(games))} games shown
<button type="reset">Show all</button></p>
</form>
<div class="table catalogue"><table>
<thead><tr><th><span class="vh">Screenshot</span></th><th>Game</th><th>Strategy</th><th>Floppy use</th><th>RAM</th><th>Runs on</th><th>Verdict</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table></div>
<p class="empty" hidden>No game matches these filters. <button type="button" class="clear">Show all games</button></p>
<dialog class="viewer" aria-labelledby="viewer-title"><form method="dialog"><p id="viewer-title"></p>
<button class="close">Close</button></form><img alt=""></dialog>
"""
    return page("catalogue", "The catalogue", main, kind="wide",
                lead=f"{n(len(games))} hard-disk adaptations, each with its strategy and verdict from a GEMDOS drive.")


# --- The tools ------------------------------------------------------------------------------------

def tools_page() -> str:
    doc = Doc((REPO / "tools" / "dev" / "README.md").read_text())
    rows = []
    for f in sorted((REPO / "tools" / "survey").glob("*.py")) + sorted((REPO / "tools").glob("*.py")) + [Path(__file__).resolve()]:
        m = re.search(r'^"""(.*?)"""', f.read_text(), re.S | re.M)
        if not m:
            continue
        text = m.group(1).strip().split("\n\n")
        first = re.sub(r"\s*\([^()]*\b(?:EPIC-\d+|STORY-\d+|[DCH]-\d\d)\b[^()]*\)", "",
                       re.sub(r"^(?:EPIC-\d+(?: STORY-\d+)?(?:, STORY-\d+)*|tools/\S+): ", "", text[0].replace("\n", " ")))
        usage = next((t.replace("Usage:", "").strip() for t in text if t.startswith("Usage:")), "")
        rows.append(f'<tr><td><code>{esc(str(f.relative_to(REPO)))}</code></td><td>{inline(first)}'
                    + (f'<br><code>{esc(usage.split(chr(10))[0])}</code>' if usage else "") + "</td></tr>")
    doc.toc.append((2, "the-survey-and-the-site", "The survey and the site"))
    main = (f"<h1>The tools</h1>\n{doc.body}\n"
            f'<h2 id="the-survey-and-the-site">The survey and the site</h2>\n'
            f"<p>The survey's scripts, in <code>tools/survey/</code>, and the packers and builders of "
            f"<code>tools/</code>. Each one's first lines say "
            f"what it reads and writes.</p>\n"
            f'<div class="table"><table><thead><tr><th>script</th><th>what it does</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')
    return page("tools", "Tools", main, rail=rail_for("tools", doc))


# --- Build and check ------------------------------------------------------------------------------

def snapshot_names(games: list[dict]) -> dict:
    """row -> the snapshot of the run that gave its verdict, or of its GEMDOS-drive run."""
    tsv = REPO / "tools" / "dev" / "builds" / "survey" / "runs.tsv"
    if not tsv.exists() or not SNAPSHOTS.is_dir():
        return {}
    runs = read_csv(tsv, "\t")
    by_run = {r["run"]: r for r in runs}
    gemdrive = {}
    for r in runs:
        if r["disk"] == "gemdrive" and r["snapshot"]:
            gemdrive.setdefault(r["row"], r["snapshot"])
    out = {}
    for g in games:
        r = by_run.get(g["run"], {})
        name = r.get("snapshot") if r.get("disk") == "gemdrive" else gemdrive.get(g["row"])
        if name and (SNAPSHOTS / name).is_file():
            out[g["row"]] = name
    # a built game: the last screen of its build's run (src/survey/ports.tsv), kept in SNAPSHOTS once its
    # run folder is gone
    for r in read_csv(REPO / "src" / "survey" / "ports.tsv", "\t"):
        if not r["shot"]:
            continue
        src, kept = LOGS / r["run"] / "shots" / r["shot"], SNAPSHOTS / f"port-{r['row']}.png"
        if src.is_file() and (not kept.is_file() or kept.read_bytes() != src.read_bytes()):
            shutil.copyfile(src, kept)
        if kept.is_file():
            out[r["row"]] = kept.name
    return out


def build(out: Path, with_snapshots: bool) -> None:
    games = read_csv(REPO / "src" / "survey" / "migration.csv")
    records = {r["row"]: r for r in read_csv(REPO / "src" / "survey" / "catalogue.csv")}
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for f in ("site.css", "site.js"):
        shutil.copy(HERE / f, out / f)
    shots = snapshot_names(games) if with_snapshots else {}
    if shots:
        (out / "snapshots").mkdir()
        for name in shots.values():
            shutil.copy(SNAPSHOTS / name, out / "snapshots" / name)
    pages = {"index": index(games), "catalogue": catalogue(games, records, shots), "tools": tools_page()}
    for key, _, notes in SECTIONS:
        for stem, _ in notes:
            doc = Doc((REPO / "src" / "notes" / f"{stem}.md").read_text())
            main = f"<h1>{doc.title}</h1>\n{doc.body}"
            pages[stem] = page(stem, doc.title, main, rail=rail_for(stem, doc))
    for name, text in pages.items():
        (out / f"{name}.html").write_text(text)
    print(f"{out}: {len(pages)} pages, {len(games)} games, {len(shots)} snapshots")


class Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.refs, self.text, self.prose, self.code = set(), [], [], [], 0

    def handle_data(self, data):
        self.text.append(data)
        if not self.code:
            self.prose.append(data)

    def handle_endtag(self, tag):
        if tag in ("code", "pre"):
            self.code -= 1

    def handle_starttag(self, tag, attrs):
        if tag in ("code", "pre"):
            self.code += 1
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for k in ("href", "src", "data-src"):
            if a.get(k):
                self.refs.append((tag, k, a[k], a.get("rel")))


def check(out: Path) -> int:
    pages, bad = {}, []
    for f in sorted(out.glob("*.html")):
        p = Links()
        p.feed(f.read_text())
        pages[f.name] = p
    for name, p in pages.items():
        for tag, attr, ref, rel in p.refs:
            if re.match(r"https?:", ref):
                if attr != "href" or tag != "a":
                    bad.append(f"{name}: loads {ref} from another site")
                elif urllib.parse.urlsplit(ref).netloc.endswith("8bitchip.info"):
                    if urllib.parse.urlsplit(ref).path in ("", "/"):
                        bad.append(f"{name}: links to the 8bitchip.info website's home page, not a game or a technical page")
                    if "nofollow" not in (rel or "").split():
                        bad.append(f"{name}: {ref}: a link to the 8bitchip.info website without rel=nofollow")
                continue
            target, _, frag = ref.partition("#")
            target = target or name
            if not (out / target).is_file():
                bad.append(f"{name}: {ref}: no file {target}")
            elif frag and "=" not in frag and target.endswith(".html") and frag not in pages[target].ids:
                bad.append(f"{name}: {ref}: no anchor #{frag} in {target}")
    for name, p in pages.items():  # the site speaks to its readers, never to the backlog (CLAUDE.md)
        for m in sorted(set(BACKLOG.findall(" ".join(p.text)))):
            bad.append(f"{name}: refers to the backlog: {m}")
        for m in sorted(set(AUTHOR.findall(" ".join(p.prose)))):  # nor names the adaptations' author
            bad.append(f"{name}: names the adaptations' author: {m}")
    games = read_csv(REPO / "src" / "survey" / "migration.csv")
    missing = [g["row"] for g in games if f"g-{int(g['row']):04d}" not in pages["catalogue.html"].ids]
    if missing:
        bad.append(f"catalogue.html: no row for {len(missing)} games, first {missing[:5]}")
    for b in bad[:40]:
        print("  " + b)
    refs = sum(len(p.refs) for p in pages.values())
    print(f"check: {len(pages)} pages, {refs} links, {len(games) - len(missing)} of {len(games)} games, "
          f"{len(bad)} problem(s)")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--no-snapshots", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    build(args.out.resolve(), not args.no_snapshots)
    return check(args.out.resolve()) if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
