# The launcher's file formats

2026-10-11. Every format below is unpacked by `tools/unpack.py`, and the result was compared
with what Hatari holds when that stage starts (memory dumps at each stage's entry, runs
`tools/dev/logs/*-ppdriver-chain`). `text+` offsets are LEMLD2's.

## The packer

One routine, twice: in `START.TOS`'s stub (text+`$32`, run from a copy of itself) and in LEMLD2
(text+`$B32`, used for `D15R_*.FIC`, and for `LS2DD.FIC` from the copy at `$80100`). It reads a
byte stream from `a1` (the stub: `a6`) and writes to `a4`:

| control byte c | meaning |
| --- | --- |
| `$00` | end of stream |
| `$01`-`$7F` | c literal bytes follow |
| `$80`-`$BF` | one offset byte d; copy (c & `$3F`) + 3 bytes from d bytes back |
| `$C0`-`$FF` | offset bytes hi, lo; copy (c & `$3F`) + 4 bytes from hi×256+lo back |

Lengths are one more than they look: the copy loops are `dbf` on (c & `$3F`) + 2 and + 3. This
settles the first pass's disagreement: its decoder's +3/+4 was right, its notes' +2/+3 were not.
It is not ICE (`FILES/CODE` and `FILES/MAIN` are, and are the game's business).

## The packed-file header

32 bytes in front of every packed stream. The unpacking code never reads it: the launcher skips
it (`$81020`, `$20306` = buffer + 32) and knows its sizes in advance.

| offset | `START.TOS` payload | `LS2DD.FIC` | `D15R_H5.FIC` | `D15R_F5.FIC` |
| --- | --- | --- | --- | --- |
| 0 | `"C3" 00 00` | same | same | same |
| +2 long, packed size | 8,811 | 4,897 | 46,793 | 47,213 |
| +6 long, unpacked size | 35,230 | 7,168 | 91,460 | 91,512 |
| +10 long | `$1B046`, LEMLD2's BSS | `$7A007C00` (open) | 0 | 0 |
| +16, name | `LEMLD2.TOS` | `LS2DD` | `G558` | `GF558` |

The `.FIC` files are exactly 32 + packed size; `START.TOS`'s data section has one pad byte after
the stream (its length is even).

## `START.TOS`

A GEMDOS program: a 230-byte text (the stub), an 8,844-byte data section (the header above and
the packed LEMLD2), BSS `$11A14`, no relocations. The stub (`tools/dev/builds/epic02/start_text.lst`)
copies the packed stream to text+`$8D40` downwards, copies its unpacker after it and jumps there.
The unpacker writes LEMLD2 to text−28, so LEMLD2's 28-byte GEMDOS header lands in the last 28
bytes of the basepage and its text on the stub's own text. Then it relocates LEMLD2 to the same
text base (the standard GEMDOS table: first long an offset, then bytes, 1 = skip 254, 0 = end),
fills the basepage's text/data/BSS fields, clears from the relocation table up to itself, and
`jmp (a0)` to the text base.

**LEMLD2.TOS** (35,230 bytes): text 34,910, data 0, BSS `$1B046`, no symbols, 177 relocations.
Relocated by `tools/unpack.py relocate` to each setup's text base it equals Hatari's memory at
LEMLD2's entry byte for byte, header included: ST TOS 1.04 (`$17A88`), STE TOS 1.62 (`$17A68`),
STE TOS 2.06 (`$1D2E4`).

## `LS2DD.FIC`

7,168 bytes, run at `$70000`, entered at `$7005A`. Equal to Hatari's memory at its entry except
for the 9 bytes the block at `$80100` patches before starting it (`launch-chain.md`):

| address | LS2DD's own | at its entry | |
| --- | --- | --- | --- |
| `$70A8E` | `$00000400` | `$0008014C` | the long of LS2DD's jump to the game at `$400`, sent to the block's code that patches MAIN first |
| `$70E38` | `48E7 3FFE 4BFA` (`movem.l d2-d7/a0-a6,-(sp)`, `lea …`) | `4EF9 0008 5000` (`jmp $85000`) | LS2DD's own floppy loader, replaced by PP's loader |

## `D15R_H5.FIC` and `D15R_F5.FIC`

91,460 and 91,512 bytes, run at `$C0100`. The two builds differ from byte `$6E9` on (`F5` is the
Falcon build, `launch-chain.md`). `D15R_H5` equals Hatari's memory at D15R's first instruction
(`$C02BC`) except for 32 bytes in 8 runs, all written before it by LEMLD2 or by GEMDOS for it:

| address | written | by |
| --- | --- | --- |
| `$C0735` | `02` | LEMLD2 stores `Dgetdrv`'s answer (drive C) in the word at `$C0734` (text+`$308`) |
| `$C0760`… | `\LEMMINGS\FILES` | GEMDOS, for LEMLD2's `Dgetpath($C0760, 0)` |
| `$D099A`, `$D099E`, `$D09A6` | `$B718C`, `$B71C2`, `$B75BE` in place of `$C19BE`, `$C1CA4`, `$C1B6E` | LEMLD2's copies of `hdv_bpb`, `hdv_rw`, `hdv_mediach` in D15R's save area (base `($C07E6)` + `$C0800` = `$D0528`, offset = the system variable's address): the driver copy's entries in place of D15R's own routines |
| `$D09DA`, `$D09DE` | `$B78F0`, `$B7918` in place of `$D65E8`, `$D6610` | `_bufl` (`$4B2`, `$4B6`): buffers in the driver copy |
| `$D09ED` | `07` | `_drvbits` (`$4C2`): A, B, C |

D15R starts with a table of five word offsets (`$10`, `$34`, `$70`, `$1BC`, `$1CA`); LEMLD2 calls
`$C0100` + the fourth (`$C02BC`) with `a1 = $FFFAA`.

## `LEMMINGS.PCH`

Not packed. Read by LEMLD2 (text+`$20E4`) as a 6-byte header, `$0140 $00C8` (320 × 200) and two
flag bytes (`$FD $FF`; LEMLD2 shows a second frame when the first is not 0), then two frames of a
32,000-byte screen and 19,232 bytes (601 × 32, colour data: presumably the "Photochrome" cover
pictures of PP's site; not decoded). It is the picture LEMLD2 shows while it loads the rest.
Total 6 + 2 × (32,000 + 19,232) = 102,470 bytes, the file's size.

## SHA-256 of the unpacked files

```
dae36fff1a766766de0477e9d22e84794c1ff844e1caaaf0cc56a7d63d05d0b6  LEMLD2.TOS
aea82756c309e65d9cd5fb4ac71538c36d12bb5ec64eabc57e13f7ab916c85cf  LS2DD.bin
53ef0628cc158898d288048356a4562b63ea44d4fcaaed3fbc96922d26b06fbc  D15R_H5.bin
5f0c5b4ef69d3ee918e6b0f882e0d8e0c6c9f73c919f983c74df20ec4a6529c1  D15R_F5.bin
```
