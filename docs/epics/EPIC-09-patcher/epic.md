---
id: EPIC-09
iteration: 2
title: The patcher: the user's download checked, patched in the browser, and given back
status: done
---

## Goal

A page of the website where a user drops the ZIP of a game, as downloaded from the 8bitchip.info
website. The page checks that it is one of the downloads this project knows, says whether the
game runs from GEMDOS and GEMDRIVE as it is, and, when a built fix makes it run, patches the ZIP in
the browser and gives it back to download (D-22). Asked by Diego, 2026-10-26; EPIC-07 and EPIC-08
come after it.

## Scope

- In scope:
  - Every archive of the mirror: its SHA-256, its games, and what the page does with it.
  - The fixes built so far: S1 for the GOS5 and GOS4 games (`tools/build_gos5.py`,
    `build_gos4.py`, with their options), S2 (`GDBPB.PRG` added), S3 (the fastload bit), S4
    (Rody and Mastico 4's `RUNME.TOS`), and the files another download completes (D-23:
    Forgotten Worlds, Rody and Mastico 2).
  - The build in JavaScript, byte for byte the Python tools' result, checked by SHA-256.
  - ZIP reading and writing in the browser, with no library from another site.
  - Every patchable archive patched by the page, compared with the card's build, a sample run in
    Hatari; the patched ZIPs tried on Diego's machine.
  - The page on the site, and its instructions.
- Out of scope:
  - The page carrying any byte of the adaptations (D-11), and publishing before D-15.
  - Fixes not built yet: the unsure games (EPIC-07), acsi2stm's GemDrive (EPIC-08). The page
    grows with them.
  - Changing a fix: the page applies what EPIC-04 to EPIC-06 built.

## Setups

- Chrome, Safari and Firefox on this Mac, the page opened from the local site.
- Hatari's three setups (ST TOS 1.04, STE TOS 1.62, STE TOS 2.06), GEMDOS drive.
- Diego's machines with the Multidevice's GEMDRIVE, from a card, power-cycled between games.

## Stories

- STORY-01: The design (Diego's decisions)
- STORY-02: The catalogue: every archive, its check and what the page does
- STORY-03: The patcher in the browser: the ZIP, the build, the download
- STORY-04: Every patchable archive patched by the page, and run
- STORY-05: The page on the site, and its instructions
- STORY-06: Verification (Diego's checkpoint)

## Notes

Written again on 2026-10-26 for D-22; the program planned before (D-17) was to install our builds
on a copy of the games, on the Atari or on a computer.

Closed 2026-10-26: `patch.html`, "Patch a game", on the site; `tools/site/patcher.js` and the data
`build_site.py` writes from `src/survey/patches.tsv` (`tools/survey/patch_table.py`). EPIC-07 and
EPIC-08 follow (D-22); their fixes join the table and the page when they are built.
