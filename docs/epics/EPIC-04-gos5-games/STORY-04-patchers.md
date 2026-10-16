---
id: STORY-04
epic: EPIC-04
title: The builds by signature: each GOS5 game's start file for a GEMDOS drive
status: done
---

## Goal

STORY-01's and STORY-02's change, made by a tool that finds its place by signature (as
`classify.py` finds the launchers), on any GOS5 game's packed `START.TOS`. It writes each game's
start file for a GEMDOS drive into `tools/dev/builds/`, with its original's signature, never into a
user's copy or this repository (D-11). GOS's code needs no change (STORY-01), so only the launcher
is changed. Installing the builds on a user's copy is EPIC-09's (D-17, D-18).

## Tasks

- [x] The launcher's checks: found in PP's packed `START.TOS` (`2278 0472 0CA9 5050 4844 FFF8`),
      with `gd_start`, `gd_forward`, `md_move_stack` and `gd_quiet` added. The file is unpacked
      and packed again with `tools/unpack.py` and `tools/pack.py`, and the packed result is
      accepted by the launcher.
- [x] Each ST/STE build of GOS5 (`D15R_5H`, `D15R_H5`, `D15R_H15`): the image of the system
      variables where the launcher finds it (`($C07E6) + $C0800`), its `TRAP #1` slot at `$84`,
      `$B7180` free, and `file_io`'s first bytes where `gd_quiet` expects them. Checked for every
      build, with the launcher variants that load each.
- [x] One command builds a game's start file from its original, with the original's SHA-256 and
      the result's. Run twice, it gives the same bytes; on an original it does not know, it says
      so and writes nothing.
- [x] On Lemmings, the build equals `tools/build_gemdrive.sh`'s byte for byte, or the differences
      are explained.

## Acceptance

The tool builds Lemmings and one game of each GOS5 build, and each reaches its title from the
GEMDOS drive on ST TOS 1.04.

## Notes

- Retitled on 2026-10-15 (D-17): it was "The patchers, by signature, for a user's copy". Patching a
  user's copy in place moved to EPIC-09.

### The launchers (2026-10-15)

`src/probes/epic04/gos5_survey.py` on the card's 87 `FIXGOS5` games: 87 different launcher
programs (each has the game's own code), none with a data section, nearly all with a 110,662-byte
BSS. GOS's `file_io` starts with `lea (sr_save,pc),a0 / move.w sr,(a0)` in every build: `D15R_H5` at
`$C0170`, `D15R_5H` at `$C014E` (entry table `0010 0034 004E 01A2 0222`, the SR kept at `$C0654`).
Three families, by the code after the `PPHD` check:

| family | games | after the check | GOS | PP's driver copy |
|---|---|---|---|---|
| A (Lemmings) | 30 | `bne.w` to PP's fallback; with the driver, `reuse_pp_driver`, `set_buffers`, `start_d15r` | `$C0100` (28), `$1C0100` (`D15R_H15`, 2 MB: No Second Prize, Street Fighter II) | GOS - `$8F80` |
| B | 46 | `bne.s` (or `.w`); with the driver, a call to GOS's entry `+12`, then `bra.w` to GOS's start | `$C0100` | none |
| B' | 11 | the same | `$1A0100` (the card's 2 MB games) | none |

Indigo's `START.TOS` is the launcher program itself, unpacked (family B).

**`tools/build_gos5.py`** puts `src/gemdrive/gos5_patch.s` (860 bytes, position-independent) at the
front of the launcher's text: the first instruction branches over it, every relocation moves by its
size (the text moves as a whole, so no PC-relative reference changes; every launcher has one
`pea (d16,pc)` into its BSS, which a block at the end would have broken), and the 14 or 16 bytes of
the `PPHD` check become a `bra.w` to the block's `gd_check`. The block makes the check itself: PP's
driver, PP's path (D-17); a cartridge's `TRAP #1` on a 68000 (`_longframe`, instead of Lemmings'
`is_falcon`, whose place differs per launcher) and `file_io` as `gd_quiet` knows it: the GEMDOS
drive's setup, then GOS's start; anything else, PP's fallback. `file_io` and its SR's place are
found at run time from GOS's entry table. The block's branches and parameters come from the
launcher, by signature (the check, the image pointer `movea.l (img).l,a6 / adda.l #img+$1A,a6`, GOS's
start in each family); the forwarder goes where family A copies PP's driver, GOS - `$8F80`, for
family B too, with GEMDRIVE's stack `$80` below it. The result is packed with the original's own
stub; `tools/pack.py` raises the stub's top when a longer program needs it.

