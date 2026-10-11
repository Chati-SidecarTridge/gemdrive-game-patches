---
id: STORY-03
epic: EPIC-03
title: The adapted games' files
status: todo
---

## Goal

The adapted games' files on this Mac, unpacked, with an inventory of what each adaptation
contains.

## Tasks

- [ ] `tools/survey/mirror.py` copies the site into the mirror (`MIRROR` in `tools/dev/dev.cfg`):
      the list, every game page, every download a page offers, PP's documentation pages and the
      archives they link, and the pages' images. It makes one request at a time, with pauses,
      resumes where it stopped, and records each file's SHA-256 in `manifest.tsv`. Done first,
      2026-10-11 (D-12).
- [ ] `tools/survey/unpack_games.py` unpacks every archive from the mirror into
      `tools/dev/builds/survey/games/<name>/`, refusing paths that leave that folder. These are
      untrusted data: nothing from them runs on the host.
- [ ] The inventory, `src/survey/files.csv`: per game, its files and sizes; the program the user
      starts (`RUNME.TOS`, `START.TOS`, …); the executables and their headers; the magic numbers
      (`Ice!`, the `.FIC` header `43 33 00 00`, `PPGX`, …); the file-name families (`D15R_*.FIC`,
      `GXUT*.PRG`, `.ST`/`.MSA` images, …).
- [ ] The Lemmings download compared with `LEMMINGS/` (the same files by SHA-256, or the
      differences), and `LEMMSRD.ZIP`'s files set against it.

## Acceptance

Every game in `catalogue.csv` is in the mirror, unpacked and inventoried, or listed with the reason
it is not (a broken link, an unknown archive format). Git tracks nothing from the mirror or under
`tools/dev/builds/survey/`.

## Notes

From STORY-01: `LEMMINGS.ZIP` in the mirror holds the same 76 files as `LEMMINGS/`, SHA-256 for
SHA-256 (`LEMMSRD.ZIP` still to set against it). `tools/unpack.py start` now accepts up to 3 zero
bytes after the packed program: several `START.TOS` stubs pad their data to a multiple of 4.
`ALISTR.ZIP` (PP's AUTOlist Run) answered 404.

From STORY-02: the first mirror followed only `dwnld.php` links. 48 game pages send their download
to PP's game-archive pages (`ASTGA/`), and others link archives directly (floppy versions, Gamex
versions…); `tools/survey/mirror.py` now follows both (the archive pages' downloads include PP's
STX images of the original disks). The resumed run fetched 381 more files (the mirror is 1.4 GB);
16 more answered 404 (14 STX images on the archive pages, `AIGLEPR.ZIP`, one picture). Every
record of `catalogue.csv` now has at least one archive on disk; 21 of its 2,006 archives are
404s on PP's site, each on a record that has another (F1 GP's are `F1GP_GX.ZIP` and
`F1GPFLOV.ZIP`).
