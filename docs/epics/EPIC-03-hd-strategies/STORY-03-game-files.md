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
