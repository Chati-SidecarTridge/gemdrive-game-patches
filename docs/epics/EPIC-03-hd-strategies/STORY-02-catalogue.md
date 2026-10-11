---
id: STORY-02
epic: EPIC-03
title: The catalogue and PP's own classification
status: done
---

## Goal

Every record of PP's list as a table in this repository, with what each game's page adds, its
terms read with STORY-01's glossary.

## Tasks

- [x] `tools/survey/catalogue.py` (standard library). It reads the list and each game's page from
      the mirror (STORY-03, D-12), never the site, and writes `src/survey/catalogue.csv`: name,
      source URL, page, downloads (archive names, RAM, machines), the list's RAM and TOS 1.04 /
      TOS 2.06 / Mega STE / Falcon / TT marks, its note, its date, the category code, and the
      page's text on the adaptation. The record count must equal the list's on the mirror's
      date.
- [x] The category code split into its parts (multipart or singleparted, RAM, TOS dependence, TPA,
      file system, XBIOS or floppy controller), counted over the catalogue and compared with the
      counts in `agcat.html`.

## Acceptance

`src/survey/catalogue.csv` holds every record of the list on the mirror's date, with the code
parsed for every game that has one, and each game's mode as its page names it (STORY-01's
glossary).

## Notes

**Done 2026-10-11.** `python3 tools/survey/catalogue.py` writes `src/survey/catalogue.csv`.

- **1,831 records**, every row of the list's table (the script checks that each 11-column row has
  a game page), from the list as mirrored at 2026-10-11T14:29:26Z; 1,829 pages (two pairs of
  records share one). The list states no total of its own ("Over 1700 games").
- PP's text stays in the mirror (D-11): a row keeps the list's cells (RAM, GX, TOS 1.04, TOS
  2.06, MSTE16, Falcon, TT, Note, Date, Val), the page's URL, its downloads (2,261 links to 2,006
  archives, with the RAM, version and machines their labels name), and what is read from the page with
  STORY-01's glossary: the category code and its parts, the TOS dependence, the source PP
  started from (STX/ST/MSA, original or crack), the monitor it needs (18 mono only, 75 colour
  and mono), the adaptation terms, and **the mode the page names**: Gamex 266, HAGA 158, HAGE 42,
  HAG2 12, Gamex + GOS 6, none 1,347. Most pages do not name their mode; the files will
  (STORY-03, STORY-04).
- Every record has a download. 48 pages send it to PP's game-archive pages (`ASTGA/`), and
  some link archives directly: the first mirror had followed only `dwnld.php`, so
  `tools/survey/mirror.py` now follows both (STORY-03).
- **The code** is on 1,610 records: 1,493 multipart, 108 singleparted; RAM 512K 1,406, 1M 165;
  T 1,105, I 313, O 32; A or E (AES) 52; P 995; L 1,088; F 300, DFC 101, FDC 4; X/X8/XB8 25.
  1,442 codes give one of PP's categories; 168 do not: `DFC` (101, never explained, STORY-01),
  a bare `M` (25), and codes without `L` or `F` (`M5TP`, `M5T`, `M1I` …).
- **Against `agcat.html`** (450 games, about 2009–2011):

  | category | from the codes (1,831 records) | agcat's totals (450) | catalogue games in agcat's lists |
  | --- | --- | --- | --- |
  | 1–2 (file system, relocatable) | 957 | 40 + 130 | 133 |
  | 3 (singleparted) | 105 | 104 | 97 |
  | 4 (file system, low RAM) | 87 | 61 | 56 |
  | 5 (XBIOS) | 27 | 6 | 5 |
  | 6 (floppy controller) | 266 | 107 | 96 |
  | not given by the code | 168 | | |

  387 of agcat's names match a record. Of the 265 that also have a parsed code, the two agree on
  186. Most of the rest were adapted again later (list dates 2020–2025: Strider, Street Fighter,
  Rockford are "low RAM" in agcat and `M5TPL` now), so the code describes the current download
  and agcat the first one. The code is the column to use; agcat's category is kept as
  `agcat_category`.
