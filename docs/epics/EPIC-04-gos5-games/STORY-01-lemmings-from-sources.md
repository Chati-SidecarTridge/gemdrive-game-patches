---
id: STORY-01
epic: EPIC-04
title: Lemmings' launcher and GOS through the GEMDOS drive, from the sources
status: todo
---

## Goal

Our build of Lemmings' launcher, changed in EPIC-02's sources, starts GOS without PP's driver.
GOS5's GEMDOS hands the file functions to the handler that was there before the launcher. The game
reaches its title from Hatari's GEMDOS drive, and the PPDRIVER reference still runs.

## Tasks

- [ ] The launcher's driver checks (`src/lemld2/lemld2.s`: `check_pp_driver`, `reuse_pp_driver`,
      `start_d15r`): with no `PPHD` driver, GOS is started as on the primary path, with no driver
      copy and no sector-0 read. The change goes in the map, and the source is regenerated.
- [ ] GOS5's `trap1` (`src/d15r/`, PP's entry): the file functions (`Fopen`, `Fclose`, `Fread`,
      `Fwrite`, `Fseek`, `Fcreate`, `Fdelete`, `Fsfirst`/`Fsnext`, `Dsetdrv`, `Dsetpath`,
      `Dgetpath`) go to the `TRAP #1` vector saved before the launcher ran. A trace shows which of
      them Lemmings uses.
- [ ] `tools/build_launcher.sh` builds it, and from the GEMDOS drive Lemmings reaches its title on
      ST TOS 1.04. Every file it opens is in Hatari's GEMDOS trace, with no `Rwabs` on C:.
- [ ] The same build from the PPDRIVER image, the reference, before and after.
- [ ] `tools/dev/all_harness.sh` still passes. PP's own launcher is unchanged, so its round trips
      hold.

## Acceptance

From the GEMDOS drive, on ST TOS 1.04, the rebuilt Lemmings reaches its title, with its file
requests in Hatari's trace. From PPDRIVER it does as before. `all_harness.sh` passes.

## Notes
