---
id: STORY-02
epic: EPIC-02
title: Unpackers, proven against Hatari's memory
status: todo
---

## Goal

Every packed launcher file unpacked on the host into exactly the bytes Hatari holds when that
stage runs.

## Tasks

- [ ] The formats described in `src/notes/`: `START.TOS`'s stub and payload, the `.FIC` header
      and payload, `LEMMINGS.PCH`.
- [ ] `tools/unpack.py` (standard library only) for each format; each output's SHA-256 equal to
      its STORY-01 dump, apart from relocations and fields the launcher fills in at run time,
      which are listed.
- [ ] H-01 and H-02 confirmed or refuted.

## Acceptance

For every stage, the unpacked file equals Hatari's dump, with every difference explained.

## Notes
