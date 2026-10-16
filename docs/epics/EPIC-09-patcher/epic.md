---
id: EPIC-09
iteration: 2
title: The patcher: a user's original start files checked by signature and replaced with our builds
status: todo
---

## Goal

One program a user runs on their own copy of the games PP adapted. It recognises each original
start file (`START.TOS`, or the game's own) by its signature, and replaces it with the build EPIC-04
to EPIC-07 made for a GEMDOS drive. A file it does not recognise, it leaves as it is. Asked by
Diego, 2026-10-15, as the last epic (D-17): "a program that verifies the signature of the original
file and replace it with previoisly custom built patched versions for GEMDOS".

## Scope

- In scope:
  - Every game EPIC-04 to EPIC-07 ported: its original start files' signatures and their
    replacements (each port epic's builds by signature, as EPIC-04 STORY-04's).
  - The builds for acsi2stm's GemDrive too, if EPIC-08 makes them work there.
  - The program: its checks (an unknown file, one already replaced, a folder in the card's layout
    or a download's), and the originals kept so that it can undo.
  - Every ported game installed by the program on a copy of its download, and run from Hatari's
    GEMDOS drive and from the Multidevice's.
  - The instructions, and the site.
- Out of scope:
  - New ports: a game the earlier epics did not port stays as it is.
  - PP's original path: our changes apply to our builds only (D-17).
  - Files missing from PP's downloads (Forgotten Worlds' GOS): the instructions' (D-19).
  - Publishing anything before D-15's clean-up.

## Open at the start (Diego's decisions, STORY-01)

- **What it carries.** A whole patched file holds PP's launcher code. D-11 keeps PP's files out of
  this repository and its publication, and `docs/publication/remove.txt` leaves our launcher sources
  to Diego. The other way carries only our changes and rebuilds the patched file from the user's
  own original: byte for byte our build, checked by the result's signature.
- **Where it runs.** On the Atari, from the drive the games are on; on a computer, before the
  files go to the card; or both.

## Setups

- Hatari's three setups (ST TOS 1.04, STE TOS 1.62, STE TOS 2.06), GEMDOS drive.
- Diego's STE with the Multidevice's GEMDRIVE, from a card, power-cycled between games.

## Stories

- STORY-01: The design: what it carries and where it runs
- STORY-02: The catalogue: every ported game's originals and replacements
- STORY-03: The program
- STORY-04: Every ported game installed by the program, and run
- STORY-05: The instructions and the site
- STORY-06: Verification (Diego's checkpoint)

## Notes

- EPIC-04 STORY-04 was a patcher of a user's copy; since D-17 it builds into `tools/dev/builds/`,
  and installing on a user's copy is this epic's.
