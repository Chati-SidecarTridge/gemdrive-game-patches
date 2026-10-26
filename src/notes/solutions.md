# How the hard-disk adaptations run from GEMDOS and GEMDRIVE, and what fixes the rest

This page gives every hard-disk adaptation on the 8bitchip.info website's list a verdict for a
GEMDOS drive: a drive that serves files by name and has no disk sectors, such as Hatari's or the
SidecarTridge Multidevice's GEMDRIVE. Of the 1,831 games, 1,608 run as they are, 212 need a fix, 1
is not feasible and 10 are unsure. Four solutions, S1 to S4, fix the 212. The page explains why
each group fails, what each solution changes, and what has been built and tested.

Each game has one row in `src/survey/migration.csv`: its
strategy, verdict, run, reason and solution. The strategies come from the games' files
(`recognising-modes.md`). The run folders are under `tools/dev/builds/survey/`:

- `runs/`: every game's run, one line each in `runs.tsv`;
- `trials/`: the trials of the fixes;
- `runs-other.tsv`: the runs of the games' other downloads.

Every verdict was reached on Hatari 2.6.1, with an ST and TOS 1.04 (an STE and TOS 1.62 for the
STE games), from Hatari's GEMDOS drive. The working reference is the same game from an ACSI disk
image booted by PPDRIVER, the hard-disk driver the adaptations look for.

## 1. In short

- **Two ways to the disk.** The games follow twelve strategies (§2). Ten strategies, with 1,627
  games, reach their files by name through the machine's GEMDOS. The other two, the Gamex launcher
  with GOS4 or GOS5 (204 games, Lemmings among them), read the disk by sectors through PPDRIVER.
  GOS is a TOS 1.04 GEMDOS that the launcher runs from RAM.
- **The verdicts.** 1,608 as it is, 212 fix, 1 not feasible, 10 unsure.
- **The fixes.** Four solutions cover the 212 games (§4):
  - S1 makes GOS read its files through the GEMDOS drive: the 204 GOS4 and GOS5 games.
  - S2 gives the GEMDOS drive a BPB, the block that describes a drive's layout: four Silmarils
    games.
  - S3 sets the fastload bit, a flag in a program's header that keeps its free memory from being
    cleared: three games whose start program Hatari ends when it loads the game.
  - S4 adds a missing start program: one game.
- **Where they stand.** Trials showed S2, S3 and S4 (§3). S1 is built for the 87 GOS5 games and
  the 117 GOS4 games. 85 GOS5 games run from the GEMDOS drive, in Hatari and with the
  Multidevice; Awesome and Prison do not yet (`gos5-gemdrive.md`). The 117 GOS4 games run in
  Hatari, and those tried with the Multidevice run there too (`gos4-gemdrive.md`). S2, S3 and S4 are built too: seven of their eight games run, in
  Hatari and on the Multidevice; Aquanaut does not yet (`small-fixes.md`).
- **Tested twice.** Every solution runs in Hatari's GEMDOS drive and then on real machines with
  the SidecarTridge Multidevice's GEMDRIVE. Only the exceptions are reported: what fails, and where
  the Multidevice differs from Hatari (§7).
- **Other downloads.** 43 of the 204 GOS games have another download on the 8bitchip.info website
  that runs as it is from the GEMDOS drive (§5). Lemmings' own 2 MB RAM-disk version is one of them.

## 2. The strategies and their verdicts

`recognising-modes.md` §1 describes each strategy, with its files and its launcher. In short, HAGA, HAGE
and HAG2 are launcher modules: HAGA reads the game's files by name for it, and HAGE and HAG2 load
TOS 1.04 into RAM and read the game's floppy from an image file. The "evidence" column names one
game per strategy that was run from the GEMDOS drive and from PPDRIVER, on the ST with TOS 1.04
and on the STE with TOS 1.62 and 2.06. The folder named is the ST run from the GEMDOS drive;
`runs.tsv` has the game's other rows.

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

