---
id: EPIC-04
iteration: 1
title: GEMDRIVE mode as an alternative way to launch Lemmings
status: todo
---

## Goal

Lemmings starts and plays from a Hatari GEMDOS drive (GEMDRIVE mode), as an alternative to a
hard-disk image, **without any change to Hatari** (C-02). The fix lives on the Atari side, in the
launcher built from EPIC-02's sources or in a program or driver that runs before it, and covers
every dependency EPIC-01 listed. Asked by Diego, 2026-10-11; EPIC-03 until the survey epic
took that number (D-10).

## Scope

- In scope: choosing the approach (with Diego); building it from source; Lemmings booting and
  playing in GEMDRIVE mode on every setup; the PPDRIVER reference still working; how a user
  applies it.
- Out of scope: any change to Hatari's code or its builds (C-02); changes to `LEMMINGS/` (C-01);
  other PPera games ("only Lemmings by now", Diego, 2026-10-11; EPIC-03 classifies them, making
  them run comes later); the SidecarTridge's GEMDRIVE
  (`../atarist-sidecart-gemdrive`; "we will work later on", Diego, 2026-10-11). Both are candidates in
  `ITERATIONS.md`.

## Setups

Hatari, the setups of EPIC-00: an ST with TOS 1.04, an STE with TOS 1.62 and an STE with TOS
2.06, each in GEMDRIVE mode and from the PPDRIVER reference image.

## Stories

- STORY-01: The approach, chosen
- STORY-02: Lemmings boots in GEMDRIVE mode
- STORY-03: Lemmings plays in GEMDRIVE mode
- STORY-04: How a user applies it
- STORY-05: Verification (Diego's checkpoint)

## Notes

The approach is chosen for Lemmings, but STORY-01 records for each option which of EPIC-03's
strategies it would also cover, so the generic ways that come later start from that.
