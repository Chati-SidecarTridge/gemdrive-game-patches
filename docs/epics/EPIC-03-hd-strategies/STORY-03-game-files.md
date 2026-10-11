---
id: STORY-03
epic: EPIC-03
title: The adapted games' files
status: done
---

## Goal

The adapted games' files on this Mac, unpacked, with an inventory of what each adaptation
contains.

## Tasks

- [x] `tools/survey/mirror.py` copies the site into the mirror (`MIRROR` in `tools/dev/dev.cfg`):
      the list, every game page, every download a page offers, PP's documentation pages and the
      archives they link, and the pages' images. It makes one request at a time, with pauses,
      resumes where it stopped, and records each file's SHA-256 in `manifest.tsv`. Done first,
      2026-10-11 (D-12).
- [x] `tools/survey/unpack_games.py` unpacks every archive from the mirror into
      `tools/dev/builds/survey/games/<name>/`, refusing paths that leave that folder. These are
      untrusted data: nothing from them runs on the host.
- [x] The inventory, `src/survey/files.csv`: per game, its files and sizes; the program the user
      starts (`RUNME.TOS`, `START.TOS`, …); the executables and their headers; the magic numbers
      (`Ice!`, the `.FIC` header `43 33 00 00`, `PPGX`, …); the file-name families (`D15R_*.FIC`,
      `GXUT*.PRG`, `.ST`/`.MSA` images, …).
- [x] The Lemmings download compared with `LEMMINGS/` (the same files by SHA-256, or the
      differences), and `LEMMSRD.ZIP`'s files set against it.

## Acceptance

Every game in `catalogue.csv` is in the mirror, unpacked and inventoried, or listed with the reason
it is not (a broken link, an unknown archive format). Git tracks nothing from the mirror or under
`tools/dev/builds/survey/`.

## Notes

**Done 2026-10-11.** `python3 tools/survey/unpack_games.py`, then `python3 tools/survey/inventory.py`.

- **Unpacked**: the mirror's 2,075 archives (2,074 ZIP, 1 RAR) into
  `tools/dev/builds/survey/games/<path in the mirror>/` (1.89 GB; two names occur twice, at the
  site's root and under `ASTGA/`, so the folder follows the path). No entry was refused, no two
  collided. ZIPs inside archives (8) are unpacked next to themselves (Stone Age keeps its game in
  two). The one failure is `CarrierCommandM.rar`, a manual (one PDF) that `bsdtar` reports with a
  CRC error. `tools/dev/builds/survey/unpacked.tsv` lists every archive.
- **The inventory**, `src/survey/files.csv`: 28,834 files, one row each: archive, path, size,
  SHA-256 (16 digits), the program to start, PP's file-name family, the kind from the first bytes
  and its detail, and the launcher marks. Kinds: data 16,661, text 4,443, programs 4,047 (1,730 of
  them PP's self-unpacking stub), PP packed 2,847 (with the name and size in their header), ST
  images 595, ATM5 117, ICE 89, STX 15, MSA 12, ZIP 8. Families: HAGA modules 1,475, D15R 1,464,
  floppy images 627, PCH 479, T14 365, GXUT 351, state saves 11, HOLE 8, AUTO 2.
- **The check**: all 1,831 records of `catalogue.csv` have a download unpacked; 33 of the archives
  pages link are 404s on PP's site, each on a record that has another. Every record has a program
  to start (2,051 found by name or as the only program, 188 records' programs a choice) except two
  that are floppy images only (Rody and Mastico 2, Ice and Fire).
- **Lemmings**: `LEMMINGS.ZIP` holds the same 76 files as `LEMMINGS/`. `LEMMSRD.ZIP` ("Download
  #2 - 2MB RAM min") is another adaptation, May 2011: 7 files, three of them `LEMMINGS/`'s
  (`GXUT260.PRG`, `LEMMINGS.PCH`, `LS2DD.FIC`), its own `START.TOS` with no `PPHD` check, a 94-byte
  `GXSPE`, and `FWRD` (739,618 bytes): all the game's files in one, behind an `FWRD` directory;
  PP's "filewise ramdisked". Its README: "Any hard disk driver, or even from floppy". **On the
  GEMDOS drive with 2 MB it reaches the title menu** (run 20261011-202133): `LEMMINGS.PCH`,
  `LS2DD.FIC` and `FWRD` opened by name, `FWRD` read whole into `$14A000`, no sector read. A
  level could not be started: the harness's `mouse` step is built on the 1 MB build's IKBD code
  (`$21A6`, `$D0A0`, `$E996`, EPIC-01), which this build does not have (its table is not in RAM at
  the title; run 20261011-202442). That is STORY-05's to settle. Only one other adaptation has an
  `FWRD` file (Pick'n'Pile).

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
