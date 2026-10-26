# Recognising the modes from the files

Every game in the list on the 8bitchip.info website (1,831 records, `src/survey/catalogue.csv`)
gets a strategy: its mode (`modes.md`), the way its adaptation reaches the game's files, as the
survey recognises it. The strategy is read from the files in the game's download
(`src/survey/files.csv`) and the signatures in its programs, not from a run. `python3 tools/survey/classify.py` writes it into `src/survey/migration.csv`. How each strategy
does from a GEMDOS drive, and how the ones that fail are fixed, is in `solutions.md`.

A game gets the strategy of its first download that is a hard-disk adaptation; the others are
listed in `other_downloads`. The counts in §1 are today's. The tables of §2 to §4 count an earlier reading
of the list, and differ by up to 7 games per strategy.

## 1. Twelve strategies, two ways to the disk

A game reaches its files in one of two ways:

- **By name**, through the machine's GEMDOS, the part of TOS that handles files. Every drive
  serves that, a GEMDOS drive included: Hatari's, or the Multidevice's GEMDRIVE, which serve files
  by name from a folder.
- **By sectors**, the numbered blocks of a disk, through a hard-disk driver. A GEMDOS drive has no
  sectors (`gemdrive-failure.md`).

Ten strategies read by name: 1,627 games. Two read by sectors, Gamex with GOS4 and with GOS5: 204
games. Every game has a strategy. Each strategy's first guess at the verdict comes from its mode
(`modes.md` §4); a run of every game then checked them (`solutions.md`).

### 1.1 The strategies that read by name

They need only the machine's GEMDOS, unless said otherwise.

#### HAGA

1,025 games. Marked by the file `HAGA`, one of the shared modules of the adaptations
made since January 2012. `RUNME.TOS` loads `HAGA` to the top of RAM. HAGA's file service reads
the game's files by name through the machine's GEMDOS. Some games also load a GOS (`D15RH`/`D15RF`
or `D15RU`) for their TOS calls: GOS is TOS 1.04's GEMDOS, modified, in high RAM. It needs 1 MB,
and any driver behind GEMDOS or none. Guess: as it is (`modes.md` §3.1).

#### HAGE

207 games. Marked by the file `HAGE`, `T14AG.FIC` and a floppy image. `HAGE` loads
TOS 1.04 with GEM into RAM (`T14AG.FIC`). The game's floppy is an image file (`FILES\X.ST`),
which HAGE reads by name. Guess: as it is (`modes.md` §3.2).

#### HAG2

134 games. Marked by the file `HAG2`, `T14GG.FIC` and a floppy image: HAGE with TOS
1.04 without GEM (`T14GG.FIC`). Guess: as it is.

#### Gamex

110 games. Marked by `GXUTnnn.PRG` and the `START` stub, with no D15R file. The stub
is the short code at the start of `START.TOS` that unpacks the launcher and starts it
(`launcher-signatures.md`). The launcher loads or starts the game's files by name. Gamex adds the
exit to the desktop and the state saves. Guess: as it is (`modes.md` §3.4).

#### Gamex + GOS 1.00

5 games. Marked by `D15R_NG1.FIC` or `D15R_F1.FIC`, and no driver checks.
The launcher reads by name, then runs the game under GOS 1.00. Guess: as it is.

#### Launcher without Gamex

18 games. Marked by the `START` stub and no `GXUT`. It reads by
name. Guess: as it is, likely.

#### FWRD RAM disk

1 game, Pick'n'Pile. Marked by a file that starts with `FWRD`. Every game
file is in that one file, read into RAM at the start, as in Lemmings' second download. It needs
2 MB. Guess: as it is.

#### Plain

123 games. With no launcher stub: the game's own program, its paths fixed ("redirect
to hard disk"). Guess: as it is, likely, unless the game reads sectors itself
(§3).

#### Plain + HOLE

3 games. Marked by `FBHOLE.PRG` or `SBHOLE.PRG`: plain, with the low 512 KB
of RAM kept free by HOLE's boot floppy. It needs the HOLE boot sector too. Guess: as it
is, with HOLE.

#### Floppy image

1 game, Ice and Fire. Its download holds only a `.ST` or `.MSA` image, for the Floppy
Image Runner or a floppy. It needs the Image Runner, which opens the image by name and makes it drive
A (`modes.md` §3.5). Guess: open.

### 1.2 The strategies that read by sectors

#### Gamex + GOS4

117 games. Marked by `D15R_HH4.FIC` or `D15R_F4.FIC`, and by `PPHD`,
`DMAread` and `'DMAr'` in the launcher. The launcher copies PPDRIVER, or boots the disk's own
driver from sector 0. GOS then reads the game's files by sectors through that driver. It needs
PPDRIVER, AHDI or HDDriver on ACSI (or IDE, Falcon), found by the launcher's driver checks.
Guess: fix (`modes.md` §3.3).

#### Gamex + GOS5

87 games. Marked by `D15R_H5`/`F5`, `H15`/`F15` or `5H`/`5F`, and the same
checks: GOS4's way with GOS5, a reduced GEMDOS "only for file I/O". Lemmings is one. Guess: fix.

## 2. Set against the 8bitchip.info website's categories

Each game page gives a category code (`modes.md` §2), read from the list into the `code_category`
column of `catalogue.csv`. This table counts each strategy's games by category:

