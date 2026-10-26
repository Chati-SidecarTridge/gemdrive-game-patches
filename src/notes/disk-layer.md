# The disk layer: D15R and the driver it uses

This page shows what sits between Lemmings and the disk when the game runs from a hard disk with
`PPDRIVER`, the hard-disk driver the Gamex launcher requires. The game asks for files by name. D15R,
the launcher's build of GOS, is a copy of TOS 1.04 that runs from RAM. Its GEMDOS reads the files by
sectors through a copy of `PPDRIVER`. A GEMDOS drive, such as Hatari's or the Multidevice's
GEMDRIVE, has no sectors, so this chain cannot work on one as it is.

Read from the sources (`src/d15r/d15r_h5.s`, `src/lemld2/lemld2.s`) and runs on ST
TOS 1.04. LEMLD2 is the launcher's main program, which sets all this up (`launch-chain.md`).

## 1. D15R is TOS 1.04 in RAM

Aligned with the TOS 1.04 UK ROM, the 91,460 bytes of `D15R_H5` sort into three kinds:

| bytes | count | what |
| --- | --- | --- |
| the ROM's own | 54,640 (59.7%) | copied unchanged |
| relocated | 9,804 (10.7%) | a ROM address moved from `$FC0000` to around `$C0100`, or a RAM address plus `$D0528` |
| other | 27,016 (29.5%) | D15R's own code, its image of TOS's RAM, its edits to TOS |

So D15R is GOS as `GAMEXdoc.html` describes it, and more. It holds TOS 1.04's GEMDOS and also its
BIOS, XBIOS, floppy driver, start-up code and data. Its own 1,852 bytes at `$C0100` hold the entry
table and `file_io`. From `$D0528` it keeps an image of TOS's RAM: each variable sits at its TOS
address plus `$D0528`. The Falcon build, `D15R_F5`, is the same, except that its
GEMDOS entry, `trap1`, reads the function number past the 68030's format word.

## 2. D15R's entry points

D15R starts with a table of word offsets from `$C0100`:

| entry | offset | does |
| --- | --- | --- |
| `swap_low_ram` | `$0010` | swaps `$8`-`$7FF` with the image: TOS's vectors in, the game's out, or back |
| `tos_paths` | `$0034` | sets the drive and path to LEMLD2's |
| `file_io` | `$0070` | loads or saves a whole file by name, for the launcher's loader |
| `init` | `$01BC` | called once by LEMLD2 |
| `file_io_2` | `$01CA` | `file_io` for a second parameter set, never seen called (§4) |

`file_io` takes the file name, path, offset, length and buffer at `$C0730`. It swaps TOS's low RAM
in, calls `Fopen`, `Fseek`, `Fread` or `Fwrite`, and `Fclose` through `TRAP #1`, and swaps the
game's low RAM back.

D15R's GEMDOS reaches the disk through BIOS calls. `Rwabs` reads sectors. `Getbpb` returns the BPB,
the block that describes a volume's layout. `Mediach` asks whether the disk changed. They go to the
vectors `hdv_rw`, `hdv_bpb` and `hdv_mediach`, which LEMLD2 points at its copy of the driver.

## 3. What the launcher needs from the resident PPDRIVER

From `reuse_pp_driver` and `set_buffers` in `src/lemld2/lemld2.s`, checked against the memory dumps
in `gemdrive-failure.md` §3:

1. The XBRA id `PPHD` 8 bytes before the routine `hdv_bpb` points to.
2. 7,204 bytes from the XBRA header that still work when copied to `$B7180`.
3. `hdv_rw` and `hdv_mediach` in that block, found by their distance from `hdv_bpb`.
4. Three slots holding TOS's own disk routines, which LEMLD2 replaces with D15R's floppy routines.
5. GEMDOS buffer headers where LEMLD2 expects them. It builds four 8 KB buffers from `$AF100`.
6. `pun_ptr` and the cookie jar pointer, saved into the image as found.

The game then calls `hdv_rw` for every read, in 1,024-byte records on drive C, and `hdv_mediach`
before each access. A replacement driver would have to provide all of this, laid out the same way.

## 4. Every call the game makes, from the hand-over to the level load

Run `20261011-182600-st-104-ppdriver-disk-calls` on ST TOS 1.04 (PASS, 13/13):

| file | when | records the driver reads |
| --- | --- | --- |
| `"FORM…"` | not a file name: the loader skips it | none |
| `IntroPar`, to `$10000` | the intro | 263, 415 × 80, 495, 496 |
| `CODE`, to `$200` | the game | 497, 498, 499 × 76, 575 |
| `leveldat` | the title screen | 263, 264, 677 × 2, 679, 680 |
| `level020` | after the click on "1 PLAYER" | 263, 407 × 2, 409 |

In all: 3 calls to the loader at `$85000`, 5 to `file_io`, none to `file_io_2`. The driver copy
gets 16 calls to `hdv_rw`, 139 to `hdv_mediach` and none to `hdv_bpb`. Names arrive in mixed case,
and D15R's GEMDOS matches them regardless, as TOS does.

## 5. For the solution

The game's requests reach GEMDOS as `Fopen` and `Fread` by name. Sectors come in only because that
GEMDOS is D15R's own. A GEMDOS drive answers `Fopen` and `Fread` by name too, at the ROM's
`TRAP #1` (`$FA002A`). The GOS5 builds use this: they send GOS's file calls to the system's GEMDOS
(`gos5-gemdrive.md`). The other options are weighed in `solutions.md` §4.

## Tools

- `src/probes/epic02/d15r_vs_tos.py [H5|F5]`: the comparison in §1.
- `src/probes/epic02/disk_calls_probe.py [<setup>]` and `disk_calls_report.py <run>`: the calls in §4.
