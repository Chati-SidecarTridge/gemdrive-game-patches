---
id: STORY-02
epic: EPIC-05
title: Operation Stealth through the GEMDOS drive
status: todo
---

## Goal

EPIC-04's builds by signature, extended to GOS4's D15R build, make Operation Stealth run from the GEMDOS
drive on the three setups.

## Tasks

- [ ] The `trap1` patch for `D15R_HH4`, handing on STORY-01's functions, found by signature.
- [ ] EPIC-04's launcher patch on GOS4's `START.TOS`.
- [ ] Operation Stealth from the GEMDOS drive on ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06:
      played past several file loads, a saved game written and read back if it has one, and no
      `Rwabs` on C:.
- [ ] The same from PPDRIVER, unpatched, as the reference.

## Acceptance

Operation Stealth plays from the GEMDOS drive on the three setups, with its traces.

## Notes
