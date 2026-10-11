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
      where it lands, and where each stage is entered.
- [ ] A Hatari memory dump of every stage at its entry (harness debugger hook), SHA-256 recorded.
- [ ] The hand-over to the game: the address, and what the launcher left resident (vectors,
      system variables, its driver, memory it reserved).
- [ ] `GXUT260.PRG`: its role, from a run on a copy of the disk setup (any write lands on the copy
      only, C-01), and whether the launch or the driver depends on it. If not, it leaves this
      epic's scope, recorded here.

## Acceptance

The chain recorded here as a table (stage, file, load address, entry, dump SHA-256), each row
backed by a run folder.

## Notes
