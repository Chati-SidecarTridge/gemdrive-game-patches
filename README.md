# Atari ST hard-disk adaptations, from GEMDOS and GEMDRIVE

The 8bitchip.info website lists 1,831 Atari ST games adapted to start from a hard disk. This
project starts every one of them from a **GEMDOS drive**, a folder that the ST sees as drive C:,
served file by file with no disk sectors: the Hatari emulator's GEMDOS drive, and the
[SidecarTridge Multi-device](https://sidecartridge.com/products/sidecartridge-multidevice-atari-st/)'s
**GEMDRIVE** on real machines. Most games run as they are. The others need a fix, and this
repository builds the fixes.

**To use it, go to <https://gemdrive.sidecartridge.com/>, "Patch a game".** Give it a game's ZIP
exactly as downloaded from the 8bitchip.info website: it says whether the game runs as it is, and
when a fix makes it run, it patches the ZIP in your browser and gives it back. This README is for
developers.

## What it found

- 1,608 games run from GEMDOS and GEMDRIVE as they are.
- 212 need a fix. 209 of them run with this project's fixes, in Hatari and on real machines with
  the Multi-device.
- 1 is not feasible, and 10 are still unsure.

Most of the games to fix use the Gamex launcher with GOS4 or GOS5: their own GEMDOS, a copy of TOS
1.04's that runs from RAM and reads the hard disk sector by sector through the `PPDRIVER` driver. A
GEMDOS drive has no driver and no sectors. The fix rebuilds the game's start program so that GOS
asks the drive for its files by name instead. Three smaller fixes cover eight other games.

## No original files

The games, their adaptations and their documentation belong to the 8bitchip.info website, a third
party. This repository and its website carry none of their files: no game, no launcher, no ZIP. The
fixes are our own code, and the patcher rebuilds the fixed file from the user's own download,
checked against this project's build by SHA-256. The tables keep each download's name, size and
hash only.

## The pieces

- **The survey** (`tools/survey/`): every game of the list, its files, its strategy (the way its
  adaptation reaches its files), its run in Hatari and its verdict (`src/survey/migration.csv`).
- **The fixes**:
  - S1, the GOS5 and GOS4 games: `tools/build_gos5.py`, `tools/build_gos4.py`, with our blocks
    `src/gemdrive/gos5_patch.s` and `gos4_patch.s`.
  - S2, a BPB for the drive: `GDBPB.PRG`, from `src/gemdrive/gdbpb.s`.
  - S3, the fastload bit: `tools/set_fastload.py`.
  - S4, a missing start program: `tools/rody2_runme.py`.
- **The patcher** (`tools/site/patcher.js`): the fixes in JavaScript, byte for byte the Python
  tools' results, run in the browser on the user's ZIP; its table is `src/survey/patches.tsv`
  (`tools/survey/patch_table.py`).
- **The website** (`tools/site/`): the findings, the modes, the solutions, the patcher and the
  catalogue of every game.
- **The reverse engineering** (`src/`): the maps of the Lemmings launcher's stages, from which
  `tools/make_sources.sh` makes sources that reassemble to the original bytes, using your own copy
  of the game in `LEMMINGS/`; and the notes (`src/notes/`).

## Building and testing

You need Python 3, Docker with the pinned toolchain image, and Hatari 2.6.1 with the TOS images.
Copy `tools/dev/dev.cfg.example` to `tools/dev/dev.cfg` and set its paths, then:

```
tools/dev/all_harness.sh                        # every check: disks, round trip, Hatari runs, the site
python3 tools/build_gos5.py START.TOS OUT.TOS   # a GOS5 game's start program, built for a GEMDOS drive
python3 tools/build_gos4.py START.TOS OUT.TOS   # the same for a GOS4 game
python3 tools/survey/sdcard.py                  # every game laid out for a microSD card, fixes applied
python3 tools/survey/patch_table.py             # the patcher's table of every archive
python3 tools/site/build_site.py --check        # the website, into tools/dev/builds/site/
```

Every fix is tested twice: in Hatari, on an emulated ST with TOS 1.04 and STE with TOS 1.62 and
2.06, from its GEMDOS drive and from a `PPDRIVER` hard-disk image as the reference; then on real
machines with the Multi-device's GEMDRIVE, from a test card. Hatari's GEMDOS drive and GEMDRIVE
behave the same on every machine; only the exceptions are reported. `tools/dev/README.md` has the
whole toolset, and `CLAUDE.md` the working rules.

## The website

The website is <https://gemdrive.sidecartridge.com/> (`CNAME`). `python3 tools/site/build_site.py`
writes it into `tools/dev/builds/site/`; it works from that folder and needs nothing from another
site. `--check` verifies every link and anchor, every game's row, and that no page loads another
site's files. CI runs it on every pull request and push to `main`.

## Licence

GNU General Public License v3.0; see [LICENSE](LICENSE). The games and their adaptations are not
covered by it, and are not part of this repository.
