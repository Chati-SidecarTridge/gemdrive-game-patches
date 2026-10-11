---
id: EPIC-02
iteration: 1
title: The PPera launcher reverse engineered and recompilable, tested with our own build
status: todo
---

## Goal

Every PPera launcher program as sources in this repository that reassemble to the original bytes,
and a build that turns them back into launcher files. Run in Hatari, our build starts the game
exactly as the originals do. From then on the launcher is code we can change and test, which
EPIC-03 needs. Asked by Diego, 2026-10-11.

## Scope

- In scope: every program in the launch chain (`START.TOS` and the program it unpacks, the `.FIC`
  stages, the handling of `LEMMINGS.PCH`, the embedded PPera driver), and `GXUT260.PRG` if the
  launch or the driver depends on it; our unpackers and packers; vasm sources (D-05) that pass the
  round-trip check (EPIC-00 STORY-03); a build of the launcher files from those sources; the
  game booted from our build in Hatari.
- Out of scope: the game's own code (`FILES/CODE`, `FILES/MAIN`) beyond where the launcher hands
  over; any change in behaviour (EPIC-03).

## Setups

Hatari: the PPDRIVER reference of EPIC-01 STORY-01 on every setup, for the originals and for our
build. GEMDRIVE runs only to show our build fails the same way as the original.

## Stories

- STORY-01: The launch chain mapped from runs
- STORY-02: Unpackers, proven against Hatari's memory
- STORY-03: A packer the launcher accepts
- STORY-04: Sources for every stage that reassemble
- STORY-05: The PPera driver, annotated
- STORY-06: Our own launcher build boots the game
- STORY-07: Verification (Diego's checkpoint)

## Notes

Tests H-01, H-02 and H-05 (`ITERATIONS.md`). The first pass's decoders
(`_archive/2026-04-first-pass/src/tools/`) may be reused once a story has checked them against
Hatari's memory (D-01). Its notes disagree with its own decoder on the LZSS match lengths (+2/+3
in `start_tos.md`, +3/+4 in `depack_start_tos.py`); the memory dump settles it.
