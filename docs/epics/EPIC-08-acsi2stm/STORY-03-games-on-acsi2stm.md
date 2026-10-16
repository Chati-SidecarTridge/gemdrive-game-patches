---
id: STORY-03
epic: EPIC-08
title: The ported games from acsi2stm's GemDrive
status: todo
---

## Goal

Every ported game's build runs from acsi2stm's GemDrive on Diego's STE, or the game is listed with
what stops it.

## Tasks

- [ ] A card for acsi2stm's GemDrive (FAT, the same folders as the Multidevice's), made by
      `tools/survey/sdcard.py` or a variant of it.
- [ ] Lemmings first: to its first level, with the mouse, as EPIC-04 STORY-03.
- [ ] Then every ported game, boot sector and `AUTO` program, DMA firmware (and PIO, if Diego's unit
      has it).
- [ ] A game that fails there and runs from the Multidevice traced to its cause, with the help of
      STORY-02's emulation; its fix in STORY-02's builds, or the reason it has none.

## Acceptance

Every ported game has a result from acsi2stm's GemDrive, and the failures their causes.

## Notes
