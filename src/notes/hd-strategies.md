# How the hard-disk adaptations run from a GEMDOS drive, and what would fix the rest

2026-10-13. The answers to Diego's questions about the hard-disk adaptations, from
`src/survey/migration.csv` (one row per game of the 8bitchip.info website's list: its strategy,
verdict, run, reason and solution), the strategies read from the files (`strategies.md`), a run of
every game and trials of the fixes. Run folders are under `tools/dev/builds/survey/`: `runs/`
(every game's run, one line each in `runs.tsv`), `trials/` (the trials), and the other downloads'
runs in `runs-other.tsv`. Every verdict was reached on Hatari 2.6.1, ST TOS 1.04 (STE TOS 1.62 for
the STE games), from its GEMDOS drive, against an ACSI image booted by the PPDRIVER hard-disk
driver as the working reference.

## 1. In short

- **How many ways**: twelve strategies (§2), which reach the disk in two ways: by name through
  the machine's GEMDOS (ten strategies, 1,627 games), or by sectors through PPDRIVER (Gamex
  with GOS4 or GOS5: 204 games, Lemmings among them).
- **The verdicts**: **1,608 as it is, 212 fix, 1 not feasible, 10 unsure**.
- **What the 212 need**: four solutions (§4). S1, GOS reading through the GEMDOS drive, covers
  the 204 GOS4/GOS5 games; S2, a BPB for the GEMDOS drive, four Silmarils games; S3, the fastload
  bit, three games whose start program Hatari ends when it starts the next one; S4 one game
  missing a file. S2, S3 and S4 were shown in trials (§3). S1 is built for the 87 GOS5 games and
  the 117 GOS4 games (2026-10-16): 85 GOS5 games run from the GEMDOS drive, in Hatari and on an STE
  with the Multidevice, Awesome and Prison not yet (`gos5-gemdrive.md`); the 117 GOS4 games run in
  Hatari (`gos4-gemdrive.md`).
- **Already there**: 43 of the 204 GOS games have another download on the 8bitchip.info website
  that runs as it is from the GEMDOS drive (§5), Lemmings' own 2 MB RAM-disk version among them.

## 2. The strategies and their verdicts

The strategies are the ones read from the files (`strategies.md` §1, where each one's files and
launcher are described). "Evidence" is one game per strategy that ran from the GEMDOS drive and
from PPDRIVER on the ST, and on the STE with TOS 1.62 and 2.06 (`runs.tsv`, the game's rows; the ST GEMDOS-drive
folder is named).

| strategy | games | reaches its files | needs | as it is | fix | not feasible | unsure | evidence |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| HAGA | 1,025 | by name: HAGA's file service, the machine's GEMDOS | GEMDOS | 1,021 | 0 | 0 | 4 | PuffysSaga, `runs/20261011-205225-st-104-gemdrive-23-puffyssaga` |
| HAGE | 207 | by name: a floppy image read by HAGE, TOS 1.04 with GEM in RAM | GEMDOS | 206 | 1 | 0 | 0 | ACC-TRIS, `runs/20261011-210725-st-104-gemdrive-2-acc-tris` |
| HAG2 | 134 | the same, TOS 1.04 without GEM | GEMDOS | 134 | 0 | 0 | 0 | Algebra compil, `runs/20261011-210725-st-104-gemdrive-1-algebra-compil` |
| plain | 123 | by name: the game's own program | GEMDOS | 113 | 6 | 1 | 3 | Air Warrior, `runs/20261012-121252-st-104-gemdrive-322-air-warrior` |
| Gamex + GOS4 | 117 | by sectors: GOS's GEMDOS through PPDRIVER | PPDRIVER, AHDI or HDDriver, resident; sectors | 0 | 117 | 0 | 0 | Operation Stealth, `runs/20261012-012833-st-104-gemdrive-1195-operation-stealth` |
| Gamex | 110 | by name: the `START` stub, Gamex | GEMDOS | 108 | 0 | 0 | 2 | Jupiter Probe, `runs/20261012-100019-st-104-gemdrive-1493-jupiter-probe` |
| Gamex + GOS5 | 87 | by sectors: the same, GOS5 | the same | 0 | 87 | 0 | 0 | Thunderhawk AH-73M, `runs/20261012-094035-st-104-gemdrive-1476-thunderhawk-ah-73m` |
| launcher without Gamex | 18 | by name: the `START` stub | GEMDOS | 18 | 0 | 0 | 0 | Tetris Abersoft, `runs/20261012-121328-st-104-gemdrive-325-tetris-abersoft` |
| Gamex + GOS 1.00 | 5 | by name, then GOS 1.00 | GEMDOS | 5 | 0 | 0 | 0 | Rana Rama, `runs/20261012-120628-st-104-gemdrive-95-rana-rama` |
| plain + HOLE | 3 | by name, low RAM kept free by HOLE | GEMDOS, HOLE's boot | 2 | 1 | 0 | 0 | Altair, `runs/20261012-110726-st-104-gemdrive-1825-altair` |
| floppy image | 1 | a floppy image only | a floppy-image driver | 0 | 0 | 0 | 1 | Ice and Fire: nothing to start (§3.6) |
| FWRD RAM disk | 1 | by name: one file read into RAM | GEMDOS, 2 MB | 1 | 0 | 0 | 0 | Pickn Pile, `runs/20261012-103322-st-104-gemdrive-1677-pickn-pile` |
| **all** | **1,831** | | | **1,608** | **212** | **1** | **10** | |