- **The strategies that read by name** run from the GEMDOS drive. Their 1,627 games give 1,608 as
  it is, 8 fix, 1 not feasible and 10 unsure. Each of the 8 has an issue of its own (§3.2–3.4). On
  the STE, each strategy ends as it does on the ST (`runs.tsv`).
- **Every GOS4 and GOS5 game is "fix".** From the GEMDOS drive on the ST, its launcher quits to the
  desktop or prints `"This prg. requires PP, AHDI or Hddriver"`. The representative games do the
  same on the STE with TOS 1.62 and 2.06, and they play from PPDRIVER on all three machines.
- **Where the verdicts come from.** 241 come from a human review of the runs, on the review page (`review.tsv`), 90
  come from the game's PPDRIVER run, and 10 from a trace or a trial looked into (`findings.tsv`).
  The other 1,490 come from the run alone.

## 3. What the games to fix need

### 3.1 GOS4 and GOS5: the driver, then sectors (204 games)

Lemmings showed it first (`gemdrive-failure.md`, `disk-layer.md`). Every GOS4 and GOS5 launcher
makes the same checks (`launcher-signatures.md`, "Other modes"). The launcher needs the driver in
two steps:

1. **The driver.** The launcher looks for a resident PPDRIVER: the mark `PPHD` just before the
   routine that `hdv_bpb` points to. If it finds it, it copies 7,204 bytes of the driver to
   `$B7180` and patches them. If not, it reads sector 0 itself, then gives up. It reads through
   the ACSI registers on TOS 1, with `DMAread` on `pun_ptr`'s device on TOS 2, and through IDE on
   a Falcon.
2. **The sectors.** GOS (D15R, TOS 1.04 running from RAM) then serves the game's file requests
   with its own GEMDOS. That GEMDOS reads the FAT volume by sectors through the driver copy, with
   `Getbpb`, `Mediach` and `Rwabs` on drive C. The two GOS versions differ in who calls it. GOS5's
   `file_io` asks for whole files by name: `Fopen`, `Fseek`, `Fread` or `Fwrite`, `Fclose`
   (`disk-layer.md` §2). In GOS4, the game runs under GOS's GEMDOS and calls it itself.

A GEMDOS drive has no driver and no sectors, so both steps fail. The runs, each with its PPDRIVER
and STE runs beside it:

- Lemmings, `runs/20261011-210525-st-104-gemdrive-695-lemmings`: the launcher quits;
- Operation Stealth (GOS4), `runs/20261012-012833-st-104-gemdrive-1195-operation-stealth`;
- Thunderhawk AH-73M (GOS5), `runs/20261012-094035-st-104-gemdrive-1476-thunderhawk-ah-73m`.

The 204 games carry 27 builds of GOS. 13 are for the ST and STE: `D15R_HH4.FIC` (5 builds, in 117
games), `D15R_5H.FIC` (1 build, in 56), `D15R_H5.FIC` (5 builds, in 31) and `D15R_H15.FIC` (2
builds, in 3). The other 14 are for the Falcon (`D15R_F4`, `_5F`, `_F5`, `_F15`).

### 3.2 Getbpb on C: (4 games)

A BPB (BIOS parameter block) tells TOS the layout of a drive: its sector and cluster sizes, and
where its FAT and directory are. Crystals of Arborea, Targhan (one download, `ARBOTARG.ZIP`),
Robinsons Requiem and Storm Master are all Silmarils games, and they start with the same kind of
`START.PRG`. Before every file, that program calls `Dgetdrv`, then BIOS `Getbpb` on that drive.
Once it gets a BPB, it opens the file through GEMDOS. From PPDRIVER, for example, it calls
`Getbpb(0x2)` at `$1C21A`, then `Fopen("MAIN.AO")`
(`runs/20261012-135728-st-104-ppdriver-1698-crystals-of-arborea`).

A GEMDOS drive has no BPB. TOS answers 0, and the program asks again, millions of times
(`runs/20261012-103727-st-104-gemdrive-1698-crystals-of-arborea`). The programs do not read
sectors: once given a BPB, they read everything by name.

