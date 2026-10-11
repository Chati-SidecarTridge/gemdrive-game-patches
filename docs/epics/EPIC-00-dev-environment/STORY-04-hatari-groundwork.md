---
id: STORY-04
epic: EPIC-00
title: Hatari groundwork: TOS, a driver, and the two disk setups
status: todo
---

## Goal

Everything the harness boots, built by script from a copy of `LEMMINGS/` and never from the
original (C-01): a folder for GEMDRIVE mode, and a bootable ACSI image holding the game as PP's
`README.TXT` asks (a partition under 512 MB, PP's driver), plus the TOS image for each machine.

## Tasks

- [ ] `tools/dev/dev.cfg.example` (committed) and `tools/dev/dev.cfg` (ignored): the path to
      Hatari, to each TOS image (C-03) and to `../atari-hd`. Every script refuses to start without
      what it needs, and says what.
- [ ] `tools/dev/make_disks.sh [<source dir>]`: copies `LEMMINGS/` (or a patched or rebuilt tree
      given as argument) into `tools/dev/builds/disks/` and builds both setups from it.
- [ ] GEMDRIVE: a folder that Hatari mounts as drive `C:` (`--harddrive`), holding `LEMMINGS/`.
      Record how Hatari's GEMDOS drive treats the case of file names on this Mac's file system,
      and which options change it.
- [ ] PPDRIVER image: built by `../atari-hd` with `--ppdriver-bootable` (D-09), one partition
      under 512 MB, run without its TUI from the script; the game copied into its FAT16
      partition (with `mcopy` at the partition's offset, since atari-hd cannot add files). It
      boots in Hatari (`--acsi`) on an ST with TOS 1.04. The exact command lines and the
      partition offset recorded here.
- [ ] Each setup booted once in Hatari, headless, on every machine of the epic, to a desktop
      that shows the drive and the `LEMMINGS` folder: screenshots recorded.
- [ ] `shasum -a 256 -c LEMMINGS.sha256` still passes after building and booting both.

## Acceptance

From a clean `tools/dev/builds/`, `tools/dev/make_disks.sh` builds both setups, and each boots in
Hatari to a desktop that shows the game's folder. `LEMMINGS/` is unchanged.

## Notes
