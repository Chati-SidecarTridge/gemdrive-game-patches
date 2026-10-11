---
id: STORY-05
epic: EPIC-03
title: Every game in Hatari's GEMDRIVE mode: the verdicts
status: todo
---

## Goal

Every game's verdict in the migration table (D-14): as it is, fix, not feasible, or unsure, from
its files (STORY-04) and a run in Hatari's GEMDRIVE mode, with each strategy's behaviour also
seen from the PPDRIVER reference.

## Tasks

- [ ] The harness and `make_disks.sh` take any game folder, start program and RAM size; today they
      assume `C:\LEMMINGS\START.TOS`. `tools/dev/all_harness.sh` must still pass.
- [ ] `tools/survey/run_all.py` runs every game on ST TOS 1.04 in GEMDRIVE mode, several Hatari
      instances at a time, keeping the trace of GEMDOS, BIOS, XBIOS and ACSI calls and screenshots,
      and long enough to see the game's first file load after its start (a level, a menu's data):
      reaching a title is not enough.
- [ ] The verdict of every game into `migration.csv`: **as it is** when its files carry no
      sector-access signature and its run gets past that first load with no failed access;
      **fix** when it stops on something a solution could supply (a driver check, BIOS or XBIOS
      sector access, a fixed RAM layout…), the stop recorded; **not feasible** when it needs
      the hardware itself or major changes (direct floppy-controller access during play, its own
      disk format…), the reason recorded; **unsure**, with what is missing, otherwise.
- [ ] For each strategy, at least two representatives (or all its games, if fewer) also run from
      the PPDRIVER image, and one of them on STE TOS 1.62 and 2.06, so a GEMDRIVE failure is told
      apart from a game that fails in Hatari anyway (as Lemmings does after "1 PLAYER").
- [ ] Where a run contradicts STORY-04's class, the class is corrected.

## Acceptance

Every row of `migration.csv` has a verdict with its run folder and, for "fix" and "not feasible",
the stop or the reason; every strategy has its PPDRIVER comparison; the "unsure" rows are listed
with what would settle them.

## Notes

The harness's `key`, `mouse` and `event` steps give a game the input it needs to get past its
title; a game that needs more is "unsure" until it gets it.

From STORY-01: `src/probes/epic03/mode_probe.py` already runs one game from the mirror on one
disk and reports its file opens, sector reads, ACSI commands, CPU faults and halts; `run_all.py`
can start from it. Some games need a monochrome monitor ("Needs monochrome capable monitor" on
their page): the harness's `--monitor mono` gives them one. A game may also need more RAM in
Hatari than its page says: Vector Invaders halts with 1 MB on both disks and plays with 2 MB, so a
game that fails on both disks with 1 MB is run again with 2 MB before its verdict.
