---
id: STORY-02
epic: EPIC-06
title: S3: the fastload bit (Spy vs Spy 2 first)
status: todo
---

## Goal

The three games whose start program gave its stack back run from the GEMDOS drive, with the
fastload bit set in the program each one starts.

## Tasks

- [ ] A tool sets bit 0 of byte 25 of the header in a user's copy of `SPY2.BOY`, `HARRIER.TOS` and
      `AQUANAUT.EXE`, after checking that the file is the expected program. Run twice, it
      changes nothing.
- [ ] Spy vs Spy 2, Strike Force Harrier and Aquanaut from the GEMDOS drive on the three setups,
      played past their first loads.
- [ ] The same, patched, from PPDRIVER: the bit changes nothing there.

## Acceptance

The three games run from the GEMDOS drive on the three setups, patched by the tool.

## Notes