**Trial.** At the program's first instruction, the debugger writes a 22-byte routine at `$380` and
points `hdv_bpb` at it. For drive 2, the routine returns PPDRIVER's BPB, stored at `$3A0`. For any
other drive, it goes on to TOS's routine at `$FC173C`. From the GEMDOS drive, the four games then
run, with no `Rwabs` on C:

| game | files opened | reached | run |
| --- | --- | --- | --- |
| Crystals of Arborea | 39 | the game screen | `trials/20261013-112306-st-104-gemdrive-1698-crystals-bpb-2` |
| Targhan | 52 | play | `trials/20261013-112427-st-104-gemdrive-1699-targhan-bpb` |
| Robinsons Requiem | 4 | its language choice, as from PPDRIVER | `trials/20261013-112427-st-104-gemdrive-1774-robinson-bpb` |
| Storm Master | 12 | its title, as from PPDRIVER | `trials/20261013-112427-st-104-gemdrive-1808-storm-bpb` |

Hatari's own compatibility list knows the case: "Program crashes if disk info is requested for
GEMDOS HD emulated drive … because program doesn't check BIOS GetBPB() function return value"
(`../hatari/doc/compatibility.html`, Statistician).

### 3.3 A start program whose stack is cleared (3 games)

Spy vs Spy 2, Strike Force Harrier and Aquanaut each have a start program that starts the game
with `Pexec`: `Pexec(0, "SPY2.BOY")`, `HARRIER.TOS` and `AQUANAUT.EXE`. Before that, the start
program shrinks its memory to its own code with `Mshrink`. Its stack stays at the top of RAM, in
the memory it gave back. From the GEMDOS drive, the game never runs and the desktop comes back.

The cause is in the way Hatari's GEMDOS drive loads a program. Hatari loads the program itself.
Unless the program's header has the fastload bit, Hatari clears the new program's free memory
(`../hatari/src/gemdos.c:4383-4395`), and the caller's stack with it. The fastload bit is bit 0 of
byte 25 of the header. Hatari then rewrites only the mode and the basepage of the saved `Pexec`
call (`gemdos.c:4504-4506`). The function number is now 0, so TOS reads the call as `Pterm0` and
ends the start program. The stack before and after the load is
`00 4b 0000 000125e4 000125e0` → `00 00 0006 00000000 00012766`
(`trials/spy2/runs/20261013-112912-st-104-gemdrive-spy2-usp`). From PPDRIVER, TOS's own `Pexec`
reads its arguments before it clears the memory, and the games run.

**Trial.** With the fastload bit set in the started program, the three games get past the start
from the GEMDOS drive:

- Spy vs Spy 2 plays its demo (`trials/spy2/runs/20261013-112748-st-104-gemdrive-spy2-fastload`);
- Strike Force Harrier reaches its simulation menu
  (`trials/sfh/runs/20261013-112833-st-104-gemdrive-sfh-fastload`);
- Aquanaut reaches its title (`trials/aquanaut/runs/20261013-113519-st-104-gemdrive-aquanaut-fastload`).

No other GEMDOS-drive run shows a program loaded and its caller ended at once.

### 3.4 Rody and Mastico 2 (1 game)

Its download has its HAGE module, its floppy image and `T14AG.FIC`, but no `RUNME.TOS`. HAGE is
the launcher module that loads TOS 1.04 with GEM into RAM and reads the game's floppy from an
image file. Rody and Mastico 4's download (`RODYM4.ZIP`) has the same layout. With its
`RUNME.TOS`, Rody and Mastico 2 reaches its title and chapter menu from the GEMDOS drive
(`trials/rodym2/`).

### 3.5 Not feasible: Great Giana Sisters STE (1 game)

During play, the game streams its music from `GS.RAW` by sectors. `GIAACSI.TOS` finds the file's
sectors through the driver's `PUN_INFO`, then reads them itself with the ACSI or IDE registers.
Its README asks for a driver "which supports PUN info" and for defragmented audio files. From the
GEMDOS drive it prints "Error in getting file location" and quits
(`runs/20261012-132330-ste-162-gemdrive-1112-great-giana-sisters-ste`).

