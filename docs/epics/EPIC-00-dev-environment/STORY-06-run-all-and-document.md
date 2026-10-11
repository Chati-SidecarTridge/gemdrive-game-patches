---
id: STORY-06
epic: EPIC-00
title: Run everything, and document it
status: done
---

## Goal

One command checks the whole environment, and the next session knows how to use it without
reading the scripts.

## Tasks

- [x] `tools/dev/all_harness.sh`: builds the disk setups, runs the round-trip check and the
      harness on every setup of EPIC-00 (ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06, each in
      GEMDRIVE mode and from the PPDRIVER image), and prints one line per run: setup, milestone
      reached, PASS/FAIL, wall time.
- [x] Its first full run recorded here, with the wall time of each session and of the whole.
- [x] `tools/dev/README.md`: setup (`dev.cfg`), every script with an example, where runs and
      logs go, the rules (C-01, C-02, C-03).
- [x] `CLAUDE.md` updated: the commands and the gotchas found in this epic.

## Acceptance

`tools/dev/all_harness.sh` runs end to end on this Mac and prints the table; `tools/dev/README.md`
and `CLAUDE.md` describe what exists and nothing that does not.

## Notes

**Done 2026-10-11.**

`tools/dev/all_harness.sh` also checks that the harness reports a failure (`must-fail.exp`),
that `LEMMINGS/` matches `LEMMINGS.sha256`, and that no Hatari is left. First full run, from an
empty `tools/dev/builds/`:

| check | result | detail | wall time |
| --- | --- | --- | --- |
| disks | PASS | gemdrive + ppdriver.img, 76 files | 1 s |
| round trip START.TOS text | PASS | 230 bytes, sha256 `0ca1e48b…` | 12 s |
| st-104 gemdrive | PASS | 6/6 steps, last files-dir | 16 s |
| st-104 ppdriver | PASS | 6/6 steps, last files-dir | 16 s |
| ste-162 gemdrive | PASS | 6/6 steps, last files-dir | 17 s |
| ste-162 ppdriver | PASS | 6/6 steps, last files-dir | 16 s |
| ste-206 gemdrive | PASS | 6/6 steps, last files-dir | 20 s |
| ste-206 ppdriver | PASS | 6/6 steps, last files-dir | 20 s |
| harness detects a failure | PASS | FAIL at step never, with a screenshot | 14 s |
| LEMMINGS.sha256 | PASS | 76 files unchanged | 0 s |
| no Hatari left | PASS | | 0 s |

Total 132 s, 0 failures. Of the 12 s of the round trip, about 3 s per Docker run (disassembly,
two assembly passes, the check).

Seen in the same runs, for EPIC-01 (`result.txt`, the PC after 10 s past `files-dir`): the three
GEMDRIVE runs end back in TOS ROM (`$FC07F8` ST 1.04, `$E0367A` STE 1.62, `$E021CE` STE 2.06),
with no disk access after `Dsetpath("FILES")`; the three PPDRIVER runs end in RAM (`$45D4`,
`$21C8`, `$2B1A`) after 31 `Rwabs` reads past `Dsetpath("FILES")`.

`tools/dev/README.md` covers setup, every script with examples, the run folder, the
expectations and debugger-script formats, the rules and the gotchas of this epic. `CLAUDE.md`
has a Commands section in place of the pre-EPIC-00 tool list, and the gotchas found here
(Docker's stale files, hex keys, never `stcmd`).
