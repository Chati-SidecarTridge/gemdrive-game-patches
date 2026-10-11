---
id: STORY-02
epic: EPIC-01
title: The GEMDRIVE runs, and where they part from the reference
status: done
---

## Goal

The same pristine launcher in GEMDRIVE mode on every setup: where it stops, what is on screen, and
the first disk call or reply that differs from the reference.

## Tasks

- [x] Each setup run in GEMDRIVE mode with the reference's milestones; the table recorded here:
      setup, last milestone, screenshot, wall time.
- [x] For each setup, the first difference from the reference's disk calls, narrowed with
      breakpoints to the instruction that takes the other path and the value that made it.
- [x] How Hatari's GEMDRIVE mode answers the calls that differ (`Rwabs`, `DMAread`, the ACSI
      registers, the driver vectors), read in `../hatari`'s sources and seen in the run.
- [x] H-04 and H-06 confirmed or refuted, with the trace lines.

## Acceptance

For every setup, the instruction address where the GEMDRIVE run parts from the reference and
the input that differs, each backed by a run folder.

## Notes

**Done 2026-10-11.** Details and run names in `src/notes/gemdrive-failure.md` §3.

| setup | GEMDRIVE: last milestone | then | wall |
| --- | --- | --- | --- |
| ST TOS 1.04 | `files-dir` | the error text ("This prg. requires PP, AHDI or Hddriver…"), a key wait, exit to the desktop | 17 s |
| STE TOS 1.62 | `files-dir` | same | 17 s |
| STE TOS 2.06 | `files-dir` | one XBIOS `DMAread`, then the same | 21 s |

- The instruction: text+`$324` `movea.l $472.w,a1` / `$328` `cmpi.l #"PPHD",-8(a1)` / `$330`
  `bne.w text+$482`. The input: `$472` (`hdv_bpb`) holds TOS's ROM routine on a GEMDOS drive
  (`$FC173C`, `$E01914`, `$E05210`) and PPDRIVER's on the image (`$12960`, `$129A4`, `$14DC4`,
  preceded by `"XBRA" "PPHD"`); `pun_ptr` (`$516`) is 0 against a `PUN_INFO`. Observed at the
  `cmpi` and the `bne` on all six runs (`src/probes/epic01/gate_probe.py`), with the live
  disassembly and the flags.
- Hatari's GEMDRIVE: a cartridge program at `$FA0000` intercepts `TRAP #1` for the GEMDOS drive
  (`../hatari/src/cart.c`); BIOS and XBIOS calls are traced only (`bios.c`, `xbios.c`), so
  `Getbpb(2)`, `Rwabs(…,2)` and `DMAread` reach TOS ROM, which has no driver for drive C:
  `Getbpb(2)` returned 0 and `Rwabs` returned -15 in STORY-03's by-hand runs; `DMAread` returned
  -1; the raw ACSI path's MFP wait timed out (`d0 = -1` at text+`$BD4`). The instruction-level
  trace of the fallback is in each gate run's `windows.txt`.
- Learned about Hatari's debugger on the way, kept in `tools/dev/README.md`: a trap's traced PC
  is the return address; a `:once` breakpoint set from a hit on the same PC fires at once;
  values of `w` are in the current (decimal) base; `cpu_exception` also logs interrupts and
  floods the output; TOS 1.04 marks its vectors with the vector number in the high byte, so
  its handler is reached at `$3FC0B0A` for an address error.
- H-04 refuted, H-06 refuted (`ITERATIONS.md`).