| strategy | games | 1–2 file system | 3 singleparted | 4 low RAM | 5 XBIOS | 6 floppy controller | code without a category | no code |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HAGA | 1,022 | 480 | 48 | 53 | 15 | 179 | 133 | 114 |
| HAGE | 203 | 200 | 0 | 0 | 0 | 0 | 0 | 3 |
| HAG2 | 130 | 118 | 0 | 1 | 5 | 1 | 2 | 3 |
| plain | 125 | 34 | 13 | 2 | 0 | 2 | 5 | 69 |
| Gamex | 117 | 50 | 38 | 2 | 5 | 3 | 15 | 4 |
| Gamex + GOS4 | 116 | 65 | 2 | 26 | 2 | 7 | 1 | 13 |
| Gamex + GOS5 | 87 | 0 | 1 | 1 | 0 | 73 | 11 | 1 |
| launcher without Gamex | 21 | 8 | 1 | 0 | 0 | 0 | 1 | 11 |
| Gamex + GOS 1.00 | 5 | 1 | 2 | 2 | 0 | 0 | 0 | 0 |
| plain + HOLE | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| floppy image | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| FWRD RAM disk | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |

What the table shows:

- **GOS5** was the adaptations' answer to category 6, games that drive the floppy controller
  during play: 73 of its 87 games.
- **GOS4** went to the file-system games bound to low RAM, categories 1–2 and 4, as `agcat.html`
  says: "Work under higher TOS versions is solveable with Image Runner or GOS 4".
- **HAGA** covers every category, category 6 included (179 games). Since 2012, the same file
  service replaces the floppy loads of the games that load during play.
- **HAGE** and **HAG2** are file-system games (categories 1–2) that need TOS 1.04 itself, with
  GEM (`A`, for AES, in the code) or without.

## 3. What the programs show

The `access` column gives the strongest disk access found in the programs the user starts. The
`START` stub is unpacked first, and only text sections are searched, at even offsets. From the
strongest:

- **registers**: the DMA and floppy-controller registers at `$FFFF8604`-`$FFFF860D`;
- **sectors**: XBIOS `Floprd` or `DMAread`, or BIOS `Rwabs`;
- **files**: GEMDOS file calls only.

The patterns are in `launcher-signatures.md` ("Disk access").

| strategy | files | sectors | registers | nothing seen |
| --- | --- | --- | --- | --- |
| HAGA | 1,001 | 3 | 18 | 0 |
| HAGE | 202 | 0 | 0 | 1 |
| HAG2 | 130 | 0 | 0 | 0 |
| plain | 77 | 9 | 4 | 35 |
| Gamex | 115 | 0 | 2 | 0 |
| Gamex + GOS4 | 1 | 0 | 115 | 0 |
| Gamex + GOS5 | 0 | 0 | 87 | 0 |
| launcher without Gamex | 17 | 2 | 0 | 2 |
| Gamex + GOS 1.00 | 5 | 0 | 0 | 0 |
| plain + HOLE | 2 | 1 | 0 | 0 |
| floppy image | 0 | 0 | 0 | 1 |
| FWRD RAM disk | 1 | 0 | 0 | 0 |

A hit is a place to look, not a verdict. The runs settle each game (`solutions.md`).

- **GOS4 and GOS5.** Every one of their launchers has the `PPHD` check. 202 of the 203 also have
  the `DMAread` fallback and `'DMAr'`. Defender 2's GOS4 launcher checks `PPHD` only.
- **HAGA with registers (18 games).** 7 of them are the disk-streaming games of January 2012
  (Dragon's Lair I, II and III, Escape, Space Ace I and II, Galaxy Force). Their folder keeps the
  2010 GOS5 `START.TOS` next to the new `RUNME.TOS`. The download's `READ_NEW.TXT` says "Run with
  RUNME.TOS" and "Tested with Steem - STemDOS", Steem's GEMDOS drive. The other 11 (Eye of Horus,
  IK+, No Buddies Land, Pro PowerBoat Simulator, BeastLord, Elvira the Arcade Game, Microprose
  Golf, Infestation, Disc, Vroom, Maupiti Island) have floppy-controller code in their
  `RUNME.TOS`. IK+'s, for example, writes a command to the floppy controller and waits for the MFP
  to signal that it is done.
- **HAGA with sectors (3 games).** Lure of the Temptress, Cannon Fodder and Operation Wolf call
  `Rwabs` or `Floprd`.
- **Plain.** The 13 plain games with sectors or registers, and the 35 whose programs show nothing
  because their code is packed, are the plain games most likely to read the floppy themselves.
- **Inside the packed files.** The `inner_evidence` column lists the same signatures in the
  download's packed files, unpacked: the game's own stages, without the D15R and T14 files. 164
  HAGA games and Lemmings (`LS2DD.FIC`) have floppy-controller code there. It is the games' own
  loaders, which the launchers patch at run time (Lemmings': `launch-chain.md`).

## 4. What the runs were to check

- The two ways to the disk: every strategy that reads by name should run from the GEMDOS drive
  past its first file load, and GOS4 and GOS5 should stop at the launcher.
- 18 games need a monochrome monitor (`monitor` = mono only), and the harness runs them with
  `--monitor mono`. Some games need more RAM than their page gives (Vector Invaders: 2 MB,
  `modes.md` §3.2).
- Lemmings has two downloads: `LEMMINGS.ZIP` (GOS5, the row's strategy) and `LEMMSRD.ZIP` (FWRD
  RAM disk, 2 MB), listed in `other_downloads`.
