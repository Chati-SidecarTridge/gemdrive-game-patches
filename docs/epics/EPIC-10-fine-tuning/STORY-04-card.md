---
id: STORY-04
epic: EPIC-10
title: The card from the current builds
status: done
---

## Goal

The test card written again from the builds as they are after EPIC-09.

## Tasks

- [x] `tools/survey/sdcard.py` run again: Aquanaut in `STILLNOT`; every fix equal to the patcher's result.
- [x] The card's changes written to Diego's card, checked file by file, without `._` files.

## Acceptance

The card matches the builds and the patcher.

## Notes

**2026-10-26.** `tools/dev/builds/sdcard-1910`, against the card's `sdcard-1245b`: Aquanaut moves from
`FIXHOLE` (now empty, gone) to `STILLNOT`, whose group is named after its first and last game, so
`STILLNOT\1MB\AWE-PRI` becomes `AQU-PRI` (Aquanaut, Awesome, Prison); `INDEX.TXT` follows, with
the solutions' new wording ("GEMDOS and GEMDRIVE"). Nothing else differs. The 208 fixes on it equal
`src/survey/patches.tsv`'s results, the patcher's, file for file.

Written to Diego's card the same day: `STILLNOT\1MB\AQU-PRI\` added and `INDEX.TXT` replaced, then,
with Diego's OK, `FIXHOLE\` and `STILLNOT\1MB\AWE-PRI\` deleted and the copy's `._` files
removed (none left outside his own `DOWNLOAD\`). Every one of the build's 26,588 files on the card,
SHA-256 for SHA-256; the extras are the ST's own (`DESKTOP.INF`, Gravity's and Guild of Thieves'
saves, Robinsons Requiem's `CONFIG.INF`) and Diego's `DOWNLOAD\`. Ejected.