The game's page also has two HAGA downloads, `GIANAA.ZIP` and `GIANAS.ZIP`, and they do the same:
the error from the GEMDOS drive, the intro from PPDRIVER (`runs-other.tsv`). Running the game would
take a new music streamer that reads through GEMDOS. That is a change to the game, not to its
launcher: the "major modification" that makes a game not feasible.

### 3.6 Unsure (10 games)

Nine games run "as it is" by the rules, but the human review marked their runs Broken on the review page. A
second look, with the PPDRIVER run beside each, kept them unsure. The tenth game has no hard-disk
version.

| game | strategy | from PPDRIVER | what would settle it |
| --- | --- | --- | --- |
| Lords of Doom, Substation, Roger, Zero-5, Spitting Images | HAGA, Gamex, plain, Gamex, plain | the program quits to the desktop too | why it quits from both disks: Hatari or the adaptation's files, not the drive |
| Utopos | plain | a desktop too | the same |
| Super Breakout mono, 9 Lives, Little Puff in Dragonland | HAGA | runs, or waits at a title | what the GEMDOS drive changes: a trace of both runs |
| Ice and Fire | floppy image | none | a run with a virtual floppy driver from the GEMDOS drive |

## 4. The solutions proposed

All four solutions leave Hatari unchanged: each changes only what runs on the Atari. None needs an
original file to be published, because a tool changes the user's own copy. Where the SidecarTridge
Multidevice's GEMDRIVE (`../atarist-sidecart-gemdrive`, version 1.0.1) would behave differently,
the text says so. Those notes come from reading its sources, before anything was run on it.

| | solution | games | what it changes | cost: work | memory | risk |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | GOS reads through the GEMDOS drive | 204 (117 GOS4, 87 GOS5), Lemmings first | each launcher's driver checks, and GOS's GEMDOS entry | two patchers by signature, then 204 runs | none beyond GOS's | the most: GOS4 games' own GEMDOS calls |
| S2 | a BPB for the GEMDOS drive | 4 | a resident program on `hdv_bpb` | small | about 100 bytes, resident | low |
| S3 | the fastload bit | 3 | one bit in the started program's header | one byte per game | none | low |
| S4 | Rody and Mastico 4's `RUNME.TOS` | 1 | one file added | a copy | none | none (shown) |

### S1. GOS reads through GEMDOS and GEMDRIVE (204 games)

**The problem.** The launcher wants PPDRIVER, and GOS reads drive C by sectors (§3.1).

**The idea.** GOS keeps everything but its disk access. Its file requests go to the `TRAP #1`
handler, the GEMDOS entry, that the machine had before the launcher ran. The HAGA adaptations'
file service has worked this way since 2012 (`modes.md` §3.1). It takes a name, an offset, a
length, a buffer and a mode, calls the machine's GEMDOS, then puts the game's state back. 1,361 of
the 1,366 games of the HAGA family run as they are. GOS5's `file_io` takes the same parameters.

In Hatari, that handler is the cartridge hook at `$FA002A`, which serves the drive from the host
folder. It takes its parameters from the stack (`gemdos.c:4028-4038`) and copies `Fread`'s data
straight into the buffer (`gemdos.c:2364-2365`). None of TOS's RAM is in the way.

**The proposal.** Two changes, both on the Atari side:

1. **The launcher's driver checks.** Each GOS launcher (`START.TOS`, packed) checks for `PPHD`
   with the same code, `2278 0472 0CA9 5050 4844 FFF8`, in all 204. 203 of them also have the
   `DMAread` fallback. The patch makes the launcher go on without a driver: no driver copy, no
   sector-0 read, and GOS started as on the launcher's main path. The launcher is unpacked and
   packed again with `tools/unpack.py` and `tools/pack.py`, which make a packed file the launcher
   accepts (`launcher-formats.md`). Lemmings' launcher sources, which reassemble to the original
   bytes, show the place: `src/lemld2/lemld2.s`, at `check_pp_driver`, `reuse_pp_driver` and
   `start_d15r`.
