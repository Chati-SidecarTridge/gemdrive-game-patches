---
id: STORY-03
epic: EPIC-04
title: Lemmings plays from the GEMDOS drive
status: todo
---

## Goal

A scripted play session of Lemmings from the GEMDOS drive on the three setups, with every file it
opens found in the trace. This is what was the Lemmings fix's acceptance (D-14, kept in git at
`7fcff84`).

## Tasks

- [ ] The session: a level played to its end, then the next one, a level of each section entered
      by its code, and the music changing. An expectation file for the harness.
- [ ] From the GEMDOS drive on ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06: every file opened is in
      Hatari's trace, with none missing and no `Rwabs` on C:.
- [ ] The same session from PPDRIVER, as the reference.
- [ ] Gamex's state save (`file_io` with `"Wr"`), if Lemmings uses one, written and read back
      through the GEMDOS drive.

## Acceptance

The session passes on the three setups from the GEMDOS drive and from PPDRIVER, with its
screenshots and traces.

## Notes
