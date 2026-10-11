# PP's modes: how his adaptations reach their files

EPIC-03 STORY-01, 2026-10-11. The vocabulary EPIC-03 classifies with. Sources:

- PP's pages, read in the mirror (D-11, D-12) and cited by name under
  <https://atari.8bitchip.info/>: `agcat.html` (his categories),
  `GAMEXdoc.html`, `GamexUsage.html`, `playfhd.html`, `plafh.html`, `fromhd.php`, `fromhd2.php`,
  `fromhd3.php` (the list and its help), `imgrun.php`, `astopensw.php`, and the 1,829 game pages
  `SCRSH/*.html`.
- His published launchers (`GamexLSrc.html`, `GamexLSrc2.html`, `GamexLSrc3.html`) and tools
  (`HOLE.ZIP`, `IMGRSRC.ZIP`, `IMGRF2X.ZIP`, `RAMTOS.ZIP`, `HDTCFIX.ZIP`, `512K_1M.ZIP`).
- The file names in the mirror's 1,947 archives (games and his tools), and the shared files
  (`HAGA`, `HAGE`, `HAG2`, `D15R*.FIC`, `T14*.FIC`) unpacked with `tools/unpack.py` and set against
  the TOS 1.04 ROM.
- Runs, one game per mode, as it is, in Hatari's GEMDOS drive (ST, TOS 1.04, 1 MB):
  `src/probes/epic03/mode_probe.py <ZIP>`, run folders
  `tools/dev/logs/20261011-*-st-104-gemdrive-<game>` (and `-ppdriver-` for the reference).

What PP writes is his account (D-01): a statement marked **PP** quotes him; **run** is what a run
showed; **code** is what his files contain. Nothing here is a verdict yet: the guesses in §4 are
STORY-05's to check, game by game.

## 1. Two ways PP sorts games

PP sorts a game by **how the original reached the floppy** (his six categories, `agcat.html`,
and the `Cat:` code on the game pages, §2), and he adapts it with **one of his launchers** (the
modes, §3). The verdict from a GEMDOS drive depends on the second: how the adapted game reaches its
files while it runs. The first says how much work the adaptation needed.

## 2. PP's six categories and the `Cat:` code

`agcat.html`, "Atari ST game categorisation by hard disk run possibility - way how to solve it",
written after "adapting about 450 Atari ST(E) games":

| # | the original game (PP) | PP's way to run it from a hard disk | code | of 450 |
| --- | --- | --- | --- | --- |
| 1 | "using regular filesys, fully relocatible", no copy protection, relative paths | "easy hard disk installable" | `MXTPL` | 40 |
| 2 | the same, with copy protection; "often file access is set for floppy A" | cracks; path corrections in the code, the Floppy Image Runner, or "resident code which removes absolute path (A:\\)" | `MXTPL` | 130 |
| 3 | "do not access floppy after start" | "take RAM content in moment of start", pack it, restore it from the hard disk: "I call them singleparted"; on later TOS, "Image Runner or GOS 4" | `SXT`, `SXI`, `SXO` | 104 |
| 4 | regular filesystem "but limited to low RAM" | "run from AUTO, using HOLE, Floppy Image Runner, GOS 4, hard disk driver in high RAM" | `MXTL` | 61 |
| 5 | "using XBIOS for loading from floppy" | the Floppy Image Runner if single-floppy, "otherwise need modifications" | `MXO`, `MXOP` | 6 |
| 6 | "direct floppy controller access, and loading from floppy during gameplay" | "modding of game code": a RAM disk, RAM swapping, or "the best: having everything needed for hard disk access in high RAM - so GEMDOS filesystem (FAT16) driver & hard disk driver" | `MXIF` | 107 |

The code's letters (PP, `agcat.html`): **M** multipart, **S** singlepart(ed); a digit for the RAM
it needs (**5** 512 KB, **1** 1 MB); **T** "TOS dependant", **I** "TOS independant", **O** "only
little TOS"; **P** "TPA (relocatible)"; **L** "using filesys"; **F** "direct Floppy access". The
game pages use more letters than `agcat.html` defines: **A** goes with "TOS/AES dep" (`M5ATPL`,
41 pages) and **E** with "AES dependant" (`M5EPL`); **X** with the XBIOS loaders of category 5
(`M5TX8`: Alternate Reality, listed there); **DFC** (97 pages, `M5DFC`) is not explained anywhere
in the mirror. 1,609 of the 1,829 pages carry a code; the most common are `M5TPL`/`M1TPL` (908),
`M#IF` (253), `M#DFC` (97), `M#TL` (80), `M#ATPL` (41); 108 codes start with `S`.

