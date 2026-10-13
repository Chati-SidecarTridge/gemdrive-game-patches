---
id: STORY-05
epic: EPIC-03
title: Every game in Hatari's GEMDRIVE mode: the verdicts
status: done
---

## Goal

Every game's verdict in the migration table (D-14): as it is, fix, not feasible, or unsure, from
its files (STORY-04) and a run in Hatari's GEMDRIVE mode, with each strategy's behaviour also
seen from the PPDRIVER reference.

## Tasks

- [x] The harness and `make_disks.sh` take any game folder, start program and RAM size; today they
      assume `C:\LEMMINGS\START.TOS`. `tools/dev/all_harness.sh` must still pass.
- [x] `tools/survey/run_all.py` runs every game on ST TOS 1.04 in GEMDRIVE mode, several Hatari
      instances at a time, keeping the trace of GEMDOS, BIOS, XBIOS and ACSI calls and screenshots,
      and long enough to see the game's first file load after its start (a level, a menu's data):
      reaching a title is not enough.
- [x] The verdict of every game into `migration.csv`: **as it is** when its files carry no
      sector-access signature and its run gets past that first load with no failed access;
      **fix** when it stops on something a solution could supply (a driver check, BIOS or XBIOS
      sector access, a fixed RAM layout…), the stop recorded; **not feasible** when it needs
      the hardware itself or major changes (direct floppy-controller access during play, its own
      disk format…), the reason recorded; **unsure**, with what is missing, otherwise.
- [x] For each strategy, at least two representatives (or all its games, if fewer) also run from
      the PPDRIVER image, and one of them on STE TOS 1.62 and 2.06, so a GEMDRIVE failure is told
      apart from a game that fails in Hatari anyway (as Lemmings does after "1 PLAYER").
- [x] Where a run contradicts STORY-04's class, the class is corrected.

## Acceptance

Every row of `migration.csv` has a verdict with its run folder and, for "fix" and "not feasible",
the stop or the reason; every strategy has its PPDRIVER comparison; the "unsure" rows are listed
with what would settle them.

## Notes

The harness's `key`, `mouse` and `event` steps give a game the input it needs to get past its
title; a game that needs more is "unsure" until it gets it.

From STORY-01: `src/probes/epic03/mode_probe.py` already runs one game from the mirror on one
disk and reports its file opens, sector reads, ACSI commands, CPU faults and halts; `run_all.py`
can start from it. Some games need a monochrome monitor ("Needs monochrome capable monitor" on
their page): the harness's `--monitor mono` gives them one. A game may also need more RAM in
Hatari than its page says: Vector Invaders halts with 1 MB on both disks and plays with 2 MB, so a
game that fails on both disks with 1 MB is run again with 2 MB before its verdict.

