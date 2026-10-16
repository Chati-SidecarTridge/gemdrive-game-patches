---
id: STORY-02
epic: EPIC-08
title: Our builds made to know it
status: todo
---

## Goal

The block the ports put in each build (`src/gemdrive/gos5_patch.s`, and the other ports' own)
takes the GEMDOS-drive path on acsi2stm's GemDrive too, with its stub moved out of the game's
RAM, and every build still runs as before on Hatari's GEMDOS drive, PP's PPDRIVER path and the
Multidevice's GEMDRIVE.

## Tasks

- [ ] gd_check: a `TRAP #1` with XBRA `A2ST` (the chain walked, as acsi2stm's own `init.s` does)
      takes the GEMDOS-drive path, on a 68000.
- [ ] The stub copied out of the game's RAM (beside gd_forward, in the place each GOS base gives
      it) and gd_forward calling the copy; the place checked against every port's games.
- [ ] Whatever else STORY-01 found (the caller's stack, the stub's own `TRAP #1`, the DMA chip
      left after a call).
- [ ] An emulation in Hatari of the stub's use of RAM (a stub at a game's low TPA, its pushes on
      the caller's stack), as `md_emulate.py` did for the Multidevice: the moved copy keeps running.
- [ ] Every port's builds rebuilt and run on Hatari's three setups, GEMDOS drive and PPDRIVER: the
      same results as before the change.

## Acceptance

The builds know acsi2stm's GemDrive, and their runs on Hatari are unchanged.

## Notes
