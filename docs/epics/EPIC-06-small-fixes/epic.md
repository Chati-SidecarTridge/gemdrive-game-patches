---
id: EPIC-06
iteration: 2
title: The small fixes from a GEMDOS drive (FIXPLAIN, FIXHOLE, FIXHAGE)
status: todo
---

## Goal

The eight games of the card's `FIXPLAIN`, `FIXHOLE` and `FIXHAGE` folders run from a Hatari
GEMDOS drive, with solutions S2, S3 and S4 (`hd-strategies.md` §3.2–3.4, §4). STORY-06's trials
already showed each of these working. This epic turns them into something a user can apply.
Chosen by Diego, 2026-10-15 (D-16): one epic for the three small groups.

- **S2, a BPB for the GEMDOS drive.** Four Silmarils games (`FIXPLAIN`): Crystals of Arborea,
  Targhan (one download), Robinsons Requiem and Storm Master. A resident program in `C:\AUTO\`
  answers `Getbpb` for the GEMDOS drive. Crystals of Arborea is the first test game.
- **S3, the fastload bit.** Spy vs Spy 2 and Strike Force Harrier (`FIXPLAIN`), and Aquanaut
  (`FIXHOLE`): the bit is set in the header of the program each start program runs. Spy vs Spy 2
  is the first test game.
- **S4, a `RUNME.TOS`.** Rody and Mastico 2 (`FIXHAGE`) starts with Rody and Mastico 4's
  `RUNME.TOS`, copied from the user's own `RODYM4.ZIP`.

## Scope

- In scope:
  - S2's resident program, built from source with the pinned toolchain (D-05).
  - S3's one-byte patch, as a tool.
  - S4's copy, as a tool or as instructions.
  - The eight games run on the three setups, and their verdicts.
  - The instructions, the card and the site.
- Out of scope:
  - A change to Hatari (C-02). S3's cause is Hatari's `Pexec`; a report to its maintainers stays a
    candidate that waits for Diego (D-15).

## Setups

As EPIC-04: Hatari's three setups, in GEMDRIVE mode and from PPDRIVER. At the checkpoint, Diego's
Multidevice, from a card. Whether S3's cause exists on the Multidevice has not been checked
(`hd-strategies.md` §4).

## Stories

- STORY-01: S2: a BPB for the GEMDOS drive (Crystals of Arborea first)
- STORY-02: S3: the fastload bit (Spy vs Spy 2 first)
- STORY-03: S4: Rody and Mastico 2's `RUNME.TOS`
- STORY-04: The instructions, the verdicts, the card and the site
- STORY-05: Verification (Diego's checkpoint)

## Notes
