---
id: EPIC-04
iteration: 2
title: The GOS5 games from a GEMDOS drive (FIXGOS5, Lemmings first)
status: in-progress
---

## Goal

The 87 games of the card's `FIXGOS5` folder, Gamex launchers with GOS5, run from a Hatari GEMDOS
drive, with Hatari unchanged (C-02). They use solution S1 (`src/notes/hd-strategies.md` §4), in
two parts:
- the launcher's driver checks are changed so that GOS starts without PP's driver;
- GOS's file requests go to the `TRAP #1` handler the machine had before the launcher. On
  Hatari's GEMDOS drive that handler is Hatari's own hook. Since STORY-01, the launcher does this
  through GOS's image of the system variables, so GOS's code stays as PP's.

Lemmings is the first test game: its launcher and GOS are EPIC-02's sources. Its first-level
problem on the reference has to be solved before its play session. The result is each game's
start file built for a GEMDOS drive, with its original's signature; the program that installs them
on a user's copy is EPIC-09 (D-17, D-18). Chosen by Diego, 2026-10-15 (D-16).

## Scope

- In scope:
  - Lemmings' launcher (`src/lemld2/`) changed in the sources, then rebuilt and run.
  - The address error that keeps the PPDRIVER reference from Lemmings' first level in Hatari
    (`ITERATIONS.md`, a candidate until now).
  - The change made by signature on each game's packed `START.TOS`, checked against every
    ST/STE build of GOS5's D15R (`D15R_5H` in 56 games, `D15R_H5` in 31, `D15R_H15` in 3;
    `hd-strategies.md` §3.1).
  - The 87 games, patched and run with `run_all.py`'s rules, with their verdicts updated.
  - The instructions for a user, and the card and the site updated.
- Out of scope:
  - GOS4 (EPIC-05).
  - The Falcon builds (`D15R_5F`, `D15R_F5`, `D15R_F15`): they would take the same patch,
    untested.
  - The 33 GOS5 games that already have a HAGA download that runs (`hd-strategies.md` §5): they
    get the patch like the rest.
  - Publishing PP's files, or any of it before D-15's clean-up.

## Setups

- Hatari's three setups from EPIC-00: ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06. Each runs in
  GEMDRIVE mode, which is the target, and from the PPDRIVER image, the reference, which has to
  keep working.
- Each game runs at the RAM its STORY-05 run needed.
- At the checkpoint, Diego's machines with the SidecarTridge Multidevice's GEMDRIVE, from a card
  with the patched games (`tools/survey/sdcard.py`'s layout).

## Stories

- STORY-01: Lemmings' launcher and GOS through the GEMDOS drive, from the sources
- STORY-02: The reference's first level: the address error at `$2B10`
- STORY-03: Lemmings plays from the GEMDOS drive
- STORY-04: The builds by signature: each GOS5 game's start file for a GEMDOS drive
- STORY-05: The 87 GOS5 games from the GEMDOS drive
- STORY-06: The instructions, the card and the site
- STORY-07: Verification (Diego's checkpoint)

## Notes

- **S1 needs only the launcher** (STORY-01, 2026-10-15). The launcher writes GOS's image of the
  system variables at run time anyway, so it points the image's `TRAP #1` at a 58-byte forwarder
  (`src/gemdrive/lemld2_gemdrive.s`). GOS's code stays as PP's. Lemmings reaches its title and
  loads its first level from Hatari's GEMDOS drive on the three setups.

- The S1 risks for GOS5, from `hd-strategies.md` §4:
  - `Fsfirst`/`Fsnext` find the DTA through TOS's current process.
  - Gamex's state saves (`file_io` with `"Wr"`) are untested.
  - On the Multidevice, the GEMDRIVE reads `_longframe` and `_dskbufp`, which GOS's image of TOS's
    RAM must hold usable values for, and the requests should carry full paths.
- GOS5's `file_io` asks for whole files by name (`disk-layer.md` §2): `Fopen`, `Fseek`, `Fread`
  or `Fwrite`, `Fclose`. That is the same request PP's HAGA file service makes, and 1,361 HAGA
  games run that way as they are.
- **Our builds only** (D-17): the launcher's changes, the keyboard wait (STORY-02's `gd_quiet`)
  among them, apply on the GEMDOS drive's path; PP's path, with his driver, stays as he made it.
