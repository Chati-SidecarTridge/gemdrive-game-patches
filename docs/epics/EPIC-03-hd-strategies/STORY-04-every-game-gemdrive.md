---
id: STORY-04
epic: EPIC-03
title: Every game in Hatari's GEMDRIVE mode
status: todo
---

## Goal

The migration table's works-as-it-is column, from a run of every game in Hatari's GEMDRIVE mode,
and each strategy's behaviour seen from the PPDRIVER reference too, confirming or correcting
STORY-03.

## Tasks

- [ ] The harness and `make_disks.sh` take any game folder, start program and RAM size; today they
      assume `C:\LEMMINGS\START.TOS`. `tools/dev/all_harness.sh` must still pass.
- [ ] `tools/survey/run_all.py` runs every game once on ST TOS 1.04 in GEMDRIVE mode, several
      Hatari instances at a time. Each run keeps the trace of GEMDOS, BIOS, XBIOS and ACSI calls
      and screenshots, and writes the verdict into `migration.csv`'s works-as-it-is column: yes,
      no (with the stop: a driver check, a sector or XBIOS access, a crash), or unsure (left for
      a look, with the screenshots).
- [ ] For each strategy, at least two representatives (or all its games, if fewer) also run from
      the PPDRIVER image, and one of them on STE TOS 1.62 and 2.06, so a GEMDRIVE failure is told
      apart from a game that fails in Hatari anyway.
- [ ] For each strategy that fails in GEMDRIVE mode: what it needs, as in EPIC-01's list of
      dependencies. Where a run contradicts STORY-03's class, the class is corrected.

## Acceptance

Every row of `migration.csv` has its works-as-it-is verdict with its run folder, no row is left
unsure without a reason, and every strategy has its PPDRIVER comparison.

## Notes

A run counts as working when its screenshots show the game's own screen (title or menu) and the
trace shows no error exit; reaching play needs input, which the harness's `key`, `mouse` and
`event` steps give where a game needs it. Lemmings is the known case that reaches its title and
then stops after "1 PLAYER" on the reference too (EPIC-01 STORY-01): the PPDRIVER comparison is
what keeps such games out of the GEMDRIVE failures.
