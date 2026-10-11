---
id: EPIC-00
iteration: 1
title: The development environment, the test tools, and Hatari as the test machine
status: todo
---

## Goal

A workspace where every later story is a short loop run from the host, without Diego. It needs:

- the original evidence pristine and checked, the first pass archived (D-01), and git;
- a pinned toolchain that disassembles and assembles 68000 code;
- a check that a reconstructed source reassembles to the original bytes;
- Hatari booting the launcher in the two disk setups the project compares: GEMDRIVE mode (a
  GEMDOS drive, `--harddrive`) and, as the working reference, an ACSI image booted by PP's own
  driver, PPDRIVER, built with `../atari-hd`.
  It runs on the machines and TOS versions PP supports, driven from the host, and ends with PASS
  or FAIL and the evidence.

Hatari is used as released, never modified (C-02). Asked by Diego, 2026-10-11: epic 0, as in the
sibling repositories (`sidecartos-config` EPIC-00, `romemul-switcher-rom` EPIC-00, firmware
EPIC-00).

## Scope

- In scope: the fresh start (archive, pristine `LEMMINGS/`, manifest, git); the pinned
  toolchain and the scripts around it; the reassembly round-trip check; the two Hatari disk
  setups, built by script from a copy of `LEMMINGS/`; the Hatari harness; one script that runs
  everything; documentation (`tools/dev/README.md`, `CLAUDE.md`).
- Out of scope: any conclusion about the launcher (EPIC-01 onwards); unpacking it (EPIC-02);
  changes to Hatari (C-02); CI.

## Setups

Hatari 2.6.1 on this Mac, ST and STE only, TOS up to 2.06 (Diego, 2026-10-11): an ST with TOS
1.04, an STE with TOS 1.62 and an STE with TOS 2.06, each with at least 1 MB (C-04); each in
GEMDRIVE mode and from the PPDRIVER image. Other TOS versions of that range can be added through
`tools/dev/dev.cfg`. No Mega STE, TT or Falcon. The verification story is a run of the harnesses
on this Mac that Diego watches and agrees with.

## Stories

- STORY-01: A clean workspace: the first pass archived, the evidence pristine, git
- STORY-02: The pinned toolchain
- STORY-03: The round-trip check: a source that reassembles to the original bytes
- STORY-04: Hatari groundwork: TOS, a driver, and the two disk setups
- STORY-05: The Hatari harness
- STORY-06: Run everything, and document it
- STORY-07: Verification (Diego's checkpoint)

## Notes

**What this Mac has (checked 2026-10-11):**

- Hatari 2.6.1 at `/usr/local/bin/hatari`. Its saved configuration
  (`~/Library/Application Support/Hatari/hatari.cfg`: STE, TOS 1.62, 4 MB) is loaded by every run
  that does not set its own `HOME`, as `romemul-switcher-rom` EPIC-00 STORY-03 found; the
  harness runs with a clean `HOME`. Hatari's sources are checked out in `../hatari`, for reading
  how its GEMDOS drive and ACSI emulation behave (reading only, C-02).
- Docker, and `stcmd` at `/usr/local/bin/stcmd`, which runs
  `logronoide/atarist-toolkit-docker-x86_64:latest` with the current folder mounted at `/tmp`
  (so paths given to a tool are `/tmp/<relative path>`). Its `$@` is unquoted, so
  `stcmd bash -c '…'` breaks; call one tool per `stcmd`. That image has `vasmm68k_mot` 2.0e,
  `vlink`, and `m68k-atari-mint-objdump`, `-as` and `-gcc`. The siblings pin tag `1.4.0`, a
  different image (D-05).
- `stcmd m68k-atari-mint-objdump -D -b binary -m m68k --adjust-vma=0x70000 /tmp/<bin>`
  reproduces the first pass's raw listings line for line (checked on its `ls2dd.bin`).
- Python 3.14 (`python3`), and mtools (`mcopy`, `mformat` at `/usr/local/bin`).
- TOS images: C-03.
- `../atari-hd` (sidecartridge/atari-hd, v0.1.0): a standard-library Python builder of Atari ST
  hard-disk images. `--ppdriver-bootable` makes a self-booting PPDRIVER image (Peter Putnik's
  PPTOSDOS, freeware) from its bundled boot blob `assets/pp_boot_blob.bin`: 15 sectors, the IPL
  at LBA 0 and 1 and the `.PRG`-format driver at LBA 2 to 14, cold-boot validated on real
  hardware by that project (its `BOOTABLE.md`). It formats the image but has no option to copy
  files into it. Its `drivers/` also holds ICD 6.5.5 and HDDriver 11.14, unused here.

**Answered by Diego, 2026-10-11:** the ACSI reference uses the PPera driver, PPDRIVER, as built
by `../atari-hd` (D-09). This is the "PP" of `README.TXT`'s "PP, AHDI or Hddriver".
