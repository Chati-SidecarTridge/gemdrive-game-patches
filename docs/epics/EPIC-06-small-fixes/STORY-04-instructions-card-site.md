---
id: STORY-04
epic: EPIC-06
title: The instructions, the verdicts, the card and the site
status: done
---

## Goal

A user can apply each fix to their own copy. The verdicts, the card and the site show the eight
games running.

## Tasks

- [x] A README for the three fixes, followed on fresh copies of the eight games.
- [x] `migration.csv` updated through `verdicts.py`, with the evidence.
- [x] The card holds the fixed games, and the site shows the new verdicts. `build_site.py
      --check` passes.

## Acceptance

Fresh copies of the eight games, fixed by following the README, run from the GEMDOS drive.

## Notes

**2026-10-26.**

- The README is `src/notes/small-fixes.md`, the site's page "Eight games with a small fix": the
  three fixes, why each game stops, the commands, Storm Master's floppy in drive A, Rody and Mastico
  2's music, and Aquanaut not working yet. Followed on fresh copies unpacked from the mirror's ZIPs
  (scratchpad `readme-test/`): the six folders it fixes are file for file the card build's
  (`sdcard-1245b`). Following it literally found one error, fixed: `tools/dev/asm.sh` writes inside
  the repository only, so `GDBPB.PRG` is built into `tools/dev/builds/` and copied.
- `solutions.tsv` names each fix's tool (S2 adds "run from the game's folder first"), and
  `verdicts.py` carried it into `migration.csv`: only those eight rows changed. The verdicts stay
  "fix"; `ports.tsv` holds the eight with their run and screenshot, Aquanaut as `fails` after
  Diego's STE.
- The card builder (`tools/survey/sdcard.py`) applies the fixes named in `ports.tsv`'s options
  (`gdbpb`, `fastload`) and added files (Rody's `RUNME.TOS`, from `RODYM4.ZIP`, now its program to
  start in `INDEX.TXT`); the card got the eight games' changes and `INDEX.TXT` (checked file by file,
  no `._` files). Aquanaut, now `fails`, goes to `STILLNOT` at the card's next write.
- The site: the new page; the home page's solutions paragraph and table (games and running per
  solution: S1 202, S2 4, S3 2, S4 1); and, at Diego's request ("a fresh look at the whole site",
  with the frontend-design skill), a new style: GEM's desktop on a monochrome monitor (a dithered
  desk, each page a window with a striped title bar holding its path cut to 8.3, the section's pages
  in a window beside it, an info line with the counts), the system's monospace for what GEM drew,
  Charter for the text. `build_site.py --check`: 14 pages, 0 problems. Checked in Chrome at 1440 px
  and at 390 px.
