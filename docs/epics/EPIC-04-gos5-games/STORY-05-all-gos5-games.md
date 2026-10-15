---
id: STORY-05
epic: EPIC-04
title: The 87 GOS5 games from the GEMDOS drive
status: todo
---

## Goal

Every game of the `FIXGOS5` group, patched by STORY-04's tool, is run from the GEMDOS drive with
`run_all.py`'s rules. The verdicts are updated, and each failure is listed with its cause.

## Tasks

- [ ] The 87 games patched (copies under `tools/dev/builds/`) and run from the GEMDOS drive on ST
      TOS 1.04, and on STE TOS 1.62 for the STE games, each at the RAM of its STORY-05 run.
- [ ] Each run looked at, as in EPIC-03 STORY-05. A game that does not run is traced, and its
      cause is listed.
- [ ] `migration.csv`: a game that runs patched gets its new verdict, with the tool as its
      solution, through `verdicts.py` (findings with the evidence).
- [ ] The games that remain, each with what would take it further.

## Acceptance

Every game of the 87 has a run of its patched copy and a verdict, and the counts are recorded
here.

## Notes
