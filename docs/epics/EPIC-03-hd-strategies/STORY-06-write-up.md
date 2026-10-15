---
id: STORY-06
epic: EPIC-03
title: The write-up: how many ways, and the solutions proposed
status: done
---

## Goal

`src/notes/hd-strategies.md` answers how many ways there are, how many games use each, what each
needs, and how many games fall under each verdict; and it proposes, for every strategy with games
to fix, the solutions that would fix them, for Diego to choose from at STORY-08.

## Tasks

- [x] The note: the table of strategies (games, what they need, the verdicts' counts, evidence),
      every claim pointing at a run folder or a row of `migration.csv`.
- [x] The solutions proposed: for each strategy with games to fix, one or more ways to make them
      run from a GEMDOS drive (a resident layer, a changed launcher, a rebuilt file set…), each
      with the games it covers, what it costs (work, memory, risk), how it stays within C-02 in
      Hatari, and where the SidecarTridge's GEMDRIVE would differ (noted, not tested). Lemmings'
      strategy (GOS) is among them, from EPIC-01's dependencies and EPIC-02's disk layer.
- [x] `migration.csv`: for every "fix" row, the solution that covers it; for every "not feasible"
      row, the reason.
- [x] `ITERATIONS.md`: the proposed solutions as candidates for iteration 2, each with its number
      of games, ready for Diego's choice.

## Acceptance

From the note and `migration.csv`, a reader can tell for any game in the list its strategy and
its verdict, and for a "fix", the solution that would make it run.

## Notes

Done (2026-10-13). `src/notes/hd-strategies.md` holds the answers: twelve strategies, two ways to
the disk; **1,608 as it is, 212 fix, 1 not feasible, 10 unsure**; four solutions for the 212.
Diego settled five of the unsure games at the start (his second look at the PPDRIVER snapshots).

- **S1, GOS reads through the GEMDOS drive** (204 GOS4/GOS5 games, Lemmings first): the
  launchers' driver checks and GOS's GEMDOS entry patched so that GOS's file requests reach the
  machine's `TRAP #1` handler, as PP's HAGA file service does; Hatari's hook needs none of TOS's
  RAM for them (its source, `gemdos.c`). A proposal: the one solution not tried.
- **S2, a BPB for the GEMDOS drive** (4 Silmarils games): their `START.PRG` asks `Getbpb` on C:
  before every file; answered by a 22-byte routine the debugger put in, all four play or reach
  their title from the GEMDOS drive (trials).
- **S3, the fastload bit** (3 games): Hatari's GEMDOS drive clears a started program's free
  memory, where the caller's stack lay, before it rewrites the saved `Pexec`, and TOS ends the
  caller; with the started program's fastload bit set, all three run (trials). Aquanaut was one of
  the unsure games.
- **S4**: Rody and Mastico 4's `RUNME.TOS` for Rody and Mastico 2 (STORY-05's trial).
- 43 of the 204 GOS games already run from the GEMDOS drive through another download of PP's
  (`tools/survey/run_other.py`, `runs-other.tsv`), Lemmings' `LEMMSRD.ZIP` among them; the
  `solution` column names them.
- **Corrected on the way**: Weird Dreams' "sector reads on C:" were its own RAM disk on M: (as it
  is; `run_all.py` counts C: only); Maddog Williams needs `PABISYS.FIL` in `C:\`, where PP's ZIP
  puts it (as it is; `run_all.py` now puts what a download keeps beside the game's folder in the
  drive's root); Great Giana Sisters STE's HAGA downloads stream by sectors too: not feasible.
- `migration.csv`'s `solution` column comes from `src/survey/solutions.tsv` through `verdicts.py`.
  `ITERATIONS.md` lists S1–S4 for Diego's choice, and two new candidates: the 10 unsure games, and
  a report to Hatari about its `Pexec` (D-15: it would leave this Mac).
