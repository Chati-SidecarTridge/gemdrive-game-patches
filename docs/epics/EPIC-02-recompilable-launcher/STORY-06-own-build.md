---
id: STORY-06
epic: EPIC-02
title: Our own launcher build boots the game
status: done
---

## Goal

One command builds the launcher files from our sources, and the game boots from them in Hatari
exactly as from the originals.

## Tasks

- [x] `tools/build_launcher.sh`: assembles every stage (`tools/dev/asm.sh`), packs them
      (`tools/pack.py`) and writes the launcher files into a disk tree under
      `tools/dev/builds/`, next to a copy of `FILES/`.
- [x] Our build boots the PPDRIVER reference to the level load on every setup, with the same
      milestones and the same disk calls as the originals (`reference-first-level.exp`).
- [x] Our build in GEMDRIVE mode stops where the original stops (EPIC-01 STORY-02).
- [x] Proof it is ours: a visible change in one source (for example a text on the launcher's
      screen) appears in the run, and reverting it restores the original bytes.
- [x] Added to `tools/dev/all_harness.sh`.

## Acceptance

`tools/dev/all_harness.sh` builds the launcher from source and boots the game from it on every
reference setup, PASS.

## Notes

**Done 2026-10-11.**

- `tools/build_launcher.sh [<src folder>] [<out folder>]` assembles the five sources, packs
  `START.TOS` (with our stub, `tools/pack.py start --stub`), `LS2DD.FIC`, `D15R_H5.FIC` and
  `D15R_F5.FIC`, each padded with zeros to PP's file's length (`--pad`) so the files take the same
  clusters on a disk and the reference's record numbers hold, and copies the rest of
  `LEMMINGS/` next to them in `tools/dev/builds/launcher/LEMMINGS/`. All four stages unpack to
  PP's bytes; the packed files differ from PP's (our packer, STORY-03) and nothing reads the
  padding. About 40 s.
- The PPDRIVER reference from our build, `reference-first-level.exp`, PASS 13/13 on ST TOS 1.04,
  STE TOS 1.62 and STE TOS 2.06 (`20261011-183234-st-104-ppdriver-ours`, `…-183255-ste-162-…`,
  `…-183316-ste-206-…`). Its GEMDOS, BIOS and XBIOS disk calls, PCs and arguments included, are
  the same as with PP's files: 173 on ST TOS 1.04 (against three runs of PP's files), 173 on STE
  TOS 1.62, 199 on STE TOS 2.06.
- From the GEMDOS drive, our build stops where PP's does (EPIC-01 STORY-02): the same 92, 92 and
  98 calls (host paths aside) as EPIC-01's gate runs, to the "requires PP" message, the raw ACSI
  read on TOS 1.x and `DMAread` on TOS 2.06 included (`…-183421-st-104-gemdrive-ours`,
  `…-183438-ste-162-…`, `…-183455-ste-206-…`).
- Proof it is ours: a copy of `src/` with LEMLD2's `"Machine: "` changed to `"REBUILT: "` builds
  (LEMLD2 then unpacks to other bytes than PP's, the rest to the same) and the info screen shows
  `REBUILT:    ST` (`…-183638-st-104-ppdriver-rebuilt/shots/info.png`); built from `src/` as it is,
  every stage is PP's bytes again.
- `tools/dev/all_harness.sh` builds the launcher from `src/` and boots it to the level load on
  ST TOS 1.04, then rebuilds the disks from `LEMMINGS/`: 17 checks, PASS, 220 s.
