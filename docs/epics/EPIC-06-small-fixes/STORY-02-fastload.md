---
id: STORY-02
epic: EPIC-06
title: S3: the fastload bit (Spy vs Spy 2 first)
status: done
---

## Goal

The three games whose start program gave its stack back run from the GEMDOS drive, with the
fastload bit set in the program each one starts.

## Tasks

- [x] A tool sets bit 0 of byte 25 of the header in a user's copy of `SPY2.BOY`, `HARRIER.TOS` and
      `AQUANAUT.EXE`, after checking that the file is the expected program. Run twice, it
      changes nothing.
- [x] Spy vs Spy 2, Strike Force Harrier and Aquanaut from the GEMDOS drive on the three setups,
      played past their first loads.
- [x] The same, patched, from PPDRIVER: the bit changes nothing there.

## Acceptance

The three games run from the GEMDOS drive on the three setups, patched by the tool.

## Notes

**2026-10-26.** `tools/set_fastload.py <program> <out>` knows the three programs by SHA-256: an
original gets bit 0 of header byte 25, a program with the bit already is written as it is (run
twice: the same bytes), any other file is refused and nothing written (`SPY2.PRG` tried). The
epic's probe `src/probes/epic06/fix_run.py <row> --fastload [--disk ppdriver]` patches a copy of the
game's folder with it. Outputs in `tools/dev/builds/epic06/runs-fastload-1210/`:

| game (row) | GEMDOS drive, each of ST 1.04, STE 1.62, STE 2.06 | PPDRIVER, patched |
|---|---|---|
| Spy vs Spy 2 (1804) | `SPY2.PRG` starts `SPY2.BOY`, 11 files, the game in play | the same on the three, 37 `Rwabs` on C: |
| Strike Force Harrier (1813) | `START.TOS` starts `HARRIER.TOS`, 6 files, a mission flown to its combat summary | the same on the three, 27 `Rwabs` |
| Aquanaut (1826) | `AQUANAUT.PRG` starts `AQUANAUT.EXE`, its title | 1.04 and 1.62 its title; 2.06 back to the desktop |

No fault. Unpatched, Spy vs Spy 2 from the GEMDOS drive (ST 1.04) starts `SPY2.BOY` and the desktop
comes back, as in the survey. Aquanaut opens no file once `AQUANAUT.EXE` is loaded: its title is
past its only load (the harness types keys and Aquanaut did not start on space; its fire button is
not reachable). Aquanaut on TOS 2.06: the list marks it "Hole" there (and on the Mega STE and the
Falcon): `FBHOLE.PRG` in its download writes a boot sector on a floppy in drive A that keeps low RAM
free at power-on. Without it, from PPDRIVER, the unpatched program halts the CPU and the patched one
quits to the desktop; from the GEMDOS drive, patched, it reaches its title with its credit lines
garbled. Neither is the bit's doing: TOS 2.06 needs the hole whatever the disk.
