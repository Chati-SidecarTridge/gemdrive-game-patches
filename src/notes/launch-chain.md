# Lemmings' launcher, from START.TOS to the game

Read on 2026-10-11. What every stage does, read from the sources in `src/` (each reassembles to
the original bytes) and checked against runs on the PPDRIVER reference
(`src/probes/epic02/chain_probe.py`, `profile_probe.py`). `text+` offsets are LEMLD2's; names
are the sources' labels. The file formats are in `launcher-formats.md`.

## The stages and their sources

| stage | source | made from |
| --- | --- | --- |
| `START.TOS`'s stub, 230 bytes | `src/start/start.s` | `start.map` |
| LEMLD2, the launcher (a GEMDOS program; includes the block and the loader) | `src/lemld2/lemld2.s` | `lemld2.map` |
| LS2DD, the game's own loader | `src/ls2dd/ls2dd.s` | `ls2dd.map` |
| D15R, PP's GOS (ST and STE build) | `src/d15r/d15r_h5.s` | `d15r_h5.map` |
| D15R, Falcon build | `src/d15r/d15r_f5.s` | `d15r_f5.map` |

Each source is made by `tools/dev/mksource.py` from its map (entries, names, comments, tables)
and the addresses Hatari executed (`profile_probe.py`, `profile_addrs.py`). `tools/dev/all_harness.sh`
reassembles all five and checks them with a `nop` inserted (`tools/dev/shiftcheck.py`).

## LEMLD2: the launch

1. **`start`**: `hw_detect` (Supexec) reads the TOS version, TOS's and the machine's RAM and the
   machine type into `hw_*`; with 512 KB it stops (`fatal_512k`), with LEMLD2 loaded too high in
   memory it stops too ("Too much low RAM occupied !").
2. **`main`**: its own stack below `$78000`; `cut_memory` (Supexec) sets `phystop` to `$80000` and
   lowers `_memtop`, so the game gets 512 KB and the top of RAM is kept for TOS's state; low
   resolution, the screen at `$78000`, the palette and MFP registers kept.
3. **`info_screen`** and **`cover`**: `show_info` (machine, RAM, TOS, "GAMEX: key F9"); M opens
   `settings_menu` (Mega STE clock, Falcon bus and caches, TT caches); then the cover picture
   (`cover_st`, `cover_falcon`; none on a TT) from `LEMMINGS.PCH`.
4. **`gamex_setup`**: the Gamex header at `$FFF40` (signature `PPGX` written by the code at
   text+`$E32`; the fields of `GAMEXdoc.html`: the restore code at `$FFD20` and `$7FD20`, the TOS
   state at `$FFF80`, the game's state and jump addresses, the Gamex key).
5. **`load_d15r`**: `D15R_H5.FIC` (`D15R_F5.FIC` if `is_falcon`), from the game's folder or
   `C:\GAMEX\`, read into `d15r_buffer` and unpacked (`depack`) to `$C0100`. **`save_low_ram`**:
   TOS's low RAM up to `low_ram_end` to `$D7008`; `tos_restore` (512 bytes) to `$FFD20`. Both are
   how Gamex returns to the Desktop later.
6. **`load_ls2dd`**: `LS2DD.FIC` to `$81000`, a fixed 4,929 bytes. **`set_paths`**:
   `Dsetpath("FILES")`, the drive and the path stored in D15R (`$C0734`, `$C0760`).
7. **`check_pp_driver`**: `hdv_bpb` must be preceded by the XBRA id `PPHD` (`gemdrive-failure.md` §3).
   - **`reuse_pp_driver`** (PP's driver is resident): copy it from its XBRA header, 7,204 bytes,
     to `$B7180`; in the copy, find the three old vectors it chains to (TOS's `hdv_bpb`,
     `hdv_rw`, `hdv_mediach`) and put D15R's copies of TOS's floppy routines in their place
     (`flop_getbpb`, `flop_rw`, `flop_mediach`); write the copy's entries into D15R's image of
     the system variables (below); **`set_buffers`**: two GEMDOS buffer lists for that image,
     four 8 KB buffers from `$AF100`.
   - **`no_pp_driver`** (no PP driver): read the disk's sector 0 by itself, through the ACSI DMA
     registers on TOS 1 (`acsi_read_sector0`, `acsi_command`, `acsi_wait`), XBIOS `DMAread` on
     `pun_ptr`'s device on TOS 2 and later, the IDE registers on a Falcon (`ide_probe`). If it is
     an executable boot sector (`boot_sector_sum` = `$1234`), **`boot_driver`**: point `TRAP #1`
     at `trap1_stub`, which gives the booting driver a fixed area (`Malloc` answers `$AF100`,
     `$186000` on a Falcon or TT; `Mshrink` of it is accepted) and passes every other call on
     (`trap1_old`, written here); run the boot sector; after 29 VBLs keep the vectors it set in
     D15R's image. On the GEMDOS-drive runs of `gemdrive-failure.md` this path finds no disk and
     ends in `error_exit`.
8. **`start_d15r`**: call D15R's init (`$C0100` + its fourth offset, `$C02BC`, with
   `a1 = $FFFAA`: it keeps the 24 bytes there), copy the block to `$80100` with interrupts off,
   jump to it.

