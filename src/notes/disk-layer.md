# The disk layer: D15R and the driver it uses

Read on 2026-10-11. What sits between the game and the disk on the PPDRIVER reference,
from the sources (`src/d15r/d15r_h5.s`, `src/lemld2/lemld2.s`) and runs on ST TOS 1.04. Names
are the sources' labels; `launch-chain.md` tells how the launcher sets it all up.

## 1. D15R is TOS 1.04 in RAM

`src/probes/epic02/d15r_vs_tos.py` aligns D15R_H5 with the TOS 1.04 UK ROM (`TOS_ST_104`) and
classifies its 91,460 bytes:

| | bytes | |
| --- | --- | --- |
| the ROM's own | 54,640 (59.7%) | |
| relocated | 9,804 (10.7%) | a ROM address made a D15R one (the copy moved from `$FC0000` to around `$C0100`), or an address in TOS's RAM plus `$D0528` (D15R keeps TOS's RAM in its own image there) |
| other | 27,016 (29.5%) | PP's code, the RAM image's contents (no ROM has them) and PP's edits |

Of the TOS 1.04 ROMs on this Mac, the UK one matches best (the keyboard table has the UK `#`
key); the other languages are within 0.5%.

What D15R holds, from `$C0100` (the sources name every routine):

| from | what |
| --- | --- |
| `$C0100` | **PP's own** (1,852 bytes, nowhere in the ROM): the entry table, `swap_low_ram`, `tos_paths`, `file_io`, `init`, `file_io_2`, `mfp_quiet`, the parameters at `$C0730`, `low_ram_save` |
| `$C0830` | TOS's start-up (`tos_start`, also `swv_vec`'s target as in TOS), the BIOS and XBIOS traps (`bios_trap`, `xbios_trap`) and their tables, the exception handler, VBL and HBL |
| `$C11CE` | the floppy driver: the XBIOS floppy functions, `flop_getbpb`, `flop_rw`, `flop_mediach` (byte for byte TOS's `hdv_*` at `$FC173C`, `$FC1A24`, `$FC18EC`) |
| `$C2166` | clock chip, printer, serial port, MIDI, keyboard processor, MFP, sound chip |
| `$C34F8` | **GEMDOS**: console, the directory tree, buffers and FAT, files and handles, processes and memory, its dispatcher (`gemdos`) and its function table (`$CF946`, every function of TOS 1.04) |
| `$C83C6` | PP's BIOS and XBIOS call stubs for GEMDOS (`bios`, `xbios`), TRAP #2 (`vdi_aes`) |
| `$C84A0` | **PP's GEMDOS entry** (`trap1`): functions 1-11 (the console) answer 0, `Super` is handled apart, the rest goes to `gemdos` |
| `$C899E` | TOS's GEMDOS dispatcher and the rest of TOS's code (timer, VT52, line-A, the VDI's entry) |
| `$CF688` | TOS's data: keyboard tables, the 6x6 font's header, GEMDOS's messages ("OUT OF INTERNAL MEMORY") |
| `$D0528` | **the image of TOS's RAM**: TOS's address + `$D0528`, its vectors and system variables (`$8`-`$7FF`) and TOS's own variables above them, up to the end of the file |

PP's edits to TOS's code, as far as the comparison shows them: TOS's RAM variables moved into the
image (1,724 absolute references relocated by `$D0528`; where TOS sets `a5`, its base for
its variables, to 0 with `suba.l a5,a5`, D15R has `lea $D0528,a5`: in seven places, the BIOS
dispatcher among them, `$FC07FE` in the ROM, `$C0C1E` in D15R); some accesses rewritten with other
addressing, which changes instruction lengths (the runs of "other" bytes in the start-up and BIOS
code); the call to the
hard-copy routine, which D15R does not include, turned into a branch to an odd address
(`no_hardcopy`: Alt-Help would end in an address error); and his own `TRAP #1` entry. The image's
device tables (`xconstat`…, `$51E`-`$59D`) are empty: TOS fills them at start-up and D15R's
`tos_start` never runs, which is why `trap1` answers the console functions with 0.

**It is PP's GOS, as his `GAMEXdoc.html` describes it, and more than that page says.** Not only
TOS 1.04's GEMDOS but its BIOS, XBIOS, floppy driver, start-up code and data, relocated to
`$C0100`, with an image of its RAM, behind PP's entry points. The Falcon build (`D15R_F5`) is the same with `trap1` (and
LEMLD2's `trap1_stub`) reading the function number past the 68030's format word.

## 2. D15R's entry points and the data it shares

| entry | offset in the table at `$C0100` | called by | does |
| --- | --- | --- | --- |
| `swap_low_ram` | `$0010` | `file_io`, `file_io_2` | exchange `$8`-`$7FF` with the image: TOS's vectors and system variables in, the game's out, or back |
| `tos_paths` | `$0034` | `file_io` (when `$C0734` is set) | a VBL tick into `_hz_200`; `Dsetdrv` and `Dsetpath` to LEMLD2's drive and path |
| `file_io` | `$0070` | PP's loader (`$C0100` + the word at `+4`), the game's copy of it | load or save a whole file by name (below) |
| `init` | `$01BC` | LEMLD2 (`start_d15r`), with `a1 = $FFFAA` | keep the 24 bytes at `$FFFAA` |
| `file_io_2` | `$01CA` | not seen called (§4) | the same as `file_io` for the second parameter set |

`io_params`, at `$C0730`: `+4` drive (a word; non-zero makes `file_io` set the paths, the loader
clears it after the first call), `+6` offset, `+$A` length, `+$E` buffer (longs), `+$12` `"Wr"` to
write, `+$22` the file name (8.3), `+$30` the path (`\LEMMINGS\FILES`, from LEMLD2's
`Dgetpath`). The result is at `$C02B4`.

**`file_io`**: with interrupts off, keep the registers and SR; `mfp_quiet` (the MFP's enables
and masks kept and cleared); a destination below `$800` goes through `$80400`; `swap_low_ram`
(TOS in); `tos_paths` if asked; `Fopen` (mode 1 with `"Wr"`), `Fseek`, `Fread` or `Fwrite`,
`Fclose`, all through `TRAP #1`, which TOS's image points at `trap1`; `swap_low_ram` (the game
back); the MFP back. D15R's GEMDOS reads the volume through BIOS `Rwabs`, `Getbpb`, `Mediach`
(its `bios` stub, `TRAP #13`), which the image sends to `hdv_rw`, `hdv_bpb`, `hdv_mediach`: the
driver copy's entries, which LEMLD2 wrote there.

## 3. What the launcher asks of PP's resident driver

From `reuse_pp_driver` and `set_buffers` (`src/lemld2/lemld2.s`), checked against the
dumps of the resident and copied driver in `gemdrive-failure.md` §3:

1. **The XBRA id `PPHD`** in the 4 bytes 8 before the routine `hdv_bpb` points to (the XBRA
   header `"XBRA" "PPHD" <old vector>` starts 12 bytes before it).
2. **7,204 bytes from that header that still work at `$B7180`**: they are copied there and run
   there (the code must not depend on where it was loaded).
3. **`hdv_rw` and `hdv_mediach` in the same block, at the same distance from `hdv_bpb` as in
   the resident copy**: their copies' addresses are computed from those distances and written
   into D15R's image (`$B71C2`, `$B75BE` on the reference).
4. **Three old-vector slots holding TOS's `hdv_bpb`, `hdv_rw`, `hdv_mediach`** (the values the
   driver chains to for drives it does not serve): LEMLD2 finds them by value in the copy and
   puts D15R's floppy routines in their place.
