---
id: STORY-05
epic: EPIC-00
title: The Hatari harness
status: done
---

## Goal

`tools/dev/hatari_harness.py` starts the loader on a given machine, TOS and disk setup, headless,
records what it does, and ends with PASS or FAIL against an expected milestone, with the
evidence. Every experiment from EPIC-01 on is one call to it.

## Tasks

- [x] Launch: the machine, TOS, RAM (at least 1 MB, C-04) and disk setup from STORY-04; a clean
      `HOME` per run; SDL's dummy video and audio drivers, `--sound off`,
      `--confirm-quit false`, `--fast-forward`; `--log-file`, `--screenshot-dir` and the run's
      traces in a run folder under `tools/dev/logs/`; output read through a pseudo-terminal, not
      a file, which arrives late (`sidecartos-config` EPIC-00 STORY-03).
- [x] The loader starts on its own: `START.TOS` autostarted from the drive (`--auto`), or the
      equivalent where the driver must boot first.
- [x] What the run records, from Hatari's own traces rather than from addresses guessed by the
      first pass: the GEMDOS calls with their file names, the XBIOS and BIOS calls, ACSI
      commands, and the program's exit or the PC where it stops. A trace is bounded by the
      run's time limit and never grows to the first pass's 800 MB.
- [x] Milestones: a run's expectations are a list of events in order (for example "`Fopen`
      `LS2DD.FIC`", "screen shows the loader's info text", "no disk access for 10 s"); the
      harness reports the last one reached. Keys go through the control socket, sent only when
      a milestone says the program is waiting for one.
- [x] Debugger hooks: a run may pass a Hatari debugger script (`--parse`) for breakpoints and
      memory dumps at chosen addresses, saved into the run folder. EPIC-02 uses this to dump each
      unpacked stage.
- [x] A screenshot per milestone and on every failure; a time limit per milestone; Hatari killed
      on expiry and no Hatari process left after any run.
- [x] After every run: `shasum -a 256 -c LEMMINGS.sha256` passes (C-01), checked by the harness.

## Acceptance

`python3 tools/dev/hatari_harness.py` boots the pristine loader on the GEMDOS drive of an ST with
TOS 1.04, prints the milestones it reached, and ends with PASS or FAIL and the run folder's path,
in under a minute, with no Hatari left running. A deliberately impossible milestone gives FAIL
with a screenshot.

## Notes

What the pristine loader does on each setup is not this story's question: the first runs only
show that the harness sees it. EPIC-01 runs the matrix and reads the results.

**Done 2026-10-11.** `tools/dev/hatari_harness.py`, standard library only, with
`tools/dev/expect/launcher-start.exp` and `tools/dev/expect/must-fail.exp`.

- Launch: `--machine st|ste`, the TOS of the setup, `--memsize 1` (MB, the default), the run's
  own copy of the disk (`--harddrive <run>/drive` or `--acsi 0=<run>/ppdriver.img`, an APFS
  clone), `--auto C:\LEMMINGS\START.TOS`, `--trace gemdos,bios,xbios,scsi_cmd`, fast-forward,
  no sound, no status bar, `--confirm-quit false`, a clean `HOME`, SDL's dummy drivers, the
  control socket in a short `/tmp/hh*` folder, and Hatari's output read through a
  pseudo-terminal. The command line is saved as `command.txt`.
- Autostart works on both disks: Hatari serves its own `DESKTOP.INF` with the autostart line
  when TOS opens the real one; TOS then does `Dsetpath("C:\LEMMINGS\")` and
  `Pexec(0, "C:\LEMMINGS\START.TOS")`.
- What is recorded comes from Hatari's own traces, no address of the first pass: every GEMDOS
  call with its file names (on both disks; in GEMDRIVE runs also the host path), BIOS and XBIOS
  calls (`Rwabs` among them), and ACSI commands (`HDC: READ SECTOR … LBA …`). At the end the
  harness dumps the registers through the control socket (`hatari-debug r`) and puts the PC in
  `result.txt`. Size of `hatari.out` after 20 s: about 6,000 lines in GEMDRIVE, 32,000 with
  PPDRIVER (its ACSI commands), no CPU trace.
- Debugger hooks: `--parse dump-start.dbg` with `b pc = TEXT && pc < $e00000 :once :trace :file
  dump-start.ini` and `savebin start_text.bin TEXT 230` stopped at the first instruction of
  `START.TOS` and wrote 230 bytes, equal to its text section in `LEMMINGS/START.TOS`. Learned on
  the way: `TEXT` alone first matches TOS's own ROM program (hence `pc < $e00000`), and Hatari
  runs a `:file` from that file's folder, so the harness copies the script and its `:file`s
  into the run folder, where relative dumps then land.
- Keys: `key space` while the launcher shows its picture ended its wait loop after 150
  `Cconis()` polls instead of 801. Scan codes go to Hatari in hex: it takes a single character
  as a character (`1` types the digit), and two or more as a number. `key f9` during the
  launcher's first poll loop changed nothing visible (1,178 `Crawio` polls, as without a key):
  how the launcher reads F9 is EPIC-01's to find.
- Acceptance: `hatari_harness.py --setup st-104 --disk gemdrive --expect
  tools/dev/expect/launcher-start.exp` PASS, 6/6 steps (`start-tos`, `info-text`, `pch`,
  `d15r`, `ls2dd`, `files-dir`) in 16.7 s. `must-fail.exp` with `--step-time 10`: FAIL at step
  `never` after 13.7 s, with `shots/fail.png`. No Hatari left after either; `LEMMINGS/`
  unchanged (checked by the harness after every run).

Seen on the way, recorded for EPIC-01 and not concluded here: on ST TOS 1.04 the pristine
launcher opens `LEMMINGS.PCH`, `D15R_H5.FIC` (not `F5`) and `LS2DD.FIC` and changes into `FILES`
on both disks. From the PPDRIVER image it then reads on through `Rwabs` from code at `$C83CE`
and shows the Lemmings title menu ("1. Loss of sleep") within 20 s. From the GEMDOS drive it
prints "This prg. requires PP, AHDI or Hddriver hard disk driver. Real hard disk emulation under
Steem or Hatari. So Pasti, ACSI, IDE HD ... Proper D15R_*.FIC file in it's DIR or in C:\GAMEX"
and TOS reads `DESKTOP.INF` again.
