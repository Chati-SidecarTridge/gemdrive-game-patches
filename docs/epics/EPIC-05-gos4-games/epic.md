---
id: EPIC-05
iteration: 2
title: The GOS4 games from a GEMDOS drive (FIXGOS4, Operation Stealth first)
status: todo
---

## Goal

The 117 games of the card's `FIXGOS4` folder, Gamex launchers with GOS4, run from a Hatari GEMDOS
drive with solution S1. They reuse EPIC-04's builds by signature, extended to GOS4's D15R build. In GOS4 the
game calls GOS's GEMDOS itself during play, so the epic first finds which functions those calls
use; that is S1's largest risk (`hd-strategies.md` §4). Operation Stealth is the first test game.
Chosen by Diego, 2026-10-15 (D-16).

## Scope

- In scope:
  - The GEMDOS calls GOS4 games make during play.
  - The patch for GOS4's ST/STE build of D15R (`D15R_HH4`, in all 117 games).
  - The launcher patch from EPIC-04, checked on GOS4's launchers.
  - The 117 games, patched and run.
  - The instructions, the card and the site.
- Out of scope:
  - The Falcon build (`D15R_F4`).
  - The five GOS4 games that already have a download that runs (`hd-strategies.md` §5): they get
    the patch like the rest.

## Setups

As EPIC-04: Hatari's ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06, in GEMDRIVE mode and from
PPDRIVER. At the checkpoint, Diego's Multidevice, from a card.

## Stories

- STORY-01: What GOS4 games ask of GOS's GEMDOS during play
- STORY-02: Operation Stealth through the GEMDOS drive
- STORY-03: The 117 GOS4 games from the GEMDOS drive
- STORY-04: The instructions, the card and the site
- STORY-05: Verification (Diego's checkpoint)

## Notes

Hatari traces only the GEMDOS calls that reach its hook, and GOS's calls do not. STORY-01 needs a
breakpoint on GOS's own `trap1` instead (EPIC-02's map of D15R gives its address in each build).
