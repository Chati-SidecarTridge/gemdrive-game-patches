---
id: STORY-03
epic: EPIC-01
title: The embedded driver, confirmed or refuted
status: todo
---

## Goal

A verdict on Diego's guess (H-07): is the PPera driver embedded in the launcher what fails in
GEMDRIVE mode?

## Tasks

- [ ] Where the launcher carries a driver of its own: the code, its load address and how it is
      installed (vectors, system variables), seen in memory on the reference run.
- [ ] Whether that driver is PPDRIVER itself, the one that booted the reference: its code
      compared with the driver in `../atari-hd/assets/pp_boot_blob.bin` (LBA 2 to 14), and with
      what PPDRIVER leaves resident before the launcher starts. Copied from memory, carried in
      the launcher's own files, or different: recorded here.
- [ ] Whether the failing path of STORY-02 runs through that driver, shown with breakpoints.
- [ ] An experiment on a patched copy (never `LEMMINGS/`): with the driver's disk access bypassed
      or answered by hand, the GEMDRIVE run gets further; reverting brings the stop back.
- [ ] H-03 and H-07 confirmed or refuted, with the evidence.

## Acceptance

H-07's verdict, backed by the breakpoint runs and the before/after experiment.

## Notes
