---
id: STORY-07
epic: EPIC-04
title: Verification (Diego's checkpoint)
status: done
---

## Goal

Diego agrees that the GOS5 games run from a GEMDOS drive, as seen in Hatari and on his
Multidevice.

## Setups

- Hatari: ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06, in GEMDRIVE mode and from PPDRIVER.
- Diego's machines with the SidecarTridge Multidevice's GEMDRIVE, from the card. A machine is
  power-cycled between games.

## Tasks

- [x] Claude runs Lemmings' session and one game of each GOS5 build on the three setups, from both
      disks.
- [x] Diego tests the patched games from the card on the Multidevice. A game that disagrees with
      Hatari is listed here, with what he saw.
- [x] Diego agrees, or the stories to reopen are listed here.

## Acceptance

Diego's agreement, recorded with the date.

## Notes

**Diego agrees, 2026-10-16**: "confirmed the 85", the 85 GOS5 games that run from the card's
`FIXGOS5` on his STE (TOS 1.62, 4 MB, the Multidevice's GEMDRIVE), power-cycled between games, as in
Hatari. The two in `STILLNOT`, Awesome and Prison, fail on both for the same cause (their cartridge
check). What he saw that Hatari did not: Chaos Engine's wait for the floppy motor (STE only), and
Magic Boy and Muzzy running on the STE, which fail on Hatari's ST at 1 MB (STORY-05).

**Claude's runs, 2026-10-16** (`tools/dev/builds/gos5/checkpoint-1658/`: the script's outputs, the
contact sheet `sheet.png`). Lemmings: a copy of `LEMMINGS/` built by `tools/build_gos5.py`, with
`gemdrive-first-level.exp` from the GEMDOS drive and `reference-first-level.exp` from PPDRIVER. One
game of each other GOS5 build and family: `src/probes/epic04/gos5_run.py`, EPIC-03's generic
expectation, at the game's RAM (STE TOS 1.62 at 4 MB for Lemmings, as STORY-04).

| Game (build, family) | ST TOS 1.04 | STE TOS 1.62 | STE TOS 2.06 |
|---|---|---|---|
| Lemmings (`D15R_H5` `G558`, A) | GEMDOS drive PASS 12/12, the level preview; PPDRIVER PASS 13/13 | the same | the same |
| Alien Storm (`D15R_5H`, B) | title or intro, both disks | title, both | title, both |
| Knightmare (`D15R_5H`, B', 2 MB) | menu, both | menu, both | menu, both |
| Matrix Marauders (`D15R_H5` `G55`, B) | play, both | play, both | play, both |
| No Second Prize (`D15R_H15`, A, 2 MB) | menu, both | menu, both | menu, both |

30 runs, 30 PASS, no `Pterm(-1)`. From the GEMDOS drive, GOS opens the game's files by name
(Alien Storm's `CHARS16.PC1` …, Knightmare's `KM8`, `KM1`, No Second Prize's `NSP`, Lemmings'
`level020`, `ground1`); from PPDRIVER only the launcher's own files, the rest by sectors, the path
as it was (D-17). Lemmings from PPDRIVER then shows, after the level load, the striped screen of the
adaptation's own crash in Hatari (STORY-02), unchanged. `shasum -a 256 -c LEMMINGS.sha256`: OK.

