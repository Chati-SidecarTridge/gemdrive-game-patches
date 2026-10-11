---
id: STORY-03
epic: EPIC-01
title: The embedded driver, confirmed or refuted
status: done
---

## Goal

A verdict on Diego's guess (H-07): is the PPera driver embedded in the launcher what fails in
GEMDRIVE mode?

## Tasks

- [x] Where the launcher carries a driver of its own: the code, its load address and how it is
      installed (vectors, system variables), seen in memory on the reference run.
- [x] Whether that driver is PPDRIVER itself, the one that booted the reference: its code
      compared with the driver in `../atari-hd/assets/pp_boot_blob.bin` (LBA 2 to 14), and with
      what PPDRIVER leaves resident before the launcher starts. Copied from memory, carried in
      the launcher's own files, or different: recorded here.
- [x] Whether the failing path of STORY-02 runs through that driver, shown with breakpoints.
- [x] An experiment on a patched copy (never `LEMMINGS/`): with the driver's disk access bypassed
      or answered by hand, the GEMDRIVE run gets further; reverting brings the stop back.
- [x] H-03 and H-07 confirmed or refuted, with the evidence.

## Acceptance

H-07's verdict, backed by the breakpoint runs and the before/after experiment.

## Notes

**Done 2026-10-11.** `src/notes/gemdrive-failure.md` §3–4.

- The launcher carries no driver. It copies the **resident** one, from the XBRA header before
  `hdv_bpb` (`$12954` on ST 1.04), 7,204 bytes to `$B7180`, and patches the copy at fixed
  offsets: the XBRA "old vector" slots and vector table (`+$9`, `+$3F`, `+$43B`, `+$495..+$49D`)
  now point at D15R's routines (`$C19BE`, `$C1CA4`, `$C1B6E`), the BPB and buffer pointers
  (`+$771..+$78B`) at `$B7904`, `$AF100`…; the copy's entries go into `$472/$476/$47E`, `$47A`
  gets `$C1F3E`, `pun_ptr` is cleared; `$84` ends up at `$C84A0`, a `TRAP #1` handler in D15R.
  Seen in the instruction trace of the primary path (`…-st-104-ppdriver-gate`, 176,044 lines)
  and the dumps of `…-st-104-ppdriver-drv` (resident and relocated copies, vectors before and
  after).
- Is it PPDRIVER? The resident driver is what PPDRIVER's boot sector loaded (LBA 2–14 at boot,
  seen in the ACSI trace) and `hdv_bpb` points into it. Its bytes do not match the blob's
  `.PRG` text (4,948 of 5,076 comparable bytes differ, 115 runs): the blob's program is not a
  plain image of the resident code. The launcher's files hold no driver: `D15R_H5.FIC` is the
  loader D15R, at `$C0100`, which reads sectors through whatever driver `Rwabs` reaches.
- The failing path does not run through the driver: it is the fallback the launcher takes when
  there is none (STORY-02).
- The experiments, with the debugger instead of patched binaries (C-01 kept trivially):
  sector 0 answered with the real PP boot sector → the launcher goes on and D15R stops at
  `Getbpb(2)` = 0; the BPB answered → `Rwabs` = -15 and an address error in LS2DD; `Mediach` and
  the first two reads answered → D15R's error restore from an unset context, a bus error, a
  halt. Each plain run brings the earlier stop back. `src/probes/epic01/fallback_probe.py`,
  `serve_rwabs.py`.
- H-03 confirmed with corrections, H-07 confirmed in substance and restated (`ITERATIONS.md`).
