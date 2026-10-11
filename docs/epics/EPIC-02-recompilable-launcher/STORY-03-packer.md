---
id: STORY-03
epic: EPIC-02
title: A packer the launcher accepts
status: done
---

## Goal

`tools/pack.py` turns an unpacked stage back into a launcher file that the original launcher code
unpacks correctly, so a stage rebuilt from source can go back on the disk.

## Tasks

- [x] `tools/pack.py` for each packed format, standard library only.
- [x] Round trip on the host: `unpack(pack(x)) == x` for every stage.
- [x] Round trip in Hatari: the original files with one stage replaced by its repacked copy boot
      the reference to the level load (`reference-first-level.exp`); the dump at that stage's entry equals the original's.
- [x] Sizes before and after for every repacked file. Byte-identical packed files are not
      required, since PP's packer is unknown; the same unpacked bytes are.

## Acceptance

Every stage repacked by our packer boots in the reference with the same memory as the original.

## Notes

**Done 2026-10-11.** `tools/pack.py fic | start` (standard library): an optimal parse of PP's
format (`src/notes/launcher-formats.md`), so never longer than his. `pack.py start` reuses the
original stub and sets its three size constants (data size, text+data end, longs to copy) for the
new payload, after checking that the in-place unpacking never writes over unread input.

| file | PP's | ours |
| --- | --- | --- |
| `START.TOS` | 9,106 | 9,014 |
| `LS2DD.FIC` | 4,929 | 4,908 (LEMLD2 reads it with a fixed count of 4,929) |
| `D15R_H5.FIC` | 46,825 | 45,786 (read into a 51,000-byte buffer) |
| `D15R_F5.FIC` | 47,245 | 46,207 |

- On the host: `tools/unpack.py` on each repacked file gives back the unpacked stage byte for
  byte (`pack.py` also checks it before writing).
- In Hatari, `src/probes/epic02/repack_roundtrip.sh`: the original files with `START.TOS`,
  `LS2DD.FIC`, `D15R_H5.FIC`, or all three replaced boot the PPDRIVER reference to the level
  load, PASS 13/13 each (ST TOS 1.04, runs `20261011-170700`, `-170723`, `-170746`, `-170810`
  `-st-104-ppdriver-chain`). Every stage's dump at its entry (LEMLD2, D15R, the block, LS2DD,
  the loader) and the game's memory at the hand-over equal the original run's
  (`…-165409-…`); only the packed forms differ.
- `D15R_F5.FIC` was repacked and round-tripped on the host only: no ST or STE loads it.
