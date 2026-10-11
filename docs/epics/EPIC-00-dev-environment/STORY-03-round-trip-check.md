---
id: STORY-03
epic: EPIC-00
title: The round-trip check: a source that reassembles to the original bytes
status: todo
---

## Goal

The test that every reconstructed source in this repository must pass: assembled, it gives the
exact bytes of the original. The project's second goal is a loader rebuilt from source, and this
check tells a complete reconstruction from a listing that only looks right.

## Tasks

- [ ] `tools/dev/roundtrip.sh <source.s> <reference.bin>`: assembles with `tools/dev/asm.sh` and
      compares; PASS, or FAIL with the first differing offset, both bytes and both SHA-256.
- [ ] `tools/dev/listing2vasm.py <listing> <out.s>`: an objdump listing turned into a vasm source
      that reassembles; where vasm would pick another encoding than the original, or the bytes
      are data, it emits `dc.w`. Standard library only.
- [ ] First use, on the smallest real piece: the 230-byte text section of the pristine
      `LEMMINGS/START.TOS` (file offsets 28 to 257). Listing, source, round trip: PASS.
- [ ] A deliberate break (one operand changed in the source) gives FAIL at the right offset.

## Acceptance

`tools/dev/roundtrip.sh` prints PASS for the START.TOS text from its generated source, and FAIL
with the offset after a deliberate one-byte change.

## Notes

This is a tool test, not a reverse-engineering result: the generated source has no labels or
comments yet. Annotating it is EPIC-02's work.
