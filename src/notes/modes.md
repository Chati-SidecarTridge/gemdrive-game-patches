# The modes: how the adaptations reach their files

The hard-disk adaptations on the 8bitchip.info website start their games in a few ways, called
modes here. For each mode this page gives the files that mark it, how the game reaches its files
while it runs, and what happens on a GEMDOS drive. A GEMDOS drive (Hatari's `--harddrive`, the
Multidevice's GEMDRIVE) serves files by name and has no sectors, the numbered blocks of a disk.
The facts come from the website's documentation, the files of its 1,947 archives, and one Hatari
run per mode (§8). The verdicts in §4 are first guesses; `solutions.md` has the
results of running every game.

## 1. Two ways the games are sorted

The 8bitchip.info website sorts the games into six categories by how the original game used the
floppy (§2). This page sorts the adaptations into modes by the launcher, the program the user
runs (`START.TOS` or `RUNME.TOS`) (§3). The category says how much work the adaptation needed. The
mode says how the adapted game reaches its files, and so whether it runs from a GEMDOS drive:

- **By name.** The game asks GEMDOS, the part of TOS that handles files, to open a file. Every
  drive serves that, a GEMDOS drive included.
- **By sectors.** The game, or a GEMDOS in RAM that it brings, reads the disk's sectors through a
  hard-disk driver. A GEMDOS drive has no sectors to give.

## 2. The six categories and the `Cat:` code

`agcat.html`, "Atari ST game categorisation by hard disk run possibility - way how to solve it",
was written after "adapting about 450 Atari ST(E) games". The quotes below are from it.

| # | the original game | the way to run it from a hard disk | code | of 450 |
| --- | --- | --- | --- | --- |
| 1 | "using regular filesys, fully relocatible", no copy protection, relative paths | "easy hard disk installable" | `MXTPL` | 40 |
| 2 | the same, with copy protection; "often file access is set for floppy A" | cracks; path corrections in the code, the Floppy Image Runner, or "resident code which removes absolute path (A:\\)" | `MXTPL` | 130 |
| 3 | "do not access floppy after start" | "take RAM content in moment of start", pack it, restore it from the hard disk: "I call them singleparted"; on later TOS, "Image Runner or GOS 4" | `SXT`, `SXI`, `SXO` | 104 |
| 4 | regular filesystem "but limited to low RAM" | "run from AUTO, using HOLE, Floppy Image Runner, GOS 4, hard disk driver in high RAM" | `MXTL` | 61 |
| 5 | "using XBIOS for loading from floppy" | the Floppy Image Runner if single-floppy, "otherwise need modifications" | `MXO`, `MXOP` | 6 |
| 6 | "direct floppy controller access, and loading from floppy during gameplay" | "modding of game code": a RAM disk, RAM swapping, or "the best: having everything needed for hard disk access in high RAM - so GEMDOS filesystem (FAT16) driver & hard disk driver" | `MXIF` | 107 |

GOS, HOLE and the Floppy Image Runner are described in §3.3 and §3.5.

Each game page gives its category as a code, such as `Cat: M5TPL`. The letters, as `agcat.html`
defines them:

| letter | meaning |
| --- | --- |
| **M**, **S** | multipart, singlepart(ed) |
| **5**, **1** | the RAM it needs: 512 KB, 1 MB |
| **T**, **I**, **O** | "TOS dependant", "TOS independant", "only little TOS" |
| **P** | "TPA (relocatible)" |
| **L** | "using filesys" |
| **F** | "direct Floppy access" |

The game pages use more letters. **A** goes with "TOS/AES dep" (`M5ATPL`, 41 pages), **E** with
"AES dependant" (`M5EPL`), **X** with the XBIOS loaders of category 5 (`M5TX8`, Alternate Reality,
listed there). **DFC** (`M5DFC`, 97 pages) is explained nowhere on the website. 1,609 of the
1,829 game pages carry a code. The most common are `M5TPL`/`M1TPL` (908), `M#IF` (253), `M#DFC`
(97), `M#TL` (80) and `M#ATPL` (41). 108 codes start with `S`.

Category 6 is the expensive one. The documentation's "best" answer to it, GOS and a hard-disk
driver in high RAM, reads the disk by sectors: it is the mode that does not run from a GEMDOS
drive (§3.3).

## 3. The modes, from a game's files

The files in a game's folder show its mode. Each of the 1,947 archives is counted once, in the
first row it matches; `recognising-modes.md` counts games instead.

| files in the folder | mode | archives | reaches its files | section |
| --- | --- | ---: | --- | --- |
| `RUNME*.TOS` + `HAGA` (+ `D15RH.FIC`/`D15RF.FIC`, or `D15RU.FIC`, or no GOS) | HAGA | 1,108 | by name | §3.1 |
| `RUNME*.TOS` + `HAGE` + `FILES\T14AG.FIC` + a floppy image | HAGE | 219 | by name (the image) | §3.2 |
| `RUNME*.TOS` + `HAG2` + `FILES\T14GG.FIC` + a floppy image | HAG2 | 141 | by name (the image) | §3.2 |
| `START.TOS` + `D15R_HH4.FIC`/`D15R_F4.FIC` | Gamex + GOS4 | 90 | by sectors | §3.3 |
| `START.TOS` + `D15R_H5`/`F5`, `H15`/`F15`, `5H`/`5F` | Gamex + GOS5 | 33 + 44 | by sectors | §3.3 |
| `START.TOS`/`.PRG` + `GXUTnnn.PRG`, no `D15R` | Gamex, no GOS | 120 | by name | §3.4 |
| `START.TOS` + `D15R_NG1.FIC`/`D15R_F1.FIC` | Gamex + GOS 1.00 | 7 | by name | §3.4 |
| `START.TOS`/`.PRG` without `GXUT` | a launcher without Gamex | 56 | by name | §3.5 |
| an `AUTO` folder | AUTO | 1 | by name | §3.5 |
| `FBHOLE.PRG`/`SBHOLE.PRG`/`HOLE.PRG` + the game's own files | HOLE | 5 (+ the tool) | by name | §3.5 |
| a floppy image (`.ST`, `.MSA`) and no launcher | for the Image Runner | 13 | by name (the image) | §3.5 |
| none of the above: tools and plain installations, and the FWRD RAM disks | | 103 | by name | §3.6, §3.7 |

The names in the table:

- **Gamex** ("gaming extra") adds an exit to the desktop and state saves. Its utility is
  `GXUTnnn.PRG`.
- **GOS** is TOS 1.04's GEMDOS 0.15, modified, loaded into high RAM before the game. Its builds
  are the `D15R…` files: GOS 1.00, GOS4, GOS5, and those of the HAGA family.
- **HAGA**, **HAGE** and **HAG2** are the shared modules of the adaptations made since January
  2012, the HAGA family.
- **T14** files hold TOS 1.04 itself, for HAGE and HAG2. §5 says how much of each D15R and T14 file
  is TOS 1.04.

**What the launchers share.** Every Gamex launcher unpacked here (Lemmings, Magnetik Tank, Clever &
Smart, Bubble Dizzy, Garfield, Castle Master) has the frame of the three published launcher
sources: the hardware screen ("Machine:", "TOS RAM:"), the RAM checks ("Too much low RAM
occupied", "Min RAM"), the Mega STE clock and the Falcon bus and cache settings (not in
Garfield's), the cover picture (a `.PCH` file), the Gamex id `PPGX` and the same unpacker. They
differ in how they read the game's files and, before 2012, in the driver checks (§3.3). In the
HAGA family the frame moved into the module (`HAGA` and `HAGE` hold the hardware screen, the
settings and the unpacker) and into `RUNME.TOS` (the RAM messages). Recoil's `START.PRG`, a
launcher without Gamex, has only the unpacker.

### 3.1 HAGA (since January 2012)

**The files.** `RUNME.TOS`, the module `HAGA`, the game's data in `FILES\` and, in most games, a
GOS. Of the 1,108 HAGA archives, 357 have `D15RH.FIC` and `D15RF.FIC`, 297 have `D15RU.FIC`, 447
have no GOS and 7 have `D15R_5H`/`5F`. The shared files (`D15R*`, `D15RU.FIC`, `HAGA`,
`HAGE`, `HAG2`, `T14AG.FIC`, `T14GG.FIC`) may be kept once, in `C:\GAMEX` (`GamexUsage.html`,
`fromhd2.php`). Only 82 of the 1,108 HAGA archives carry a floppy image.

The documentation promises any driver. `fromhd2.php`: "Earlier adaptations, before Jan. 2012
work only with mine drivers, AHDI, and Seimet's Hddriver. Later ones, where you can see file HAGA
or HAGE, HAG2 in root folder of game will work with any decent driver". `fromhd3.php` tells
beginners to take adaptations "done after date Jan. 13 2012 … They work well with all decent hard
disk driver SW, in emulators." Its state saves are programs: "File with name GSxx.TOS will be
created … Yes, it is runnable !"

**How it starts**, from Wormhole's files (`WORMHOLE.ZIP`, May 2020):

- `RUNME.TOS`, a plain GEMDOS program of 1,515 bytes, reads `HAGA` from the game folder, or else
  `C:\GAMEX\HAGA`, and copies it to the top of RAM (`$F8000` with 1 MB).
- `HAGA` is about 13 KB of code of its own (0.4% of it is found in TOS 1.04). It starts with a
  table of 16 word offsets to its entries: hardware detection, the Mega STE, Falcon and TT
  settings, the cover, the start, the state saves (`GSAU.TOS`, `GSxx.TOS`), the hooks and the file
  service (entry 4). It also checks for PPDRIVER (`PPHD`), as Lemmings' launcher does, and handles
  the disk vectors. It exists in 25 versions; the two most common cover 912 of its 1,109 copies.
- `D15RU.FIC` is a GOS: TOS 1.04's BIOS, XBIOS and GEMDOS in RAM, 89,632 bytes unpacked (the game
  pages: "new HAGA file with single D15R* (TOS 1.04 in RAM) solution"). It starts before the game,
  for the game's TOS calls. By their names, `D15RH`/`D15RF` are an ST and a Falcon build, as
  `D15R_H5`/`F5` are (`launch-chain.md`).

**How the game reaches its files.** Through HAGA's file service. The game hands it a parameter
block: a buffer, an offset, a length, a mode word (`'cR'` or `'Wr'`) and a name. The service saves
the game's state, calls the machine's GEMDOS (`Fopen` or `Fcreate`, `Fseek`, `Fread` or `Fwrite`,
`Fclose`), and gives the game its machine back. The data is in the adaptations' packed format,
several streams to a file: Wormhole's `FILES\WHD` holds `DATA1.DAT` to `DATA5.DAT`.

**On a GEMDOS drive** it runs. Wormhole reaches its title from the GEMDOS drive (run
20261011-190920) and from PPDRIVER (20261011-190812):

- From the GEMDOS drive, Hatari serves every file by name: `HAGA`, `WHLA`, `D15RU.FIC`, `WHD`.
  `WHD` is opened from HAGA's own code (PC `$F902C`, its copy at `$F8000`).
- From PPDRIVER, the same `Fopen`s become TOS's own `Rwabs` on drive C (PC `$FC9206`, the ROM).
- The only sector reads from the GEMDOS drive are GOS's, when it starts: `Getbpb(0)` and two
  `Rwabs` on drive A, which has no floppy. GOS carries on. The documentation: "keep some floppy
  disk in your floppy drive A … Important mostly for earlier adaptations".

Quest for Galaxia (HAGA with `D15RH`) and Andromeda (HAGA, no GOS) behave the same.

### 3.2 HAGE and HAG2

**The files.** The module, a TOS 1.04 to load into RAM, and the game's original floppy as an image
file in `FILES\`:

- `HAGE` loads `T14AG.FIC`: 179,269 bytes unpacked ("T14AGH22.TOS"), TOS 1.04 from `$FC0000` to
  `$FEC000`, GEM included. Breakout ACC's page: "TOS/AES dep … HAGE-fying", `M5ATPL`.
- `HAG2` loads `T14GG.FIC`: 87,363 bytes unpacked ("T14G16.TOS"), the BIOS, XBIOS and GEMDOS
  only, like the D15R files.
- `HAGE` and `HAG2` (12,394 bytes each, most common versions) differ in 11 bytes: their own name,
  the TOS file they load (`C:\GAMEX\T14AG.FIC` or `C:\GAMEX\T14GG.FIC`, and `FILES\…` in the game)
  and its size.

215 of the 219 HAGE archives and all 141 HAG2 archives carry the image.

**How the game reaches its files.** The game runs on the TOS in RAM and reads its floppy, drive A,
by sectors. The module serves those reads from the image file, which it reads by name with the
machine's GEMDOS.

**On a GEMDOS drive** it runs. In Breakout ACC (HAGE, run 20261011-192118), TOS 1.04 starts in RAM
and reaches its GEM desktop; the game is a desk accessory. TOS's floppy reads are `Rwabs` on drive
0, from the RAM copy (PC `$C4172`). Between them, HAGE reads the image `FILES\B.ST` with the
machine's GEMDOS, from its own code (PC `$F8FF6`): `Fread(6144)` from the start, then
`Fseek(12288)` and `Fread(35328)`. 180 (HAG2, colour, 20261011-193147) reaches its title the same
way, from `T14GG.FIC` and the image `FILES\1.ST`.

**Vector Invaders needs 2 MB, not the 1 MB its page gives** ("Needs monochrome capable monitor",
"min 1 MB RAM"):

- With 1 MB it halts, in colour or monochrome, on the ST with TOS 1.04 and the STE with TOS 1.62,
  from the GEMDOS drive and from PPDRIVER alike (runs 20261011-192209, -192639, -194136 mono,
  -194301 mono PPDRIVER, -194842 STE mono). After the image's first 6,144 bytes, HAG2 asks for
  `Fseek(-113984)` and `Fread(193856)` into `$82800`, and an `RTE` in the RAM TOS takes an Address
  Error (PC `$DA9EA`, `hatari.log`).
- With 2 MB, monochrome, from the GEMDOS drive (20261011-195006), the same `HAG2` seeks to 6,144
  and the game plays.
- The image is not the cause: a copy whose boot sector's sector count matches the trimmed file
  (720 → 144) halts the same way (20261011-194559).

### 3.3 Gamex with GOS4 and GOS5 (before 2012)

**The files.** `START.TOS` and a GOS: `D15R_HH4.FIC` or `D15R_F4.FIC` for GOS4 (90 archives),
`D15R_H5`/`F5`, `H15`/`F15` or `5H`/`5F` for GOS5 (33 + 44). Lemmings is one (§7).

`GAMEXdoc.html` gives the RAM map with 1 MB. GOS4: "768KB-860KB GEMDOS 0.15", "700KB-768KB Hard
disk driver, buffers - used while playing game". GOS5: "Modded, reduced GEMDOS 0.15, only for
file I/O". `GamexUsage.html` supports four drivers, PPDRIVER, AHDI, Hddriver and ICD's ("other
drivers are not supported"), and in emulators "only when real hard disk emulation is set".
`fromhd.php`, on GEMDOS drives: "some game hard disk adaptations use such functions [XBIOS sector
access], and worse: direct hard disk access - that's not present in GEMdrive".

**How the game reaches its files.** First the launcher makes sure a driver is there. Every GOS4
and GOS5 launcher looked at has the three checks of Lemmings' launcher (`launch-chain.md` step 7,
`gemdrive-failure.md`):

1. It looks for PPDRIVER's `PPHD` signature through `hdv_bpb`, and if it finds it, copies
   PPDRIVER to `$B7180`.
2. Otherwise it reads `pun_ptr`, and reads sector 0 with XBIOS `DMAread`.
3. It boots the driver found in that sector (the `'DMAr'` pattern).

They are in Lemmings' `LEMLD2.TOS` and in the unpacked launchers of Magnetik Tank (GOS4), Clever &
Smart and Bubble Dizzy (GOS5) (§5). The game then reads its files through GOS's GEMDOS, which reads
the disk by sectors through that driver (`disk-layer.md`).

**On a GEMDOS drive** these games do not start. Magnetik Tank (run 20261011-191703) and Clever &
Smart (20261011-191754) load their GOS, ask for the current path and quit (`Pterm0`) without a
message, back to the desktop. Bubble Dizzy (20261011-191845) loads a data file (`BUDI.FIC`)
first, then quits the same way. Lemmings prints `This prg. requires PP, AHDI or Hddriver`
(`gemdrive-failure.md`).

From PPDRIVER all three play: Magnetik Tank in its first room (20261011-192804), Clever & Smart in
play (20261011-192854), Bubble Dizzy at its high scores (20261011-192945). They make 42, 61 and 56
`Rwabs` calls on drive C, and open no file by name once GOS has started.

### 3.4 Gamex without GOS, and with GOS 1.00

**The files.** `START.TOS` or `START.PRG` and `GXUTnnn.PRG`, with no `D15R` file (120 archives),
or, with GOS 1.00, `D15R_NG1.FIC` or `D15R_F1.FIC` (7).

The three published launcher sources are one of each kind (`astopensw.php`: "1: for TPA
executables 2: For games not using TOS 3: Using GOS 1.00, for singleparted game"):

- Castle Master (`GamexLSrc.html`) `Pexec`s the game's own programs, `CASTLE1.TOS` and
  `CASTLE2.CTE`.
- Sideways (`GamexLSrc2.html`) is "singleparted + packed": one `Fopen` of `S123.FIC`, unpacked
  into place.
- Starglider (`GamexLSrc3.html`) installs the "modded GEMDOS 0.15 of TOS 1.04" (`D15R_NG1.FIC`) in
  high RAM "and run[s] under GEMDOS 0.15", "AUTO run without reset of ST".

**How the game reaches its files.** By name, with the machine's GEMDOS. Gamex only adds the exit to
the desktop and the state save (`GAMEXdoc.html`: "Gamex handles not loading of game files, it is
on launcher"). Castle Master's and Garfield's (GOS 1.00) launchers, unpacked, have neither the
`PPHD` nor the `DMAread` check.

**On a GEMDOS drive** both run, with no sector reads. Castle Master (run 20261011-191521) opens
`CASTLEM.PCH` and `CASTLE1.TOS` by name and reaches "Choose your character". Garfield
(20261011-191612) loads `D15R_NG1.FIC`, `GART.FIC` and `GASM.FIC` by name and plays its intro.

### 3.5 The rest

- **A launcher without Gamex** (56 archives): `START.TOS` or `START.PRG` without `GXUT`. Recoil's
  has only the Gamex launchers' unpacker, reads one packed file (`RECCODE.FIC`) by name, and
  reaches its attract screens from the GEMDOS drive.
- **HOLE** (`HOLE.ZIP`, `plafh.html`; 5 archives, and the tool) is not a launcher. It keeps the
  low 512 KB (or 1 MB) of RAM free for the game, one of the answers to category 4. `FBHOLE` and
  `SBHOLE` write a floppy boot sector that does it before the hard disk boots; `HOLE.PRG` does it
  from a floppy's AUTO folder. The game is its own files ("Working games on TOS 2.06, Falcon: Millennium 2.2, Chuckie Egg 2,
  Monthy Python, F16 Falcon, Aquanaut …"). Aquanaut, started without HOLE (run 20261011-193036):
  `AQUANAUT.PRG` `Pexec`s `AQUANAUT.EXE` by name and both end at once, back on the desktop. It was
  not run with HOLE's floppy.
- **AUTO** (1 archive, not run): the game starts from the AUTO folder (`agcat.html` category 4;
  Goal: "run from AUTO folder of boot partition on hard disk").
- **The Floppy Image Runner** (`imgrun.php`, `IMGRUN3.S`) runs a game from an image file: "copy
  image file in high RAM and restart TOS, then mounting RAMdisk as drive A … Hard disk driver is
  discarded"; "GEMDos file access and XBIOS A floppy read is mapped to RAMdisk". It opens the image
  with GEMDOS `Fopen` and hooks `hdv_bpb`, `hdv_rw` and `hdv_mediach`. `IMGRF2X` adds TOS 1.04 in
  RAM (`T14UIDUB.FIC`, a whole TOS 1.04 ROM). It does not work for "games using direct FDC access".
  The 13 archives that hold only a floppy image were not run.
- **RAM TOS** (`RAMTOS.ZIP`): SELTOS and RAMTOS install a TOS 1.00, 1.04 or 2.06 ROM image in RAM
  and restart.
- **iTOS**, an improved TOS (1.04i, 1.62i) with a hard-disk driver inside, from the same website,
  needs its own GOS (`fromhd2.php`: "different ones (D15R***.FIC) are needed for improved TOS").
  `D15RI.FIC` ("D15I81.TOS") is in 2 archives; Space Ace's page says it needs iTOS. iTOS is not one
  of the regular TOS versions ("1.00-4.04") the adaptations support.
- **Small tools**: `HDTCFIX` (Hddriver's Timer C fix for some games), `512K_1M` (makes a bigger
  machine act like 512 KB or 1 MB), `GXUTnnn.PRG` (the Gamex utility: continue, save the state,
  free RAM). `AUTOlist Run` (`plafh.html`: "for easy launch of games (running only from AUTO) from
  hard disk") was not looked at: its download, `ALISTR`, answered 404 when the site was copied.

### 3.6 Plain installations

**The files.** The game's own program and data, copied to the hard disk, with no launcher, no
Gamex and no GOS. This is how the documentation handles the games of categories 1 and 2 (§2): a
game that already reads its files through GEMDOS needs only its paths changed from drive A to the
folder it runs from ("redirect to hard disk"), and the copy protection removed.

**How the game reaches its files.** Through the machine's GEMDOS, by name, as on the original
floppy. Nothing is loaded before the game.

**On a GEMDOS drive.** A GEMDOS drive serves exactly that, so a plain installation runs as it is,
unless the game does something besides opening files. Of the 123 games, 113 run as they are. The
others:

- Four Silmarils games ask BIOS `Getbpb` for the drive's layout before every file and wait until
  they get one. A GEMDOS drive has none to give (fix S2, `GDBPB.PRG`).
- Two start programs give back the memory their stack is in, then start the game. Hatari's GEMDOS
  drive clears that memory when it loads the game, and the start program ends (fix S3, the
  fastload bit).
- Great Giana Sisters STE streams its music from a file's sectors through the hard-disk driver
  during play: not feasible from a GEMDOS drive.
- Three games (Roger, Utopos, Spitting Images) fail in Hatari from the PPDRIVER disk too; their
  verdict is unsure.

### 3.7 FWRD RAM disk

**The files.** One `FWRD` file holds every file of the game: a directory, then the files. Only
two adaptations have one, Pick'n'Pile and Lemmings' second download, `LEMMSRD.ZIP` ("2MB RAM
min"). The documentation calls a RAM disk the "usual way" for games that load during play
(`playfhd.html`).

**How the game reaches its files.** The start program reads the whole `FWRD` file into RAM by
name, once. From then on the game loads its files from RAM, and the disk is not used.

**On a GEMDOS drive.** The one read at the start is by name, so it runs as it is. Pick'n'Pile
reaches its title, and `LEMMSRD.ZIP` reaches Lemmings' title menu, from the GEMDOS drive. It needs
2 MB of RAM. Whether Lemmings plays a level this way was not tried.

## 4. First guesses at the verdicts

Before every game was run (`solutions.md`), each mode got a guess at the verdict: as it is,
fix or not feasible.

| mode | guess | why |
| --- | --- | --- |
| HAGA | as it is | it reads by name (§3.1). Still to check: the state saves (`GSxx.TOS`, written through the same service) and GOS's two reads of drive A |
| HAGE, HAG2 | as it is | it reads the image by name (§3.2). Some games need the harness's `--monitor mono`, or more RAM than their page says |
| Gamex, no GOS; Gamex + GOS 1.00 | as it is | it reads by name, and the launcher has no driver checks (§3.4) |
| Gamex + GOS4, GOS5 | fix | the launcher needs a driver, and GOS reads by sectors (§3.3) |
| a launcher without Gamex | as it is, likely | Recoil runs; not all of these launchers had been read yet (`recognising-modes.md` reads them) |
| HOLE, AUTO, plain | as it is, likely | the game reads by name; HOLE needs its floppy boot sector, AUTO a boot from C: |
| FWRD RAM disk | as it is | one file read whole into RAM by name at the start (§3.7) |
| floppy image for the Image Runner | open | the image is read by name, then the machine resets with the driver discarded |
| iTOS | not feasible as it is | it needs iTOS, not a regular TOS |

So the work to fix is in the Gamex launchers with GOS4 or GOS5, from before 2012 (about 167
archives), not in the HAGA family (about 1,468).

## 5. Signatures and the GOS builds

`launcher-signatures.md` ("Other modes") has the byte patterns that mark each mode: the HAGA
family's names and module table, the three driver checks of the GOS4 and GOS5 launchers (absent
from the GOS 1.00 and Gamex-only ones), the GOS builds' header names, and the TOS-in-RAM files.

How much of each shared file is TOS 1.04, as 16-byte runs found in the UK ROM, without relocation:

| files | TOS 1.04 |
| --- | --- |
| `D15R_NG1`, `F1`, `HH4`, `F4` | 89–90%: nearly whole copies of the BIOS, XBIOS and GEMDOS |
| `D15RH`, `RF`, `RU` | 67–74% |
| `T14AG` (with GEM), `T14GG` | 67%, 64% |
| `D15R_5H`, `5F` | 58% |
| `D15R_H5`, `F5`, `H15`, `F15` | 44% (70.4% for `D15R_H5` once relocation is counted: `disk-layer.md` §1) |

## 6. The glossary

Terms from the list's Note column and from the game pages:

| term | meaning | mode or category |
| --- | --- | --- |
| Gamex, GX; statesave, savestate, "exit to Desktop" | the "gaming extra" system (`GAMEXdoc.html`: "should mean something like 'gaming extra', 'games exitable'"). In 112 Note cells, mostly dated 2009–2011 | any launcher with `GXUT` or HAGA |
| HAGA, Haga, H | the launcher family of January 2012. All 17 Note cells "H" are on rows dated 2012 (e.g. Millennium 2.2, To Be On Top) | HAGA |
| HAGE, "new HAGE system", "HAGE-fying"; HAG2, "HAG2 v." | TOS 1.04 in RAM, with GEM (HAGE) or without (HAG2), and a floppy image | HAGE, HAG2 |
| GOS, "gamex + GOS" | "special GEMDOS adaptation" (Bombuzal's page). "D15R … abrev. means GEMDOS 0.15 relocated, reassembled" (`GamexUsage.html`) | §3.3, §3.4 |
| "TOS 1.04 in RAM", "single D15R*" | `D15RU.FIC`, one GOS for every machine | HAGA |
| singleparted, singlepart | the RAM at the game's start, packed, and restored from disk (§2, category 3) | Cat `S…` |
| filed | a game stored outside the file system, made into files (`playfhd.html`: "transfer disk content to file(s)") | Lemmings |
| filewise ramdisked | all the game's files in one `FWRD` file, read whole into RAM at the start (§7) | Lemmings |
| "redirect to hard disk" (325 pages) | the game's floppy paths changed to the hard disk (`agcat.html` category 2: "path corrections in code") | Cat 2 |
| "instead ramdisk, load from drive" | levels read from disk during play instead of from a RAM disk (Clever & Smart's page) | GOS5 |
| "xbios loads directed to image files on hard disk" | the XBIOS floppy reads served from an image file (Black Cauldron) | Cat 5 |
| deprot, deprotected, crk | the copy protection removed; the source was a crack | any |
| "src. STX/ST/MSA img. of org./crk." | what the adaptation started from | any |
| TOS dep, TOS indep, little TOS dep, TOS/AES dep, STOS dep | how much the game uses TOS (T, I, O, A in the code, §2) | the code |
| Tr., Trainer, "Unlim. lives" | cheats added (562 + 118 Note rows) | none |
| C-M | colour and mono ("Color and mono mode") | none |
| "done by JY" (16 pages) | a HAGA adaptation made by another author, "JY" | HAGA |
| light green background | the adaptations made after January 13 2012, on the download pages (`fromhd3.php`) | HAGA family |

## 7. Lemmings, the worked example

Lemmings is Gamex with GOS5 (`D15R_H5`/`F5`), from before 2012. `LEMMINGS.ZIP` on the website
holds the same 76 files as `LEMMINGS/`, SHA-256 for SHA-256. Its page says "Added gamex,
deprotected, filed, filewise ramdisked" and gives no `Cat:`. Its launcher has the three driver
checks (§3.3, §5). GOS reads its files by sectors, through the copy of PPDRIVER that the launcher
carries (`disk-layer.md`), and from a GEMDOS drive it stops at the check (`gemdrive-failure.md`).
Its first guess is "fix", like the other 166 archives of §3.3.

Its page offers a second download, `LEMMSRD.ZIP` ("2MB RAM min"): the other Lemmings adaptation,
with no GOS and no driver check. It is "filewise ramdisked": every file is in one `FWRD` file (a
directory, then the files), read whole into RAM at the start. `playfhd.html` calls a RAM disk the
"usual way" for games that load during play. Only two adaptations have one: this one and
Pick'n'Pile. It reaches the title menu from the GEMDOS drive as it is (`recognising-modes.md`). Whether
it plays a level there was not tried.

## 8. Sources

- The 8bitchip.info website, read in a local copy (never republished here): `agcat.html`,
  `GAMEXdoc.html`, `GamexUsage.html`, `playfhd.html`, `plafh.html`, `fromhd.php`, `fromhd2.php`,
  `fromhd3.php` (the list and its help), `imgrun.php`, `astopensw.php`, and the 1,829 game pages
  `SCRSH/*.html`.
- Its published launcher sources (`GamexLSrc.html`, `GamexLSrc2.html`, `GamexLSrc3.html`) and
  tools (`HOLE.ZIP`, `IMGRSRC.ZIP`, `IMGRF2X.ZIP`, `RAMTOS.ZIP`, `HDTCFIX.ZIP`, `512K_1M.ZIP`).
- The file names in its 1,947 archives (games and tools), and the shared files (`HAGA`, `HAGE`,
  `HAG2`, `D15R*.FIC`, `T14*.FIC`), unpacked with `tools/unpack.py` and compared with the TOS
  1.04 ROM.
- One game per mode run as it is from Hatari's GEMDOS drive (ST, TOS 1.04, 1 MB) with
  `src/probes/epic03/mode_probe.py <ZIP>`: run folders
  `tools/dev/logs/20261011-*-st-104-gemdrive-<game>`, and `-ppdriver-` for the reference.

A statement from the documentation counts here only once a run shows it.
