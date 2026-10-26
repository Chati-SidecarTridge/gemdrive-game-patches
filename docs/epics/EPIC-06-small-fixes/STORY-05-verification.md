---
id: STORY-05
epic: EPIC-06
title: Verification (Diego's checkpoint)
status: done
---

## Goal

Diego agrees that the eight games run from a GEMDOS drive, as seen in Hatari and on his
Multidevice.

## Setups

- Hatari: ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06, in GEMDRIVE mode and from PPDRIVER.
- Diego's machines with the Multidevice's GEMDRIVE, from the card, power-cycled between games.

## Tasks

- [x] Claude runs the eight games on the three setups, from both disks.
- [x] Diego tests them from the card. A game that disagrees with Hatari is listed here. On the
      Multidevice, S3's games show whether its `Pexec` needs the fix at all.
- [x] Diego agrees, or the stories to reopen are listed here.

## Acceptance

Diego's agreement, recorded with the date.

## Notes

**Diego's STE, 2026-10-26** (TOS 1.62, 4 MB, the Multidevice's GEMDRIVE, the card's `PPHD` from
`sdcard-1245b`, power-cycled between games; `GDBPB.PRG` run from the game's folder before the S2
games, no AUTO boot, Diego's choice).

| game | result |
|---|---|
| Crystals of Arborea | OK |
| Targhan | OK |
| Robinsons Requiem | OK |
| Storm Master | its title and credits, then halted with the floppy LED on; with any floppy in drive A it goes past the credits |
| Spy vs Spy 2 | OK |
| Strike Force Harrier | OK |
| Aquanaut | reboots while loading, after its loading picture |
| Rody and Mastico 2 | OK: the chapter menu takes the mouse only once its music has finished, then a chapter starts |

Storm Master: at the credits `STORM.PRG` drives the floppy controller itself (`btst #5,$FFFA01`
with `$FF8604` and `$FF8800` in a0/a1, in a packed part of `STORM.PRG` at file offset `$3F8D`) and
waits for it to answer; Hatari with no disk in A stops there from the GEMDOS drive and from PPDRIVER
alike (`20261026-132049-st-104-ppdriver-fix-storm-master-none`), so it is the adaptation's, not
the drive's: it needs a disk in drive A.

Aquanaut: `AQUANAUT.PRG` keeps 0x110 bytes and starts `AQUANAUT.EXE` right above itself, which keeps
193 KB, and both put the screen at fixed addresses (`$78000`, `$75000`). In Hatari (STE TOS 1.62,
4 MB, `20261026-134418-ste-162-gemdrive-fix-aquanaut-fastload`) it is loaded at `$1258A` and reaches
its title; with 64, 128, 192 or 256 KB kept resident first from `C:\AUTO\` (scratch programs in
`tools/dev/builds/epic06/reserve/`), it falls back to the desktop: it runs only where a bare TOS
loads it. GEMDRIVE and the Multidevice's TOS 1.62 leave the free memory higher; hence the reboot.
`FBHOLE.PRG` in its download writes a boot sector that keeps the RAM up to `$80000`; the same done
from `C:\AUTO\` (`src/gemdrive/gdhole.s`, a test, not on the card) loads it at `$87AE0`, and
`AQUANAUT.EXE` ends in `Pterm(-1)` from a stray PC on the four setups. Not understood yet: Aquanaut
leaves the "runs" list until it is (Diego, 2026-10-26).

**Claude's runs** (STORY-01 to STORY-03's tables): the S2 games and Rody and Mastico 2 on ST TOS
1.04, STE TOS 1.62 and STE TOS 2.06 from the GEMDOS drive, their PPDRIVER reference being EPIC-03's
survey runs; the S3 games on the three setups from both disks. Not answered: whether the S3 games
need the bit on the Multidevice at all (their unpatched start programs were not tried there; the
card holds the patched ones).

**Diego agrees, 2026-10-26**: "close, commit and push this epic". Seven of the eight games run from
the GEMDOS drive and on his STE with the Multidevice. Aquanaut stays open: `ports.tsv` marks it
`fails`, the card's next write puts it in `STILLNOT`, and the site reports it as failing on the
Multidevice; it goes on with the unsure games (EPIC-07). Along the way the site was reworked at
Diego's requests: the GEM look, the texts rewritten, the hardware testing and its failures reported
(`src/survey/hardware.tsv`, exceptions only), the pages merged into six, the dates after 2025
removed, and a check of a game's name on the home page.
