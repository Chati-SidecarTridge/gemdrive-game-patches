---
id: STORY-04
epic: EPIC-09
title: Every patchable archive patched by the page, and run
status: done
---

## Goal

The page run on every archive of the mirror, in a browser, and its output compared and run.

## Tasks

- [x] Every archive given to the page: the action the table says, and for a fix a ZIP whose files equal the original plus the card build's changes.
- [x] A sample of the patched ZIPs, one of each fix, unpacked onto Hatari's GEMDOS drive and run on the three setups.
- [x] A ZIP that is not one of the mirror's, and a damaged one: refused.

## Acceptance

Every archive handled as the table says; the sample runs.

## Notes

**2026-10-26.**

- Every archive: `src/probes/epic09/patch_test.py --sample 100000`
  (`tools/dev/builds/epic09/test-20261026-165059`): 2,074 archives in 85 s, each recognised with the
  table's action; 208 patched, each patched ZIP checked with `zipfile` against its original (every
  entry the same bytes but the fix's file, which is our build, and the added files): 0 problems.
- Run as a user would: `src/probes/epic09/run_patched.py` unpacks a patched ZIP onto Hatari's GEMDOS
  drive and starts the game's program from the ZIP's own folder (`GDBPB.PRG` copied into `C:\AUTO\`,
  as a user runs it first). One of each fix, on ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06
  (`tools/dev/builds/epic09/runs-1653/`), counted from the game's own start, no sector read on C: in
  any: Lemmings 10 files; Operation Stealth 60 to 73; Crystals of Arborea 39 (2 pressed once its menu
  is up: at 12 s it was not yet); Spy vs Spy 2 `SPY2.PRG` starts `SPY2.BOY`, 11 files; Rody and
  Mastico 2 `RUNME.TOS` from part 4, 12 files; Forgotten Worlds the same 4 files as its EPIC-04 build
  run, `D15R_5H.FIC` among them, taken from the user's `ALIENSTO.ZIP`. (`run_all.analyse` counts only
  after a start in `C:\GAME\` or `C:\LEMMINGS\`, so these were counted from the run's own start.)
- A ZIP not in the table (one byte changed): not known. A truncated one: "this is not a ZIP file".
