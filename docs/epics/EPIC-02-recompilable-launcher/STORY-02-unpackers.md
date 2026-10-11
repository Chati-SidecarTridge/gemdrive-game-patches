---
id: STORY-02
epic: EPIC-02
title: Unpackers, proven against Hatari's memory
status: done
---

## Goal

Every packed launcher file unpacked on the host into exactly the bytes Hatari holds when that
stage runs.

## Tasks

- [x] The formats described in `src/notes/`: `START.TOS`'s stub and payload, the `.FIC` header
      and payload, `LEMMINGS.PCH`.
- [x] `tools/unpack.py` (standard library only) for each format; each output's SHA-256 equal to
      its STORY-01 dump, apart from relocations and fields the launcher fills in at run time,
      which are listed.
- [x] H-01 and H-02 confirmed or refuted.

## Acceptance

For every stage, the unpacked file equals Hatari's dump, with every difference explained.

## Notes

**Done 2026-10-11.** The formats are in `src/notes/launcher-formats.md`; `tools/unpack.py start |
fic | relocate` (standard library) unpacks them. Against the dumps of STORY-01:

- `LEMLD2.TOS` (35,230 bytes, 177 relocations), relocated to the text base: equal to Hatari's
  memory at its entry, 34,938 bytes, 0 differences, on ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06.
- `LS2DD.bin` (7,168 bytes): 9 bytes differ, the block's two patches at `$70A8E` (the jump to the
  game, `$400` → `$8014C`) and `$70E38` (`jmp $85000` over LS2DD's own loader).
- `D15R_H5.bin` (91,460 bytes): 32 bytes differ, all written before D15R's first instruction:
  the current drive at `$C0734`, the `Dgetpath` result at `$C0760`, and the system variables
  LEMLD2 saves in D15R's area (`hdv_bpb`, `hdv_rw`, `hdv_mediach`, `_bufl`, `_drvbits`).
- `D15R_F5.bin` (91,512 bytes): unpacked, header sizes match; no dump, since only a Falcon loads
  it (STORY-01).
- `LEMMINGS.PCH` is not packed: a 6-byte header and two frames of a screen and colour data, the
  picture shown while loading.

The match lengths settle the first pass's disagreement: +3 and +4. H-01 confirmed, H-02 confirmed
with additions (`ITERATIONS.md`). The first pass's decoders were not reused.
