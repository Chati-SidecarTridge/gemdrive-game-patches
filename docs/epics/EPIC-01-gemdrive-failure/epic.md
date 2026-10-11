---
id: EPIC-01
iteration: 1
title: Why the game fails in Hatari's GEMDRIVE mode
status: todo
---

## Goal

Find out, from runs, why PP's pristine launcher does not start Lemmings from a Hatari GEMDOS drive
(GEMDRIVE mode, `--harddrive`), and confirm or refute Diego's guess (H-07): the PPera driver
embedded in the launcher. The answer is the full list of what the launcher asks of the disk that a
GEMDOS drive cannot give, which is what EPIC-03 has to provide. Asked by Diego, 2026-10-11.

## Scope

- In scope: the pristine `LEMMINGS/` only (on copies, C-01); a working reference, the same game
  booting from an ACSI image with PP's own driver, PPDRIVER (D-09); GEMDRIVE runs on the EPIC-00
  setups; the first point where the two part, and every later one, found with experiments on
  patched copies; the verdicts on H-03, H-04, H-06 and H-07; the write-up.
- Out of scope: reconstructing the launcher (EPIC-02); the fix (EPIC-03); changing Hatari (C-02).

## Setups

Hatari, the setups of EPIC-00: an ST with TOS 1.04, an STE with TOS 1.62 and an STE with TOS
2.06, each in GEMDRIVE mode and from the PPDRIVER reference image, with at least 1 MB (C-04).

## Stories

- STORY-01: The reference: the game booting from a PPDRIVER image
- STORY-02: The GEMDRIVE runs, and where they part from the reference
- STORY-03: The embedded driver, confirmed or refuted
- STORY-04: Everything else GEMDRIVE lacks
- STORY-05: The write-up
- STORY-06: Verification (Diego's checkpoint)

## Notes

What GEMDRIVE mode is: Hatari serves the drive's GEMDOS calls (`Fopen`, `Fread`, `Fsfirst`, …)
from a host folder by intercepting `TRAP #1`; the drive has no sectors behind it, so a program
that reads it through BIOS `Rwabs`, XBIOS `DMAread` or the ACSI registers finds no disk. To be
checked against `../hatari`'s sources and a run in STORY-02, not assumed.
