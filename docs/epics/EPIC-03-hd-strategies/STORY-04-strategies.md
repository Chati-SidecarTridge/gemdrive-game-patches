---
id: STORY-04
epic: EPIC-03
title: The strategies, from the files
status: todo
---

## Goal

Each game assigned a strategy based on what its files contain. The strategies are defined by that
evidence, not by PP's names alone.

## Tasks

- [ ] The signatures of each launcher family, starting from Lemmings' (`src/notes/launcher-signatures.md`,
      EPIC-02): the `PPHD` gate, the `.FIC` header and its packer, GOS (D15R), and the Gamex
      header `PPGX`. Also the signatures of disk access in the start programs and in the stages our
      unpackers can open: GEMDOS file calls, BIOS `Rwabs`, XBIOS `Floprd` and `DMAread`, the ACSI,
      floppy-controller and IDE registers.
- [ ] `tools/survey/classify.py` writes each game's strategy and the evidence for it into the
      migration table, `src/survey/migration.csv`, one row per game. A game that no signature
      explains is marked unclassified with the reason, and is not forced into a class.
- [ ] The strategies defined: name; how it runs from a hard disk; what it needs from the disk and
      the system (files, sectors, a driver and which one, fixed RAM); its signature; its games.
      Each one is set against PP's categories.

## Acceptance

Every game in the mirror has a row in `migration.csv` with a strategy, or is marked unclassified
with its reason. The note gives the number of strategies and the number of games in each.

## Notes
