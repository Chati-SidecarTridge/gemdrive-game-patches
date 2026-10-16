# Signatures of PP's launcher, for the survey of his adaptations

2026-10-11. Byte patterns that identify each piece of Lemmings' launcher, to look for in PP's
other adaptations. Hex, `??` for a byte that varies. Every pattern was
checked against Lemmings' files: "found in" lists where it occurs (offsets in the file as stored;
"unpacked" means in the output of `tools/unpack.py`). Several survive PP's packer and can be
found in the packed files directly.

| piece | pattern | found in | what it shows |
| --- | --- | --- | --- |
| `START.TOS`'s stub | `4BFA FFFE 204D D1FC ?? ?? ?? ?? 2C4D DDFC ?? ?? ?? ?? 284E 243C ?? ?? ?? ?? 2D20 5382 66FA 264C 43FA 000C` | `START.TOS` +$1C (the text's start) | a program that is PP's self-unpacking shell; the three longs are its sizes (`src/notes/launcher-formats.md`) |
| packed-file header | `4333 0000` then packed and unpacked size (longs) | `START.TOS` +$102 (its data), `LS2DD.FIC` +0, `D15R_H5.FIC` +0 | a stream in PP's format; the name follows at +16 |
| PP's unpack routine (LEMLD2's form) | `4280 7806 7A3F 4240 1019 6B0E 670A 5340 18D9 51C8 FFFC 60EE` | `LEMLD2.TOS` +$B4E (text+$B32), `GXUT260.PRG` +$2314 | a program that unpacks PP's format itself |
| PP's unpack routine (the stub's form) | `4240 101E 6B0C 672A 5340 18DE 51C8 FFFC 60EE` | `START.TOS` +$58 | the same, reading through `a6` |
| the PP-driver check | `2278 0472 0CA9 5050 4844 FFF8` (`movea.l $472.w,a1; cmpi.l #'PPHD',-8(a1)`) | `START.TOS` +$3F4 (inside the packed data), `LEMLD2.TOS` +$340, `GXUT260.PRG` +$14E6 | the program requires PP's resident driver: it will not run from a GEMDOS drive (`gemdrive-failure.md`) |
| the requirement message | `"This prg. requires PP"` | `START.TOS` +$838, `LEMLD2.TOS` +$872 | the same, from its text |
| the Gamex id | `"PPGX"` (`5050 4758`) | `START.TOS` +$D53, `LEMLD2.TOS` +$E50, `GXUT260.PRG` +$256 | Gamex gamestates (`GAMEXdoc.html`) |
| D15R's entry table | `0010 0034 0070 01BC 01CA` | `D15R_H5.FIC` +$21 (packed), both D15Rs unpacked +0 | PP's GOS, this build of it |
| GOS's GEMDOS entry, ST/STE | `302F 0006 B07C 000B 6E ?? B07C 0001 65 ?? 7000 4E73` | `D15R_H5` unpacked +$83A0 | PP's TRAP #1 entry in front of TOS's GEMDOS |
| the same, Falcon | `302F 0008 B07C 000B 6E ?? B07C 0001 65 ?? 7000 4E73` | `D15R_F5` unpacked +$83B8 | the Falcon build (68030 frames) |
| TOS's GEMDOS message | `"*** OUT OF INTERNAL MEMORY"` | `D15R_H5.FIC` +$AAB4 (packed), both D15Rs unpacked | a copy of TOS's GEMDOS (from TOS 1.04 here) in the file |
| the loader's call into D15R | `41F9 000C 0100 7000 3028 0004 D1C0 4E90` (`lea $C0100,a0; moveq #0,d0; move.w 4(a0),d0; adda.l d0,a0; jsr (a0)`) | `LEMLD2.TOS` +$99E | a game loader that reads files through GOS's `file_io` |

Not signatures of the launcher: `LS2DD` is the game's own loader (protection, ICE, its floppy
code) and changes from game to game; PP's patches to it and to the game (LEMLD2's block) are
specific to Lemmings.

How the survey uses them (`strategies.md`): the PP-driver check in a `START.TOS` launcher, with the
requirement message or the `DMAread` fallback ("Other modes"), marks a game that cannot run from a
GEMDOS drive as it is (the HAGA modules have the check too, and their games run); the GOS
patterns mark one whose files are read by PP's GEMDOS in RAM, which reaches the disk by sectors
through the driver; the packer header and the stub mark files to unpack first (`tools/unpack.py`)
before looking further.

