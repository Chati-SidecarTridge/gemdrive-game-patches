---
id: STORY-02
epic: EPIC-01
title: The GEMDRIVE runs, and where they part from the reference
status: todo
---

## Goal

The same pristine launcher in GEMDRIVE mode on every setup: where it stops, what is on screen, and
the first disk call or reply that differs from the reference.

## Tasks

- [ ] Each setup run in GEMDRIVE mode with the reference's milestones; the table recorded here:
      setup, last milestone, screenshot, wall time.
- [ ] For each setup, the first difference from the reference's disk calls, narrowed with
      breakpoints to the instruction that takes the other path and the value that made it.
- [ ] How Hatari's GEMDRIVE mode answers the calls that differ (`Rwabs`, `DMAread`, the ACSI
      registers, the driver vectors), read in `../hatari`'s sources and seen in the run.
- [ ] H-04 and H-06 confirmed or refuted, with the trace lines.

## Acceptance

For every setup, the instruction address where the GEMDRIVE run parts from the reference and
the input that differs, each backed by a run folder.

## Notes
