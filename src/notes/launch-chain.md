# Lemmings' launcher, from START.TOS to the game

This page follows Lemmings' Gamex launcher, LEMLD2, from `START.TOS` to the game. The launcher
loads GOS, a copy of TOS 1.04's GEMDOS that runs from RAM, and hands over to the game. The game
then asks a small loader for each file by name, and GOS reads it by sectors through the PPDRIVER
hard-disk driver. That is why the game needs a hard-disk driver (`gemdrive-failure.md`).

Read from the sources in `src/`, which reassemble to the original bytes, and
checked against runs on the PPDRIVER reference disk. Names are the sources' labels. The file
formats are in `launcher-formats.md`.

## The stages and their sources

| stage | source |
| --- | --- |
| `START.TOS`'s stub, 230 bytes | `src/start/start.s` |
| LEMLD2, the launcher, with the block and the loader below | `src/lemld2/lemld2.s` |
| LS2DD, the game's own loader | `src/ls2dd/ls2dd.s` |
| D15R, which holds GOS (ST and STE build) | `src/d15r/d15r_h5.s` |
| D15R, Falcon build | `src/d15r/d15r_f5.s` |

The sources reassemble to the original files, so they are not in the repository: only their maps
are (`src/<stage>/<stage>.map`, the names, comments and addresses). `tools/make_sources.sh` makes
the sources from the maps and your own copy of the Lemmings download, unpacked into `LEMMINGS/`.

## LEMLD2: the launch

1. **`start`** reads the TOS version, the RAM and the machine type. It stops with 512 KB.
2. **`main`** sets `phystop` to `$80000`, so the game gets 512 KB and the top of RAM keeps TOS's
   state.
3. **`info_screen`** and **`cover`** show the machine, then the cover from `LEMMINGS.PCH`.
4. **`gamex_setup`** writes the Gamex header at `$FFF40` (fields in `GAMEXdoc.html`).
5. **`load_d15r`** unpacks `D15R_H5.FIC` (`D15R_F5.FIC` on a Falcon) to `$C0100`.
   **`save_low_ram`** keeps TOS's low RAM at `$D7008`, for the return to the desktop.
6. **`load_ls2dd`** reads `LS2DD.FIC` to `$81000`. **`set_paths`** calls `Dsetpath("FILES")`.
7. **`check_pp_driver`** looks for the XBRA id `PPHD` before `hdv_bpb` (`gemdrive-failure.md` §3).
   - With PPDRIVER resident, **`reuse_pp_driver`** copies it (7,204 bytes) to `$B7180`. In the
     copy, D15R's floppy routines replace the three TOS vectors the driver chains to.
     **`set_buffers`** gives GOS four 8 KB buffers from `$AF100`.
   - Without it, **`no_pp_driver`** reads sector 0 itself: by ACSI DMA on TOS 1, XBIOS
     `DMAread` on TOS 2, IDE on a Falcon. If sector 0 is an executable boot sector,
     **`boot_driver`** runs it and keeps the vectors it sets. From a GEMDOS drive this path finds
     no disk and ends in `error_exit`.
8. **`start_d15r`** calls D15R's init, copies the block to `$80100` and jumps to it.

## The block at `$80100`: the hand-over

The block unpacks LS2DD to `$70000` and copies the loader to `$85000`. It patches LS2DD, the
intro and the game's code (`MAIN`, `CODE`), so that their floppy loading goes to the loader.
`CODE` gets its own copy of the loader, at `$E892`. The block starts LS2DD, and `start_game`
(`$8014C`) starts the game with `jmp $400`. **`patch_code`** (`$801D0`) also adds the level
entry ("map 001-120") and other fixes.

## The loader at `$85000`: how the game reads a file

The game calls the loader where it would read its floppy, with the file name at `a0` and the
destination at `a1`. The loader skips calls that are not files (`disk-layer.md` §4). It copies
the 8.3 name into D15R's parameters at `$C0752` and asks for 105,220 bytes, the size of MAIN, the
largest file. Then it calls D15R's **`file_io`** (`$C0170`) with interrupts off.

## D15R: how GOS reads the file

D15R is TOS 1.04 in RAM: its GEMDOS, BIOS and XBIOS, its floppy routines, and an image of TOS's
low RAM (`$8`-`$7FF`). LEMLD2 replaces that image's `hdv_*` vectors, `_bufl` and `_drvbits` with
the driver copy's.

**`file_io`** swaps the game's low RAM out and TOS's image in. It calls `Fopen`, `Fseek`, `Fread`
(or `Fwrite`) and `Fclose`, then swaps back. GOS reads the FAT volume by sectors with BIOS
`Rwabs`, through the driver copy (`gemdrive-failure.md` §2). The TOS in ROM takes no part.
Neither does Hatari's GEMDOS-drive hook, which sits on the ROM's `TRAP #1`, not in TOS's image.

## Other findings

- LS2DD is unchanged except for the patches above. It holds a protection, an ICE depacker and a
  floppy loader. The source keeps the code it decrypts at run time as stored bytes.
- On the Falcon, D15R_F5 and LEMLD2's `trap1_stub`, the `TRAP #1` handler it gives a booting
  driver, read the function number at `8(sp)`. The 68030's exception frame has a format word
  the 68000's lacks.
- `GXUT260.PRG` carries LEMLD2's unpack routine and its PPDRIVER check
  (`launcher-signatures.md`).

## Evidence and tools

- `src/probes/epic02/chain_probe.py <setup>`: a dump of every stage at its entry.
- `src/probes/epic02/profile_probe.py`, `profile_addrs.py`: the addresses Hatari executed.
- `tools/dev/mksource.py` makes each source from its map (`src/<stage>/<stage>.map`).
  `tools/dev/all_harness.sh` reassembles all five and checks them with a `nop` inserted.