- The "by name" strategies run from the GEMDOS drive: their 1,627 games give 1,608 as it is, 8
  fix (each an issue of its own game, §3.2–3.4), 1 not feasible and 10 unsure. The STE runs end
  as the ST runs do, strategy by strategy (`runs.tsv`).
- Every GOS4 and GOS5 game is "fix": from the GEMDOS drive its launcher quits to the desktop, or
  prints `"This prg. requires PP, AHDI or Hddriver"`, on the ST; the representatives do the same on
  the STE with TOS 1.62 and 2.06, and play from PPDRIVER on all three.
- 241 verdicts are Diego's answers on the review page (`review.tsv`), 90 come from a game's
  PPDRIVER run, 10 from a trace or a trial looked into (`findings.tsv`), the other 1,490 from the
  run alone.

## 3. What the games to fix need

### 3.1 GOS4 and GOS5: the driver, then sectors (204 games)

It was found first in Lemmings (`gemdrive-failure.md`, `disk-layer.md`), and every
GOS4/GOS5 launcher has the same checks (`launcher-signatures.md`, "Other modes"):

1. The launcher wants a resident PPDRIVER (`PPHD` before `hdv_bpb`), copies 7,204 bytes of it to
   `$B7180` and patches them; without it, it reads sector 0 itself (ACSI registers on TOS 1,
   `DMAread` on `pun_ptr`'s device on TOS 2, IDE on a Falcon) and gives up.
2. GOS (D15R, TOS 1.04 in RAM) then serves the game's file requests with its own GEMDOS, which
   reads the FAT volume by sectors (`Getbpb`, `Mediach`, `Rwabs` on drive C) through that copy.
   GOS5's `file_io` asks for whole files by name: `Fopen`, `Fseek`, `Fread` or `Fwrite`, `Fclose`
   (`disk-layer.md` §2). In GOS4 the game runs under GOS's GEMDOS and calls it itself.

A GEMDOS drive has no driver and no sectors. Runs: Lemmings
`runs/20261011-210525-st-104-gemdrive-695-lemmings` (the launcher quits), Operation Stealth (GOS4)
`runs/20261012-012833-st-104-gemdrive-1195-operation-stealth` and Thunderhawk AH-73M (GOS5)
`runs/20261012-094035-st-104-gemdrive-1476-thunderhawk-ah-73m`, each with its PPDRIVER and STE runs.

The 204 games carry 27 builds of GOS: 13 for the ST and STE (`D15R_HH4.FIC` 5 builds in 117
games, `D15R_5H.FIC` 1 in 56, `D15R_H5.FIC` 5 in 31, `D15R_H15.FIC` 2 in 3) and 14 for the Falcon
(`D15R_F4`, `_5F`, `_F5`, `_F15`).

### 3.2 Getbpb on C: (4 games)

Crystals of Arborea, Targhan (one download, `ARBOTARG.ZIP`), Robinsons Requiem and Storm Master,
all Silmarils games, start with the same kind of `START.PRG`: before every file it calls
`Dgetdrv`, then BIOS `Getbpb` on that drive, and opens the file through GEMDOS once it gets a BPB
(`runs/20261012-135728-st-104-ppdriver-1698-crystals-of-arborea`: `Getbpb(0x2)` at `$1C21A`, then
`Fopen("MAIN.AO")`). A GEMDOS drive has no BPB: TOS answers 0 and the program asks again, millions
of times (`runs/20261012-103727-st-104-gemdrive-1698-crystals-of-arborea`). They do not read
sectors: given a BPB, they read everything by name.

**Trial**: at the program's first instruction the debugger puts a 22-byte routine at `$380`
(`hdv_bpb` for drive 2 returns PPDRIVER's BPB, at `$3A0`; any other drive goes on to TOS's
`$FC173C`) and points `hdv_bpb` at it. From the GEMDOS drive, with no `Rwabs` on C:
afterwards:

| game | files opened | reached | run |
| --- | --- | --- | --- |
| Crystals of Arborea | 39 | the game screen | `trials/20261013-112306-st-104-gemdrive-1698-crystals-bpb-2` |
| Targhan | 52 | play | `trials/20261013-112427-st-104-gemdrive-1699-targhan-bpb` |
| Robinsons Requiem | 4 | its language choice, as from PPDRIVER | `trials/20261013-112427-st-104-gemdrive-1774-robinson-bpb` |
| Storm Master | 12 | its title, as from PPDRIVER | `trials/20261013-112427-st-104-gemdrive-1808-storm-bpb` |

Hatari's own list knows the case: "Program crashes if disk info is requested for GEMDOS HD
emulated drive … because program doesn't check BIOS GetBPB() function return value"
(`../hatari/doc/compatibility.html`, Statistician).

### 3.3 A program started by a program that gave its stack back (3 games)

Spy vs Spy 2, Strike Force Harrier and Aquanaut: the start program shrinks its memory to its own
code (`Mshrink`) with its stack still at the top of RAM, then starts the game (`Pexec(0,
"SPY2.BOY")`, `HARRIER.TOS`, `AQUANAUT.EXE`); the game never runs and the desktop comes back.
Hatari's GEMDOS drive loads the program itself: without the fastload bit in its header it
clears the new program's free memory (`../hatari/src/gemdos.c:4383-4395`), the caller's stack with
it, then rewrites only the mode and the basepage of the saved `Pexec` call (`gemdos.c:4504-4506`);
the function number has been cleared to 0, and TOS reads the call as `Pterm0`. The stack before
and after the load: `00 4b 0000 000125e4 000125e0` → `00 00 0006 00000000 00012766`
(`trials/spy2/runs/20261013-112912-st-104-gemdrive-spy2-usp`). From PPDRIVER, TOS's own `Pexec`
takes its arguments before it clears, and the games run.

**Trial**: with the fastload bit set (header byte 25, bit 0) in the started program, Spy vs Spy 2
plays its demo (`trials/spy2/runs/20261013-112748-st-104-gemdrive-spy2-fastload`), Strike Force
Harrier reaches its simulation menu (`trials/sfh/runs/20261013-112833-st-104-gemdrive-sfh-fastload`)
and Aquanaut its title (`trials/aquanaut/runs/20261013-113519-st-104-gemdrive-aquanaut-fastload`).
No other GEMDOS-drive run shows a program loaded and the caller ended at once.

### 3.4 Rody and Mastico 2 (1 game)

Its download has no `RUNME.TOS` (its HAGE module, floppy image and `T14AG.FIC` are there).
With Rody and Mastico 4's (`RODYM4.ZIP`, the same layout) it reaches its title and chapter menu
from the GEMDOS drive (`trials/rodym2/`).

### 3.5 Not feasible: Great Giana Sisters STE (1 game)

It streams its music from `GS.RAW` during play by sectors: `GIAACSI.TOS` finds the file's
sectors through the driver's `PUN_INFO` and reads them with the ACSI or IDE registers itself
(its README asks for a driver "which supports PUN info" and defragmented audio files). From the
GEMDOS drive it prints "Error in getting file location" and quits
(`runs/20261012-132330-ste-162-gemdrive-1112-great-giana-sisters-ste`). The page's two HAGA
downloads do the same (`GIANAA.ZIP`, `GIANAS.ZIP`: the error from the GEMDOS drive, the intro
from PPDRIVER; `runs-other.tsv`). Running it would take a new music streamer that reads
through GEMDOS: a change to the game, not to its launcher, the "major modification" that makes a
game not feasible.

### 3.6 Unsure (10 games)

Nine are Diego's Broken on runs the rules call "as it is", kept after a second look with the
PPDRIVER run beside them; the tenth has no hard-disk version.

| game | strategy | from PPDRIVER | what would settle it |
| --- | --- | --- | --- |
| Lords of Doom, Substation, Roger, Zero-5, Spitting Images | HAGA, Gamex, plain, Gamex, plain | the program quits to the desktop too | why it quits from both disks: Hatari or the adaptation's files, not the drive |
| Utopos | plain | a desktop too | the same |
| Super Breakout mono, 9 Lives, Little Puff in Dragonland | HAGA | runs, or waits at a title | what the GEMDOS drive changes: a trace of both runs |
| Ice and Fire | floppy image | none | a run with a virtual floppy driver from the GEMDOS drive |

## 4. The solutions proposed

All four keep Hatari unchanged: each changes what runs on the Atari, and none needs an original
file to be published: a tool changes the user's own copy. The SidecarTridge's
GEMDRIVE (`../atarist-sidecart-gemdrive`, version 1.0.1) is noted where it would differ, from its
sources; nothing was run on it.

| | solution | games | what it changes | cost: work | memory | risk |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | GOS reads through the GEMDOS drive | 204 (117 GOS4, 87 GOS5), Lemmings first | each launcher's driver checks, and GOS's GEMDOS entry | two patchers by signature, then 204 runs | none beyond GOS's | the most: GOS4 games' own GEMDOS calls |
| S2 | a BPB for the GEMDOS drive | 4 | a resident program on `hdv_bpb` | small | about 100 bytes, resident | low |
| S3 | the fastload bit | 3 | one bit in the started program's header | one byte per game | none | low |
| S4 | Rody and Mastico 4's `RUNME.TOS` | 1 | one file added | a copy | none | none (shown) |

### S1. GOS reads through the GEMDOS drive (204 games)

GOS keeps everything but its disk. Its file requests go to the `TRAP #1` handler the machine had
before the launcher, as the HAGA adaptations' own file service has done since 2012 (`modes.md`
§3.1: a name, an offset, a length, a buffer and a mode; the machine's GEMDOS; then the game's state
back),
and 1,361 of the 1,366 HAGA-family games run as they are. GOS5's `file_io` takes the same
parameters. In Hatari that handler is the cartridge hook at `$FA002A`, which serves the drive from
the host folder: it takes its parameters from the stack (`gemdos.c:4028-4038`) and copies
`Fread`'s data straight into the buffer (`gemdos.c:2364-2365`), with none of TOS's RAM in the way.

