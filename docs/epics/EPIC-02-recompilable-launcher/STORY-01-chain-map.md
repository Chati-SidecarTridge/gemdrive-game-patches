---
id: STORY-01
epic: EPIC-02
title: The launch chain mapped from runs
status: todo
---

## Goal

Which program loads which, where it is placed in memory, where it is entered, and what it leaves
resident, from the reference run, with a memory dump of every stage as it starts.

## Tasks

- [ ] From the reference run's traces and breakpoints: every file the launcher opens, by whom,
      where it lands, and where each stage is entered, starting from EPIC-01's addresses.
- [ ] A Hatari memory dump of every stage at its entry (harness debugger hook), SHA-256 recorded.
- [ ] The hand-over to the game: the address, and what the launcher left resident (vectors, system
      variables, D15R, the relocated driver, and the memory it reserved), set against GOS5's RAM
      map in `GAMEXdoc.html`.
- [ ] `D15R_F5.FIC`: the reference opens `D15R_H5.FIC` (EPIC-01). What the other file is, and what
      would make the launcher choose it.
- [ ] `GXUT260.PRG`: PP's documentation describes the Gamex utility as the program that resumes,
      saves and restores gamestates (`GAMEXdoc.html`). This is to be confirmed from a run on a copy
      of the disk setup (any write lands on the copy only, C-01), together with whether the launch
      depends on it. If it does not, it leaves this epic's scope, recorded here.

## Acceptance

The chain recorded here as a table (stage, file, load address, entry, dump SHA-256), each row
backed by a run folder.

## Notes
