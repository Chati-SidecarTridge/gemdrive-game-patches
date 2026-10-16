---
id: EPIC-08
iteration: 2
title: The ports on acsi2stm's GemDrive
status: todo
---

## Goal

The builds EPIC-04 to EPIC-07 made for a GEMDOS drive also run the games from acsi2stm's GemDrive,
the other GEMDRIVE (<https://github.com/retro16/acsi2stm>), or this epic says why they cannot.
Asked by Diego, 2026-10-16 (D-18): "there is another 'variant' of the GEMDRIVE approach: the
acsi2stm GEMDRIVE. While not part of our project at this moment, I would like to add an epic at
the end of the conversion to check if it could work also with this variant our solution". A change
it needs goes into the same builds, and Hatari's GEMDOS drive and the Multidevice's GEMDRIVE keep
running them.

## What its code says (read 2026-10-16, v5.00, commit `aae0f60`; to be observed, D-01)

- **Not a cartridge.** An STM32 on the ACSI port. At boot it hands the ST a boot sector; the STM32
  then uploads a 456-byte stub into memory it `Malloc`s and hooks `TRAP #1` with XBRA `A2ST`
  (`acsi2stm/GemDrive.cpp`: `onBoot`, `installHook`; `asm/GEMDRIVE/boot.s`). `GEMDRIVE.PRG` or
  `GEMDRPIO.PRG` in `AUTO` do the same as a resident program (`asm/GEMDRIVE/prg.s`, `init.s`).
- **The ST runs the STM32's commands.** Every GEMDOS call sends one command byte over the ACSI DMA,
  then the stub runs the STM32's commands until it returns: read or write memory, push on the
  stack, a DMA to an address, a `TRAP #1` of its own, return (`asm/GEMDRIVE/syshook.s`). GEMDOS
  itself is in the STM32. The stub polls the MFP's GPIP bit 5 for each reply: no interrupt and no
  timer during a call, and no timeout. It locks the DMA chip with `flock` (`$43E`) and sends a call
  that comes while `flock` is set straight to TOS. The PIO firmware's stub (`asm/GEMDRPIO`) moves
  the bytes without DMA.
- **What the STM32 reads.** At boot it keeps the OS header's `os_beg` and `p_run` of the machine's
  TOS; each `Fopen` and `Fcreate` tags its file with the basepage at `p_run` (`getBasePage`), used
  to close a process's files at `Pterm`. `Fsfirst` and `Fsnext` use `Fgetdta`, `Pexec` `Malloc`.
- **Drives.** From C:, or from L: when a slot is in ACSI mode; long names cut.

## What that means for our builds (each to check)

1. **gd_check** takes the GEMDOS-drive path only for a `TRAP #1` in the cartridge range: acsi2stm's
   is in RAM, so our builds take PP's fallback. It has to know XBRA `A2ST`.
2. **The stub is in the game's RAM**: `Malloc`'d at boot, or the resident program's, low in the
   TPA, which the games overwrite. Like GEMDRIVE's stack (`md_move_stack`), it has to move out of
   it: a copy beside gd_forward, called by gd_forward. The stub reaches its variables PC-relative,
   and the STM32 keeps no address of it after `installHook`; the resident program's handlers sit in
   its basepage's command line.
3. **`p_run`** is in TOS's RAM above `$800`, outside GOS's image of low RAM: the games overwrite
   it, so the files' tag is whatever is there. Harmless if it only matters at `Pterm`.
4. **The caller's stack.** The stub's commands push on the stack of the call (GOS's, PP's loader's
   below `$84000`), where the Multidevice's GEMDRIVE moves to its own: how deep it goes.
5. **Low RAM during `file_io`** is GOS's image: `flock` is GOS's, and a `TRAP #1` of the stub's
   (command `$96`) goes through GOS's vector to gd_forward again.
6. **Interrupts masked during loads**: the stub polls, so it needs none; an STM32 error stalls the
   machine.
7. **The DMA chip**, shared with the floppy controller: the games that read the FDC through it (the
   floppy motor waits, EPIC-04 STORY-05) after a call of the stub's.
8. **acsi2stm's ACSI mode** (a disk image with PP's driver) is PP's own path: our builds already
   take it (D-17); its compatibility list has "GemDrive + PP driver".

## Scope

- In scope:
  - The builds of EPIC-04 to EPIC-07, and the change that makes them run from acsi2stm's GemDrive:
    the boot sector and the `AUTO` program, DMA and PIO firmware.
  - Hatari's GEMDOS drive, PP's PPDRIVER path and the Multidevice's GEMDRIVE still running every
    build after the change.
- Out of scope:
  - acsi2stm's firmware and driver, which stay as they are (the fix is on the Atari side, as for
    Hatari, C-02).
  - Games the ports did not port.
  - acsi2stm's code in this repository: it is GPLv3, cited by URL and commit, never copied.

## Setups

- Hatari: ST TOS 1.04, STE TOS 1.62 and STE TOS 2.06, GEMDOS drive and PPDRIVER, for the builds
  after the change. Hatari cannot run acsi2stm's GemDrive (its ACSI port takes a disk image) and is
  not changed (C-02): what Hatari can show of it is an emulation of the stub's use of RAM, as
  `src/probes/epic04/md_emulate.py` did for the Multidevice.
- An ACSI2STM on Diego's STE, from its SD card, power-cycled between games: the only place the
  protocol itself runs (STORY-01 asks which unit and firmware).

## Stories

- STORY-01: acsi2stm's GemDrive read: what a call does on the ST
- STORY-02: Our builds made to know it
- STORY-03: The ported games from acsi2stm's GemDrive
- STORY-04: Verification (Diego's checkpoint)

## Notes
