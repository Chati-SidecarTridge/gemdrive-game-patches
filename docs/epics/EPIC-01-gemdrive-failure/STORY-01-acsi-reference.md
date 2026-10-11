---
id: STORY-01
epic: EPIC-01
title: The reference: the game booting from a PPDRIVER image
status: done
---

## Goal

The pristine launcher booting Lemmings in Hatari from the PPDRIVER image of EPIC-00 STORY-04, with
every step of a good boot written down as the harness's expected milestones. This is what the
GEMDRIVE runs are compared with.

## Tasks

- [x] The pristine launcher run from the PPDRIVER image on each setup of the epic; the milestones it
      shows up to the first level, as harness expectations.
- [x] The disk calls of a good boot recorded (GEMDOS with file names, BIOS, XBIOS, ACSI
      commands), in order, from the run's traces.
- [x] If the game does not boot from the PPDRIVER image on some setup, the setup, the stop and its
      evidence recorded here, and Diego told before going on.

## Acceptance

A harness run per setup that reaches the first level from the PPDRIVER image, PASS, with its trace of
disk calls in the run folder.

## Notes

**Done 2026-10-11**, with one limit: the reference reaches the title menu and the first level's
data load on every setup, not the level itself (below).

- `tools/dev/expect/reference-first-level.exp`: `start-tos`, `pch`, `ls2dd`, `files-dir`, then
  D15R's sector reads `root-dir` (65), `psyglogo` (387×8 → `$60000`), `dmalogo` (397×8),
  `main-file` (815×100 → `$A00`), `intropar` (415×80 → `$10000`), `code-file` (499×76 → `$A00`),
  the title (no output for 4 s, about 17 s after start), a click on "1 PLAYER", `leveldat`
  (677×2), `level-020` (407×2 → `$41800`). PASS on ST TOS 1.04 (run
  `20261011-144024-st-104-ppdriver-first-level`, 34 s); the six gate runs of STORY-02 reach the
  title on STE 1.62 and 2.06 too.
- The disk calls of a good boot, every `Rwabs` mapped onto the image's directories and FAT, are
  the table in `src/notes/gemdrive-failure.md` §2: after `Dsetpath("FILES")` nothing goes
  through GEMDOS any more; D15R reads the root directory, the `LEMMINGS` and `FILES`
  directories, FAT copy 2 and then each file's clusters through BIOS `Rwabs` on drive C
  (1,024-byte logical sectors, logical *n* = DOS sectors 2*n*+1 and 2*n*+2), with `Mediach(2)`
  between reads and partial sectors through bounce buffers at `$B3100`/`$B5100`.
- The title menu is mouse-driven in IKBD absolute mode (`AbsMouseMode 295,155`,
  `ReadAbsMousePos` every frame); F1, F2, Return and Space do nothing. Hatari's control socket
  has no mouse motion and its debugger cannot write the ACIA (memory writes bypass the I/O
  handlers). The harness gained a `mouse x y` step that makes the game's own IKBD sender
  transmit a "load mouse position" command by rewriting its byte table at `$D0A0` for one frame
  (sender entry `$21A6`, exit `$E996`), then `event doubleclick` clicks. "1 PLAYER" is at
  (70,150) in the IKBD's coordinates; (70,125) misses it.
- **The game does not reach the first level in Hatari.** Right after `LEVEL020` is loaded it
  raises an address error at `$2B10` (`move.l (a0)+,(a1)+` with `a0 = $3E409`, odd, read from
  `($36,a3)`); TOS 1.04's handler ends in `Pterm(-1)` 27 times, the supervisor stack reaches
  `$66`, the CPU spins in LS2DD's fault catcher at `$700C8`. The 3,048 bytes at `$41800` equal
  `FILES/LEVEL020` (run `…-click-exc3`), so the loader is not the cause. Same with X = 72, with
  `--memsize 4`, and on STE TOS 2.06 (no `Pterm` there, the same end). Recorded as a candidate in
  `ITERATIONS.md`; Diego is told in the epic's report. The reference for this epic ends at the
  level load, which is enough for its comparison.