2. **GOS's GEMDOS entry.** Each D15R build has its own GEMDOS entry, `trap1`
   (`302F 0006 B07C 000B …`). The patch makes it pass the file functions to the handler saved
   before the launcher ran: `Fopen`, `Fclose`, `Fread`, `Fwrite`, `Fseek`, `Fcreate`, `Fdelete`,
   `Fsfirst`/`Fsnext`, `Dsetdrv`, `Dsetpath` and `Dgetpath`. There are 13 ST/STE builds to patch
   (§3.1). The new code goes where D15R's own code sits, at the start of each build (1,852 bytes
   in `D15R_H5`).

- **Work.** The two patchers, which find their place by signature as `classify.py` does. A script
  that applies them to a copy of a game. Then a run of the 204 games with `run_all.py`. Lemmings
  comes first: its launcher and GOS are rebuilt from sources that reassemble to the original
  bytes, with their round trips and tests. The Falcon builds take the same patch, untested: the
  Falcon is out of scope.
- **Memory.** None beyond GOS's own. The driver copy at `$B7180` and its buffers go unused.
- **Risks.**
  - GOS4 games call GOS's GEMDOS themselves during play. Hatari's trace does not show these calls,
    because it sees only the calls that reach its hook. Logged at GOS's own dispatcher, they are
    the file calls, `Pexec` to start programs, and `Fsfirst` to search. The GOS4 build passes on
    all three (`gos4-gemdrive.md`).
  - `Fsfirst` and `Fsnext` find the DTA through TOS's current process (`gemdos.c:3043-3049`). A
    game that owns low RAM may have overwritten it.
  - Gamex's state saves (`file_io` with `"Wr"`) are untested.
  - From PPDRIVER, the reference, the original launcher stops at Lemmings' first level in Hatari,
    on an address error. The cause is a keyboard packet cut in two by a disk load. The S1 build
    lets a packet under way finish before each load (`gos5-gemdrive.md`), and Lemmings plays its
    first level from the GEMDOS drive, in Hatari and with the Multidevice.
    The original launcher is left as it is.
- **SidecarTridge.** Its GEMDRIVE also hooks `TRAP #1` from cartridge ROM. But it reads
  `_longframe` (`$59E`) and runs a wait loop in RAM at `_dskbufp` (`$4C6`, or on the stack). It
  also calls `TRAP #1` again through `$84` for paths without a drive letter and for
  `Fsfirst`/`Fsnext` (`gemdrive.s:244-266`, `811-815`, `1100-1111`, `1344-1349`). With GOS's
  image of TOS's RAM in place, those variables and vectors must hold usable values. The requests
  should also carry full paths (`C:\…`).

**Built for GOS5** (`gos5-gemdrive.md`). The build changes the launcher only.
`tools/build_gos5.py` finds each launcher by signature, in all 87. It puts a block of code
(`src/gemdrive/gos5_patch.s`) in front of the launcher's text, and turns the `PPHD` check into a
branch to that block. GOS's code stays unchanged. GOS keeps its own image of the system variables,
and the block points the `TRAP #1` vector of that image at a forwarder. The forwarder is a short
routine that passes the file functions to the machine's handler, with names cut to 8.3, and every
other call to GOS. On the Multidevice, the block also moves GEMDRIVE's stack out of the game's
memory. Before each load, it lets a keyboard message under way finish.

The result: 85 games run. Five of them need a disk in drive A, because they wait for the floppy
motor themselves. Forgotten Worlds needs two GOS files from another download, Magic Boy needs 2 MB
and Muzzy an STE. Awesome and Prison still fail. Each refuses the cartridge in the port, and two
bytes of one of its files turn that check off.