Two changes, both on the Atari side:

1. **The launcher's driver checks.** In each GOS launcher (`START.TOS`, packed), the `PPHD`
   check (`2278 0472 0CA9 5050 4844 FFF8`, in all 204; 203 have the `DMAread` fallback too) made
   to go on without a driver: no driver copy, no sector-0 read, GOS started as on the primary
   path. Unpacked and packed again with `tools/unpack.py` and `tools/pack.py` (a packed file the
   launcher accepts, `launcher-formats.md`). The launcher's sources, which reassemble to the
   original bytes, show where in Lemmings' (`src/lemld2/lemld2.s`: `check_pp_driver`,
   `reuse_pp_driver`, `start_d15r`).
2. **GOS's GEMDOS entry.** In each D15R build, `trap1` (D15R's own entry, `302F 0006 B07C 000B …`)
   passes the file functions (`Fopen`, `Fclose`, `Fread`, `Fwrite`, `Fseek`, `Fcreate`, `Fdelete`,
   `Fsfirst`/`Fsnext`, `Dsetdrv`, `Dsetpath`, `Dgetpath`) to the handler saved before the launcher
   ran. 13 ST/STE builds (§3.1); D15R's own code at their start (1,852 bytes in `D15R_H5`) is where
   it goes in.

- **Work**: the two patchers (by signature, as `classify.py` finds them), a script that applies
  them to a copy of a game, then the 204 games run with `run_all.py`. Lemmings first: its
  launcher and GOS are rebuilt from sources that reassemble to the original bytes, with their round
  trips and tests. The Falcon builds take the same patch, untested (Falcon is out of scope).
