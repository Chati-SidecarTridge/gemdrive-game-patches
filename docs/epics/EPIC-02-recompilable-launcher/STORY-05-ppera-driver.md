---
id: STORY-05
epic: EPIC-02
title: The PPera driver, annotated
status: todo
---

## Goal

The embedded PPera driver understood completely, since EPIC-03 replaces or feeds it: its
interface to the launcher and the game, how it is installed, and how it reaches the disk.

## Tasks

- [ ] Its entry points, calling conventions and the data it shares with the launcher and the
      game, documented in its source and in `src/notes/ppera-driver.md`.
- [ ] How it finds the disk, the partition and the files (sectors, FAT, directory, or GEMDOS),
      checked by breakpoints on the reference run.
- [ ] Every call the game makes into it during play, seen on the reference run.

## Acceptance

`src/notes/ppera-driver.md` describes the interface well enough that a replacement could be
written from it, every point backed by a source line and a run.

## Notes
