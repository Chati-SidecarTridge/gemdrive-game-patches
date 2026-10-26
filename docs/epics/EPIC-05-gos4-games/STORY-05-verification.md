---
id: STORY-05
epic: EPIC-05
title: Verification (Diego's checkpoint)
status: done
---

## Goal

Diego agrees that the GOS4 games run from a GEMDOS drive, as seen in Hatari and on his
Multidevice.

## Setups

- Hatari: ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06, in GEMDRIVE mode and from PPDRIVER.
- Diego's machines with the Multidevice's GEMDRIVE, from the card, power-cycled between games.

## Tasks

- [x] Claude runs Operation Stealth and a sample of GOS4 games on the three setups, from both
      disks.
- [x] Diego tests the patched games from the card. A game that disagrees with Hatari is listed
      here.
- [x] Diego agrees, or the stories to reopen are listed here.

## Acceptance

Diego's agreement, recorded with the date.

## Notes

**Claude's runs, 2026-10-16** (`tools/dev/builds/epic05/checkpoint-2057/`: one output per run, the
contact sheet `sheet.png`). `src/probes/epic04/gos5_run.py` with each game's build, at its RAM, on
ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06, from the GEMDOS drive and from PPDRIVER: a game of each
GOS4 build and launcher shape, and the two the batches needed fixes for.

| game | why | GEMDOS drive (each setup) | PPDRIVER: PP's path |
|---|---|---|---|
| Operation Stealth | `4e53` | 74 files by name, the first scene | 348 `Rwabs` on C, the same scene |
| Strider | `51ad` | 13, its title | 54, its title |
| Erik | `7206`, `Pexec` 3 and 4 | 6, its title | its title |
| Noddy's Playtime | `48ea`, `Pexec` from `data\` | 11, its menu | its menu |
| Defender 2 | `5264`, its own launcher shape | 10, its menu | its menu |
| Grandad | 2 MB, an unpacked launcher | 9, its plot | its plot |
| Starblade | `Getbpb(2)` | 12, its title | its title |
| Gravity | `Mediach(0)`, the floppy routines | 30, in play | in play |

48 runs, no fault; from the GEMDOS drive no sector read on C and the same files on the three
setups; from PPDRIVER each reads C through PPDRIVER (38 to 348 `Rwabs`, the same on the three).


**Diego's STE, 2026-10-26** (TOS 1.62, 4 MB, the Multidevice's GEMDRIVE, the card `PPHD`, built
2026-10-16 20:46; power-cycled between games). The card's `PPHD` had become an empty file (a FAT
repair, cause not looked into, Diego's choice); written again from `sdcard-2046` and checked file by
file before the tests.

| game | result |
|---|---|
| Operation Stealth | OK, the first scene and play |
| Guild of Thieves | OK, a game saved to the card and restored |
| Erik | OK |
| Noddy's Playtime | "Insert disk 1" forever, the Multidevice's LED blinking; with the fix below (card `sdcard-1129`), OK: its menu and an activity |
| Defender 2 | OK |
| Grandad | OK |
| Starblade | OK |
| Gravity | OK |
| Strider | OK |
| F16 Falcon | OK, flies; its menu's "Read mission disk" fails, as the adaptation has no mission disk (`MISSION.LOD`, `DISK.2`; the 8bitchip.info list's "Falcon with Mis. Disks" has them) |

Noddy: the game opens `data\driving.dat` with `Fopen` mode 2, never closes it, and has GOS run
it (`Pexec`), which the forwarder loads with `Fopen` mode 0 (`gos4_calls.py`, from PPDRIVER:
`20261026-105647-st-104-ppdriver-gos4-calls-noddyspt`). GOS and Hatari's GEMDOS drive let a file be
opened twice; md-drives-emulator's GEMDRIVE has FatFs's lock (`FF_FS_LOCK 32`), which refuses an
open of a file open for writing, `FR_LOCKED`, answered -33, so the game asks for its disk. Of the
GOS4 runs, 50 games open files with mode 2 and none writes through one (Ranx writes `RANX.ERI`,
made by `Fcreate`); Noddy is the only one that opens a file again while it is open for writing. The
forwarder now opens mode 2 as mode 0 on the drive (`gos4_patch.s`, `gd_named`). Batch
`tools/dev/builds/epic05/batch-1104`: the self-test PASS on the three setups, 117 PASS, no fault,
the same files opened as `batch-2008` (F16 Falcon at 2 MB, Ranx and Windsurf run again alone:
54, 35, 43). The card build `sdcard-1129` differs from `sdcard-2046` in the 117 GOS4 `START.TOS`
only. Worth raising with md-drives-emulator: TOS lets a file be opened twice, GEMDRIVE does not.

The card's 117 GOS4 `START.TOS` replaced with `sdcard-1129`'s and checked, the other 26,467 files
unchanged (2026-10-26). Noddy's Playtime then OK on the STE: the ten games run.

**Diego agrees, 2026-10-26**: "yes, close it", after the ten games ran on his STE from the
card, Noddy's Playtime with the read/write fix. The 117 GOS4 games run from a GEMDOS drive in
Hatari; ten of them, one of each kind, checked on the Multidevice.
