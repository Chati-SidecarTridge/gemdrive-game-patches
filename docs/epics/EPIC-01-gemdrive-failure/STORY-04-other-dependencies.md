---
id: STORY-04
epic: EPIC-01
title: Everything else GEMDRIVE lacks
status: done
---

## Goal

The full list of what the launcher and the game ask of the disk that GEMDRIVE mode does not give,
not just the first: the fix must cover all of it (iteration 2, D-14).

## Tasks

- [x] Past the first stop, with each known cause bypassed on a patched copy, the GEMDRIVE run
      pushed on until it reaches the first level or the next stop; each stop recorded.
- [x] The disk access during play (a level loaded, a level number entered as `README.TXT`
      describes) checked the same way.
- [x] The list recorded here: each dependency, where it is in the code, what GEMDRIVE answers
      instead, and the run that shows it.

## Acceptance

A patched copy that reaches play in GEMDRIVE mode, and the list of everything it had to bypass;
or, if none does, the stop that could not be passed and why.

## Notes

The patched copies here are probes for finding dependencies, not the fix (iteration 2).

**Done 2026-10-11**, on the second branch of the acceptance: no by-hand run reaches play. The
list is `src/notes/gemdrive-failure.md` §5; in short: (1) a resident, PPDRIVER-shaped driver with
the XBRA `PPHD` header, (2) failing that, a raw-readable PP boot sector, which still leaves D15R
uninitialised, (3) `Getbpb(2)` with PPDRIVER's BPB, (4) `Mediach(2)` = 0, (5) `Rwabs` on drive 2
serving the whole FAT volume with 1,024-byte sectors, (6) the fixed memory map, (7) `TRAP #1`
owned by D15R from the first read on.

- The stops, each answered by the debugger at run time on the pristine files (no binary
  patched): the driver gate → sector 0 → `Getbpb(2)` (TOS: 0) → `Rwabs` (TOS: -15) → D15R's
  error restore with a context the fallback path never saved (`$C8486`, `movea.l (a0)+,sp`
  → sp = 0 → bus error, Hatari halts). This last one is the stop that could not be passed: it
  is not a disk answer but the state D15R gets only from the primary path, with a real driver.
- Disk access during play: not observed. The reference itself stops after the first level's
  data is loaded (STORY-01's open issue), so what the game reads while playing (`GROUNDn`,
  `OBJECTSn`, further `LEVELnnn`, music) is known only from the file set, not from a run. It
  goes through the same D15R reads, which is dependency (5) either way.
- Serving every read from the image by hand (`serve_rwabs.py`, one run per read) answered the
  root and `LEMMINGS` directories before D15R's error path ended it; the mechanism works and can
  be reused once the primary path is reachable.