- All 87 recognised (`--info`); 86 packed, Indigo's written back unpacked.
- Built twice, the same bytes; an original it does not know: an error, nothing written.
- Lemmings by the tool: `gemdrive-first-level.exp` PASS 12/12 on ST TOS 1.04, STE TOS 1.62 (4 MB)
  and STE TOS 2.06 (`…-gos5-lem`), and from PPDRIVER PP's path as before, 13/13. Against
  `tools/build_gemdrive.sh`'s build the bytes differ: the change sits at the front, not before
  `no_pp_driver`, and finds `file_io` at run time; the behaviour is the same, by the same test.
- From the GEMDOS drive on ST TOS 1.04 (`src/probes/epic04/gos5_run.py`, EPIC-03's generic
  expectation): Alien Storm (B) reaches its title, GOS reading `CHARS16.PC1` … `SELECT.PC1` by name;
  Knightmare (B', 2 MB) its menu, `KM1`, `KM2`, `KM8`; no `Rwabs`, no crash.
- `tools/dev/make_disks.sh` now takes file names with spaces (Knightmare's download has some).
- **On Diego's STE (TOS 1.62, 4 MB) from the Multidevice's GEMDRIVE (2026-10-15)**: Alien Storm with
  the tool's `START.TOS` (`f23dc6db…`, on his card in `FIXGOS5\1MB\ALI-ZOU\ALIENSTO\`): "it works
  too". The first game besides Lemmings, and the first of family B, on the hardware.

### All 87 (2026-10-15)

`src/probes/epic04/gos5_run.py` for each game (the card's folder copied, its start program rebuilt,
EPIC-03's generic expectation on ST TOS 1.04 at the card's RAM, five at a time); the screenshots
looked over on contact sheets. Four rounds, each finding a difference between the launchers or
GOS builds, fixed in `gos5_patch.s` or the tool:

- **The older `D15R_H5` builds** (`G52`, `G55`, `G552`: 22 games) start `file_io` with
  `move.l a0,-(sp)` before the `lea`; `gd_check` refused them and PP's fallback quit to the desktop.
  `gd_quiet` now does what the `jmp` replaced in both shapes, keeps the caller's SR itself and goes
  on after `move.w sr,(a0)`: some old games call the loader with interrupts let in, and the older
  builds, saving the SR after `gd_quiet` had masked it, gave them back no VBL (Muzzy, Matrix
  Marauders, Shadow Warriors, Spellbound Dizzy: black). Giving the SR back before `file_io` instead
  let a VBL that came during the wait run inside the loader (Popeye 2, Warp): interrupts stay
  masked until `file_io` restores them.
- **Family A's GOS start** is where PP's two paths meet: the `bra.w` that ends `set_buffers`, not
  `start_d15r` (Jetsons-like launchers copy a loader to `$3F400` on the way).
- **A dot that ends a name part** goes, as GEMDOS reads it: Video Kid's `RESIDENT.` is `FILES\RESIDENT`.
- `make_disks.sh` takes file names with spaces; the probe takes each game's own start program
  (Chaos Engine's `START2M.TOS`).

Result (`tools/dev/builds/gos5/batch-2205/summary.tsv`, the runs in `tools/dev/logs/*-gos5-*`):

- **78 reach their title, menu or play**, every GOS5 build among them (`GH5R4` Alien Storm, `G558`
  Lemmings, `G555` Chase H.Q., `G552` Clever & Smart, `G55` Matrix Marauders, `G52` Chaos Engine,
  `G158` Dragon Breed, `G157` Street Fighter II).
- **9 do what they do from PPDRIVER with PP's own path** (each run that way too): Fire and Forget II,
  Venus the Flytrap and Heimdall stay black at 10, 30 and 45 s; Muzzy shows its game, then the CPU
  halts; Jetsons, Magic Boy, Prison and Popeye 2 crash; Forgotten Worlds' download lacks the
  `D15R_5H.FIC` its launcher asks for (beside it or in `C:\GAMEX\`).
- The latest block is 918 bytes; Lemmings and Alien Storm, built by the earlier block, were played
  on Diego's STE.

