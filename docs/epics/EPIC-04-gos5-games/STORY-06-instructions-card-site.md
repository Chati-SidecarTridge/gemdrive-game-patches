---
id: STORY-06
epic: EPIC-04
title: The instructions, the card and the site
status: done
---

## Goal

A user can patch their own copy of a GOS5 game and run it from a GEMDOS drive. Diego's test card
and the website show the result.

## Tasks

- [x] A README a user can follow on a fresh copy: what the patch changes, how to run the tool,
      and how to undo it.
- [x] In it, the games that need more than the build: a disk in drive A (Pit Fighter, Chaos Engine,
      Fire and Forget II, Venus the Flytrap, Jetsons), and Forgotten Worlds' two GOS files copied from
      another game's download (`D15R_5H.FIC`, `D15R_5F.FIC`, alike in all 56 that carry them, D-19).
- [x] `tools/survey/sdcard.py`: the card holds the patched GOS5 games, under the verdict they
      have now.
- [x] Diego's card brought to the new layout: Muzzy, Magic Boy and Prison into `STILLNOT`, with
      their builds (it removes their folders from `FIXGOS5`: Diego's word first).
- [x] The site: the GOS5 band, the catalogue's verdicts, and the solution's page updated.
      `build_site.py --check` passes.

## Acceptance

The README, followed on a fresh copy of a GOS5 game, gives a game that runs from the GEMDOS
drive. The card and the site show the new verdicts.

## Notes

- **The instructions** are `src/notes/gos5-gemdrive.md`, a page of the site ("The GOS5 games,
  built", under Strategies and solutions). Followed on a fresh copy of Gods' download
  (`tools/dev/builds/gos5/readme-1433/`): the original kept as `START.ORG`, built, its title menu
  from the GEMDOS drive (`tools/dev/logs/20261016-143402-st-104-gemdrive-readme-gods`); the tool on
  the built file again: "0 PPHD checks, not one", nothing written.
- **The card**: `src/survey/ports.tsv` holds each GOS5 game's build options (`--floppy` for five),
  its result (`runs`, or `fails`: Muzzy, Magic Boy, Prison) and the files it adds from another
  download (Forgotten Worlds' two, D-19). `sdcard.py` builds each one's start program in place, adds
  those files, and puts the games that fail in a new folder, `STILLNOT` (Diego, 2026-10-16: "a
  folder for games 'still not working' after passing the patching tests"). Built into
  `tools/dev/builds/sdcard-1428/`: against the earlier layout, only the 87 start programs and
  Forgotten Worlds' two files differ, the 84 builds byte for byte the ones on Diego's card
  (`card-1335`), and the three games moved to `STILLNOT/1MB/MAG-PRI/`. `gos5_run.py` now takes the
  originals from the unpacked downloads (`run_all.plan`), with the table's options and files.
- **The site**: the verdicts are unchanged (all 87 stay fix); the catalogue shows their new reasons
  and solutions, the solutions page (`solutions.md` §1 and S1) what was built.
- **The site was out of date** (Diego, 2026-10-16: "remember we are building a website for our
  research. is it updated?"): the home page called S1 a proposal and the first iteration "now
  ending", its solutions table took S1's name from the last row of `solutions.tsv` (Forgotten
  Worlds'), the Tools page had none of the GOS5 tools, the GOS5 games' pictures were their failing
  runs. Now: the 84 built games marked on the home page's squares (amber with a green centre) and
  in the legend ("of them built, and running from the GEMDOS drive"), "built: runs" in the
  catalogue, each built game's picture the last screen of its build's run (`ports.tsv`'s `run` and
  `shot`, kept in the snapshots as `port-<row>.png`; Muzzy and Magic Boy halt before theirs and keep
  their old one), S1's name its first row's, the home page's text, and the Tools page.
- **No reference to the backlog on the site** (D-20, CLAUDE.md): the home page's list of epics is
  gone, its text says where the work stands in words; the notes, the Tools page and the catalogue's
  reasons and solutions were rewritten without epics, stories, decisions or hypotheses codes;
  `build_site.py --check` fails on one (0 problems).
- **Diego's card** (his "yes", 2026-10-16): `STILLNOT/1MB/MAG-PRI/` written from `sdcard-1428`
  (Magic Boy 27 files, Muzzy 6, Prison 9, each read back by SHA-256), the card's `INDEX.TXT`
  replaced by the new one, then the three folders in `FIXGOS5/1MB/ALI-ZOU/` removed (checked
  first: PP's files, as the old layout has them).
- **The card, again** (2026-10-16): Magic Boy and Muzzy run on Diego's STE, so `sdcard-1518` has
  them back in `FIXGOS5/1MB/ALI-ZOU/` with their builds and Prison alone in `STILLNOT/1MB/PRI-PRI/`;
  written to the card (his "serve yourself"). Then Awesome, which hangs on his STE for the same
  kind of check as Prison's (Diego's "yes"): `ports.tsv` has it as `fails`, `sdcard-1635` puts both
  in `STILLNOT/1MB/AWE-PRI/`. On the card, two renames and no delete: `PRI-PRI` to `AWE-PRI`, and
  `AWESOME` moved there from `FIXGOS5/1MB/ALI-ZOU/` (each folder first checked against the layout by
  SHA-256), and `INDEX.TXT` replaced. Read back: `STILLNOT` 18 files, `FIXGOS5` 1,340, all as
  `sdcard-1635`. The instructions list both under "Still not working", the site counts 85 built
  and running.
- **The site no longer names the adaptations' author** (D-21, Diego, 2026-10-16): the nine notes,
  the Tools page, the catalogue's reasons and labels ("Floppy use", "Runs on") and the builder's text
  say "the 8bitchip.info website", "the Gamex launcher", "PPDRIVER", "the original files"; `PPHD`,
  `PPDRIVER` and the launcher's quoted message stay. `pp-modes.md` is now `modes.md` ("The modes"),
  its quote marker **doc**; the strategy `PP launcher` is now `launcher without Gamex` (`classify.py`
  checked against `migration.csv`: the same strategy for all 1,831). The footer's home-page link is
  gone: the site links to the 8bitchip.info website for the 1,831 game pages and 13 technical pages
  only. `build_site.py --check` fails on PP, PPera or Putnik outside code and on a home-page link:
  0 problems, 7,675 links.
