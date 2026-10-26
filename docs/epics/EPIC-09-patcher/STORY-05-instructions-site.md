---
id: STORY-05
epic: EPIC-09
title: The page on the site, and its instructions
status: done
---

## Goal

The patcher as a page of the website, reached from the home page's check and from each game's
row in the catalogue, with plain instructions.

## Tasks

- [x] The page: drop or choose a ZIP, the check, the result in plain words, the download.
- [x] Linked from the home page and from the catalogue; the instructions on it.
- [x] `build_site.py --check` passes; the page works from the site's folder.

## Acceptance

A user can patch a game from the site's folder by following the page.

## Notes

**2026-10-26.** `patch.html`, "Patch a game", in the site's menu: a GEM alert box to drop or choose
the ZIP, the answer in plain words for each action (patched, with what changed, the program to start,
`GDBPB.PRG` first, a floppy in drive A for `--floppy` builds, and the download as
`<NAME>-GEMDRIVE.ZIP`; a second download asked for and checked; nothing to patch; no fix yet, with a
link to the game's catalogue row; another download, naming the main one; not a game; unknown), and the
steps after. The home page's check has a "Patch a game" button; each catalogue row whose fix runs has
"Patch it". `src/probes/epic09/ui_test.py` drives the page in headless Chrome through its file input:
the eight cases answer as above, and each offered download is the patcher's ZIP (SHA-256). Opened from
the site's folder (`file://`), Chrome counts it a secure context: hashing, `DecompressionStream`, the
2,074 rows and the blocks all work. `build_site.py --check`: 7 pages, 0 problems. Safari and Firefox
not tried yet.
