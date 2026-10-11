---
id: STORY-04
epic: EPIC-02
title: Sources for every stage that reassemble
status: done
---

## Goal

A vasm source per launcher stage in `src/` that reassembles to the stage's unpacked bytes, with its
code and data told apart, its entry points and absolute addresses labelled, and every routine
named and commented.

## Tasks

- [x] A source for each stage of STORY-01, started with `tools/dev/listing2vasm.py`; code and data
      separated, entry points and absolute addresses labelled.
- [x] Every routine named and given a one-line comment; the disk-access, file-loading and
      hand-over routines described in full.
- [x] Relocations expressed as labels, so a change that moves code still assembles correctly.
- [x] `tools/dev/roundtrip.sh` PASS for each stage, added to `tools/dev/all_harness.sh`.
- [x] The signatures of each stage (its file header, its packer, the `PPHD` gate, D15R) written up
      in `src/notes/launcher-signatures.md` as byte patterns, for EPIC-03's survey to look for in
      other games.
- [x] H-05 confirmed or refuted.

## Acceptance

`tools/dev/all_harness.sh` shows a PASS round trip for every stage; inserting a `nop` in a
stage's source reassembles with every label reference still correct.

## Notes

PP's published Gamex launcher sources (epic notes) guide the names and the structure; every name
taken from them has to fit our bytes.

**Done 2026-10-11.** Five sources, each made by `tools/dev/mksource.py` from a map and the
stage's bytes, each reassembling to them byte for byte:

| source | instructions | as `dc.w` | reassembles to |
| --- | --- | --- | --- |
| `src/start/start.s` | 82 | 0 | `START.TOS`'s text, 230 bytes |
| `src/lemld2/lemld2.s` | 6,349 | 8 | `LEMLD2.TOS`, 35,230 bytes: header, text and relocation table (`vasm -Ftos`) |
| `src/ls2dd/ls2dd.s` | 806 | 0 | LS2DD, 7,168 bytes |
| `src/d15r/d15r_h5.s` | 9,798 | 0 | D15R_H5, 91,460 bytes |
| `src/d15r/d15r_f5.s` | 9,814 | 0 | D15R_F5, 91,512 bytes |

- Code and data apart: code is what a trace reaches (`tools/dev/m68k.py`, lengths and flow, equal
  to objdump on all 11,450 of LEMLD2's instructions it decodes) from the map's entries, its
  pointer tables (D15R's GEMDOS, BIOS and XBIOS function tables, the GEMDOS dispatcher's switch,
  and the vectors and code pointers of its image of TOS's RAM) and the addresses
  Hatari executed (`src/probes/epic02/profile_probe.py`, `profile_addrs.py`: four profiles, from
  LEMLD2's entry to the title). The rest is `dc.b`, strings as text. The 8 `dc.w` in LEMLD2 are
  its 68010/68030 instructions for the Falcon and TT (`movec`, `pmove`), named in their comments.
- Every routine has a name and a one-line comment (no subroutine is left as `L_…`); TOS's names
  for system variables, vectors and registers come from `src/include/atari.i`. The launch, the
  block, the loader, D15R's `file_io` and the hand-over are described in full in
  `src/notes/launch-chain.md`.
- Labels for everything that moves: branch targets, PC-relative operands, LEMLD2's relocated
  longs (its relocation table is vasm's, equal to PP's), absolute addresses inside D15R and LS2DD,
  pointer tables, the block's and the loader's run addresses (`block_run+(label-block)`), and
  operands the code patches at run time (`trap1_old equ L_b7e+2`). `tools/dev/shiftcheck.py`
  inserts a `nop` in the middle of each source and checks every reference moved with its target:
  0 that stayed put, in all five.
- `tools/dev/all_harness.sh` runs the round trip and the `nop` check for every source (16 checks,
  PASS, 162 s, after the last change to the sources).
- `src/notes/launcher-signatures.md`: 12 byte patterns, each checked against Lemmings' files, for
  EPIC-03.
- H-05 confirmed with a correction (`ITERATIONS.md`).

Found on the way: D15R is TOS 1.04 in RAM, more than a GEMDOS: its GEMDOS with every function, its
BIOS and XBIOS traps, its floppy `hdv_*` routines byte for byte, and an image of TOS's low RAM
that `file_io` swaps in for each file the game reads (H-08, STORY-05). The Falcon build differs
in reading `TRAP #1`'s arguments past the 68030's format word. LS2DD's protection decrypts part
of it at run time; those bytes stay as stored. `listing2vasm.py` (EPIC-00) took `pea` for a
68030 instruction (its `p[a-z]` pattern); fixed.
