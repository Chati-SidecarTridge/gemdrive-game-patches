---
id: STORY-04
epic: EPIC-03
title: The strategies, from the files
status: done
---

## Goal

Each game assigned a strategy based on what its files contain. The strategies are defined by that
evidence, not by PP's names alone.

## Tasks

- [x] The signatures of each launcher family, starting from Lemmings' (`src/notes/launcher-signatures.md`,
      EPIC-02): the `PPHD` gate, the `.FIC` header and its packer, GOS (D15R), and the Gamex
      header `PPGX`. Also the signatures of disk access in the start programs and in the stages our
      unpackers can open: GEMDOS file calls, BIOS `Rwabs`, XBIOS `Floprd` and `DMAread`, the ACSI,
      floppy-controller and IDE registers.
- [x] `tools/survey/classify.py` writes each game's strategy and the evidence for it into the
      migration table, `src/survey/migration.csv`, one row per game. A game that no signature
      explains is marked unclassified with the reason, and is not forced into a class.
- [x] The strategies defined: name; how it runs from a hard disk; what it needs from the disk and
      the system (files, sectors, a driver and which one, fixed RAM); its signature; its games.
      Each one is set against PP's categories.

## Acceptance

Every game in the mirror has a row in `migration.csv` with a strategy, or is marked unclassified
with its reason. The note gives the number of strategies and the number of games in each.

## Notes

**Done 2026-10-11.** `python3 tools/survey/classify.py` writes `src/survey/migration.csv`; the note
is `src/notes/recognising-modes.md`; the disk-access patterns are in `src/notes/launcher-signatures.md`.

- **12 strategies**, no game unclassified: HAGA 1,022, HAGE 203, HAG2 130, plain 125, Gamex 117,
  Gamex + GOS4 116, Gamex + GOS5 87, PP launcher 21, Gamex + GOS 1.00 5, plain + HOLE 3, FWRD RAM
  disk 1, floppy image 1. They reach the disk in two ways: by name through the machine's GEMDOS
  (1,628 games) or by sectors through a driver (GOS4 and GOS5, 203 games, every launcher with the
  `PPHD` check, 202 with the `DMAread` fallback too).
- Against PP's categories: GOS5 is category 6 (73 of 87), GOS4 categories 1–2 and 4, HAGA every
  category (179 of category 6), HAGE and HAG2 categories 1–2.
- Each row also has `access` (the strongest disk access its start programs show: files, sectors,
  registers) and `inner_evidence` (the same in its PP-packed stages). 18 HAGA games show register
  access: 7 keep the old GOS5 `START.TOS` next to `RUNME.TOS`, 11 have floppy-controller code in
  `RUNME.TOS`; STORY-05's runs settle them.
- The verdict columns (`verdict`, `run`, `reason`, `solution`) are empty, for STORY-05 and
  STORY-06.