- **Memory**: none beyond GOS's own. The driver copy at `$B7180` and its buffers go unused.
- **Risk**:
  - GOS4 games call GOS's GEMDOS themselves during play, which Hatari's trace does not show (it
    sees only the calls that reach its hook). Logged at GOS's own dispatcher, they make the file
    calls, start programs with `Pexec` and search with `Fsfirst`; the GOS4 build hands on all three
    (`gos4-gemdrive.md`).
  - `Fsfirst`/`Fsnext` find the DTA through TOS's current process (`gemdos.c:3043-3049`), which a
    game that owns low RAM may have overwritten.
  - Gamex's state saves (`file_io` with `"Wr"`) are untested.
  - On the reference, Lemmings does not reach its first level in Hatari (an address error, its
    cause still a candidate). That blocks S1's play session with Lemmings, not its first runs.
- **SidecarTridge**: its GEMDRIVE also hooks `TRAP #1` from cartridge ROM, but it reads
  `_longframe` (`$59E`), runs a wait loop in RAM at `_dskbufp` (`$4C6`, or on the stack), and calls
  `TRAP #1` again through `$84` for paths without a drive letter and for `Fsfirst`/`Fsnext`
  (`gemdrive.s:244-266`, `811-815`, `1100-1111`, `1344-1349`). With GOS's image of TOS's RAM in
  place, those must hold usable values, and the requests should carry full paths (`C:\…`).

