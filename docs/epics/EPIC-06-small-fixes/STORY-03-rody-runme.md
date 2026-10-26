---
id: STORY-03
epic: EPIC-06
title: S4: Rody and Mastico 2's RUNME.TOS
status: done
---

## Goal

Rody and Mastico 2 runs from the GEMDOS drive with Rody and Mastico 4's `RUNME.TOS`, taken from
the user's own `RODYM4.ZIP`.

## Tasks

- [x] A tool, or a line of instructions, copies `RUNME.TOS` from a user's `RODYM4.ZIP` into Rody
      and Mastico 2's folder, after checking that both downloads are the expected ones.
- [x] Rody and Mastico 2 from the GEMDOS drive on the three setups: its title, its chapter menu,
      and a chapter started.

## Acceptance

Rody and Mastico 2 plays a chapter from the GEMDOS drive on the three setups.

## Notes

**2026-10-26.** `tools/rody2_runme.py <RODYM4 folder> <RODYM2 folder>` checks Rody and Mastico 4's
`RUNME.TOS` and Rody and Mastico 2's `HAGE` and `FILES\R.ST` by SHA-256, and copies the
`RUNME.TOS`; run again it leaves it (the same file), and it refuses Rody and Mastico 5's folder for
either side. Rody and Mastico 2's `HAGE` is byte for byte the one of parts 4 and 5, which is why
part 4's start program fits. The probe `fix_run.py 41 --rody2` (outputs in
`tools/dev/builds/epic06/runs-rody/`): on ST 1.04, STE 1.62 and STE 2.06, `RUNME.TOS` starts, 11
files opened, HAGE reads the floppy image (48 floppy calls), no fault, the title and then the
chapter menu, the same screen on the three.

A chapter is not started in Hatari. The harness moves the pointer with TOS's Alt and arrow keys
(`fix_run.py --steps`), and a held Alt+Insert or Hatari's `doubleclick` on a chapter's picture
moves the menu's red marker to it, but no click, double click, right click, or click on the book
afterwards starts the chapter; Rody and Mastico 4, which runs as it is, does the same with the same
steps (`20261026-122818-st-104-gemdrive-fix-rody-and-mastico-4-none`). So the chapter is left to
the checkpoint on Diego's machine, with a real mouse; the task stays open until then.

2026-10-26, Diego's STE with the Multidevice: the chapter menu ignores the mouse until its music has
finished, then a chapter starts. Hatari's clicks came during the music.
