---
id: STORY-01
epic: EPIC-03
title: PP's modes and strategies, understood
status: done
---

## Goal

Before any game is classified, a clear understanding of the different ways PP adapts games to
run from a hard disk: his modes (Gamex and its GOS versions, HAGA/HAGE/HAG2, the Floppy Image
Runner, HOLE, AUTO start, singleparting, RAM disks, plain installation…), what each one does,
how it reaches the disk, what it needs from the system, and how to recognise it from a game's
files. This is the vocabulary the rest of the epic classifies with. Asked by Diego, 2026-10-11.

## Tasks

- [x] PP's own documentation read in the mirror (STORY-03's copy, D-12; never the live site):
      `GAMEXdoc.html`, `GamexUsage.html`, `agcat.html`, `plafh.html`, `playfhd.html`,
      `fromhd.php`, `fromhd2.php`, the help of `fromhd3.php`, `imgrun.php`, `astopensw.php` and
      the pages they link. Every mode or method PP names, with his words and the page.
- [x] His published launcher sources read (`GamexLSrc.html`, `GamexLSrc2.html`, `GamexLSrc3.html`:
      a TPA game, a singleparted game that does not use TOS, GOS 1.00), set against Lemmings'
      launcher (EPIC-02's sources and `src/notes/launch-chain.md`): what is common to every Gamex
      launcher, what differs by mode, and the GOS versions (1.00, GOS4, GOS5; the `D15R_*` files
      and their builds).
- [x] His tools looked at from the mirror (HOLE, the Floppy Image Runner `IMGRFWS`, `AUTOlist`,
      `HDTCFIX`, `RAMTOS`, the "HAGA"/"HAGE"/"HAG2" files): what each does for a game and when PP
      uses it; their programs unpacked or disassembled with EPIC-02's tools where the text does
      not say.
- [x] The glossary of the list's Note column and the game pages' text ("Gamex", "HAGA", "filed",
      "singleparted", "filewise ramdisked", "deprotected", "Tr." …), each term mapped to a mode.
- [x] `src/notes/pp-modes.md`: one section per mode: what it is, how a game in that mode runs from
      a hard disk (files or sectors, which driver, which TOS, fixed RAM), the files and byte
      patterns that mark it (`src/notes/launcher-signatures.md` extended), PP's sources, and a
      first guess at its verdict from a GEMDOS drive (as it is, fix, not feasible), to be checked
      by STORY-05. Lemmings' mode (Gamex with GOS5 and PP's driver) as the worked example.

## Acceptance

From `src/notes/pp-modes.md` alone, a reader can tell which mode an adaptation uses from its
files and PP's page, and what that mode asks of the disk and the system; every statement points
at PP's text, one of his sources, or a run.

## Notes

D-01 applies: PP's documents are hypotheses until a run shows them. Lemmings is the only mode
seen in runs so far (EPIC-01, EPIC-02).

**Done 2026-10-11.** `src/notes/pp-modes.md`; signatures in `src/notes/launcher-signatures.md`
("Other modes"); runs with `src/probes/epic03/mode_probe.py <ZIP> [--disk …]`.

- PP sorts games two ways: by how the original reached the floppy (`agcat.html`'s six
  categories, the `Cat:` code on 1,609 game pages) and by the launcher he wrote (the mode). The
  mode decides the GEMDOS-drive verdict.
- The modes, from the files of the 1,947 archives: HAGA (1,108), HAGE (219), HAG2 (141), Gamex
  without GOS (120), Gamex + GOS 1.00 (7), GOS4 (90), GOS5 (77), PP's launcher without Gamex (56),
  HOLE, AUTO, floppy images for the Image Runner, and 103 with none of these.
- One game per mode on the GEMDOS drive (ST TOS 1.04): Wormhole, Quest for Galaxia, Andromeda
  (HAGA), Breakout ACC (HAGE), 180 (HAG2), Castle Master (Gamex), Garfield (GOS 1.00) and Recoil
  reach their game, every file opened by name through the machine's GEMDOS. Magnetik Tank (GOS4),
  Clever & Smart and Bubble Dizzy (GOS5) quit at their launcher's driver checks, as Lemmings
  does; on PPDRIVER all three play, reading by sectors. Vector Invaders (HAG2, monochrome) halts
  with 1 MB on both disks and plays with 2 MB (the harness gained `--monitor mono`); Aquanaut
  stops without HOLE.
- HAGA's file service calls the machine's GEMDOS (`Fopen`/`Fcreate`, `Fseek`, `Fread`/`Fwrite`),
  which is why it works with "any decent driver" and with Hatari's GEMDOS drive; HAGE and HAG2
  load TOS 1.04 into RAM and serve its floppy from the game's image file, read by name.
- First guesses: the HAGA family (about 1,468 archives) and the Gamex launchers without GOS4/GOS5
  as they are; GOS4/GOS5 (about 167) fix; iTOS not feasible as it is. STORY-05 checks each game.
- Side findings for later stories: `LEMMINGS.ZIP` = `LEMMINGS/` (STORY-03); `tools/unpack.py
  start` accepts up to 3 zero bytes of padding; `--monitor mono` and 2 MB for games like Vector
  Invaders (STORY-05); `ALISTR.ZIP` (AUTOlist) answered 404; "DFC" and "filewise ramdisked" stay open.
