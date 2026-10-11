---
id: STORY-04
epic: EPIC-02
title: Sources for every stage that reassemble
status: todo
---

## Goal

A vasm source per launcher stage in `src/` that reassembles to the stage's unpacked bytes, with its
code and data told apart, its entry points and absolute addresses labelled, and every routine
named and commented.

## Tasks

- [ ] A source for each stage of STORY-01, started with `tools/dev/listing2vasm.py`; code and data
      separated, entry points and absolute addresses labelled.
- [ ] Every routine named and given a one-line comment; the disk-access, file-loading and
      hand-over routines described in full.
- [ ] Relocations expressed as labels, so a change that moves code still assembles correctly.
- [ ] `tools/dev/roundtrip.sh` PASS for each stage, added to `tools/dev/all_harness.sh`.
- [ ] The signatures of each stage (its file header, its packer, the `PPHD` gate, D15R) written up
      in `src/notes/launcher-signatures.md` as byte patterns, for EPIC-03's survey to look for in
      other games.
- [ ] H-05 confirmed or refuted.

## Acceptance

`tools/dev/all_harness.sh` shows a PASS round trip for every stage; inserting a `nop` in a
stage's source reassembles with every label reference still correct.

## Notes

PP's published Gamex launcher sources (epic notes) guide the names and the structure; every name
taken from them has to fit our bytes.
