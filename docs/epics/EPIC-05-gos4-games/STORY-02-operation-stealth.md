---
id: STORY-02
epic: EPIC-05
title: Operation Stealth through the GEMDOS drive
status: done
---

## Goal

EPIC-04's builds by signature, extended to GOS4's D15R build, make Operation Stealth run from the GEMDOS
drive on the three setups.

## Tasks

- [x] The `trap1` patch for `D15R_HH4`, handing on STORY-01's functions, found by signature.
- [x] EPIC-04's launcher patch on GOS4's `START.TOS`.
- [x] Operation Stealth from the GEMDOS drive on ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06:
      played past several file loads, a saved game written and read back if it has one, and no
      `Rwabs` on C:.
- [x] The same from PPDRIVER, unpatched, as the reference.

## Acceptance

Operation Stealth plays from the GEMDOS drive on the three setups, with its traces.

## Notes

### The change (2026-10-16)

`src/gemdrive/gos4_patch.s` (1,794 bytes), put at the front of the launcher's text by
`tools/build_gos4.py` as `build_gos5.py` does with GOS5's block (its relocation, packing and
info-screen code reused: `patch_block`, `build` and `info_screen` now take their parameters; the 87
GOS5 builds came out byte for byte the same as `sdcard-1635`'s).

- **The launchers** (`build_gos4.py --info` on the 117): one `PPHD` check, then PP's path, which
  ends with a `bra` to code that copies a Gamex routine to low RAM and jumps into GOS
  (`jmp $C0100`); in PP's path, `lea table,a6 / move.l a6,pointer` gives the driver table GOS
  takes: `$C00E0` at `$C0030` in 110, `$1C00E0` at `$1C0030` in the 6 2 MB ones, `$C0098` at `$5FA`
  in Defender 2's. None of the 19 shapes of the code after the join uses PP's path's registers.
- **GOS4** is TOS 1.04 started from RAM: it clears low RAM from `$980`, sets the vectors itself
  (`move.l #trap1,$84.w`, one in each of the five builds), copies the driver table (`hdv_bpb`,
  `hdv_rw`, `hdv_mediach`, `_drvbits`, the two `_bufl`), `Dsetdrv`, `Dsetpath`, then
  `Pexec(0, <program>)`, and boots itself again when it returns (`D15R_HH4` `4e53` at
  `$C03AE`-`$C046A`).
- **gd_check**: without PPDRIVER, with a cartridge's `TRAP #1` on a 68000, it finds GOS's
  `move.l #trap1,$84.w` in RAM (the launcher has loaded GOS before its check) and points that long
  at the forwarder copied to `$B7180`; writes the driver table as PP's path does, with no driver
  (`hdv_*` fail, the machine's `_drvbits`, two lists of two free buffers at `$AF100`); moves the
  Multidevice's stack as EPIC-04's; then joins PP's path.
- **The forwarder**: STORY-01's functions to the machine, each as a copy of the call on its own
  stack (the caller's parameters untouched), every register but `d0` given back as GEMDOS does
  (without it, the loader's `a2` was lost: `OSTL`'s fixups read to `$36FC`, a halt on the three
  setups). **Handles**: the machine's handle of each file opened is kept in a table and the call
  returns GOS's number, 6 and up, the lowest free. Without it Operation Stealth halted on the STEs:
  PP's adaptation code at `$6A00` puts back a 1,088-byte snapshot of the game's variables in which
  the open resource file is handle 6, so the game closed 6, which Hatari passed to the ROM's GEMDOS
  (on GOS4's RAM: a halt on TOS 1.62 and 2.06, unnoticed on 1.04, whose RAM layout is GOS4's), and
  left Hatari's 64 open (`…-174829-…-fclose6`, `…-175025-…-watch-23616`). **`Pexec` 0 and 3**: the
  program loaded through the machine into GOS's `Pexec(5)` basepage, relocated, its BSS (and the TPA
  unless fastload) cleared, then GOS's `Pexec(6)`. **`Fsfirst`, `Fsnext`**: GOS's current process put
  in the ROM's `p_run` for the call where that is not GOS's (`$5662` on TOS 1.62, `$5CD4` on 2.06;
  1.04's `$5622` is GOS's), as Hatari takes the DTA from there.

### Runs

| what | ST TOS 1.04 | STE TOS 1.62 | STE TOS 2.06 |
|---|---|---|---|
| Operation Stealth, built, GEMDOS drive (`gos5_run.py`) | `…-175627`: title, the first scene, 74 files by name, handles 64 and 65 only, no `Rwabs`, no fault | `…-175630`: the same | `…-175632`: the same |
| the original, PPDRIVER (`gos4_calls.py`) | `…-171512`: the same scene, 348 `Rwabs` | `…-174424` | `…-174427` |
| built, PPDRIVER: PP's path | `…-174422`: 348 `Rwabs`, as the original | | |
| `gos4_selftest.py` (Herman's folder, `HERL` replaced) | `…-180307`: PASS | `…-180453`: PASS | `…-180453`: PASS |

`src/probes/epic05/gos4_selftest.s` runs as the game's program under GOS4: Fcreate (6), Fwrite,
Fclose, Fopen (6), Fseek and Fread (the bytes back), a second Fcreate while 6 is open (7),
Fsetdta and Fsfirst (16 bytes, its name), Fdelete and Fsfirst (nothing), Fopen of `TEST.OUTPUT`
(cut to `TEST.OUT`); it is itself loaded by the forwarder (relocated, its BSS cleared). On the host,
each run's drive holds `RESULT.OUT` `PASS` and `TEST.OUT` `WRITTEN BY GOS4!`, `TEST2.OUT` gone.

Gamex's F9 leaves the game for the desktop from the GEMDOS drive (`…-175920-…-gamex-f9`).
Operation Stealth's own save needs its pointer moved in its interactive part, which Hatari's
control socket cannot do (only buttons and keys); its intro takes F10 and the arrow keys as
"next line" (`…-180037-…-opsteal-menu`).

**A game's save, written and read back** (Guild of Thieves, GOS4, whose save is typed: `save`, a
file name, `y`; `…-181212-st-104-gemdrive-guild-save-restore`): `Fcreate("game1")`,
`Fwrite(64, 12941)`, the 12,941-byte `game1` on the host's drive; then `restore`: `Fopen("game1")`,
`Fread(64, 12941)`, and the game goes on ("In the Boat"). Operation Stealth's own save is the one
not made: it needs the pointer moved, which Hatari's control socket cannot do in this game.

**Done 2026-10-16**: the patch built by signature for the 117 launchers and the five GOS4 builds;
Operation Stealth from the GEMDOS drive on the three setups as from PPDRIVER; the forwarder's file
calls, its loader and a game's save shown.

