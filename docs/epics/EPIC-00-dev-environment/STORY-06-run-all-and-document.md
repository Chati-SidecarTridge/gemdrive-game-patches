---
id: STORY-06
epic: EPIC-00
title: Run everything, and document it
status: todo
---

## Goal

One command checks the whole environment, and the next session knows how to use it without
reading the scripts.

## Tasks

- [ ] `tools/dev/all_harness.sh`: builds the disk setups, runs the round-trip check and the
      harness on every setup of EPIC-00 (ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06, each in
      GEMDRIVE mode and from the PPDRIVER image), and prints one line per run: setup, milestone
      reached, PASS/FAIL, wall time.
- [ ] Its first full run recorded here, with the wall time of each session and of the whole.
- [ ] `tools/dev/README.md`: setup (`dev.cfg`), every script with an example, where runs and
      logs go, the rules (C-01, C-02, C-03).
- [ ] `CLAUDE.md` updated: the commands and the gotchas found in this epic.

## Acceptance

`tools/dev/all_harness.sh` runs end to end on this Mac and prints the table; `tools/dev/README.md`
and `CLAUDE.md` describe what exists and nothing that does not.

## Notes
