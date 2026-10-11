---
id: STORY-06
epic: EPIC-03
title: The write-up: how many ways, and the solutions proposed
status: todo
---

## Goal

`src/notes/hd-strategies.md` answers how many ways there are, how many games use each, what each
needs, and how many games fall under each verdict; and it proposes, for every strategy with games
to fix, the solutions that would fix them, for Diego to choose from at STORY-08.

## Tasks

- [ ] The note: the table of strategies (games, what they need, the verdicts' counts, evidence),
      every claim pointing at a run folder or a row of `migration.csv`.
- [ ] The solutions proposed: for each strategy with games to fix, one or more ways to make them
      run from a GEMDOS drive (a resident layer, a changed launcher, a rebuilt file set…), each
      with the games it covers, what it costs (work, memory, risk), how it stays within C-02 in
      Hatari, and where the SidecarTridge's GEMDRIVE would differ (noted, not tested). Lemmings'
      strategy (GOS) is among them, from EPIC-01's dependencies and EPIC-02's disk layer.
- [ ] `migration.csv`: for every "fix" row, the solution that covers it; for every "not feasible"
      row, the reason.
- [ ] `ITERATIONS.md`: the proposed solutions as candidates for iteration 2, each with its number
      of games, ready for Diego's choice.

## Acceptance

From the note and `migration.csv`, a reader can tell for any game in the list its strategy and
its verdict, and for a "fix", the solution that would make it run.

## Notes
