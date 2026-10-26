# The launcher's file formats

The Gamex launcher's files for Lemmings use one packer, with a 32-byte header in front of each
packed file. `tools/unpack.py` unpacks them all. Each result matched Hatari's memory
at the start of that stage (runs `tools/dev/logs/*-ppdriver-chain`), apart from the few bytes
written into it before it starts. LEMLD2 is the launcher's main program. `text+` offsets are in its
text section.

## The packer

One routine, found in `START.TOS`'s stub (text+`$32`) and in LEMLD2 (text+`$B32`). It reads a byte
stream:

| control byte c | meaning |
| --- | --- |
| `$00` | end of stream |
| `$01`-`$7F` | c literal bytes follow |
| `$80`-`$BF` | one offset byte d: copy (c & `$3F`) + 3 bytes from d bytes back |
| `$C0`-`$FF` | offset bytes hi, lo: copy (c & `$3F`) + 4 bytes from hi×256+lo back |

It is not ICE. Only the game's own `FILES/CODE` and `FILES/MAIN` are ICE-packed.

## The packed-file header

The unpacker never reads these 32 bytes: the launcher skips them and knows the sizes in advance.

| offset | `START.TOS` payload | `LS2DD.FIC` | `D15R_H5.FIC` | `D15R_F5.FIC` |
| --- | --- | --- | --- | --- |
| 0 | `"C3" 00 00` | same | same | same |
| +2 long, packed size | 8,811 | 4,897 | 46,793 | 47,213 |
| +6 long, unpacked size | 35,230 | 7,168 | 91,460 | 91,512 |
| +10 long | `$1B046`, LEMLD2's BSS | `$7A007C00` (open) | 0 | 0 |
| +16, name | `LEMLD2.TOS` | `LS2DD` | `G558` | `GF558` |

## What each file unpacks to

- **`START.TOS`** is a GEMDOS program: a 230-byte text (the stub), an 8,844-byte data section (the
  header above and the packed LEMLD2), BSS `$11A14`, no relocations. The stub
  (`tools/dev/builds/epic02/start_text.lst`) copies the packed stream down to text+`$8D40`, copies
  its unpacker after it and jumps there. The unpacker writes LEMLD2 to text−28, so LEMLD2's 28-byte
  GEMDOS header lands in the last 28 bytes of the basepage and its text on the stub's own text. It
  then relocates LEMLD2 at that text base with the standard GEMDOS table, fills in the basepage's
  text, data and BSS fields, clears memory from the relocation table up to itself, and jumps to the
  text base.
- **`LEMLD2.TOS`** is 35,230 bytes: text 34,910, BSS `$1B046`, 177 relocations. Relocated, it
  equals Hatari's memory at its entry: `$17A88` on ST TOS 1.04, `$17A68` on STE TOS 1.62, `$1D2E4`
  on STE TOS 2.06.
- **`LS2DD.FIC`** is the game's own loader, 7,168 bytes, run at `$70000`. The launcher patches 9
  bytes before it starts (`launch-chain.md`). At `$70A8E` the jump to the game goes to the launcher
  first. At `$70E38` the floppy loader becomes `jmp $85000`, the launcher's loader.
- **`D15R_H5.FIC`** and **`D15R_F5.FIC`** are GOS, a copy of TOS 1.04 that runs from RAM
  (`disk-layer.md`). They are 91,460 and 91,512 bytes, run at `$C0100`, and differ from byte `$6E9`
  on. `F5` is the Falcon build. LEMLD2 and GEMDOS write 32 bytes into `D15R_H5` before it starts:
  the drive (`$C0735`), the path `\LEMMINGS\FILES` (`$C0760`), the driver copy's entries for
  `hdv_bpb`, `hdv_rw` and `hdv_mediach` (`$D099A`, `$D099E`, `$D09A6`), its buffers in `_bufl`
  (`$D09DA`, `$D09DE`), and drives A, B, C in `_drvbits` (`$D09ED`).
- **`LEMMINGS.PCH`** is not packed. It is the picture LEMLD2 shows while it loads. A 6-byte header
  (`$0140 $00C8`, 320 × 200, then two flag bytes) is followed by two frames of a 32,000-byte screen
  and 19,232 bytes of colour data: 102,470 bytes in all.

## SHA-256 of the unpacked files

```
dae36fff1a766766de0477e9d22e84794c1ff844e1caaaf0cc56a7d63d05d0b6  LEMLD2.TOS
aea82756c309e65d9cd5fb4ac71538c36d12bb5ec64eabc57e13f7ab916c85cf  LS2DD.bin
53ef0628cc158898d288048356a4562b63ea44d4fcaaed3fbc96922d26b06fbc  D15R_H5.bin
5f0c5b4ef69d3ee918e6b0f882e0d8e0c6c9f73c919f983c74df20ec4a6529c1  D15R_F5.bin
```
