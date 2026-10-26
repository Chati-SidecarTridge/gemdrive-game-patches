# Signatures of the Gamex launcher, for the survey of the adaptations

A signature is a byte pattern that marks one piece of a program. This page lists the signatures of
Lemmings' launcher, of the other modes, and of the ways a program reaches the disk. The survey of
the adaptations looks for them in every game's files (`recognising-modes.md`). A hit is a place to look,
not a proof: data can hold the same bytes, and a routine can be present and never run.

## The pieces of Lemmings' launcher

Checked against Lemmings' files. Patterns are hex, `??` is a byte that varies, and
offsets are in the file as stored. "Unpacked" means after `tools/unpack.py`. Several patterns
survive the packer and can be found in the packed files directly.

| piece | pattern | found in |
| --- | --- | --- |
| `START.TOS`'s unpacking stub | `4BFA FFFE 204D D1FC ?? ?? ?? ?? 2C4D DDFC ?? ?? ?? ?? 284E 243C ?? ?? ?? ?? 2D20 5382 66FA 264C 43FA 000C` | `START.TOS` +$1C |
| packed-file header (`launcher-formats.md`) | `4333 0000`, then the packed and unpacked sizes | `START.TOS` +$102, `LS2DD.FIC` +0, `D15R_H5.FIC` +0 |
| the unpack routine | `4280 7806 7A3F 4240 1019 6B0E 670A 5340 18D9 51C8 FFFC 60EE` | `LEMLD2.TOS` +$B4E, `GXUT260.PRG` +$2314; the stub's form, reading through `a6`, at `START.TOS` +$58 |
| the `PPDRIVER` check | `2278 0472 0CA9 5050 4844 FFF8` (`movea.l $472.w,a1; cmpi.l #'PPHD',-8(a1)`) | `START.TOS` +$3F4 (packed), `LEMLD2.TOS` +$340, `GXUT260.PRG` +$14E6 |
| the requirement message | `"This prg. requires PP"` | `START.TOS` +$838, `LEMLD2.TOS` +$872 |
| the Gamex id | `"PPGX"` (`5050 4758`) | `START.TOS` +$D53, `LEMLD2.TOS` +$E50, `GXUT260.PRG` +$256 |
| D15R's entry table | `0010 0034 0070 01BC 01CA` | `D15R_H5.FIC` +$21 (packed), both D15Rs unpacked +0 |
| GOS's GEMDOS entry | `302F 0006 B07C 000B 6E ?? B07C 0001 65 ?? 7000 4E73` (Falcon: `0008` for `0006`) | `D15R_H5` unpacked +$83A0, `D15R_F5` +$83B8 |
| TOS's GEMDOS message | `"*** OUT OF INTERNAL MEMORY"` | `D15R_H5.FIC` +$AAB4 (packed), both D15Rs unpacked |
| the loader's call into D15R | `41F9 000C 0100 7000 3028 0004 D1C0 4E90` | `LEMLD2.TOS` +$99E |

`PPDRIVER` is the hard-disk driver the launcher requires. D15R is the launcher's build of GOS, a
copy of TOS 1.04 that runs from RAM (`disk-layer.md`). `LS2DD`, the game's own loader, has no
signature: it changes from game to game.

The survey reads them this way. The `PPDRIVER` check, with the message or the `DMAread` fallback,
marks a launcher that cannot run from a GEMDOS drive as it is. The GOS patterns mark a game whose
files GOS reads by sectors through the driver. The header and the stub mark files to unpack first.

## Other modes

Checked (`modes.md`) on the files named, as stored or unpacked:

| mode | pattern | found in |
| --- | --- | --- |
| HAGA family launcher | `"C:\GAMEX\HAG"` + `A`/`E`/`2`, and `"Starting GOS ..."` | `RUNME.TOS` of Wormhole, Quest for Galaxia, Breakout ACC, Vector Invaders |
| HAGA family module | starts `0100` then 15 more word offsets; `"GSAU.TOS"`; `"FILES\D15H5.FIC"` | `HAGA`, `HAGE`, `HAG2` |
| HAGE / HAG2 | `"T14AG.FIC"` / `"T14GG.FIC"` | `HAGE`, `HAG2` |
| GOS4/GOS5 launcher, driver checks | `2278 0472 0CA9 5050 4844 FFF8` (`PPHD`); `2278 0516` … `3F3C 002A 4E4E` (`pun_ptr`, `DMAread`); `263C 444D 4172` (`'DMAr'`) | unpacked `START.TOS` of Lemmings, Magnetik Tank, Clever & Smart, Bubble Dizzy; not in Garfield's or Castle Master's |
| GOS builds | packed-file header names: `D15R_NG1.PRG`, `D15R_F12.PRG` (GOS 1.00); `D15R_H62.PRG`, `D15R_F69.TOS` (GOS4); `G552`, `GF552`, `G158`, `GF158` (GOS5); `GH5R4`, `GF5R4` (`5H`/`5F`); `D15RH.TOS`, `D15RF.TOS`, `D15RU.TOS` (HAGA); `D15I81.TOS` (iTOS) | the most common version of each file |
| TOS in RAM | header names `T14AGHnn.TOS` (with GEM), `T14Gnn.TOS` (without) | `T14AG.FIC`, `T14GG.FIC` |

The `PPHD` check alone does not mark a game that fails. The HAGA modules have it too, and their
games run from a GEMDOS drive. The launchers that fail have all three driver checks and load a GOS4
or GOS5 file.

## Disk access

`tools/survey/classify.py` sorts the games by strategy with these patterns (`recognising-modes.md`). It
looks at even offsets in a program's text section, after unpacking:

| access | pattern | what it is |
| --- | --- | --- |
| GEMDOS file | `3F3C 003D 4E41`, `3F3C 003F 4E41`, `3F3C 004B 4E41`; `703D 3F00 4E41`, `703F 3F00 4E41` | `Fopen`, `Fread`, `Pexec` through `TRAP #1` |
| BIOS `Rwabs` | `3F3C 0004 4E4D` | sectors through the driver |
| XBIOS `Floprd` | `3F3C 0008 4E4E` | floppy sectors |
| XBIOS `DMAread` | `3F3C 002A 4E4E` | ACSI sectors (TOS 2.x) |
| DMA and floppy-controller registers | `FFFF 8604`-`FFFF 860D`; `41F8`…`4BF8 8604`/`8606`; `31FC xxxx 8604`/`8606` | the hardware itself: ACSI or the floppy controller |
