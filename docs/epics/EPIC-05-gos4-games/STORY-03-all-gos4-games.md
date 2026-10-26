---
id: STORY-03
epic: EPIC-05
title: The 117 GOS4 games from the GEMDOS drive
status: done
---

## Goal

Every game of the `FIXGOS4` group, patched, is run from the GEMDOS drive with `run_all.py`'s
rules. The verdicts are updated, and each failure is listed with its cause.

## Tasks

- [x] The 117 games patched (copies under `tools/dev/builds/`) and run from the GEMDOS drive at the
      RAM of their STORY-05 run.
- [x] Each run looked at. A game that does not run is traced, and its cause is listed.
- [x] `migration.csv` updated through `verdicts.py`, with the evidence.

## Acceptance

Every game of the 117 has a run of its patched copy and a verdict, and the counts are recorded
here.

## Notes

### The runs (2026-10-16)

`src/probes/epic04/gos5_run.py <ZIP> --setup st-104 --disk gemdrive` for each of the 117 (it takes
`tools/build_gos4.py` for a GOS4 game): the card's folder from the download, its start program
built, EPIC-03's generic expectation (10 s, 30 s, the space bar, 45 s), five at a time, at the RAM of
the game's survey run: 111 at 1 MB, 5 at 2 MB, and F16 Falcon at 2 MB too (`--memsize 2`): its
launcher puts GOS at `$1C0100`, though its run and the card have it at 1 MB. Batches in
`tools/dev/builds/epic05/batch-*` (`games.txt`, one output per game, `summary.tsv`, contact sheets).

| batch | block | result |
|---|---|---|
| `batch-1814` | STORY-02's | 105 at a title, a menu or in play; 8 halted (Amazing Spiderman, Bobo, Chariots of Wrath, Death Bringer, Erik, Gravity, Phoenix, Time): a program `Pexec`'d from the forwarder returned through a context the program had overwritten; 2 white (Starblade, Windsurf Willy): `Getbpb(2)` answered "none", forever; Asterix and Winter Games read drive A |
| `rerun-1849`, `rerun2-1857` | `Pexec` 0 handed to GOS; floppies to GOS, a BPB for C, `Dfree` | the 8 and the 2 run; Gravity's `Mediach(0)` loop and Chariots' fault gone (STORY-02, "Changed after") |
| `batch-1900` | the same | 113 clean; Battle Probe opens `""`, which Hatari passes to the ROM's GEMDOS (`Getbpb(2)`, one `Rwabs` on C); Bobo one fault (a bus error at `$1E592`, not seen in its 3 other runs nor in the reference) |
| `batch-ref-1937` | the same, from PPDRIVER | PP's path: all 117 read drive C through PPDRIVER, no fault (D-17 kept) |
| `batch-2008` | empty and endless names answered by the forwarder | 115 clean; Asterix and Winter Games read drive A as their originals do (`rerun2-1857`: the same `Rwabs` on A at the launcher's PC, the same `Floprd`); Slightly Magic black: it sets `Dsetpath("")` before each file, which the forwarder answered -33 |
| `final-2038` | `Dsetpath("")` answered 0, as GOS | Slightly Magic plays (11 files), Battle Probe clean (21 files), Bobo 21 files; Operation Stealth on STE TOS 1.62 and 2.06, 74 files; `gos4_selftest.py` PASS on the three setups |

Each 45 s screen was looked at on contact sheets (`batch-1814`), the ten that failed again after
each fix (`rerun-1849/sheet.png`, `final-2038/fixed6.png`), and the final batch against the
reference's screen at the same moment (`compare4`: most differ only by timing, a GEMDOS drive
loading at once where PPDRIVER reads sectors; the six that differ wholly are each at another point
of their attract loop, `compare-top6.png`; three nearly blank: Lode Runner between levels, Robocop
in its intro, Slightly Magic, above). The games that stop at a question stop at the same one from
PPDRIVER (`prompts.png`): King's Quest I and III, Space Quest I ("If you have made a backup copy of
disk 1…"), Manhunter and Manhunter 2 (a question from the manual), Emmanuelle (the colour chart),
Asterix ("Do you wish to start a saved game?"), Winter Games ("Insert disk 2 in drive B"), Battle
Tech ("Do you wish to use two drives?").

**Result**: 117 of 117 run from Hatari's GEMDOS drive with their start program built, on ST TOS
1.04, to the screen their original reaches from PPDRIVER; none reads drive C by sectors. Asterix
and Winter Games also read drive A, as their originals do.

**The verdicts** (`verdicts.py`): the 117 stay `fix`, each with its finding (`src/survey/findings.tsv`:
"runs from the GEMDOS drive with its START.TOS built for it (tools/build_gos4.py), in Hatari on an
ST with TOS 1.04", and what more: F16 Falcon at 2 MB, Asterix and Winter Games on drive A, Operation
Stealth on the STEs, Guild of Thieves' save) and S1 "built by tools/build_gos4.py" as the solution
(`solutions.tsv`); `src/survey/ports.tsv` has the 117 with their run and picture (45 s, or 30 s for
Lode Runner and Robocop, whose 45 s screen is nearly blank, 10 s for Magic Fly, black from 30 s as
its original). The totals stay 1,608 as it is, 212 fix, 1 not feasible, 10 unsure.

**Done 2026-10-16.**

