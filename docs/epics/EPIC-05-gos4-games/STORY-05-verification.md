---
id: STORY-05
epic: EPIC-05
title: Verification (Diego's checkpoint)
status: in-progress
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
- [ ] Diego tests the patched games from the card. A game that disagrees with Hatari is listed
      here.
- [ ] Diego agrees, or the stories to reopen are listed here.

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

