# Signatures of PP's launcher, for EPIC-03's survey

EPIC-02 STORY-04, 2026-10-11. Byte patterns that identify each piece of Lemmings' launcher, for
EPIC-03 to look for in PP's other adaptations. Hex, `??` for a byte that varies. Every pattern was
checked against Lemmings' files: "found in" lists where it occurs (offsets in the file as stored;
"unpacked" means in the output of `tools/unpack.py`). Several survive PP's packer and can be
found in the packed files directly.

| piece | pattern | found in | what it shows |
| --- | --- | --- | --- |
| `START.TOS`'s stub | `4BFA FFFE 204D D1FC ?? ?? ?? ?? 2C4D DDFC ?? ?? ?? ?? 284E 243C ?? ?? ?? ?? 2D20 5382 66FA 264C 43FA 000C` | `START.TOS` +$1C (the text's start) | a program that is PP's self-unpacking shell; the three longs are its sizes (`src/notes/launcher-formats.md`) |
| packed-file header | `4333 0000` then packed and unpacked size (longs) | `START.TOS` +$102 (its data), `LS2DD.FIC` +0, `D15R_H5.FIC` +0 | a stream in PP's format; the name follows at +16 |
| PP's unpack routine (LEMLD2's form) | `4280 7806 7A3F 4240 1019 6B0E 670A 5340 18D9 51C8 FFFC 60EE` | `LEMLD2.TOS` +$B4E (text+$B32), `GXUT260.PRG` +$2314 | a program that unpacks PP's format itself |
| PP's unpack routine (the stub's form) | `4240 101E 6B0C 672A 5340 18DE 51C8 FFFC 60EE` | `START.TOS` +$58 | the same, reading through `a6` |
| the PP-driver check | `2278 0472 0CA9 5050 4844 FFF8` (`movea.l $472.w,a1; cmpi.l #'PPHD',-8(a1)`) | `START.TOS` +$3F4 (inside the packed data), `LEMLD2.TOS` +$340, `GXUT260.PRG` +$14E6 | the program requires PP's resident driver: it will not run from a GEMDOS drive (EPIC-01) |
| the requirement message | `"This prg. requires PP"` | `START.TOS` +$838, `LEMLD2.TOS` +$872 | the same, from its text |
| the Gamex id | `"PPGX"` (`5050 4758`) | `START.TOS` +$D53, `LEMLD2.TOS` +$E50, `GXUT260.PRG` +$256 | Gamex gamestates (`GAMEXdoc.html`) |
| D15R's entry table | `0010 0034 0070 01BC 01CA` | `D15R_H5.FIC` +$21 (packed), both D15Rs unpacked +0 | PP's GOS, this build of it |
| GOS's GEMDOS entry, ST/STE | `302F 0006 B07C 000B 6E ?? B07C 0001 65 ?? 7000 4E73` | `D15R_H5` unpacked +$83A0 | PP's TRAP #1 entry in front of TOS's GEMDOS |
| the same, Falcon | `302F 0008 B07C 000B 6E ?? B07C 0001 65 ?? 7000 4E73` | `D15R_F5` unpacked +$83B8 | the Falcon build (68030 frames) |
| TOS's GEMDOS message | `"*** OUT OF INTERNAL MEMORY"` | `D15R_H5.FIC` +$AAB4 (packed), both D15Rs unpacked | a copy of TOS's GEMDOS (from TOS 1.04 here, H-08) in the file |
| the loader's call into D15R | `41F9 000C 0100 7000 3028 0004 D1C0 4E90` (`lea $C0100,a0; moveq #0,d0; move.w 4(a0),d0; adda.l d0,a0; jsr (a0)`) | `LEMLD2.TOS` +$99E | a game loader that reads files through GOS's `file_io` |

Not signatures of the launcher: `LS2DD` is the game's own loader (protection, ICE, its floppy
code) and changes from game to game; PP's patches to it and to the game (LEMLD2's block) are
specific to Lemmings.

How to use them (EPIC-03 STORY-03): the PP-driver check and the requirement message mark a game
that cannot run from a GEMDOS drive as it is; the GOS patterns mark one whose files are read by
PP's GEMDOS in RAM, which reaches the disk by sectors through the driver; the packer header and
the stub mark files to unpack first (`tools/unpack.py`) before looking further.
