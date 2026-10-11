---
id: STORY-05
epic: EPIC-03
title: The write-up: how many ways, and a generic way for each
status: todo
---

## Goal

`src/notes/hd-strategies.md` answers how many ways there are, how many games use each, what each
needs, and which work in GEMDRIVE mode as they are. For each strategy that does not, it sketches a
generic way to adapt it, and `migration.csv` names that way for every game that needs adapting.

## Tasks

- [ ] The note: the table of strategies (games, needs, works as it is in GEMDRIVE mode, evidence),
      with every claim pointing at a run folder or a row of `migration.csv`.
- [ ] For each strategy that fails: one or more generic ways to adapt it for a GEMDOS drive, each
      with its cost, the games it would cover, and how it stays within C-02 in Hatari. Where the
      SidecarTridge's GEMDRIVE would differ, that is noted, but not tested.
- [ ] `migration.csv`'s adaptation column: for every game that does not work as it is, the generic
      way that would adapt it, or "none yet" with the reason.
- [ ] `ITERATIONS.md`: the generic ways added as candidates, each with its number of games, and
      where Lemmings' fix (EPIC-04) sits among them.

## Acceptance

From the note and `migration.csv`, a reader can tell for any game in the list its strategy,
whether it works from a GEMDOS drive as it is, and if not, how it would be adapted.

## Notes
