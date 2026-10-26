---
id: STORY-01
epic: EPIC-06
title: S2: a BPB for the GEMDOS drive (Crystals of Arborea first)
status: done
---

## Goal

A resident program, run from `C:\AUTO\`, makes the four Silmarils games run from the GEMDOS drive.

## Tasks

- [x] The program, in vasm source (D-05). It hooks `hdv_bpb` with XBRA. For the GEMDOS drive's
      number it returns an 18-byte BPB, and for any other drive it chains to the routine before
      it, as the trial's 22-byte routine did (`solutions.md` §3.2). It stays resident in
      about 100 bytes.
- [x] Crystals of Arborea from the GEMDOS drive with the program in `C:\AUTO\`, on the three
      setups: it plays, with no `Rwabs` on C: and its files opened by name.
- [x] Targhan, Robinsons Requiem and Storm Master, the same.
- [x] A game that does not need the program (a HAGA game) still runs with the program installed.

## Acceptance

The four games run from the GEMDOS drive with the program, on the three setups.

## Notes

**2026-10-26.** `src/gemdrive/gdbpb.s`, assembled by `tools/dev/asm.sh --tos` into `GDBPB.PRG`
(298 bytes; 82 resident with the XBRA header `GDBP`, Ptermres 338). It asks the routine before it
first and gives its BPB (PPDRIVER's partition's, from the trial) only when that one has none for a
drive from C: up that `_drvbits` holds, so the GEMDOS drive's letter does not matter (Hatari's C:,
the Multidevice's own); a second run finds `GDBP` in the chain and only prints. The probe
`src/probes/epic06/fix_run.py <row> --bpb` (first written as `bpb_run.py`) lays the drive out as `run_all.py` does, at the survey run's
RAM, with the program in `C:\AUTO\` (without `--bpb`: not; `--keys`: the keys to press). Outputs in
`tools/dev/builds/epic06/runs-1156/`:

| game (row) | keys | each of ST 1.04, STE 1.62, STE 2.06 |
|---|---|---|
| Crystals of Arborea (1698) | 2 at the compilation's menu | 36 `Getbpb(C:)` answered, 39 files opened, the game screen |
| Targhan (1699) | 1 | 49, 52 files, in play |
| Robinsons Requiem (1774) | run_all's | 4, 4 files, its language choice |
| Storm Master (1808) | run_all's | 23, 26 files, its title |
| Stormlord (478, HAGA, no BPB needed) | run_all's, 4 MB | no `Getbpb(C:)`, 4 files, in play as in its survey run |

No `Rwabs` on C:, no fault. Without the program (Arborea, ST 1.04): 6,359,547 `Getbpb(C:)`,
nothing opened. Stormlord at 1 MB faults with and without the program (a negative `Fseek` on `SL2`,
then address errors in TOS): `run_all.py` had moved it to 4 MB, and the probe now takes the survey
run's RAM.