**Built for GOS4** (`gos4-gemdrive.md`). The change is of the same kind.
`tools/build_gos4.py` finds each launcher by signature, in all 117, and adds its own block
(`src/gemdrive/gos4_patch.s`). GOS4 is TOS 1.04 started from RAM, and it sets up its own
`TRAP #1`. The block points that vector, in GOS's copy in memory, at a forwarder. The forwarder:

- passes the file calls to the machine's handler, with names cut to 8.3 and file handles numbered
  as GOS numbers its own;
- reads the programs that are started with `Pexec` through the drive;
- gives `Fsfirst` the game's DTA;
- leaves drives A and B to GOS's floppy code, and gives drive C a BPB.

All 117 run in Hatari. F16 Falcon needs 2 MB. Asterix and Winter Games also read drive A, as they
do with PPDRIVER.

**Not proposed, for the same 204 games:**

- **A driver that serves sectors from a disk image.** A resident driver shaped like PPDRIVER would
  answer `Rwabs` from a disk-image file on the GEMDOS drive. It would carry the `PPHD` mark and
  follow the layout at the offsets the launcher patches (`gemdrive-failure.md` §5). Its code would
  have to fit in the 7,204 bytes the launcher copies. The original files would stay unchanged, but
  the games would live in an image, which Hatari's ACSI image already gives.
- **A driver that makes a FAT volume out of the folder.** The same driver, with the directory and
  FAT sectors built from `Fsfirst`/`Fsnext`, so that the files stay loose in the folder. It is the
  most work, under the same 7,204-byte limit.
- **The games' other downloads.** No work, but only for the 43 games that have one (§5).

### S2. A BPB for GEMDOS and GEMDRIVE (4 games)

**The problem.** The four Silmarils programs wait for a BPB that a GEMDOS drive does not give
(§3.2).