**Built for GOS5** (2026-10-16; `gos5-gemdrive.md`). One change, in the launcher only:
`tools/build_gos5.py` puts a block of code (`src/gemdrive/gos5_patch.s`) in front of each
launcher's text, found by signature in all 87, and turns the `PPHD` check into a branch to it.
GOS's code stays unchanged: the block points the `TRAP #1` of GOS's image of the system variables at
a forwarder that hands the file functions to the machine's handler, names cut to 8.3, and the rest
to GOS. On the Multidevice it also moves GEMDRIVE's stack out of the game's memory, and before each
load it lets a keyboard message under way finish. 85 games run; five need a disk in drive A (their
own wait for the floppy motor), Forgotten Worlds two GOS files from another download, Magic Boy 2 MB
and Muzzy an STE. Awesome and Prison still fail: each refuses the cartridge in the port, and two bytes
of one of its files turn its check off.

**Built for GOS4** (2026-10-16; `gos4-gemdrive.md`). The same kind of change, by
`tools/build_gos4.py` with its own block (`src/gemdrive/gos4_patch.s`), found by signature in all 117
launchers. GOS4 is TOS 1.04 started from RAM and sets up its own `TRAP #1`; the block points it, in
GOS's copy in memory, at a forwarder that hands the file calls to the machine's handler with names
cut to 8.3 and handles numbered as GOS's, reads the programs that are started (`Pexec`) through the
drive, gives `Fsfirst` the game's DTA, leaves drives A and B to GOS's floppy and gives drive C a BPB.
All 117 run in Hatari; F16 Falcon needs 2 MB; Asterix and Winter Games also read drive A, as with
PPDRIVER.

**Not proposed, for the same 204 games:**
- **A driver that serves records**: a resident driver shaped like PPDRIVER (the `PPHD` mark, laid
  out at the offsets the launcher patches, `gemdrive-failure.md` §5) that answers `Rwabs` from a
  disk-image file on the GEMDOS drive. The original files would stay unchanged, but the games would
  live in an image, which Hatari's ACSI image already gives. Its code must also fit the 7,204 bytes
  the launcher copies.
- **A driver that makes a FAT volume out of the folder**: the same, with directory and FAT
  sectors built from `Fsfirst`/`Fsnext`, so files stay loose. The most work, under the same
  7,204-byte limit.
- **The games' other downloads**: no work, but only for the 43 games that have one (§5).

### S2. A BPB for the GEMDOS drive (4 games)

