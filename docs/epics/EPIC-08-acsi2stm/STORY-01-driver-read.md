---
id: STORY-01
epic: EPIC-08
title: acsi2stm's GemDrive read: what a call does on the ST
status: todo
---

## Goal

The eight points of the epic answered from acsi2stm's code at the release tested: what the stub
does on the ST during a file call, where it lives, what it reads and writes, and how deep it goes
on the caller's stack. Each answer says what our builds have to do about it.

## Tasks

- [ ] The release and commit to test, and Diego's unit: which ACSI2STM, which firmware (DMA or PIO),
      boot sector or `AUTO` program.
- [ ] The stub's layout in both variants (the boot sector's 456 bytes, the resident program with its
      handlers in the basepage): what a copy elsewhere needs, and that the STM32 keeps no address
      of it.
- [ ] Per file function gd_forward hands on (`Dsetpath`, `Fopen`, `Fread`, `Fseek`, `Fclose`,
      `Fcreate`, `Fwrite`, `Fdelete`, `Dgetpath`): the STM32's commands, the memory it reads (the
      basepage at `p_run`, low RAM), the stack it uses, its own `TRAP #1` calls.
- [ ] How the STM32 picks the drive of a name with no drive letter (the current drive it keeps,
      `Dsetdrv`), against GOS, which keeps its own.
- [ ] The answers in `src/notes/` (a note on acsi2stm's GemDrive beside `gemdrive-failure.md`),
      citing acsi2stm by URL, file and commit.

## Acceptance

The note answers the eight points, each with what our builds have to do.

## Notes
