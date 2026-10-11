---
id: STORY-05
epic: EPIC-02
title: The disk layer: D15R and the driver it uses, annotated
status: done
---

## Goal

The disk layer the launcher installs, understood completely, since a solution (iteration 2) replaces or feeds it.
That means D15R (PP's GOS, if H-08 holds), the relocated copy of PP's resident driver, and how
the game reaches its files through them. EPIC-01 found that the launcher carries no driver of its
own (`src/notes/gemdrive-failure.md` §3).

## Tasks

- [x] D15R compared with the GEMDOS of TOS 1.04 (the ROM on this Mac, C-03): which code matches,
      what PP changed, and H-08 confirmed or refuted.
- [x] D15R's entry points and the data it shares with the launcher and the game, documented in its
      source and in `src/notes/disk-layer.md`. The entry points are its `TRAP #1` handler at
      `$C84A0` and the routines the relocated driver's XBRA slots point to (`$C19BE`, `$C1CA4`,
      `$C1B6E`).
- [x] The interface the launcher uses on PP's resident driver: what it copies, the offsets it
      patches, the entries it calls, and so what a replacement driver would have to provide,
      shown with breakpoints on the reference run.
- [x] Every call the game makes into the disk layer, from the hand-over to the level load, seen on
      the reference run.

## Acceptance

`src/notes/disk-layer.md` describes D15R and the driver interface well enough that either could be
replaced from it, with every point backed by a source line and a run.

## Notes

**Done 2026-10-11.** `src/notes/disk-layer.md`.

- D15R against TOS 1.04 UK (`src/probes/epic02/d15r_vs_tos.py`): 59.7% of its bytes are the ROM's,
  10.7% the same addresses relocated (ROM to D15R, and TOS's RAM to its image at `$D0528`), the
  rest PP's code, the RAM image and PP's edits. D15R holds TOS 1.04's GEMDOS, BIOS, XBIOS, floppy
  driver, start-up code and data, behind PP's entries and his `TRAP #1` entry. **H-08 confirmed,
  and wider** (`ITERATIONS.md`).
- Its entry points (the table at `$C0100`: `swap_low_ram`, `tos_paths`, `file_io`, `init`,
  `file_io_2`), `trap1`, the floppy routines the driver copy chains to (`flop_getbpb`, `flop_rw`,
  `flop_mediach`), and the shared data (`io_params` at `$C0730`, the RAM image) are named and
  commented in `src/d15r/d15r_h5.s` and described in the note (§2).
- What the launcher asks of PP's resident driver, six points, from `reuse_pp_driver` and
  `set_buffers` and EPIC-01's dumps (§3).
- Every call from the hand-over to the level load (`src/probes/epic02/disk_calls_probe.py`, run
  `20261011-182600-st-104-ppdriver-disk-calls`, PASS): 3 to PP's loader, 5 to `file_io` (IntroPar,
  CODE in two parts, leveldat, level020), 16 `hdv_rw` and 139 `hdv_mediach` on the driver copy,
  no `file_io_2`, no `hdv_bpb`. The game reads its level files through its own copy of the loader
  at `$E892`, not `$85000` (§4).
