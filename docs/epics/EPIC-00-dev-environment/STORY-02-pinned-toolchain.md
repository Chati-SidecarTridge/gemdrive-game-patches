---
id: STORY-02
epic: EPIC-00
title: The pinned toolchain
status: todo
---

## Goal

Every disassembly and every assembly runs from one pinned image (D-05) through two short scripts,
so a listing or a binary made today is made the same way next month.

## Tasks

- [ ] `tools/dev/toolchain.sh`, sourced by every script: the pinned image
      (`logronoide/atarist-toolkit-docker-x86_64:1.4.0`) and a `docker run` helper that mounts
      the repository at `/work`. `stcmd` is not used: it follows `latest`.
- [ ] Check that `1.4.0` carries `vasmm68k_mot`, `vlink` and `m68k-atari-mint-objdump`, with
      their versions recorded here. If it lacks vasm, record the choice made (D-05).
- [ ] `tools/dev/disasm.sh <bin> <vma> <out>`: a raw binary disassembled for the 68000 at a
      given load address, into a listing.
- [ ] `tools/dev/asm.sh <source.s> <out.bin>`: vasm Motorola syntax to a raw binary, with no
      optimisation (`-no-opt`), so every instruction keeps the encoding it was written with.
- [ ] Both scripts refuse to start without Docker or the image, and say so.

## Acceptance

`tools/dev/disasm.sh` gives the same listing as the first pass's
`_archive/2026-04-first-pass/src/disasm/ls2dd.raw.asm` for its `ls2dd.bin` at `0x70000`, apart
from the file path in the header line; a three-instruction source assembled by
`tools/dev/asm.sh` and disassembled back shows the same three instructions.

## Notes
