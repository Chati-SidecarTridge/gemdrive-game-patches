---
id: STORY-04
epic: EPIC-04
title: The patchers, by signature, for a user's copy
status: todo
---

## Goal

STORY-01's two changes, made by tools that find their place by signature (as `classify.py` finds
the launchers). They patch a user's own copy of any GOS5 game, without PP's files being part of
this repository (D-11).

## Tasks

- [ ] The launcher's checks: found in PP's packed `START.TOS` (`2278 0472 0CA9 5050 4844 FFF8`),
      unpacked and packed again with `tools/unpack.py` and `tools/pack.py`. The packed result is
      accepted by the launcher.
- [ ] GOS5's `trap1`: found and patched in each ST/STE build (`D15R_5H`, `D15R_H5`, `D15R_H15`),
      with every build's patch site listed.
- [ ] One command patches a game's folder in place, on a copy, and says what it changed. Run
      twice, it changes nothing.
- [ ] On Lemmings, the patched copy equals STORY-01's build byte for byte, or the differences are
      explained.

## Acceptance

The tool patches Lemmings and one game of each GOS5 build, and each reaches its title from the
GEMDOS drive on ST TOS 1.04.

## Notes
