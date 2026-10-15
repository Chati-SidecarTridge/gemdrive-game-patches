---
id: STORY-01
epic: EPIC-05
title: What GOS4 games ask of GOS's GEMDOS during play
status: todo
---

## Goal

The GEMDOS functions GOS4 games call during play, with their parameters, so that the patch hands
on every one a game needs.

## Tasks

- [ ] A probe: a breakpoint on GOS4's `trap1` in `D15R_HH4` that prints the function and its
      parameters, on the PPDRIVER image, where the games run.
- [ ] Operation Stealth and a sample of other GOS4 games (one per launcher variant, by
      `classify.py`'s signatures), each played past its first file load.
- [ ] The list of functions used, and how each one differs from the GOS5 file requests EPIC-04
      handles: paths, DTA, handles, `Fsfirst`, writes.

## Acceptance

The table of functions per game, from traces, and what the patch must hand on.

## Notes