Progress (2026-10-11): the harness takes `--drive` (a run's own C:), `--start`, `--memsize`,
`--monitor` and `--log-root`; `make_disks.sh` takes any folder; `tools/dev/all_harness.sh` passes
(17/17). `tools/survey/run_all.py` runs every game five at a time and proposes a verdict from the
trace (files missing, sector reads on C:, a return to the desktop, CPU halts and faults, a screen
still moving), with a second run at 2 MB for a game that halts or faults at 1 MB. Each run's last
screen goes to `tools/dev/builds/survey/snapshots/` (Diego, 2026-10-11: for the website, and shown
while testing: `tools/survey/sheet.py` makes a contact sheet of the new ones every 15 minutes).
Diego offered to look the runs over: a row he checks gets his verdict, marked as his, in
`migration.csv`.

**Diego's review** (`tools/survey/review.py`, http://localhost:8642 on this Mac): each game's snapshot
with OK / Broken / Not sure and a note, written to `src/survey/review.tsv`. Diego, 2026-10-11: "if
i dont check any button, it means i trust your guess" — a game without an answer keeps
`run_all.py`'s proposal; an answer overrides it. His first answers (rows 1–5, all OK) set two
rules: a still screen that is not the desktop, with no exit and nothing missing, is a game waiting
at its menu or title ("as it is"); for HAGE and HAG2, TOS in RAM's desktop is where the game starts
from ("as it is"). Other checks added on his word: the desktop is told on screen by its menu bar
whatever its colours (`tools/survey/screens.py`, learned in low, medium and high resolution), and
an unexpected exit by breakpoints on `Pterm0`/`Pterm`/`Ptermres` matched to the start program;
the RAM is the largest the list, the page and the launcher give (some launchers say "Min RAM for
this is 2MB" against a README's 1 MB), and the monitor monochrome when the page or the README says
so. A missing `*.HST` (PP's cover pictures, one of a pair) is not a failure.


Progress (2026-10-12): Diego answered 331 games (71 OK, 182 Broken, 78 Not sure); the rules were
set again from his answers (a single address or bus error is a launcher's hardware probe, not a
failure; GEM programs call GEMDOS from the ROM's AES, so a program counts as quit only when its own
exit leaves the desktop on screen) and every game was judged again, 217 of them run again. Later
checks, each from a run that showed it:

- **More RAM that changes nothing does not count.** 41 games ended the same with 2 and 4 MB as
  with their page's RAM (halts, quits, files missing: Glad Killing Impact, Monkeys and Balloons…):
  the first run counts, not the 4 MB one (`run_all.py`; their lines of `runs.tsv` set back).
- **The right program.** 45 archives hold several programs and none is RUNME or START; the run took
  the first by name, so F1 GP Ultimate ran its image converter, Space Quest 3 its music driver,
  Silent Service II its copier. Now a program a README says to start or run comes first and
  utilities last: 8 games changed program, and all 8 run "as it is".
- **A blank last screen is not a game at its title.** 56 runs end on a screen of one colour
  (Defender 2: a GOS4 launcher with no disk under it); they are "unsure" until the PPDRIVER run
  tells them apart (`screens.py`'s `blank`). One blank screenshot is not enough: the harness takes
  its last one as Hatari quits, often in a fade or a load (Klax loading `KLAR.FIC`; from the
  GEMDOS drive files load at once, so the moments differ from PPDRIVER's), and 26 games came out
  "fix" from that alone. A run is blank only when its last three screenshots are, and a run's
  snapshot is its last screenshot with something on it.
- **The PPDRIVER reference decides** (task 4): every game not "as it is", and two per strategy,
  run from a PPDRIVER image too (`run_all.py --disk ppdriver`, each run its own image, five at a
  time). Glad Killing Impact and Monkeys and Balloons halt from PPDRIVER exactly as from the
  GEMDOS drive: Hatari halts them, the drive does not. `verdicts.py`: the same outcome from
  PPDRIVER is "as it is" (the drive changes nothing); PPDRIVER running what the GEMDOS drive does
  not is "fix"; anything else "unsure".
- **STE games run on the STE**: Revenge of Mutant Camels STE halts on the ST and runs on STE TOS
  1.62.
- **Findings** (`src/survey/findings.tsv`): a game looked into from its own trace gets the verdict
  the trace shows, with the evidence. Great Giana Sisters STE streams its music from GS.RAW's
  sectors ("Error in getting file location" from a GEMDOS drive; its page's HAGA downloads read
  through GEMDOS): fix. Rody and Mastico 2's archive has no RUNME.TOS; Rody and Mastico 4's starts
  it: fix. Ice and Fire is three floppy images, no hard-disk version: unsure until a virtual
  floppy driver is tried.
- **Answers on a replaced run.** An answer stands while the run that counts ends as the one Diego
  answered on; 19 were given on a run since replaced by one that ends otherwise (a run that
  started in time, the right program, more RAM): the new run's proposal counts and review.py shows
  them again as not reviewed (`stale.txt`).
- **What the PPDRIVER comparison corrected.** A PPDRIVER run starts from `C:\LEMMINGS\`: the
  analysis now finds its start there too (it looked for `C:\GAME\` only, and saw no exit or read).
  On a PPDRIVER image a program's sector reads on C: are answered, and Hatari reports a file not
  found only on its GEMDOS drive, so neither counts there. A file not found that is nowhere in PP's
  archive (26 games: saves, high-score tables, Gobliiins' other loaders `foader.prg`…) is missing
  from any disk alike: only a file the archive has and the drive did not find counts. Under
  HAGE's and HAG2's TOS in RAM, sector reads are PP's floppy-image service (Lords of Conquest reads
  D: 78 times from both disks); a device above P: is no drive (Pole Position's Rwabs on 52).
- **The boot block of C:.** Crystals of Arborea's and Targhan's `START.PRG` (one compilation) ask
  `Getbpb(2)` over and over from the GEMDOS drive, which has none, and stay on a blank screen;
  from PPDRIVER they get it, read C: by sectors and show their menu: fix, and STORY-04's "plain" is
  wrong for them. Defender 2's GOS4 launcher does the same (374 requests). Eight requests or more
  are now a sector-access signal.
- **A second program that does nothing from the GEMDOS drive.** Spy vs Spy 2 (`SPY2.BOY`) and
  Strike Force Harrier (`HARRIER.TOS`): their start program's `Pexec` of the game loads it from
  the GEMDOS drive (Hatari's own loader, no error) and the game ends without a system call; from
  PPDRIVER TOS loads it and it plays. Fix, the cause to find (`SPY2.BOY` is position-independent:
  not its load address).
- **Hatari itself fails** with Pac-Land from both disks ("string allocation failed", Hatari exits
  after its first level loads): the drive changes nothing. Oxyd Highres needs a monochrome
  monitor ("Highres" in its name, "monochrome" in its README) and then runs from both disks.
- **The STE** (task 4): one game per strategy on STE TOS 1.62 and 2.06 from both disks behaves as
  on the ST; the analysis knows the STE's ROM at $E00000 (BIOS below $E10000, the desktop above).
  From PPDRIVER on TOS 2.06, HAGE and HAG2 stop: "Too much low RAM occupied. Read usage how to fix
  it." (ACC-TRIS, Algebra): PP's driver and TOS 2.06 leave HAGE too little low RAM in 1 MB; the
  GEMDOS drive takes none of the Atari's RAM, and from it they run.

Corrected in STORY-06 (2026-10-13; `src/notes/hd-strategies.md` §6): Weird Dreams and Maddog
Williams as it is, Aquanaut fix, Great Giana Sisters STE not feasible; the counts are now 1,608 as
it is, 212 fix, 1 not feasible, 10 unsure. The results as STORY-05 left them:

**Results (2026-10-13)**, `src/survey/migration.csv` from `tools/survey/verdicts.py`: 1,831 games,
**1,606 as it is, 213 fix, 12 unsure, 0 not feasible**; by whose word: the run 1,489, its PPDRIVER
comparison 96, Diego 243, a trace looked into 3. 2,070 runs in `tools/dev/builds/survey/runs.tsv`
(1,831 GEMDOS drive on ST TOS 1.04, 189 PPDRIVER on the ST, 50 on the STE).

| strategy | games | as it is | fix | unsure |
|---|---:|---:|---:|---:|
| HAGA | 1,025 | 1,021 | 0 | 4 |
| HAGE | 207 | 206 | 1 | 0 |
| HAG2 | 134 | 134 | 0 | 0 |
| plain | 123 | 112 | 7 | 4 |
| Gamex + GOS4 | 117 | 0 | 117 | 0 |
| Gamex | 110 | 108 | 0 | 2 |
| Gamex + GOS5 | 87 | 0 | 87 | 0 |
| PP launcher | 18 | 17 | 1 | 0 |
| Gamex + GOS 1.00 | 5 | 5 | 0 | 0 |
| plain + HOLE | 3 | 2 | 0 | 1 |
| floppy image | 1 | 0 | 0 | 1 |
| FWRD RAM disk | 1 | 1 | 0 | 0 |

- **Fix**: every GOS4 and GOS5 launcher (204: they quit to the desktop from the GEMDOS drive,
  the driver checks of STORY-04; from PPDRIVER they run, on ST and STE alike). Five programs read
  C: by sectors (Crystals of Arborea, Targhan, Robinsons Requiem and Storm Master ask for its boot
  block for ever; Weird Dreams' launcher reads 418 sectors), their access corrected from "files" to
  "sectors" (task 5; with Defender 2's GOS4 launcher and Robotron 2084's two reads, which play
  anyway). Two start programs whose game does nothing when started from the GEMDOS drive (Spy vs
  Spy 2, Strike Force Harrier: four runs each, 1 to 4 MB). Great Giana Sisters STE (its audio by
  sectors) and Rody and Mastico 2 (no RUNME.TOS in PP's archive), from their traces.
- **Unsure** (12): 11 are Diego's Broken on games whose GEMDOS-drive run the rules call "as it
  is", kept after a second look with the PPDRIVER snapshot beside each (review.py's "to settle",
  2026-10-13; the same look made Color Beyond Time, Empire Strikes Back PD, Resolution 101, Police
  Quest II and Wolfenstein 3D OK). PPDRIVER fails too for Lords of Doom, Substation, Roger, Zero-5,
  Maddog Williams, Utopos and Spitting Images; it runs, or waits at a title, for Super Breakout
  mono, 9 Lives, Little Puff and Aquanaut. The cause of each is still to find. Ice and Fire: three
  floppy images, settled by a virtual floppy driver run from the GEMDOS drive.
- **Not feasible**: none seen. No game needed the floppy controller during play from the GEMDOS
  drive that it did not also need from PPDRIVER.
- **Hatari, not the drive**: 39 games halt (18), end blank (13), quit (6) or on a desktop (2) the
  same way from both disks (Glad Killing Impact, Monkeys and Balloons, Never Mind…), and Hatari
  itself quits with Pac-Land; they count as "as it is", the reason recorded ("the same from
  PPDRIVER").