**The fix.** A resident program, run from `C:\AUTO\`, hooks `hdv_bpb` with an XBRA header. For
the GEMDOS drive's number, it returns a BPB. For any other drive, it calls the routine that was
there before. The trial's routine (§3.2) is the core of that program: 22 bytes and an 18-byte BPB.

- **Work.** Small.
- **Memory.** About 100 bytes, resident.
- **Risk.** A program that reads C: by sectors once it has a BPB would get TOS's error. None of the
  four did.
- **SidecarTridge.** Its GEMDRIVE has no `hdv_*` hooks either (none in `gemdrive.s`), so the same
  program applies there.

**Built.** `GDBPB.PRG` is 82 bytes in memory and answers for any drive from C: up that has no BPB
of its own. It is run once before the game. The four games run in Hatari and on the Multidevice;
Storm Master also needs a floppy in drive A (`small-fixes.md`).

### S3. The fastload bit (3 games)

**The problem.** Hatari clears the started program's free memory, and the start program's stack
with it (§3.3).

**The fix.** Set bit 0 of byte 25 of the header in `SPY2.BOY`, `HARRIER.TOS` and `AQUANAUT.EXE`.
Hatari then leaves their free memory as it is, with the caller's stack in it.

- **Work.** One byte per game. Another way is to move the start programs' stack into the memory
  they keep. Their sources are in the downloads (`SPY22.S`, `START1.S`).
- **Risk.** A program that counts on zeroed memory. None of the three showed it.
- **Hatari.** The cause is Hatari's: `GemDOS_PexecBpCreated` relies on the caller's stack after it
  clears the free memory. That calls for a report upstream, not a change here: Hatari stays as it
  is.
- **SidecarTridge.** Its GEMDRIVE runs `Pexec` modes 0 and 3 itself (`gemdrive.s:1412-1415`).
  Whether it clears memory the same way is not checked.

**Built.** `tools/set_fastload.py` sets the bit. Spy vs Spy 2 and Strike Force Harrier then play,
in Hatari and on the Multidevice. Aquanaut reaches its title in Hatari but reboots on the
Multidevice; it is not solved yet (`small-fixes.md`).

### S4. Rody and Mastico 4's `RUNME.TOS` (1 game)

**The problem.** Rody and Mastico 2's download has no start program (§3.4).

**The fix.** Copy `RUNME.TOS` from `RODYM4.ZIP` into Rody and Mastico 2's folder. The trial already
showed it works.

**Built.** `tools/rody2_runme.py` makes the copy. The game reaches its chapter menu in Hatari and
runs on the Multidevice (`small-fixes.md`).

## 5. The GOS games' other downloads

43 of the 204 GOS games have another download whose strategy reads by name (the
`other_downloads` column). `tools/survey/run_other.py` ran each one from the GEMDOS drive, with
`run_all.py`'s rules. All 43 run as they are (`runs-other.tsv`, with the snapshots in
`snapshots-other/`). Every snapshot was looked at: each shows a title, a menu, the attract mode or
play. The 43 are:

- 33 GOS5 games with a HAGA download, most of them "done by JY" (`…JY.ZIP`);
- five GOS4 games: Strider 2, Axel's Magic Hammer and Street Fighter (HAGA), and Alien Syndrome
  and Strider (HAG2);
- Lemmings' `LEMMSRD.ZIP` (FWRD RAM disk, 2 MB), which reaches its title
  (`runs/20261013-112842-st-104-gemdrive-695-lemmsrd-lemmings`);
- Magic Boy's `MAGICBRD.ZIP` (Gamex);
- Corruption, Fish and Guild of Thieves's `COMP.ZIP` (plain). It must be in `C:\COMP`, as its
  README asks. In `C:\GAME` it stops with "No System Resources".

In `migration.csv`, the `solution` column names the other download after S1: "or … runs as it is".

## 6. Corrections made on the way

- **Weird Dreams.** Its first run counted "418 sector reads on C:". They were reads of its own RAM
  disk, drive M: (device 12), on both disks, and the two runs end on the same title. The game runs
  as it is. `run_all.py` now counts sector reads and `Getbpb` on C: only. That also drops Robotron
  2084's two reads of drive H:, and both games' access is "files" again.
- **Maddog Williams.** Its ZIP keeps `PABISYS.FIL` beside the game's folder, and the game opens
  `C:\PABISYS.FIL`. The survey mounted only the folder, so the game quit from both disks.
  `run_all.py` now puts in the drive's root whatever a download keeps beside the game's folder. The
  game then reaches its difficulty menu (`runs.tsv`), and further, with keys, its first screen
  (`trials/20261013-114212-st-104-gemdrive-1672-maddog-root-1n`). It runs as it is. The human review's Broken
  was given on the run without the file, so the game is listed in `stale.txt`.
- **Great Giana Sisters STE.** An earlier finding said its HAGA downloads read through GEMDOS. They
  do not (§3.5), so the game is not feasible.
- **Aquanaut.** S3's cause (§3.3) explains its failure, so it is "fix" rather than "unsure".

## 7. How the solutions are tested

Every game was run on the first bench, the Hatari emulator's GEMDOS drive. Every solution is then
tried on the second, real Atari machines with the SidecarTridge Multidevice's GEMDRIVE, before it
counts. The real machines find failures that Hatari does not show, and each one is reported here
and in the catalogue.

### 7.1 The two benches

| | Hatari's GEMDOS drive | The Multidevice's GEMDRIVE |
|---|---|---|
| What it is | Hatari 2.6.1 serves a folder of the host computer as drive C:, file by file | A cartridge in the ST's cartridge port serves a folder of its microSD card as a GEMDOS drive, file by file |
| Machines | an emulated ST with TOS 1.04 and STE with TOS 1.62 and 2.06, 1 to 4 MB | real machines: an ST, an STE, a Mega ST and a Mega STE |
| Reference | the same game from a hard-disk image with the `PPDRIVER` driver | the game's own verdict from Hatari |
| What runs there | every game of the list, and every build, by script | every fix, and a sample of the games that run as they are, from a test card |

Both serve files by name and have no disk sectors, so a game that runs on one should run on the
other. They differ in what surrounds the drive: GEMDRIVE runs on the Atari itself, from cartridge
ROM, and uses some of the Atari's RAM; real machines have real floppy drives, real timing and the
memory left over by what ran before.

### 7.2 How a game is tried on the Multidevice

- The test card holds every game in a folder named by its verdict and RAM:
  `PPHD\<verdict>\<RAM>\<group>\<game>\`, with `INDEX.TXT` giving each game's program to start.
  `FIXGOS5`, `FIXGOS4`, `FIXPLAIN`, `FIXHOLE` and `FIXHAGE` hold the fixed games, `STILLNOT` the
  fixed games that still fail.
- The card is written by `tools/survey/sdcard.py` and checked file by file against the build.
- The machine is switched off and on between games. After a reset, memory and hooked vectors are
  left over from the game before, and some games fail. A game that fails after a reset is tried
  again after a power cycle before the failure counts.

### 7.3 What is reported

Hatari's GEMDOS drive and the Multidevice's GEMDRIVE behave the same on every machine. A game runs
on any machine and from both drives unless it is reported in this section, so only the exceptions are listed:
where the Multidevice differs from Hatari, and what fails. Every fix was tried on the Multidevice:
the GOS5 and GOS4 builds and the small fixes, and a sample of the games that run as they are.

### 7.4 Where the Multidevice differs from Hatari

- **GEMDRIVE's stack in the game's memory** (the GOS games). GEMDRIVE runs the calls it serves on a
  1 KB stack that it reserves at boot, at the bottom of free memory. A GOS game uses that memory
  for itself. Found by reading GEMDRIVE's source and reproducing its memory use in Hatari, where
  the game then stopped, before the first card test. The builds move GEMDRIVE's stack into memory
  the game leaves alone (`gos5-gemdrive.md`).
- **A keyboard packet cut by a load** (Lemmings). On the STE, pressing space during the intro hung
  the game. A disk load had cut a mouse packet from the keyboard in two, and the game then read
  every packet out of step. Hatari showed the same cause as an address error at the first level.
  The builds let a packet under way finish before each load.
- **A file locked by GEMDRIVE** (Noddy's Playtime). The game opens a file for reading and writing,
  never closes it, and later loads it again. GOS and Hatari allow that. GEMDRIVE keeps its files in
  FatFs, which refuses to open again a file that is open for writing, and that cannot be changed.
  The game took the refusal for a missing disk and asked for disk 1 forever. The GOS4 build now
  opens such a file for reading only (`gos4-gemdrive.md`).
- **Free memory that starts higher** (Aquanaut). The game reboots the machine while it loads. It
  runs only at the address where a bare TOS 1.04 loads it, and with GEMDRIVE free memory starts
  higher. Not solved (`small-fixes.md`).
- **The floppy drive** (Chaos Engine). On the STE the game waits for the floppy motor. With any
  floppy in drive A it goes on.
- **What a reset leaves behind** (3D Construction Kit). Three bombs after other games and a reset;
  it runs after a power cycle.

### 7.5 Failures on both benches

- **Awesome and Prison** refuse a cartridge in the port, and both GEMDRIVEs need one there
  (`gos5-gemdrive.md`).
- **Storm Master** drives the floppy controller itself at its credits and waits for a disk in drive
  A. It does the same from a hard disk with `PPDRIVER`.
- **The ten unsure games** fail in Hatari and on the Multidevice; why is still to be found.

### 7.6 How a failure is reported

A failure on the Multidevice is recorded with what was seen and the machine, in
`src/survey/hardware.tsv`. The catalogue shows it in the game's row, and this section lists its
cause once it is known. A game that fails only on the Multidevice is reported even when it runs in Hatari.

## Tools

- `tools/survey/run_other.py`: the other downloads (§5).
- `src/survey/solutions.tsv`: each solution, by row or by strategy. `verdicts.py` writes it into
  `migration.csv`'s `solution` column, with the other downloads that run as they are.
- `src/survey/findings.tsv`: the verdicts settled by a trace or a trial, with their runs.
