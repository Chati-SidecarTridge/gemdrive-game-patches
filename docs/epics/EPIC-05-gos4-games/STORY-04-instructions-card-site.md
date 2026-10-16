---
id: STORY-04
epic: EPIC-05
title: The instructions, the card and the site
status: done
---

## Goal

EPIC-04's README, tool, card and site cover GOS4 too.

## Tasks

- [x] The README and the tool cover GOS4, and are followed on a fresh copy of a GOS4 game.
- [x] The card holds the patched GOS4 games, under the verdict they have now.
- [x] The site updated. `build_site.py --check` passes.

## Acceptance

A fresh copy of a GOS4 game, patched by following the README, runs from the GEMDOS drive. The
card and the site show the new verdicts.

## Notes

- **The instructions** are `src/notes/gos4-gemdrive.md`, a page of the site beside the GOS5 one
  ("The GOS4 games, built"), and the tool `tools/build_gos4.py` (EPIC-04's README and tool stay the
  GOS5 games'). Followed on a fresh copy of Strider's download, unpacked from the mirror
  (`tools/dev/builds/gos4/readme-2054/`): the original kept as `START.ORG`, built, run from the GEMDOS
  drive (`tools/dev/logs/20261016-205446-st-104-gemdrive-readme-strider`: its files by name, no
  `Rwabs`, its title); the tool on the built file again: "0 PPHD checks, not one", nothing written;
  the info screen shows "Patched for GEMDRIVE HD by SidecarTridge" under the game's keys
  (`…-readme-strider-info`).
- **The card**: `tools/survey/sdcard.py` builds a GOS4 game's start program with `build_gos4.py`
  (`ports.tsv` has the 117, STORY-03), and `INDEX.TXT`'s header names `FIXGOS4` among the built.
  `tools/dev/builds/sdcard-2046/` against `sdcard-1635` (Diego's card): the 117 `FIXGOS4\…\START.TOS`
  and `INDEX.TXT` differ, nothing else; Slightly Magic's and Battle Probe's are byte for byte the
  builds of their last runs (`final-2038`).
- **The site**: the new page; the home page's legend and solutions count the GOS4 games among the
  built (202 of 212 fix: 85 GOS5 and 117 GOS4), the project's paragraph says where the work stands;
  `hd-strategies.md` §1, the risk that GOS4's calls were not known (now answered), and "Built for
  GOS4"; the 117 catalogue rows show "built: runs" and their build's picture (`port-<row>.png`).
  `build_site.py --check`: 13 pages, 7,702 links, 0 problems.
- **Diego's card** (his "Update", 2026-10-16): its `FIXGOS4` matched `sdcard-1635` byte for byte; the
  117 `START.TOS` written from `sdcard-2046`, and `INDEX.TXT`; read back, `FIXGOS4` (4,984 files),
  `FIXGOS5` (1,340), `STILLNOT` (18) and `INDEX.TXT` are all `sdcard-2046`'s. Nothing deleted.

**Done 2026-10-16.**

