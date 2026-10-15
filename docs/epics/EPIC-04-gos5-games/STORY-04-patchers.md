---
id: STORY-04
epic: EPIC-04
title: The patchers, by signature, for a user's copy
status: todo
---

## Goal

STORY-01's change, made by a tool that finds its place by signature (as `classify.py` finds the
launchers). It patches a user's own copy of any GOS5 game, without PP's files being part of this
repository (D-11). GOS's code needs no change (STORY-01), so only the launcher is patched.

## Tasks

- [ ] The launcher's checks: found in PP's packed `START.TOS` (`2278 0472 0CA9 5050 4844 FFF8`),
      with `gd_start` and `gd_forward` added. The file is unpacked and packed again with
      `tools/unpack.py` and `tools/pack.py`, and the packed result is accepted by the launcher.
- [ ] Each ST/STE build of GOS5 (`D15R_5H`, `D15R_H5`, `D15R_H15`): the image of the system
      variables where the launcher finds it (`($C07E6) + $C0800`), its `TRAP #1` slot at `$84`,
      and `$B7180` free. Checked for every build, with the launcher variants that load each.
- [ ] One command patches a game's folder in place, on a copy, and says what it changed. Run
      twice, it changes nothing.
- [ ] On Lemmings, the patched copy equals STORY-01's build byte for byte, or the differences are
      explained.

## Acceptance

The tool patches Lemmings and one game of each GOS5 build, and each reaches its title from the
GEMDOS drive on ST TOS 1.04.

## Notes