5. **GEMDOS buffer headers at the same distance from `hdv_mediach` as `_bufl`'s**: LEMLD2 makes
   two buffer lists there, with four 8 KB buffers from `$AF100` (`_bufl` in the image).
6. **`pun_ptr` and the cookie jar pointer** are saved into the image as found (`pun_ptr` is
   cleared afterwards on the reference, `gemdrive-failure.md` §3).

And from the game, through D15R (§4): `hdv_rw` for every read (logical 1,024-byte records on
drive C, per the BPB it gave), `hdv_mediach` before each access (answering 0); `hdv_bpb` not
after the hand-over (on the reference, D15R's `Getbpb(2)` comes before it: `gemdrive-failure.md` §4). A replacement driver would have to provide exactly that, laid out the
same way; or D15R's GEMDOS could be bypassed altogether (what the GOS5 builds do: `gos5-gemdrive.md`).

## 4. Every call the game makes, from the hand-over to the level load

`src/probes/epic02/disk_calls_probe.py st-104`, then `disk_calls_report.py` on run
`20261011-182600-st-104-ppdriver-disk-calls` (PASS, 13/13):

| call | what | the driver's reads |
| --- | --- | --- |
| loader, a0 = `"FORM…"`, d1 = 5 | not a file name (it starts with `F`): `loader_skip`, nothing read | |
| loader `"IntroPart2"` → `file_io` `IntroPar` (cut to 8 characters), to `$10000` | the intro | directory 263, 415 × 80, 495, 496; `Mediach` × 23 |
| loader `"CODE"` to `$200` → `file_io` `CODE` 1,536 bytes through `$80400`, then `file_io` `CODE` from offset 1,536 to `$800` | the game | 497, 498; then 499 × 76, 575; `Mediach` × 50 |
| `file_io` `leveldat` (the game's own copy of the loader, at `$E892`, not `$85000`) | level data, at the title | 263, 264, 677 × 2, 679, 680; `Mediach` × 45 |
| `file_io` `level020`, after the click on "1 PLAYER" | the first level | 263, 407 × 2, 409; `Mediach` × 21 |

In all: 3 calls to the loader at `$85000`, 5 to `file_io`, none to `file_io_2`, 16 to the driver
copy's `hdv_rw`, 139 to its `hdv_mediach`, none to its `hdv_bpb`. Names arrive in mixed case
(`leveldat`); D15R's GEMDOS matches them regardless, as TOS does.

## 5. For the solution

The game asks for files **by name** and the request reaches GEMDOS as `Fopen`/`Fread` by name.
The sectors only come in because that GEMDOS is D15R's own, behind `trap1` in TOS's image, and it
reads the volume through the driver copy. Hatari's GEMDOS drive answers `Fopen`/`Fread` by name
too, at the ROM's `TRAP #1` (`$FA002A`, which the game's own vectors still hold,
`launch-chain.md`). Where the fix goes in (a driver that serves records, a `file_io` that calls
the system's GEMDOS, or something else) was weighed with the other solutions in
`hd-strategies.md` §4; the GOS5 builds send GOS's file calls to the system's GEMDOS
(`gos5-gemdrive.md`). This is what they started from.

## Tools

- `src/probes/epic02/d15r_vs_tos.py [H5|F5]`: the comparison of §1.
- `src/probes/epic02/disk_calls_probe.py [<setup>]` and `disk_calls_report.py <run>`: §4.