## Other modes

2026-10-11 (`pp-modes.md`). Checked on the files named, as stored or unpacked
by `tools/unpack.py` (`start` for `START.TOS`):

| mode | pattern | found in |
| --- | --- | --- |
| HAGA family launcher | `"C:\GAMEX\HAG"` + `A`/`E`/`2`, and `"Starting GOS ..."` | `RUNME.TOS` of Wormhole (+$44F, +$5B8), Quest for Galaxia, Breakout ACC, Vector Invaders |
| HAGA family module | starts `0100` then 15 more word offsets; `"GSAU.TOS"`; `"FILES\D15H5.FIC"` | `HAGA` (+$3F8), `HAGE`, `HAG2` (+$3D2) |
| HAGE / HAG2 | `"T14AG.FIC"` / `"T14GG.FIC"` | `HAGE`, `HAG2` (+$2AF7) |
| GOS4/GOS5 launcher, driver checks | `2278 0472 0CA9 5050 4844 FFF8` (`PPHD`); `2278 0516` … `3F3C 002A 4E4E` (`pun_ptr`, `DMAread`); `263C 444D 4172` (`'DMAr'`) | unpacked `START.TOS` of Lemmings (+$340, +$4BA, +$4EE), Magnetik Tank (+$358, +$4B0, +$4E4), Clever & Smart (+$31C, +$496, +$4CA), Bubble Dizzy (+$3CA, +$408, +$43C); not in Garfield's or Castle Master's |
| GOS builds | packed-file header (`4333 0000`) names: `D15R_NG1.PRG`, `D15R_F12.PRG` (GOS 1.00); `D15R_H62.PRG`, `D15R_F69.TOS` (GOS4); `G552`, `GF552`, `G158`, `GF158` (GOS5); `GH5R4`, `GF5R4` (`5H`/`5F`); `D15RH.TOS`, `D15RF.TOS`, `D15RU.TOS` (HAGA); `D15I81.TOS` (iTOS) | the most common version of each file |
| TOS in RAM | header names `T14AGHnn.TOS` (with GEM), `T14Gnn.TOS` (without) | `T14AG.FIC`, `T14GG.FIC` |

`START.TOS` stubs pad their data with up to 3 zero bytes (Clever & Smart, Bubble Dizzy, Castle
Master; Lemmings 1): `tools/unpack.py start` now accepts that.

The `PPHD` check alone does not mark a game that fails: the HAGA modules have it too (`HAGA`
+$2C2, `HAGE` and `HAG2` +$2CA) and their games run from a GEMDOS drive. The launchers that stop
there have all three driver checks and load a GOS4 or GOS5 file.

## Disk access

For the strategies (`strategies.md`, `tools/survey/classify.py`). Looked for in a program's text
section at even offsets, PP's stub unpacked first, and in PP-packed files unpacked:

| access | pattern | what it is |
| --- | --- | --- |
| GEMDOS file | `3F3C 003D 4E41`, `3F3C 003F 4E41`, `3F3C 004B 4E41`; `703D 3F00 4E41`, `703F 3F00 4E41` | `Fopen`, `Fread`, `Pexec` through `TRAP #1` (HAGA's file service puts the number in `d0` first) |
| BIOS `Rwabs` | `3F3C 0004 4E4D` | sectors through the driver |
| XBIOS `Floprd` | `3F3C 0008 4E4E` | floppy sectors |
| XBIOS `DMAread` | `3F3C 002A 4E4E` | ACSI sectors (TOS 2.x) |
| DMA / floppy-controller registers | `FFFF 8604`-`FFFF 860D`; `lea $8604.w`/`$8606.w` (`41F8`…`4BF8 8604`/`8606`); `move.w #…,$8604.w`/`$8606.w` (`31FC xxxx 8604`/`8606`) | the hardware itself: ACSI or the floppy controller |

A hit is a place to look, not a proof: data can hold the same bytes (an odd-offset hit in Lords of
Chaos' `RUNME.TOS` was data), and a routine can be present and never run.