Category 6 is the expensive one, and PP's "best" answer to it is the mode that does not run from a
GEMDOS drive (§3.3): his GEMDOS and a hard-disk driver in high RAM, reaching the disk by sectors.

## 3. The modes, from a game's files

The mode shows in the game folder's files. Counts are of the 1,947 archives, each counted once in
the first row that matches (STORY-03 makes the real table, game by game):

| files in the folder | mode | archives | how the game reaches its files | run on the GEMDOS drive |
| --- | --- | --- | --- | --- |
| `RUNME*.TOS` + `HAGA` (+ `D15RH.FIC`/`D15RF.FIC`, or `D15RU.FIC`, or no GOS) | HAGA | 1,108 (357 / 297 / 447, 7 with `D15R_5H`/`5F`) | HAGA's file service: the machine's own GEMDOS, by name | Wormhole, Quest for Galaxia, Andromeda: title screens |
| `RUNME*.TOS` + `HAGE` + `FILES\T14AG.FIC` + a floppy image | HAGE | 219 (215 with an image) | TOS 1.04 (with GEM) in RAM; its floppy reads come from the image, which HAGE reads with the machine's GEMDOS | Breakout ACC: TOS 1.04's desktop, drive A on the image |
| `RUNME*.TOS` + `HAG2` + `FILES\T14GG.FIC` + a floppy image | HAG2 | 141 (all with an image) | the same with TOS 1.04 without GEM | 180: its title; Vector Invaders (monochrome, 2 MB): in play |
| `START.TOS`/`.PRG` + `GXUTnnn.PRG`, no `D15R` | Gamex, no GOS | 120 | the machine's GEMDOS: the launcher loads or `Pexec`s the game's files | Castle Master: "Choose your character" |
| `START.TOS` + `D15R_NG1.FIC`/`D15R_F1.FIC` | Gamex + GOS 1.00 | 7 | the machine's GEMDOS before the game starts; the game runs under GOS | Garfield: its intro |
| `START.TOS` + `D15R_HH4.FIC`/`D15R_F4.FIC` | Gamex + GOS4 | 90 | GOS's GEMDOS, by sectors, through a driver it copies or boots | Magnetik Tank: back to the desktop |
| `START.TOS` + `D15R_H5`/`F5`, `H15`/`F15`, `5H`/`5F` | Gamex + GOS5 | 33 + 44 | the same (Lemmings, EPIC-01/02) | Clever & Smart, Bubble Dizzy: back to the desktop |
| `START.TOS`/`.PRG` without `GXUT` | PP's launcher without Gamex | 56 | the machine's GEMDOS (Recoil: one packed file, `RECCODE.FIC`) | Recoil: its attract screens |
| an `AUTO` folder | AUTO | 1 | the machine's GEMDOS, started at boot | not run |
| `FBHOLE.PRG`/`SBHOLE.PRG`/`HOLE.PRG` + the game's own files | HOLE | 5 (+ the tool) | the machine's GEMDOS; HOLE only keeps the low 512 KB free | Aquanaut, without HOLE: back to the desktop |
| a floppy image (`.ST`, `.MSA`) and no launcher | for the Image Runner | 13 | the image, read with GEMDOS `Fopen`, becomes drive A | not run |
| none of the above | | 103 | (PP's tools, plain installations: STORY-03) | |

**What the launchers share** (code): every Gamex launcher unpacked here (Lemmings, Magnetik Tank,
Clever & Smart, Bubble Dizzy, Garfield, Castle Master) has the frame of PP's three published
sources: the hardware screen ("Machine:", "TOS RAM:"), the RAM checks ("Too much low RAM
occupied", "Min RAM"), the Mega STE clock and Falcon bus and cache settings (not in Garfield's),
the cover picture (a `.PCH` file), the Gamex id `PPGX` and PP's unpacker. What differs is how the
game's files are read (the table) and, before 2012, the driver checks (§3.3). In the HAGA family
the frame moved into the shared module (`HAGA`, `HAGE`: the hardware screen, the settings, the
unpacker) and `RUNME.TOS` (the RAM messages). Recoil's `START.PRG`, a launcher without Gamex, has
only the unpacker.

### 3.1 HAGA (since January 2012)

**PP** (`fromhd2.php`): "Earlier adaptations, before Jan. 2012 work only with mine drivers, AHDI,
and Seimet's Hddriver. Later ones, where you can see file HAGA or HAGE, HAG2 in root folder of game
will work with any decent driver". `fromhd3.php`: beginners should take adaptations "done after
date Jan. 13 2012 … They work well with all decent hard disk driver SW, in emulators." Saves:
"File with name GSxx.TOS will be created … Yes, it is runnable !" `GamexUsage.html`/`fromhd2.php`:
the shared files (`D15R*`, `D15RU.FIC`, `HAGA`, `HAGE`, `HAG2`, `T14AG.FIC`, `T14GG.FIC`) may live
once in `C:\GAMEX`. HAGA games carry a floppy image less often than HAGE and HAG2 ones (82 of
1,108).

**Code** (Wormhole, `WORMHOLE.ZIP`, May 2020): `RUNME.TOS` (1,515 bytes, a plain GEMDOS program)
reads `HAGA` from the game folder, else `C:\GAMEX\HAGA`, and copies it to the top of RAM (`$F8000`
with 1 MB). `HAGA` is about 13 KB of PP's code (0.4% of it found in TOS 1.04), starting with a table
of 16 word offsets to its entries: hardware detection and the Mega STE/Falcon/TT settings, the
cover, the start, the state saves (`GSAU.TOS`, `GSxx.TOS`), the hooks, and a **file service**
(entry 4): from a parameter block (buffer, offset, length, a `'cR'`/`'Wr'` mode word, a name) it
saves the game's state and calls the machine's GEMDOS (`Fopen`/`Fcreate`, `Fseek`,
`Fread`/`Fwrite`, `Fclose`), then gives the game its machine back. It also checks for PP's driver
(`PPHD`, as Lemmings' launcher does) and handles the disk vectors. The `HAGA` file exists in 25
versions; the most common two cover 912 of the 1,109 copies. `D15RU.FIC` is a GOS (TOS 1.04's
BIOS, XBIOS and GEMDOS in RAM, 89,632 bytes unpacked; "new HAGA file with single D15R* (TOS 1.04
in RAM) solution" on the game pages), started before the game; by their names `D15RH`/`D15RF`
are an ST and a Falcon build, as `D15R_H5`/`F5` are (EPIC-02). Game data is PP's
packed format, several streams in one file (Wormhole's `FILES\WHD`: `DATA1.DAT`…`DATA5.DAT`).

**Run** (Wormhole, 20261011-190920 on the GEMDOS drive, 20261011-190812 on PPDRIVER): both reach
the title. On the GEMDOS drive every file (`HAGA`, `WHLA`, `D15RU.FIC`, `WHD`) is opened by name
and served by Hatari; `WHD` is opened from HAGA's own code (PC `$F902C`, its copy at `$F8000`).
On PPDRIVER the same `Fopen`s become TOS's own `Rwabs` on drive C (PC `$FC9206`, the ROM). The
only sector reads on the GEMDOS drive are GOS's: `Getbpb(0)` and two `Rwabs` on drive A when it
starts, with no floppy; it carries on (PP: "keep some floppy disk in your floppy drive A …
Important mostly for earlier adaptations"). Quest for Galaxia (HAGA + `D15RH`) and Andromeda (HAGA,
no GOS) do the same.

### 3.2 HAGE and HAG2

**Code**: `HAGE` and `HAG2` (12,394 bytes each, most common versions) differ in 11 bytes: their
own name, the TOS file they load (`C:\GAMEX\T14AG.FIC` or `C:\GAMEX\T14GG.FIC`, and `FILES\…` in
the game) and its size. `T14AG.FIC` unpacks to 179,269 bytes ("T14AGH22.TOS") that cover TOS
1.04 from `$FC0000` to `$FEC000`, GEM included; `T14GG.FIC` to 87,363 bytes ("T14G16.TOS"), the
BIOS, XBIOS and GEMDOS only, like the D15R files. Breakout ACC's page: "TOS/AES dep … HAGE-fying",
`M5ATPL`.

**Run** (Breakout ACC, 20261011-192118): `HAGE` loads `T14AG.FIC`, TOS 1.04 starts in RAM and
reaches its GEM desktop (the game is a desk accessory). Between TOS's floppy reads (`Rwabs` on
drive 0 from the RAM copy, PC `$C4172`), HAGE reads the game's floppy image `FILES\B.ST` with the
machine's GEMDOS, from its own code (PC `$F8FF6`): `Fread(6144)` from the start, then `Fseek(12288)`
and `Fread(35328)`. The game keeps its floppy, as an image, and HAGE stands in for the drive.

**Run** (Vector Invaders; its page: "Needs monochrome capable monitor", "min 1 MB RAM"): with
1 MB it halts, in colour or monochrome, on ST TOS 1.04 and STE TOS 1.62, on the GEMDOS drive and on
PPDRIVER alike (20261011-192209, -192639, -194136 mono, -194301 mono PPDRIVER, -194842 STE mono):
after the image's first 6,144 bytes HAG2 asks for `Fseek(-113984)` and `Fread(193856)` into
`$82800`, and an `RTE` in the RAM TOS takes an Address Error (PC `$DA9EA`, `hatari.log`). With
2 MB, monochrome, on the GEMDOS drive (20261011-195006) the same `HAG2` seeks to 6,144 and the game
plays. Not the image: a copy with its boot sector's sector count made to match the trimmed file
(720 → 144) halts the same (20261011-194559). So in Hatari this adaptation needs 2 MB, not the 1 MB
its page gives, whichever the disk. 180 (HAG2, colour,
20261011-193147) reaches its title: `HAG2` loads `T14GG.FIC` and reads the game's image
`FILES\1.ST` by name, as Breakout ACC does.

### 3.3 Gamex with GOS4 and GOS5 (before 2012)

**PP** (`GAMEXdoc.html`): the RAM map with 1 MB, GOS4: "768KB-860KB GEMDOS 0.15", "700KB-768KB Hard
disk driver, buffers - used while playing game"; GOS5: "Modded, reduced GEMDOS 0.15, only for
file I/O". `GamexUsage.html`: "Supported hard disk drivers are: mine (PP), AHDI, Hddriver … ICD
drivers, other drivers are not supported"; in emulators they work "only when real hard disk
emulation is set". `fromhd.php`, on GEMDOS drives: "some game hard disk adaptations use such
functions [XBIOS sector access], and worse: direct hard disk access - that's not present in
GEMdrive".

**Code**: every GOS4/GOS5 launcher looked at has the checks EPIC-01 found in Lemmings
(`src/notes/launch-chain.md` step 7, `src/notes/gemdrive-failure.md`): the `PPHD` check on
`hdv_bpb`; PP's driver copied to `$B7180`; otherwise `pun_ptr` and XBIOS `DMAread` of sector 0 and
the driver booted from it (`'DMAr'`). Found in Lemmings' `LEMLD2.TOS` and in Magnetik Tank's
(GOS4), Clever & Smart's and Bubble Dizzy's (GOS5) unpacked launchers (§5). The game's files are
then read by GOS's GEMDOS, by sectors through that driver (`src/notes/disk-layer.md`).

**Run**: Magnetik Tank (20261011-191703) and Clever & Smart (20261011-191754) load their GOS, ask
for the current path and quit (`Pterm0`) without a word; Bubble Dizzy (20261011-191845) also loads a
data file (`BUDI.FIC`) first, then quits the same way. On PPDRIVER all three play (20261011-192804
Magnetik Tank in its first room, 20261011-192854 Clever & Smart in play, 20261011-192945 Bubble
Dizzy's high scores), with 42, 61 and 56 `Rwabs` on drive C and no file opened by name after the
GOS: from there the game's files are read by sectors. Lemmings prints "This prg. requires PP,
AHDI or Hddriver" (EPIC-01).

### 3.4 Gamex without GOS, and with GOS 1.00

**PP**: his three published launchers (`astopensw.php`: "1: for TPA executables 2: For games not
using TOS 3: Using GOS 1.00, for singleparted game"). Castle Master (`GamexLSrc.html`) `Pexec`s
the game's own programs (`CASTLE1.TOS`, `CASTLE2.CTE`); Sideways (`GamexLSrc2.html`) is
"singleparted + packed": one `Fopen` of `S123.FIC`, unpacked into place; Starglider
(`GamexLSrc3.html`) installs "modded GEMDOS 0.15 of TOS 1.04" (`D15R_NG1.FIC`) in high RAM "and
run[s] under GEMDOS 0.15", "AUTO run without reset of ST". All three read with the machine's
GEMDOS; Gamex's part is the exit to the desktop and the state save (`GAMEXdoc.html`: "Gamex
handles not loading of game files, it is on launcher").

**Code**: neither Castle Master's nor Garfield's (GOS 1.00) unpacked launcher has the `PPHD` or
`DMAread` checks.

**Run**: Castle Master (20261011-191521) opens `CASTLEM.PCH` and `CASTLE1.TOS` by name and
reaches "Choose your character"; Garfield (20261011-191612) loads `D15R_NG1.FIC`, `GART.FIC`,
`GASM.FIC` by name and plays its intro. No sector reads in either.

### 3.5 The rest

- **HOLE** (`HOLE.ZIP`, `plafh.html`): not a launcher. FBHOLE/SBHOLE write a floppy boot sector
  that keeps the low 512 KB (or 1 MB) free before the hard disk boots; `HOLE.PRG` does it from a
  floppy's AUTO folder. The game is its own files ("Working games on TOS 2.06, Falcon: Millennium
  2.2, Chuckie Egg 2, Monthy Python, F16 Falcon, Aquanaut …"). PP's answer to category 4.
  **Run** (Aquanaut, 20261011-193036, started without HOLE): `AQUANAUT.PRG` `Pexec`s
  `AQUANAUT.EXE` by name and both end at once, back on the desktop; not run with HOLE's floppy.
- **AUTO** (`agcat.html` category 4; Goal: "run from AUTO folder of boot partition on hard disk").
- **The Floppy Image Runner** (`imgrun.php`, `IMGRUN3.S`): "copy image file in high RAM and
  restart TOS, then mounting RAMdisk as drive A … Hard disk driver is discarded"; "GEMDos file
  access and XBIOS A floppy read is mapped to RAMdisk". It opens the image with GEMDOS `Fopen` and
  hooks `hdv_bpb`/`hdv_rw`/`hdv_mediach`. `IMGRF2X` adds TOS 1.04 in RAM (`T14UIDUB.FIC`, a whole
  TOS 1.04 ROM). It does not work for "games using direct FDC access".
- **RAM TOS** (`RAMTOS.ZIP`): SELTOS/RAMTOS install a TOS 1.00, 1.04 or 2.06 ROM image in RAM
  and restart ("making possible work with diverse versions of TOS without changing (EP)ROM's").
- **iTOS**: PP's own improved TOS (1.04i, 1.62i) with a hard-disk driver inside; "different ones
  (D15R***.FIC) are needed for improved TOS" (`fromhd2.php`). `D15RI.FIC` ("D15I81.TOS") is in
  2 archives; Space Ace's page says "needs PP iTOS". Not regular TOS, which PP supports "1.00-4.04".
- **Small tools**: `HDTCFIX` (Hddriver's Timer C fix for some games), `512K_1M` (make a bigger
  machine act like 512 KB or 1 MB), `GXUTnnn.PRG` (Gamex utility: continue, save the state, free
  RAM).
  `AUTOlist Run` (`plafh.html`: "for easy launch of games (running only from AUTO) from hard
  disk"): its download, `ALISTR`, answered 404 when the site was mirrored, so it is not looked at.

## 4. First guesses at the verdicts

For STORY-05 to check game by game (D-14: as it is / fix / not feasible):

| mode | guess | why |
| --- | --- | --- |
| HAGA | as it is | runs reach the game; files by name through the machine's GEMDOS. To check: the state saves (`GSxx.TOS`, written through the same service), and GOS's two reads of drive A |
| HAGE, HAG2 | as it is | Breakout ACC, 180 and Vector Invaders run; the floppy image is read by name. Some games need the harness's `--monitor mono` or more RAM than their page says (Vector Invaders: 2 MB) |
| Gamex, no GOS; Gamex + GOS 1.00 | as it is | runs reach the game; no driver checks in the launcher |
| Gamex + GOS4, GOS5 | fix | the launcher needs a driver (PP's, or one it can boot from sector 0) and GOS reads by sectors; EPIC-01 and these runs |
| PP's launcher without Gamex | as it is, likely | Recoil runs; these launchers are not all read yet (STORY-03) |
| HOLE, AUTO, plain | as it is, likely | the game reads by name; HOLE needs its floppy boot sector (Aquanaut stops without it), AUTO a boot from C: |
| floppy image for the Image Runner | open | the image is read by name, then a reset with the driver discarded |
| iTOS | not feasible as it is | needs PP's own TOS |

So the "fix" work is the pre-2012 Gamex launchers with GOS4/GOS5 (about 167 archives), not the
HAGA family (about 1,468): the opposite of what EPIC-01's Lemmings alone suggested.

## 5. Signatures and the GOS builds

The byte patterns that mark each mode are in `launcher-signatures.md` ("Other modes"): the HAGA
family's names and module table, the three driver checks of the GOS4/GOS5 launchers (absent from
the GOS 1.00 and Gamex-only ones), the GOS builds' header names, and the TOS-in-RAM files.

How much of each shared file is TOS 1.04 (16-byte runs found in the UK ROM, without relocation):
`D15R_NG1`/`F1`/`HH4`/`F4` 89–90% (nearly whole copies of BIOS, XBIOS and GEMDOS), `D15RH`/`RF`/`RU`
67–74%, `T14GG` 64%, `T14AG` 67% (with GEM), `D15R_5H`/`5F` 58%, `D15R_H5`/`F5`/`H15`/`F15` 44%
(EPIC-02 found 70.4% for `D15R_H5` once relocation is counted).

## 6. The glossary

Terms from the list's Note column and the game pages, and where they belong:

| term | meaning | mode or category |
| --- | --- | --- |
| Gamex, GX | PP's "gaming extra" system: exit to the desktop, state saves (`GAMEXdoc.html`: "should mean something like 'gaming extra', 'games exitable'"); in 112 Note cells, mostly dated 2009–2011 | any launcher with `GXUT` or HAGA |
| HAGA, Haga, H | the January 2012 launcher family; all 17 Note cells "H" are on rows dated 2012 (e.g. Millennium 2.2, To Be On Top) | HAGA |
| HAGE, "new HAGE system", "HAGE-fying" | TOS 1.04 with GEM in RAM + floppy image | HAGE |
| HAG2, "HAG2 v." | TOS 1.04 without GEM in RAM | HAG2 |
| GOS, "gamex + GOS" | "special GEMDOS adaptation" (Bombuzal's page): TOS 1.04's GEMDOS 0.15 in RAM, "D15R … abrev. means GEMDOS 0.15 relocated, reassembled" (`GamexUsage.html`); GOS 1.00, GOS4, GOS5 | §3.3, §3.4 |
| "TOS 1.04 in RAM", "single D15R*" | `D15RU.FIC`, one GOS for every machine | HAGA |
| singleparted, singlepart | the RAM at the game's start, packed, restored from disk (`agcat.html` 3) | Cat `S…` |
| filed | a game stored outside the file system made into files (`playfhd.html`: "transfer disk content to file(s)") | Lemmings |
| filewise ramdisked | not defined by PP. `playfhd.html` calls a RAM disk the "usual way" for games that load during play; Lemmings, though, reads its level files from the disk during play (EPIC-02), so it does not mean all files in RAM. Open | Lemmings |
| "redirect to hard disk" (325 pages) | the game's floppy paths changed to the hard disk (`agcat.html` 2: "path corrections in code") | Cat 2 |
| "instead ramdisk, load from drive" | levels read from disk during play instead of a RAM disk (Clever & Smart's page) | GOS5 |
| "xbios loads directed to image files on hard disk" | the XBIOS floppy reads served from an image file (Black Cauldron) | Cat 5 |
| deprot, deprotected, crk | the copy protection removed; the source was a crack | any |
| "src. STX/ST/MSA img. of org./crk." | what PP started from | any |
| TOS dep, TOS indep, little TOS dep, TOS/AES dep, STOS dep | the game's use of TOS (T, I, O, A) | the code |
| "Cat: M5TPL" … | §2 | |
| Tr., Trainer, "Unlim. lives" | cheats added (562 + 118 Note rows) | none |
| C-M | colour and mono ("Color and mono mode") | none |
| statesave, savestate, "exit to Desktop" | Gamex | any Gamex mode |
| "done by JY" (16 pages) | a HAGA adaptation made by someone else, "JY" | HAGA |
| light green background | adaptations after January 13 2012 on the download pages (`fromhd3.php`) | HAGA family |

## 7. Lemmings, the worked example

Lemmings is Gamex with GOS5 (`D15R_H5`/`F5`), from before 2012 (`LEMMINGS.ZIP` in the mirror holds
the same 76 files as `LEMMINGS/`, SHA-256 for SHA-256). Its page: "Added gamex, deprotected,
filed, filewise ramdisked"; no `Cat:`. Its launcher has the three driver checks (§3.3, §5), its
files are read by GOS by sectors through PP's driver copy (`src/notes/disk-layer.md`), and from a
GEMDOS drive it stops at the check (EPIC-01). In this note's terms: mode Gamex + GOS5, first guess
"fix", like the other 166 archives of §3.3.