## The block, at `$80100`

LEMLD2 text+`$604`, 1,600 bytes, with the machine bytes (`hw_*`) in it.

- **`block`**: unpack `LS2DD.FIC` from `$81020` to `$70000`; copy the loader (block+`$30E`, 904
  bytes) to `$85000`; patch LS2DD: `jmp $85000` over the start of its `load_file` (`$70E38`), and
  its jump to the game at `$70A8C` now goes to `start_game`; `jmp $7005A`.
- **`start_game`** (`$8014C`): patch MAIN (`jmp $85000` over its floppy loader at `$2C24`;
  `start_intro`, `load_code_main` and `patch_code` hooked in at `$2B96`, `$2BBE`, `$2C00`);
  `jmp $400`, **the hand-over to the game**.
- **`start_intro`** (`$80180`): patch the intro at `$10204`/`$10244` the same way; `jmp $10000`.
- **`load_code_main`**, **`load_code_intro`** (`$801A2`, `$801B6`): the loader reads `CODE`; back
  into LS2DD (`$70030`, `$70032`), which unpacks it.
- **`patch_code`** (`$801D0`): PP's changes to CODE: the loader copied into the game at `$E892`
  and hooked in (`$22D8`, `$4074`, `$21BE`), the level entry ("map 001-120") and other fixes;
  `jmp $400`.

## The loader, at `$85000`: how the game reads a file

LEMLD2 text+`$912`. Called where the game (or LS2DD) would read its floppy, with the file's name
at `a0` and the destination at `a1`:

1. A name that starts below `"0"` or with `"F"` (the game passes data starting `"FORM"` this way,
   `disk-layer.md` §4), or `d1 = 100`: not a file, `loader_skip` returns 0.
2. The name (8.3) is copied into D15R's parameters (`io_params`, the name at `$C0752`).
3. Offset 0, length `$19B04` (105,220 bytes, the largest file, MAIN), destination `a1`. A
   destination below `$800` (over the vectors) is loaded in two parts (`loader_low`): the bytes
   under `$800` first, then the rest from that offset.
4. Its stack to `$84000`, interrupts off, and a call to D15R's third entry, **`file_io`**
   (`$C0170`); then the caller's stack and SR back, the result in `d1`.

## D15R: `file_io` and the TOS behind it

D15R is TOS 1.04 in RAM: its GEMDOS (`gemdos`, its table of every function), its BIOS and
XBIOS (`TRAP #13`, `#14`), its floppy `hdv_*` routines (byte for byte), and a complete image of
TOS's low RAM ($8-$7FF) in which the vectors point into D15R: `TRAP #1` to `trap1`, `TRAP #13`
to `$C0BEE`, `hdv_*` to its floppy routines (LEMLD2 replaces those, `_bufl` and `_drvbits` by
the driver copy's). PP's own code sits in front: the entry table and these entries.

**`file_io`** (entry 2): save the CPU state, `mfp_quiet`; for a destination below `$800`, read
into `$80400` and copy afterwards; **`swap_low_ram`**: the game's `$8-$7FF` out, TOS's image in;
`tos_paths` once (drive and path); `Fopen` (mode 0, or 1 for writing with `"Wr"`), `Fseek` to
the offset, `Fread` (or `Fwrite`) of the length, `Fclose`; swap back, MFP back; the result in `$C02B4`. With
TOS's image in, every `TRAP #1` goes to D15R's own GEMDOS, which reads the FAT volume by sectors
with BIOS `Rwabs` through `hdv_rw`: the driver copy, PPDRIVER's code (`gemdrive-failure.md` §2). The ROM's
TOS is not used, and neither is Hatari's GEMDOS-drive hook (it sits on the ROM's `TRAP #1`,
`$84` = `$FA002A` in the game's state, never in TOS's image). Nothing calls `file_io_2` (entry 4)
in the reference's runs (`disk-layer.md` §4).

## LS2DD

The game's own loader, unchanged by PP except for the two patches above: a trace-vector and
stack-overwriting protection, decryption of `$6E9A4`-`$709A5` in place, an ICE depacker, palette
fades, and a floppy loader that drives the FDC, the DMA and the sound chip's port A itself. The
decrypted code (`$70000`-`$70042`, `$7065C`-`$70742` run changed during the intro) is kept as the
stored bytes; reproducing the decryption was not attempted (it is not a plain XOR of the file).

## On the Falcon

D15R_F5 reads `TRAP #1`'s function number at `8(sp)`, LEMLD2's `trap1_stub` too (`trap1_frame`
set to 8): the 68030's exception frame has a format word the 68000's has not.

## Found on the way

`GXUT260.PRG` carries LEMLD2's unpack routine and its PP-driver check (`launcher-signatures.md`).
