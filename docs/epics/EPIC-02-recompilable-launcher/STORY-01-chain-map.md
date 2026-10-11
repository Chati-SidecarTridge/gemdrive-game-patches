---
id: STORY-01
epic: EPIC-02
title: The launch chain mapped from runs
status: done
---

## Goal

Which program loads which, where it is placed in memory, where it is entered, and what it leaves
resident, from the reference run, with a memory dump of every stage as it starts.

## Tasks

- [x] From the reference run's traces and breakpoints: every file the launcher opens, by whom,
      where it lands, and where each stage is entered, starting from EPIC-01's addresses.
- [x] A Hatari memory dump of every stage at its entry (harness debugger hook), SHA-256 recorded.
- [x] The hand-over to the game: the address, and what the launcher left resident (vectors, system
      variables, D15R, the relocated driver, and the memory it reserved), set against GOS5's RAM
      map in `GAMEXdoc.html`.
- [x] `D15R_F5.FIC`: the reference opens `D15R_H5.FIC` (EPIC-01). What the other file is, and what
      would make the launcher choose it.
- [x] `GXUT260.PRG`: PP's documentation describes the Gamex utility as the program that resumes,
      saves and restores gamestates (`GAMEXdoc.html`). This is to be confirmed from a run on a copy
      of the disk setup (any write lands on the copy only, C-01), together with whether the launch
      depends on it. If it does not, it leaves this epic's scope, recorded here.

## Acceptance

The chain recorded here as a table (stage, file, load address, entry, dump SHA-256), each row
backed by a run folder.

## Notes

**Done 2026-10-11.** `src/probes/epic02/chain_probe.py <setup>` puts a breakpoint on each stage's
entry and dumps it (`savebin`) on the PPDRIVER reference, then runs `reference-first-level.exp`:
PASS on ST TOS 1.04 (`20261011-165409-st-104-ppdriver-chain`, and `…-165111-…`, the same bytes),
STE TOS 1.62 (`…-165131-ste-162-ppdriver-chain`) and STE TOS 2.06 (`…-165151-ste-206-ppdriver-chain`).
B is the program's text base: `$17A88` (ST 1.04), `$17A68` (STE 1.62), `$1D2E4` (STE 2.06).

| stage | file | loaded by, to | entry | dump at entry, SHA-256 (ST 1.04) |
| --- | --- | --- | --- | --- |
| stub | `START.TOS`, 230-byte text + 8,844-byte data | TOS `Pexec`, B | B | `stub.bin` `a8d1f869…77d9`, equal to the file's bytes 28-9,101; the same on all three |
| LEMLD2 | packed in `START.TOS`'s data, after a 32-byte `C3` header naming `LEMLD2.TOS` | the stub: unpacked to B−28 (a GEMDOS header: text `$885E`, data 0, BSS `$1B046`), relocated to B, its BSS cleared | B, from the stub's copy of itself at B+`$8D40` (`jmp (a0)` at B+`$8DF2`) | `lemld2.bin` (header + text) `1ce3abf2…393e`; relocated, so it differs per setup |
| pictures | `LEMMINGS.PCH`, 102,470 bytes | LEMLD2's `Fread`s: 6 → `$3BE66`, 32,000 → `$34100`, 19,232 → `$22C1A`, 32,000 → `$2C300`, 19,232 → `$2773A` | data | – |
| D15R | `D15R_H5.FIC` | LEMLD2 reads up to 51,000 bytes into its BSS (B+`$885E`) and unpacks from +32 to `$C0100` (91,460 bytes) | `$C0100` + the word at `$C0106` = `$C02BC`, called from text+`$5E6` after LEMLD2 saved `$472`, `$476`, `$47E`, `$4B2`, `$4B6`, `$516`, `$5A0` into D15R's area | `d15r.bin` `c1d61923…7ca1`; the same on all three |
| block | LEMLD2 text+`$604`, 1,600 bytes, with the machine (TOS version `01 04`/`02 06`, machine type) written at +`$22E`..+`$235` | LEMLD2, to `$80100`, interrupts off | `$80100` | `block.bin` `03de581a…4715`; differs per setup by those bytes and two relocated longs (+`$5AE`, +`$5C4`) |
| LS2DD | `LS2DD.FIC`, 4,929 bytes | LEMLD2's `Fread` to `$81000` (the dump equals the file); the block unpacks `$81020` → `$70000`, 7,168 bytes, and patches it: `jmp $85000` at `$70E38`, the long `$8014C` at `$70A8E` | `$7005A` | `ls2dd.bin` `3faf11b6…0446`; the same on all three |
| loader | block+`$30E`: 818 bytes of the block and the 86 zero bytes after it | the block, to `$85000` (904 bytes) | through LS2DD's patch at `$70E38`; first entered before D15R's first sector read | `loader.bin` `dfe46fb1…be75`; differs per setup only at +`$2A0`/+`$2B6` (relocated LEMLD2 addresses) |
| game | `FILES/MAIN` (ICE-packed), read by D15R by sectors to `$A00` (EPIC-01 §2) | LS2DD, through the loader and D15R | `$400`, from block+`$4C` (`$8014C`), which patches MAIN (`jmp $85000` at `$2C24`, hooks at `$2B96`, `$2BBE`, `$2C00`) and ends in `jmp $400` | `game-handover.bin` (`$A00`-`$5FFFF`) `5e0123d0…24c5` |

