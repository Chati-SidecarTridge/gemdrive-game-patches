---
id: STORY-04
epic: EPIC-00
title: Hatari groundwork: TOS, a driver, and the two disk setups
status: done
---

## Goal

Everything the harness boots, built by script from a copy of `LEMMINGS/` and never from the
original (C-01): a folder for GEMDRIVE mode, and a bootable ACSI image holding the game as PP's
`README.TXT` asks (a partition under 512 MB, PP's driver), plus the TOS image for each machine.

## Tasks

- [x] `tools/dev/dev.cfg.example` (committed) and `tools/dev/dev.cfg` (ignored): the path to
      Hatari, to each TOS image (C-03) and to `../atari-hd`. Every script refuses to start without
      what it needs, and says what.
- [x] `tools/dev/make_disks.sh [<source dir>]`: copies `LEMMINGS/` (or a patched or rebuilt tree
      given as argument) into `tools/dev/builds/disks/` and builds both setups from it.
- [x] GEMDRIVE: a folder that Hatari mounts as drive `C:` (`--harddrive`), holding `LEMMINGS/`.
      Record how Hatari's GEMDOS drive treats the case of file names on this Mac's file system,
      and which options change it.
- [x] PPDRIVER image: built by `../atari-hd` with `--ppdriver-bootable` (D-09), one partition
      under 512 MB, run without its TUI from the script; the game copied into its FAT16
      partition (with `mcopy` at the partition's offset, since atari-hd cannot add files). It
      boots in Hatari (`--acsi`) on an ST with TOS 1.04. The exact command lines and the
      partition offset recorded here.
- [x] Each setup booted once in Hatari, headless, on every machine of the epic, to a desktop
      that shows the drive and the `LEMMINGS` folder: screenshots recorded.
- [x] `shasum -a 256 -c LEMMINGS.sha256` still passes after building and booting both.

## Acceptance

From a clean `tools/dev/builds/`, `tools/dev/make_disks.sh` builds both setups, and each boots in
Hatari to a desktop that shows the game's folder. `LEMMINGS/` is unchanged.

## Notes

**Done 2026-10-11.**

- `tools/dev/dev.cfg.example` (committed) holds this Mac's paths, relative to the repository
  where they can be: Hatari, the three TOS images (C-03) and `../atari-hd`; `dev.cfg` is a copy,
  git-ignored. Shell scripts read it through `tools/dev/devcfg.sh`, Python through
  `tools/dev/devcfg.py`. Without `dev.cfg`, `make_disks.sh` and the harness stop and say to
  copy the example; the harness also stops when the disk setups are missing.
- TOS images, versions read from their headers: ST `TOS 1.04 - English UK - 50Hz.img` (`0104`,
  192 KB), STE `TOS 1.62 - English-UK - 50Hz` (`0162`, 256 KB), STE
  `TOS 2.06 - English-UK - 50Hz` (`0206`, 256 KB).
- `tools/dev/make_disks.sh` builds both setups in about 1.3 s into `tools/dev/builds/disks/`:
  `gemdrive/LEMMINGS/` (76 files, `.DS_Store` left out, dates kept), `ppdriver.img`, and
  `SOURCE.txt` with the SHA-256 of every file.
- The PPDRIVER image, made without atari-hd's TUI (it still asks for a file name and a
  confirmation, given on stdin):
  `printf 'ppdriver.img\ny\n' | python3 -I ../atari-hd/atari_hd.py --no-tui --ppdriver-bootable --size 32 --auto default --auto-n 1`.
  Layout "MBR + PPera TOS&DOS dual BPB": one partition at LBA 63, 65,536 sectors, 512-byte
  sectors in its DOS view and 1,024-byte in its TOS view, OEM name `PPGDODBC`. The game goes in
  through the DOS view, `MTOOLS_SKIP_CHECK=1 mcopy -s -m -i ppdriver.img@@32256`, and is checked
  by copying everything back out and comparing all 76 SHA-256.
- Both disks get `tools/dev/DESKTOP.INF` at their root, the first pass's TOS 1.04 desktop file
  unchanged: it opens a window on `C:\LEMMINGS\*.*`. TOS 1.62 and 2.06 read it too.
- File-name case on the GEMDOS drive: Hatari matches Atari names against host names without
  regard to case by itself (`../hatari/src/gemdos.c`: "Host file names are handled case
  insensitively"; exact match tried first, then case-insensitive), and this Mac's data volume
  is case-insensitive APFS anyway. `--gemdos-case off|upper|lower` only changes the case of
  names the Atari creates; `--gemdos-conv` converts characters. Bearing on H-04, whose verdict
  is EPIC-01's.
- Booted once each, headless, to the desktop (`hatari_harness.py --no-auto`), about 21.5 s per
  run; every screenshot shows the `C:\LEMMINGS` window with its 8 items:

| setup | GEMDRIVE | PPDRIVER |
| --- | --- | --- |
| ST, TOS 1.04 | PASS | PASS |
| STE, TOS 1.62 | PASS | PASS |
| STE, TOS 2.06 | PASS | PASS |

  In GEMDRIVE runs Hatari logs `GEMDOS HDD emulation, C: <-> …/drive` and
  `Gemdos_Boot(GEMDOS_EMU_ON=1)`. In PPDRIVER runs it logs `Mounting ACSI HD image`,
  `GEMDOS_EMU_ON=0` and no host path at all, and its `scsi_cmd` trace shows the driver booting:
  `READ SECTOR … LBA 0x0`, then 11 sectors from LBA 2 (atari-hd's blob: IPL at LBA 0 and 1,
  driver at LBA 2 to 14).
- `shasum -a 256 -c LEMMINGS.sha256`: 76 OK after building and booting everything; no Hatari
  left running.
