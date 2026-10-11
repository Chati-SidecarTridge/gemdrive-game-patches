---
id: STORY-01
epic: EPIC-03
title: The approach, chosen
status: todo
---

## Goal

A decision (`D-NN`) on how GEMDRIVE mode gets what the launcher and the driver need, taken by
Diego from the options with their costs.

## Tasks

- [ ] The candidate approaches, each set against EPIC-01's list of dependencies and EPIC-02's
      driver interface. Examples, to be confirmed by those epics: our launcher with the driver's
      disk access replaced by GEMDOS file calls; a resident replacement for the PPera driver that
      serves its interface from GEMDOS; a program run before the original launcher that makes the
      GEMDOS drive look like the disk the driver expects.
- [ ] For each approach: what changes, whether it would carry over to other PPera games without
      per-game work (for later, not tested now), what it costs in memory (the launcher's fixed addresses and the 1 MB minimum, C-04),
      and the risks.
- [ ] Diego's choice recorded as a decision in `DECISIONS.md`.

## Acceptance

The decision in `DECISIONS.md`, accepted by Diego, with the comparison it was taken from.

## Notes
