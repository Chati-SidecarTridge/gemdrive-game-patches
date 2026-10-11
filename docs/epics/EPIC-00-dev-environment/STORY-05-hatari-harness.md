---
id: STORY-05
epic: EPIC-00
title: The Hatari harness
status: todo
---

## Goal

`tools/dev/hatari_harness.py` starts the loader on a given machine, TOS and disk setup, headless,
records what it does, and ends with PASS or FAIL against an expected milestone, with the
evidence. Every experiment from EPIC-01 on is one call to it.

## Tasks

- [ ] Launch: the machine, TOS, RAM (at least 1 MB, C-04) and disk setup from STORY-04; a clean
      `HOME` per run; SDL's dummy video and audio drivers, `--sound off`,
      `--confirm-quit false`, `--fast-forward`; `--log-file`, `--screenshot-dir` and the run's
      traces in a run folder under `tools/dev/logs/`; output read through a pseudo-terminal, not
      a file, which arrives late (`sidecartos-config` EPIC-00 STORY-03).
- [ ] The loader starts on its own: `START.TOS` autostarted from the drive (`--auto`), or the
      equivalent where the driver must boot first.
- [ ] What the run records, from Hatari's own traces rather than from addresses guessed by the
      first pass: the GEMDOS calls with their file names, the XBIOS and BIOS calls, ACSI
      commands, and the program's exit or the PC where it stops. A trace is bounded by the
      run's time limit and never grows to the first pass's 800 MB.
- [ ] Milestones: a run's expectations are a list of events in order (for example "`Fopen`
      `LS2DD.FIC`", "screen shows the loader's info text", "no disk access for 10 s"); the
      harness reports the last one reached. Keys go through the control socket, sent only when
      a milestone says the program is waiting for one.
- [ ] Debugger hooks: a run may pass a Hatari debugger script (`--parse`) for breakpoints and
      memory dumps at chosen addresses, saved into the run folder. EPIC-02 uses this to dump each
      unpacked stage.
- [ ] A screenshot per milestone and on every failure; a time limit per milestone; Hatari killed
      on expiry and no Hatari process left after any run.
- [ ] After every run: `shasum -a 256 -c LEMMINGS.sha256` passes (C-01), checked by the harness.

## Acceptance

`python3 tools/dev/hatari_harness.py` boots the pristine loader on the GEMDOS drive of an ST with
TOS 1.04, prints the milestones it reached, and ends with PASS or FAIL and the run folder's path,
in under a minute, with no Hatari left running. A deliberately impossible milestone gives FAIL
with a screenshot.

## Notes

What the pristine loader does on each setup is not this story's question: the first runs only
show that the harness sees it. EPIC-01 runs the matrix and reads the results.