Every file the launcher opens itself, in order (`hatari.out`, GEMDOS trace): `LEMMINGS.PCH`,
`D15R_H5.FIC`, `LS2DD.FIC`, then `Dsetpath("FILES")` and `Dgetpath` into D15R's area
(`$C0760`). From then on everything is D15R's sector reads (EPIC-01 §2). After MAIN starts, the
block's other entries handle the rest: +`$80` patches the intro at `$10204` and jumps to
`$10000`; +`$A2`/+`$B6` ask the loader for `"CODE"` and go back into LS2DD (`$70030`/`$70032`);
+`$D0` patches CODE (the loader copied into the game at `$E892`, `jmp`s at `$22D8`, `$4074`,
`$21BE`, bytes at `$D89B`, `$3F47`, …): PP's changes to the game. (These offsets were first
written here as +`$6C`, +`$8E`/+`$A2` and +`$BC`; STORY-04's source corrected them.)

**What is resident at the hand-over** (`lowmem-*.bin`, `high-handover.bin`), set against GOS5's
RAM map in `GAMEXdoc.html`:

- `phystop` is `$80000` and `_memtop` `$78000` already at LS2DD's entry: the machine is cut to
  512 KB for the game, as Gamex does for "games working with 512KB".
- 700-768 KB, "hard disk driver, buffers": the driver copy at `$B7180` (`"XBRA" "PPHD"`, its old
  vector `$C19BE` in D15R) and the buffers from `$AF100` (pages `$AF000`-`$B8FFF` in use).
- 768-860 KB, "modded GEMDOS" and its workspace: D15R, `$C0100`-`$D6543`, starting with a table of
  entry offsets (`$10`, `$34`, `$70`, `$1BC`, `$1CA`).
- 860 KB-1 MB, "space for storing TOS state": D15R's init copies 24 bytes from `$FFFAA`.
- Vectors at the hand-over: bus error `$8` → `$700A0` and VBL `$70` → `$70A92` (both LS2DD's); the
  game then puts its own VBL in (`$2AD6`). `TRAP #1` (`$84`) is Hatari's cartridge `$FA002A` at
  every stop, and `hdv_bpb` is still the resident driver's `$12960` at LS2DD's entry. EPIC-01 saw
  `$84` = `$C84A0` and the copy's entries in `$472`… during the first `Rwabs`. So D15R puts
  its vectors in for a disk call and takes them out again, as PP describes ("storing CPU, MFP
  state, and set correct values for GEMDOS and execute file I/O. After it restoring"). STORY-05
  follows that.

**`D15R_F5.FIC` is the Falcon build.** LEMLD2 opens `D15R_H5.FIC` when the byte at text+`$A06` is
0 and `D15R_F5.FIC` when it is not; failing that, the same name in `C:\GAMEX\`, then the message
"Proper D15R_*.FIC file in it's DIR". The only writer of that byte is the Falcon branch of its
machine detection (text+`$10AE`: machine code 4, reads `$FFFF8006`, writes the Falcon bus
register `$FFFF8007`, sets up the 68030 MMU with `pmove`). Every ST and STE run opened
`D15R_H5.FIC`.

**`GXUT260.PRG` is not part of the launch.** Started on its own (`--start
C:\LEMMINGS\GXUT260.PRG`, runs `…-165007-st-104-ppdriver-gxut` and `…-165016-st-104-gemdrive-gxut`),
it shows a GEM dialog: "GAMEX-utility for gamestate store, playing stored gamestates, V 0.9, By
P. Putnik 2011", with Enter notes, Save current state, Play saved gamestate, Play game in RAM, Show
info, Free RAM and Exit. It works in both disk modes. No launch opens it, so it leaves this epic's
scope; it matters again for saved gamestates (EPIC-03, iteration 2).

Found on the way: `LEVELDAT` is read at the title in every reference run, before any click. EPIC-01
had it after the click, and `reference-first-level.exp` passed only by timing; this story moved it
before the title step and corrected EPIC-01's note. The harness gained `--start <path>`.
