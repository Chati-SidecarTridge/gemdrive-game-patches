---
id: STORY-03
epic: EPIC-00
title: The round-trip check: a source that reassembles to the original bytes
status: done
---

## Goal

The test that every reconstructed source in this repository must pass: assembled, it gives the
exact bytes of the original. The project's second goal is a loader rebuilt from source, and this
check tells a complete reconstruction from a listing that only looks right.

## Tasks

- [x] `tools/dev/roundtrip.sh <source.s> <reference.bin>`: assembles with `tools/dev/asm.sh` and
      compares; PASS, or FAIL with the first differing offset, both bytes and both SHA-256.
- [x] `tools/dev/listing2vasm.py [--verbose] <listing> <bin> <out.s>`: an objdump listing turned
      into a vasm source that reassembles; where vasm would pick another encoding than the
      original, or the bytes are data, it emits `dc.w`. Standard library only.
- [x] First use, on the smallest real piece: the 230-byte text section of the pristine
      `LEMMINGS/START.TOS` (file offsets 28 to 257). Listing, source, round trip: PASS.
- [x] A deliberate break (one operand changed in the source) gives FAIL at the right offset.

## Acceptance

`tools/dev/roundtrip.sh` prints PASS for the START.TOS text from its generated source, and FAIL
with the offset after a deliberate one-byte change.

## Notes

This is a tool test, not a reverse-engineering result: the generated source has no labels or
comments yet. Annotating it is EPIC-02's work.

**Done 2026-10-11.**

- `tools/dev/roundtrip.sh` assembles into `tools/dev/builds/roundtrip/` and compares in Python:
  PASS with size and SHA-256, or FAIL with the first differing offset, both bytes, both
  lengths and both SHA-256.
- `tools/dev/listing2vasm.py` converts objdump's GNU syntax to Motorola syntax (registers,
  `(a0)+`, `-(a0)`, `(d,a0)`, `(d,a0,d0.w)`, `($target,pc)`, register lists, sized
  mnemonics), puts each line's address in a comment, and assembles in the pinned toolchain until
  every line gives its original bytes. Absolute operands are tried `.w` then `.l`; a line that
  vasm rejects or that gives other bytes after every try becomes `dc.w` with the disassembly in
  its comment; runs of 8 or more zero bytes become one `dcb.b`. Branches and PC-relative lines
  are held as data until every other line matches, so a line of another length cannot push them
  out of range; then they come back. It takes the original binary as a third argument, because
  the listing cannot always show every byte, and checks the whole result against it.
- First use, the 230-byte text of the pristine `START.TOS`: 82 lines, all 82 as instructions,
  2 passes, about 1 s; round trip PASS, `0ca1e48b…d07f`. With `moveq #44,d2` at `$28` changed to
  `#45`: FAIL at offset `0x29`, assembled `2d`, original `2c`.
- Stress test on a larger input, the first pass's `lemld2.text` (34,910 bytes): 11,291 lines,
  11,105 as instructions and 186 as data (68020 forms, `.short`, other encodings such as
  `btst #123,d0`), 5 passes, about 6 s; round trip PASS, `5df49e64…90f7`.

Found on the way, each fixed and kept as a rule:

- objdump hides runs of zero bytes behind a `...` line, and stops before a last instruction cut
  short by the end of the file: `disasm.sh` passes `-z`, and the converter takes its bytes from
  the binary, not the listing.
- objdump prints the 8-bit displacement of an indexed operand as 16 hex digits without `0x`
  (`%fp@(000000000000004d,%d2:w)`): read as hex, signed.
- vasm stops after 5 errors by default: `asm.sh` passes `-maxerrors=0`.
- **Docker Desktop served a container a source the host had just rewritten in place at its old
  length**, so vasm assembled a file cut off mid-line (the listing showed `dbf %d0,0x84` for
  `0x8456`). Every container input now goes through `tc_stage`: a copy under a fresh name in
  `tools/dev/builds/.stage/`, removed after the run, never next to the original (a first version
  staged next to it and left a copy in `_archive/`, removed). `asm.sh` adds the source's folder
  to vasm's include path.
