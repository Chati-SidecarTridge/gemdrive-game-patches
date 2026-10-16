# The strategies, from the files

2026-10-11. Every game of PP's list (`src/survey/catalogue.csv`, 1,831 records)
gets a strategy in `src/survey/migration.csv`, from what its download contains
(`src/survey/files.csv`) and the signatures in its programs. `python3 tools/survey/classify.py`
writes it. The strategies are PP's modes (`pp-modes.md`) where the files show them; a game
gets the strategy of its first download that is a hard-disk adaptation, and its other downloads
are listed in `other_downloads`.

## 1. Twelve strategies, two ways to the disk

| strategy | games | how it runs from a hard disk | what it needs | the files that mark it | first guess (from PP's modes) |
| --- | --- | --- | --- | --- | --- |
| HAGA | 1,022 | `RUNME.TOS` loads `HAGA` to the top of RAM; HAGA's file service reads the game's files by name through the machine's GEMDOS; a GOS (`D15RH`/`D15RF` or `D15RU`) for the game's TOS calls, or none | any driver, or none at all, behind GEMDOS; 1 MB | the file `HAGA` | as it is |
| HAGE | 203 | `HAGE` loads TOS 1.04 with GEM into RAM (`T14AG.FIC`); the game's floppy is an image file (`FILES\X.ST`) that HAGE reads by name | the same | the file `HAGE`, `T14AG.FIC`, a floppy image | as it is |
| HAG2 | 130 | the same with TOS 1.04 without GEM (`T14GG.FIC`) | the same | the file `HAG2`, `T14GG.FIC`, a floppy image | as it is |
| Gamex | 117 | PP's `START` stub loads or starts the game's files by name; Gamex for exit and state saves | GEMDOS | `GXUTnnn.PRG`, PP's stub, no D15R | as it is |
| Gamex + GOS4 | 116 | the launcher copies PP's driver, or boots the disk's own driver from sector 0; GOS (TOS 1.04's GEMDOS in RAM) reads the files by sectors through it | PP's, AHDI or HDDriver on ACSI (or IDE, Falcon); the driver checks | `D15R_HH4.FIC`/`D15R_F4.FIC`; `PPHD`, `DMAread`, `'DMAr'` in the launcher | fix |
| Gamex + GOS5 | 87 | the same with GOS5, PP's reduced GEMDOS "only for file I/O"; Lemmings | the same | `D15R_H5`/`F5`, `H15`/`F15`, `5H`/`5F`; the same checks | fix |
| Gamex + GOS 1.00 | 5 | the launcher reads by name, then runs the game under GOS 1.00 | GEMDOS | `D15R_NG1.FIC`/`D15R_F1.FIC`, no driver checks | as it is |
| PP launcher | 21 | PP's `START` stub without Gamex | GEMDOS | PP's stub, no `GXUT` | as it is, likely |
| FWRD RAM disk | 1 | every game file in one `FWRD` file read into RAM at the start (Pick'n'Pile; Lemmings' second download) | GEMDOS; 2 MB | a file starting `FWRD` | as it is |
| plain | 125 | the game's own program, its paths fixed ("redirect to hard disk") | GEMDOS | no PP launcher | as it is, likely, unless the game reads sectors itself (§3) |
| plain + HOLE | 3 | the same, the low 512 KB kept free by HOLE's boot floppy | GEMDOS and the HOLE boot sector | `FBHOLE.PRG`/`SBHOLE.PRG` | as it is with HOLE |
| floppy image | 1 | a floppy image only (Ice and Fire), for the Image Runner or a floppy | the Image Runner | `.ST`/`.MSA` only | open |

No game is left unclassified. The twelve reach the disk in **two ways**: by name, through the
machine's GEMDOS (every strategy but two: 1,628 games), or by sectors through a hard-disk driver the
launcher finds or boots (Gamex + GOS4 and GOS5: 203 games). A GEMDOS drive serves the first and has
nothing for the second (`gemdrive-failure.md`). A run of every game checks it (`hd-strategies.md`).

## 2. Set against PP's categories

The category comes from each page's code (`catalogue.csv`, `code_category`, read from PP's list):

| strategy | games | 1–2 file system | 3 singleparted | 4 low RAM | 5 XBIOS | 6 floppy controller | code without a category | no code |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HAGA | 1,022 | 480 | 48 | 53 | 15 | 179 | 133 | 114 |
| HAGE | 203 | 200 | 0 | 0 | 0 | 0 | 0 | 3 |
| HAG2 | 130 | 118 | 0 | 1 | 5 | 1 | 2 | 3 |
| plain | 125 | 34 | 13 | 2 | 0 | 2 | 5 | 69 |
| Gamex | 117 | 50 | 38 | 2 | 5 | 3 | 15 | 4 |
| Gamex + GOS4 | 116 | 65 | 2 | 26 | 2 | 7 | 1 | 13 |
| Gamex + GOS5 | 87 | 0 | 1 | 1 | 0 | 73 | 11 | 1 |
| PP launcher | 21 | 8 | 1 | 0 | 0 | 0 | 1 | 11 |
| Gamex + GOS 1.00 | 5 | 1 | 2 | 2 | 0 | 0 | 0 | 0 |
| plain + HOLE | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| floppy image | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| FWRD RAM disk | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |

GOS5 is PP's answer to category 6, games that drive the floppy controller during play (73 of
87). GOS4 went to the file-system games bound to low RAM (categories 1–2 and 4), as
`agcat.html` says ("Work under higher TOS versions is solveable with Image Runner or GOS 4").
HAGA covers every category, category 6 included (179 games): since 2012 the same file service
replaces the floppy loads of games that load during play. HAGE and HAG2 are file-system games
(categories 1–2) that need TOS 1.04 itself, with GEM (`A` in the code, AES) or without.

## 3. What the programs show

`access` is the strongest disk access found in the programs the user starts (PP's stub unpacked
first; text sections only, at even offsets): **registers** (the DMA/floppy-controller registers at
`$FFFF8604`-`$FFFF860D`), **sectors** (XBIOS `Floprd` or `DMAread`, BIOS `Rwabs`), **files** (GEMDOS
file calls only). The patterns are in `launcher-signatures.md` ("Disk access").

| strategy | files | sectors | registers | nothing seen |
| --- | --- | --- | --- | --- |
| HAGA | 1,001 | 3 | 18 | 0 |
| HAGE | 202 | 0 | 0 | 1 |
| HAG2 | 130 | 0 | 0 | 0 |
| plain | 77 | 9 | 4 | 35 |
| Gamex | 115 | 0 | 2 | 0 |
| Gamex + GOS4 | 1 | 0 | 115 | 0 |
| Gamex + GOS5 | 0 | 0 | 87 | 0 |
| PP launcher | 17 | 2 | 0 | 2 |
| Gamex + GOS 1.00 | 5 | 0 | 0 | 0 |
| plain + HOLE | 2 | 1 | 0 | 0 |
| floppy image | 0 | 0 | 0 | 1 |
| FWRD RAM disk | 1 | 0 | 0 | 0 |

- Every GOS4/GOS5 launcher has the `PPHD` check; 202 of 203 also have the `DMAread` fallback and
  `'DMAr'`. Defender 2's GOS4 launcher checks `PPHD` only.
- **HAGA with registers** (18): 7 are the disk-streaming games of January 2012 (Dragon's Lair I,
  II, III, Escape, Space Ace I and II, Galaxy Force) whose folder keeps the 2010 GOS5 `START.TOS`
  next to the new `RUNME.TOS`; PP's `READ_NEW.TXT` says "Run with RUNME.TOS" and "Tested with
  Steem - STemDOS" (Steem's GEMDOS drive). The other 11 (Eye of Horus, IK+, No Buddies Land, Pro
  PowerBoat Simulator, BeastLord, Elvira the Arcade Game, Microprose Golf, Infestation, Disc,
  Vroom, Maupiti Island) have floppy-controller code in their `RUNME.TOS` (IK+'s writes a command
  to the floppy controller and waits for the MFP to signal it done), and 3 call `Rwabs` or `Floprd` (Lure
  of the Temptress, Cannon Fodder, Operation Wolf). Their runs settle it (`hd-strategies.md`).
- **plain with sectors or registers** (13), and the 35 plain programs where nothing shows (their
  code is packed): the plain games most likely to read the floppy themselves.
- `inner_evidence` lists the same signatures in the download's PP-packed files, unpacked (the
  game's own stages; D15R and T14 left out). 164 HAGA games and Lemmings (`LS2DD.FIC`) have
  floppy-controller code there: the games' own loaders, which PP's launchers patch at run time
  (Lemmings': `launch-chain.md`), so this is not a verdict either.

## 4. What the runs were to check

- The two-way split is the hypothesis to test: every "by name" strategy should run from the GEMDOS
  drive past its first file load; GOS4 and GOS5 should stop at the launcher.
- 18 games need a monochrome monitor (`monitor` = mono only; the harness's `--monitor mono`), and
  some need more RAM than their page gives (Vector Invaders: 2 MB, `pp-modes.md`).
- Lemmings has two downloads: `LEMMINGS.ZIP` (GOS5, the row's strategy) and `LEMMSRD.ZIP` (FWRD RAM
  disk, 2 MB), listed in `other_downloads`.
