---
id: STORY-02
epic: EPIC-00
title: The pinned toolchain
status: done
---

## Goal

Every disassembly and every assembly runs from one pinned image (D-05) through two short scripts,
so a listing or a binary made today is made the same way next month.

## Tasks

- [x] `tools/dev/toolchain.sh`, sourced by every script: the pinned image
      (`logronoide/atarist-toolkit-docker-x86_64:1.4.0`) and a `docker run` helper that mounts
      the repository at `/work`. `stcmd` is not used: it follows `latest`.
- [x] Check that `1.4.0` carries `vasmm68k_mot`, `vlink` and `m68k-atari-mint-objdump`, with
      their versions recorded here. If it lacks vasm, record the choice made (D-05).
- [x] `tools/dev/disasm.sh <bin> <vma> <out>`: a raw binary disassembled for the 68000 at a
      given load address, into a listing.
- [x] `tools/dev/asm.sh <source.s> <out.bin> [<listing>]`: vasm Motorola syntax to a raw
      binary, with no optimisation (`-no-opt`), so every instruction keeps the encoding it was
      written with; optionally vasm's listing (`-L`).
- [x] Both scripts refuse to start without Docker or the image, and say so.

## Acceptance

`tools/dev/disasm.sh` gives the same listing as the first pass's
`_archive/2026-04-first-pass/src/disasm/ls2dd.raw.asm` for its `ls2dd.bin` at `0x70000`, apart
from the file path in the header line; a three-instruction source assembled by
`tools/dev/asm.sh` and disassembled back shows the same three instructions.

## Notes

**Done 2026-10-11.**

- `tools/dev/toolchain.sh` pins `logronoide/atarist-toolkit-docker-x86_64:1.4.0` by tag and
  digest (`sha256:016434131cf5…eebe`, the reference `romemul-switcher-rom` uses), with
  `tc_require`, `tc_path` (host path to `/work/…`, refusing anything outside the repository)
  and `tc_run`. Listings come back on stdout and are written by the host.
- In `1.4.0`: `vasmm68k_mot` 2.0f (Motorola syntax module 3.19f, M68k backend 2.8c),
  `vlink` 0.18a, `m68k-atari-mint-objdump` from binutils 2.30 (MiNT 20180703). `latest` is a
  different image (`5065daced2ef`, vasm 2.0e).
- `tools/dev/disasm.sh` defaults to `m68k:68000`. With `m68k`, the first pass's arch, its listing
  of `ls2dd.bin` at `0x70000` was identical to the first pass's `ls2dd.raw.asm` apart from the
  header line naming the file; with `m68k:68000`, 101 lines differ, where bytes that are not a
  68000 instruction show as `.short`. About 3.4 s per call, most of it Docker. Since STORY-03 it
  passes objdump `-z`: the same comparison then differs only where the first pass's listing
  hid runs of zero bytes behind `...` (2 such lines, now 490 lines of zeros).
- Three instructions (`moveq #5,d0`, `lea ($10,pc),a0`, `rts`) assemble to
  `7005 41fa 000c 4e75` and disassemble back to the same three. vasm's listing gives section,
  address, bytes and source line for each line, which STORY-03 uses.
- Without Docker or the image both scripts stop with what to do (`tc_require`); seen with
  `docker` off the `PATH` and with a missing tag. A path outside the repository was refused
  (`tc_path`); since STORY-03 inputs reach the container as fresh copies (`tc_stage`), so only
  `asm.sh`'s outputs must be inside the repository.
