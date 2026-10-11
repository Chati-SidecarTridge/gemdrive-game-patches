---
id: STORY-05
epic: EPIC-02
title: The disk layer: D15R and the driver it uses, annotated
status: todo
---

## Goal

The disk layer the launcher installs, understood completely, since EPIC-04 replaces or feeds it.
That means D15R (PP's GOS, if H-08 holds), the relocated copy of PP's resident driver, and how
the game reaches its files through them. EPIC-01 found that the launcher carries no driver of its
own (`src/notes/gemdrive-failure.md` §3).

## Tasks

- [ ] D15R compared with the GEMDOS of TOS 1.04 (the ROM on this Mac, C-03): which code matches,
      what PP changed, and H-08 confirmed or refuted.
- [ ] D15R's entry points and the data it shares with the launcher and the game, documented in its
      source and in `src/notes/disk-layer.md`. The entry points are its `TRAP #1` handler at
      `$C84A0` and the routines the relocated driver's XBRA slots point to (`$C19BE`, `$C1CA4`,
      `$C1B6E`).
- [ ] The interface the launcher uses on PP's resident driver: what it copies, the offsets it
      patches, the entries it calls, and so what a replacement driver would have to provide,
      shown with breakpoints on the reference run.
- [ ] Every call the game makes into the disk layer, from the hand-over to the level load, seen on
      the reference run.

## Acceptance

`src/notes/disk-layer.md` describes D15R and the driver interface well enough that either could be
replaced from it, with every point backed by a source line and a run.

## Notes
