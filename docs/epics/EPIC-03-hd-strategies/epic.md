---
id: EPIC-03
iteration: 1
title: The ways PP's adaptations run from a hard disk, classified
status: done
---

## Goal

Every game in PP's list of hard-disk adaptations (<https://atari.8bitchip.info/fromhd3.php>, 1,831
records on 2026-10-11) classified by the strategy its adaptation uses to run from a hard disk,
and the answers to Diego's questions: how many different ways there are, how many games use each,
what each one needs from the disk and the system, and which of them run from a Hatari GEMDOS drive
today. The result is a **migration table** with, for every game, its strategy and one of three
verdicts (D-14):

1. **as it is**: it runs from a GEMDOS drive unchanged; shown by its files (no sector-access
   signature) and by a run that gets past its first file load, not only to its title;
2. **fix**: it needs adapting, and the table names the solution that would do it (one per
   strategy, or several where a strategy has variants);
3. **not feasible**: it cannot run from a GEMDOS drive without major modifications, with the
   reason (for example a game that drives the floppy controller itself during play), so the
   verdict can be revisited.

A game the evidence does not settle is **unsure**, with what is missing. The epic also proposes
the solutions, each with the games it covers and its cost; at its checkpoint Diego chooses which
become iteration 2's epics and in what order. All of it, with the project's documentation, is
published as a website with the repository (STORY-07); the repository goes public only after
what cannot be published is removed (D-15). Asked by Diego, 2026-10-11 (D-10, D-14).

## Scope

- In scope: the list and each game's page; PP's own documentation of his methods (below); every
  adapted game's files, in the mirror made ahead of the epic (STORY-03, D-11, D-12); static
  signatures of their launchers, starting from EPIC-02's (`src/notes/launcher-signatures.md`)
  and read with EPIC-02's tools (`tools/unpack.py`, `tools/dev/mksource.py`, the profile probes);
  every game run in GEMDRIVE mode, for its verdict; each strategy's representatives also run from
  the PPDRIVER reference; for each strategy with games to fix, the solutions proposed, with the
  games they cover and their cost; the migration table; the website (designed with the
  frontend-design skill) and what publication needs.
- Out of scope: building the solutions (iteration 2's epics, chosen at this epic's checkpoint);
  the SidecarTridge's GEMDRIVE itself, beyond noting where it would differ from Hatari's; Falcon,
  TT and TOS above 2.06 (as in EPIC-00); committing or publishing PP's files (D-11); publishing
  anything: the work is local until the clean-up and Diego's word (D-15).

## Setups

Hatari, the setups of EPIC-00: an ST with TOS 1.04, an STE with TOS 1.62 and an STE with TOS 2.06,
in GEMDRIVE mode and from a PPDRIVER image with the game copied in, at the RAM size the list
gives for the game (1 or 2 MB). Every game runs once on ST TOS 1.04 in GEMDRIVE mode; one
representative of each strategy also runs on all three setups.

## Stories

- STORY-01: PP's modes and strategies, understood
- STORY-02: The catalogue and PP's own classification
- STORY-03: The adapted games' files
- STORY-04: The strategies, from the files
- STORY-05: Every game in Hatari's GEMDRIVE mode: the verdicts
- STORY-06: The write-up: how many ways, and the solutions proposed
- STORY-07: The website: the documentation and the catalogue, for the internet
- STORY-08: Verification and the choice of solutions (Diego's checkpoint)

## Notes

What PP's site already says. D-01 applies to his documents as it does to the first pass: a claim
counts once a story here has seen it happen in a run.

- **His classification of the originals** (`agcat.html`, about 450 games): six sections by how the
  game reaches the floppy. 1: the regular file system, relocatable, unprotected (40 games).
  2: the same, protected (130). 3: singleparted, loaded whole before the start (104). 4: the
  regular file system, bound to low RAM (61). 5: XBIOS floppy access (6). 6: direct
  floppy-controller access during play (107). Each game's page carries the code (`MXTPL`, `SXT`
  `SXI` `SXO`, `MXTL`, `MXO` `MXOP`, `MXIF`); Lemmings is `M5IF`, section 6. That is the
  original's category, not the adaptation's strategy, which is this epic's axis: the same category
  can be adapted in more than one way. Lemmings itself has two downloads: `LEMMINGS.ZIP` (1 MB, the
  files in `LEMMINGS/`) and `LEMMSRD.ZIP` (2 MB, also Falcon and TT).
- **The strategies he names**: plain installation, with path fixes for protected games; HOLE (TOS
  memory laid out as for an AUTO start, from the Desktop); AUTO start (`AUTOlist`); the Floppy
  Image Runner (`IMGRFWS`, floppy images mapped onto drive A, `imgrun.php`); singleparting (the
  game packed whole and restored in RAM); Gamex launchers with **GOS** ("Gemdos or Gaming OS",
  `GAMEXdoc.html`): GOS 1.00 without disk support; GOS4 and GOS5, a modded GEMDOS 0.15 of TOS 1.04
  in high RAM, with the hard-disk driver installed again below it. His driver, PPTOSDOS, is
  "PC relative" and is only copied; with other drivers he has to "boot and install it again". RAM
  disks ("filewise ramdisked", Lemmings' page).
- **Two generations of adaptations** (`fromhd2.php`): those before January 2012 work only with
  PP's own drivers, AHDI and HDDriver; later ones, with a file `HAGA`, `HAGE` or `HAG2` in the
  game's root folder, work with "any decent driver" for the AHDI FAT16 file system. For "big
  %-age of games" he runs his modified TOS 1.04 from RAM instead of the machine's TOS.
- **His published launcher sources** (`astopensw.php`): `GamexLSrc.html` (Castle Master, a TPA
  game), `GamexLSrc2.html` (Sideways, singleparted, does not use TOS), `GamexLSrc3.html`
  (Starglider, GOS 1.00, which loads `D15R_NG1.FIC`, "Packed GEMDOS, GOS 1.00").
- **His view of GEMdrive** (`fromhd.php`): it serves the `TRAP #1` file calls, so "Xbios direct
  disk sector access", and "direct hard disk access", which "some game hard disk adaptations use",
  cannot work on it. Such games need a real disk or a disk image. EPIC-01 showed one such case;
  this epic counts how many there are.
- **Lemmings is GOS5 with PP's own driver**, now shown by EPIC-02 (H-08 confirmed): D15R is TOS
  1.04 in RAM, the game asks PP's loader for files by name and D15R's GEMDOS reads them by
  sectors through a copy of PP's driver (`src/notes/disk-layer.md`). GOS5's RAM map in
  `GAMEXdoc.html` matches its addresses. Lemmings is the first known game of that strategy, and
  the one whose verdict ("fix") and solution are already best understood.
- The downloaded files stay on this Mac, never committed or published (D-11, C-03).
