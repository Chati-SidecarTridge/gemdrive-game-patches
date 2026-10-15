---
id: STORY-08
epic: EPIC-03
title: Verification and the choice of solutions (Diego's checkpoint)
status: in-progress
---

## Goal

Diego agrees with the strategies, the verdicts and the solutions proposed, seen in Hatari and on
the SidecarTridge Multidevice's GEMDRIVE, and chooses which solutions become iteration 2's epics
and in what order.

## Setups

- Hatari, ST TOS 1.04: one representative of each strategy from the GEMDOS drive and from the
  PPDRIVER image, as in STORY-05.
- Diego's machines with the SidecarTridge Multidevice's GEMDRIVE: every game from a microSD card
  (asked by Diego, 2026-10-13). A preview: the Multidevice's GEMDRIVE is otherwise later work
  (`ITERATIONS.md`).

## Tasks

- [x] The test card's folder: `tools/survey/sdcard.py` lays every game out in
      `tools/dev/builds/sdcard/` as `<verdict>\<RAM>\<group>\<ZIP's name>\`: first the verdict
      from Hatari's GEMDOS drive, the games that need a fix split by strategy (`WORKS`, `FIXGOS4`,
      `FIXGOS5`, `FIXHAGE`, `FIXPLAIN`, `FIXHOLE`, `UNSURE`, `NOFIX`), then the RAM its run needed
      (`1MB`, `2MB`, `4MB`), then groups of at most 80 games (`10T-AST`: more in one folder
      exhaust the machine's memory, Diego, 2026-10-13), then the game; `INDEX.TXT` gives each
      game's program to start. Diego copies it to the card.
- [ ] Diego tests games from the card on the Multidevice's GEMDRIVE; a game that disagrees with
      its verdict from Hatari is listed here, with what he saw.
- [ ] Claude walks Diego through the website and runs one representative of each strategy in
      GEMDRIVE mode and from the PPDRIVER reference.
- [ ] D-15's removal list shown to Diego; going public only on his word, after the clean-up.
- [ ] Diego's choice of solutions and their order recorded as a decision in `DECISIONS.md`, and
      their epics written (EPIC-04 on), each with a first test game.
- [ ] Diego agrees, or the stories to reopen are listed here.

## Acceptance

Diego's agreement and his choice of solutions, recorded with the date.

## Notes

### The test card (2026-10-13)

`python3 tools/survey/sdcard.py`, then copy `tools/dev/builds/sdcard/` to the card's root.

1,831 games in 1,828 folders (three downloads hold two games each: `FUTUREWG`, `MOONPATR`,
`ARBOTARG`), 26,580 files, 1,545 MB. Every ZIP name already fits in eight characters.

| Folder | 1MB | 2MB | 4MB |
|---|--:|--:|--:|
| `WORKS` | 1,331 in 17 groups | 256 in 4 | 19 |
| `FIXGOS4` | 112 in 2 | 5 | |
| `FIXGOS5` | 74 | 13 | |
| `FIXHAGE` | 1 | | |
| `FIXHOLE` | 1 | | |
| `FIXPLAIN` | 5 | | |
| `UNSURE` | 6 | 4 | |
| `NOFIX` | | 1 | |

- **RAM** is the RAM of the run that gave the verdict, not PP's list: `run_all.py` ran a game in
  trouble again with 2 MB, then 4 MB, and 19 games ran only with 4 MB, a figure the list never
  gives. Two games had no run (no program to start: Rody and Mastico 2, Ice and Fire): the list's
  figure.
- **Groups**: a RAM folder is cut into the fewest groups of at most 80 games, of even size (16
  of 79 and one of 67 in `WORKS\1MB`), in alphabetical order, each named after the first three
  characters of its first and last game (`10T-AST`, `ATA-BLI`, ...); a RAM folder with fewer games
  has one group, so every game is at the same depth. Two neighbours can share their letters
  (`CIR-DEL`, `DEL-FAM`). Six games have more than 80 files in their own folder, which cannot be
  split: `CIVILIZ` 115, `SUPERCAU` 112, `ROBINSON` 108, `SPACEHAR` 93, `AIRBUCKS` 87, `CHRONOQ` 84.
- **A game's folder** holds what the runs had as `C:\GAME\` (the folder of the program started),
  so the program is at the folder's top, and beside it what the download keeps next to that
  folder. Maddog Williams opens `C:\PABISYS.FIL` (its run's trace), so that file is at the card's
  root. Zero-5's folder keeps its own `README.TXT` and `ZERO5.INF` over the download's top-level
  copies of the same names. Air Bucks and Annihilator keep, two levels up, files the runs did
  not have either (a README, PP's untouched original).
- **Checked** by a script of its own: every file on the card equals, byte for byte, the file of
  its download at the same relative path; every file of each download is on the card but for the
  four cases above; every program `INDEX.TXT` names exists; no folder above the games holds more
  than 80 entries, and every group is named after its first and last game.
- **Differences from Hatari's runs**: the games run four folders deep (`C:\WORKS\1MB\10T-AST\X\`), not
  from `C:\GAME\`; a game that names its folder in full would not find it. Eighteen downloads
  have names that do not fit 8.3: documents and pictures, but for Lode Runner's `TABLO[.LOR` (`[`
  has no place in a FAT short name), Lombard Rally's `FILES\LOMBARD_O.PRG` and Starblaze's
  `FILES\SBLAZE_org.IMG`.

### Diego's tests on the Multidevice

**Power-cycle between games.** After other games and a reset, memory and hooked vectors are left
over, and some games fail. Diego says this is a known problem. A game that fails after a reset
is tried again after a full power cycle before it counts against its verdict.

- **3D Construction Kit** (`WORKS\1MB\10T-AST\3DCONKIT\3DKIT.PRG`, plain, as it is), STE TOS 1.62 4 MB
  (2026-10-13): three bombs after other games and a reset; it works after a power cycle. Its
  verdict stands.
  - Its run in STORY-05 had stopped at the language dialog, which the run's keys do not answer.
  - Run again in Hatari with the dialog skipped (`-lUK` written into its basepage's command line
    at its first instruction, the switch its `README.KIT` gives), it reaches the editor on all
    five setups tried: ST TOS 1.04 and STE TOS 1.62, at 1 and 4 MB, from the card's path. It also
    reaches the editor from `C:\GAME\` on STE TOS 1.62 at 4 MB.
