---
id: STORY-01
epic: EPIC-05
title: What GOS4 games ask of GOS's GEMDOS during play
status: done
---

## Goal

The GEMDOS functions GOS4 games call during play, with their parameters, so that the patch hands
on every one a game needs.

## Tasks

- [x] A probe: a breakpoint on GOS4's `trap1` in `D15R_HH4` that prints the function and its
      parameters, on the PPDRIVER image, where the games run.
- [x] Operation Stealth and a sample of other GOS4 games (one per launcher variant, by
      `classify.py`'s signatures), each played past its first file load.
- [x] The list of functions used, and how each one differs from the GOS5 file requests EPIC-04
      handles: paths, DTA, handles, `Fsfirst`, writes.

## Acceptance

The table of functions per game, from traces, and what the patch must hand on.

## Notes

### The probe (2026-10-16)

`src/probes/epic05/gos4_calls.py <ZIP>`: the game's folder copied from its download (EPIC-04's
`gos5_run.original`), its `D15R_HH4.FIC` unpacked, GOS's GEMDOS dispatcher found by signature
(`movea.l (8,a6),a0 / move.w (a0),(-26,a6) / cmpi.w #87,(-26,a6)`, one in each build), and a
`:trace` breakpoint just after the `movea` dumps the parameters and the two names they may point
to, at every call; the original game from the PPDRIVER image, ST TOS 1.04 at the game's RAM, 120 s
(screenshots, space, Return, a click); `--report` lists the calls. GOS4 is `D15R_HH4`, a relocatable
GEMDOS program (GOS5's D15R is not), which the launcher relocates to `$C0100`, or `$1C0100` for a 2 MB
game: Operation Stealth's RAM at 40 s (`20261016-171229-st-104-ppdriver-opsteal-dump`) has `TRAP #1`
= `$C901C`, text `+$8F1C`, the build's `btst #5,(sp)` entry; Grandad's (`…-172301-…-grandad-dump`)
the dispatcher at `$1C0100` + its offset.

The 117 launchers (`sdcard-1635`'s `FIXGOS4`): 112 packed by PP's stub and 5 unpacked (Herman, Hoog,
Ranx, Grandad, Grandad 2, as Indigo among the GOS5 games), all with one `PPHD` check followed by
`bne.w`; five builds of `D15R_HH4` (by SHA-256: `4e5335a3…` 64 games, `51ad6351…` 46, `7206fd06…` 5,
`48eaecbd…` Noddy's Playtime, `5264001c…` Defender 2), the dispatcher at text `+$941C` in the first,
`+$9698` to `+$96C6` in the others. The sample: one game per build, an unpacked launcher, a 2 MB game.

| game (build) | run `tools/dev/logs/20261016-…-gos4-calls-*` | reached | GEMDOS calls to GOS |
|---|---|---|---|
| Operation Stealth (`4e53`) | `171512-…-opstealf` | play, its first scene | Cconis 43,970, Fread 849, Fseek 79, Fopen 70, Fclose 66, Dgetdrv 40, Dgetpath 38, Malloc 19, Crawcin 5, Fgetdta 2, Fsfirst 2, Dsetdrv, Dsetpath, Pexec, Mshrink |
| Strider (`51ad`) | `171953-…-strider` | title, high scores | Fopen 9, Fread 9, Fclose 9, Dsetdrv, Dsetpath, Pexec |
| Erik (`7206`) | `171958-…-erik` | title | Crawio 1,178, Pexec 4 (0, 0, 3, 4), Dsetdrv, Dsetpath, Mshrink, Pterm0, Cconws |
| Defender 2 (`5264`) | `172002-…-defndr2` | its attract loop | Fopen 6, Fread 6, Fclose 6, Pexec 2 (0, 3), Dsetdrv, Dsetpath, Mshrink, Malloc |
| Noddy's Playtime (`48ea`) | `172006-…-noddyspt` | its menu | Pexec 4 (all 0), Mshrink 4, Fopen 4 (mode 2), Malloc 3, Fread 3, Fclose 3, Mfree 3, Cconws 2, Dsetdrv, Dsetpath, Pterm |
| Herman (`4e53`, unpacked launcher) | `172008-…-herman` | title | Fopen 2, Fread 2, Fclose 2, Dsetdrv, Dsetpath, Pexec |
| Grandad (`51ad`, 2 MB, unpacked launcher) | `172402-…-grandad` | play, the entrance hall | Fread 21, Fopen 6, Fclose 6, Fsetdta 6, Fsfirst 5, Dsetdrv, Dsetpath, Pexec, Cconws |

Every launcher first does `Dsetdrv(2)`, `Dsetpath("\LEMMINGS\FILES")` (or `"\LEMMINGS"`), then
`Pexec(0, <the game's program>)` (`OSTL`, `STLAU`, `ERIKR`, `DEF2.SGP`, `NOLAU`, `HERL`, `GRANDAD`):
in GOS4 the game is a process of GOS's. No `Fcreate`, `Fwrite` or `Fdelete` in these runs; Grandad's
menu has "Save game".

### What the patch must hand on, against EPIC-04's `gd_forward`

EPIC-04's `gd_forward` hands Dsetpath, Fcreate, Fopen, Fclose, Fread, Fwrite, Fdelete, Fseek and
Dgetpath to the machine's `TRAP #1`, names cut to 8.3, and the rest to GOS. GOS5's `file_io` only
ever made those. For GOS4:

- **The same nine**: Fopen (modes 0 and 2), Fread, Fseek, Fclose, Dsetpath, Dgetpath (drive 3: the
  game then opens full paths, `C:\LEMMINGS\FILES\VOL.1`), Fcreate, Fwrite, Fdelete.
- **`Pexec` 0 and 3**, the launcher's and the games' own (Erik's `ERIK.CTE`, Noddy's `data\intro.dat`,
  Defender 2's `SAFESNG2.PRG`): GOS's Pexec reads the program through its own file code, by sectors,
  not through `TRAP #1`, and Hatari's GEMDOS drive answers Pexec by having the GEMDOS it chains to
  (the ROM's, whose memory is not the game's) make the basepage (`../hatari/src/gemdos.c`,
  `GemDOS_Pexec`). So the patch loads programs itself: GOS's `Pexec(5)` for the basepage in GOS's
  memory, the file read through the machine's `TRAP #1` and relocated, then GOS's `Pexec(4)` (mode
  0) or the basepage returned (mode 3). Modes 4 and 5 stay GOS's.
- **`Fsfirst` and `Fsnext`** (Operation Stealth, Grandad, each with `Fsetdta` or `Fgetdta`): to the
  machine, into the game's DTA. The Multidevice asks for the DTA through `$84` (`Fgetdta`, which
  GOS answers with the game's); Hatari reads it from the ROM's current process (`act_pd`, taken
  from the ROM's OS header at boot, `gemdos.c` 4292, 3043), which under GOS is still the launcher's.
  So around the call the patch makes the ROM's current process one whose DTA is the game's.
  `Fsetdta` and `Fgetdta` stay GOS's.
- **GOS's own**: Dsetdrv and Dgetdrv (GOS keeps drive C, as `gd_install` copies `_drvbits`),
  Malloc, Mfree, Mshrink, Pterm and Pterm0, Cconis, Crawio, Crawcin, Cconws.
- **Handles**: the machine's (Hatari's from 64), where GOS's start at 6; `gd_forward` sends every
  Fread, Fseek and Fclose to the machine, so a game reading GOS's standard handles (none seen)
  would need the handle checked. A child that ends without closing a file (Noddy opens
  `data\driving.dat` twice) leaves the machine's handle open: GOS closes only its own.
- **Writes**: none seen; Grandad's save, and Operation Stealth's, are STORY-02's.