A program run from `C:\AUTO\`, resident: on `hdv_bpb` (XBRA), for the GEMDOS drive's number it
returns a BPB, and for any other drive it chains to the routine before it. The trial's routine
(§3.2) is that program's core: 22 bytes and an 18-byte BPB.

- **Work**: small. **Memory**: about 100 bytes, resident.
- **Risk**: a program that, once given a BPB, reads C: by sectors would get TOS's error. None of
  the four did.
- **SidecarTridge**: its GEMDRIVE has no `hdv_*` hooks either (none in `gemdrive.s`), so the same
  program applies there.

### S3. The fastload bit (3 games)

Set bit 0 of byte 25 of the header in `SPY2.BOY`, `HARRIER.TOS` and `AQUANAUT.EXE`. Hatari then
leaves their free memory, where the caller's stack lies, as it is.

- **Work**: one byte per game; the other way is to move the start programs' stack into the memory
  they keep (their sources are in the downloads: `SPY22.S`, `START1.S`).
- **Risk**: a program that counts on zeroed memory; none of the three showed it.
- **Hatari**: the cause is Hatari's (`GemDOS_PexecBpCreated` relies on the caller's stack after
  clearing the free memory). A report upstream, not a change here: Hatari stays as it is.
- **SidecarTridge**: its GEMDRIVE runs `Pexec` modes 0 and 3 itself (`gemdrive.s:1412-1415`);
  whether it clears memory the same way is not checked.

### S4. Rody and Mastico 4's `RUNME.TOS` (1 game)

Copied from `RODYM4.ZIP` into Rody and Mastico 2's folder (§3.4). Already shown.

## 5. The GOS games' other downloads

43 of the 204 GOS games have another download whose strategy runs by name (`other_downloads`);
`tools/survey/run_other.py` ran each from the GEMDOS drive with `run_all.py`'s rules, and all 43
run as they are (`runs-other.tsv`, snapshots in `snapshots-other/`, every one looked at: a title,
a menu, the attract mode or play):

- 33 GOS5 games with a HAGA download, most of them "done by JY" (`…JY.ZIP`), and Strider 2,
  Axel's Magic Hammer and Street Fighter (HAGA), Alien Syndrome and Strider (HAG2), all GOS4;
- Lemmings' `LEMMSRD.ZIP` (FWRD RAM disk, 2 MB), to its title
  (`runs/20261013-112842-st-104-gemdrive-695-lemmsrd-lemmings`);
- Magic Boy's `MAGICBRD.ZIP` (Gamex);
- Corruption, Fish and Guild of Thieves's `COMP.ZIP` (plain), in `C:\COMP` as its README asks: in
  `C:\GAME` it stops with "No System Resources".

`migration.csv`'s `solution` column names them after S1 ("or … runs as it is").

## 6. Corrections made on the way

- **Weird Dreams**: its first run's "418 sector reads on C:" were its own RAM disk, drive M:
  (device 12), on both disks; the two runs end on the same title. As it is. `run_all.py` now
  counts sector reads and `Getbpb` on C: only (Robotron 2084's two reads of drive H: go too), and
  both games' access is "files" again.
- **Maddog Williams**: its ZIP keeps `PABISYS.FIL` beside the game's folder, and the game opens
  `C:\PABISYS.FIL`. The survey mounted the folder only, and the game quit from both disks.
  `run_all.py` now puts what a download keeps beside the game's folder in the drive's root: it
  reaches its difficulty menu (`runs.tsv`), and further, with keys, the game's first screen
  (`trials/20261013-114212-st-104-gemdrive-1672-maddog-root-1n`). As it is. Diego's Broken was on
  the run without the file, so it is listed in `stale.txt`.
- **Great Giana Sisters STE**: an earlier finding said its HAGA downloads read through GEMDOS.
  They do not (§3.5): not feasible.
- **Aquanaut**: S3's cause (§3.3), so fix rather than unsure.

## Tools

- `tools/survey/run_other.py`: the other downloads (§5).
- `src/survey/solutions.tsv`: each solution by row or strategy; `verdicts.py` writes it into
  `migration.csv`'s `solution` column, with the other downloads that run as they are.
- `src/survey/findings.tsv`: the verdicts settled by a trace or a trial, with their runs.
