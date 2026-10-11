---
id: EPIC-02
iteration: 1
title: The PPera launcher reverse engineered and recompilable, tested with our own build
status: done
---

## Goal

Every PPera launcher program as sources in this repository that reassemble to the original bytes,
and a build that turns them back into launcher files. Run in Hatari, our build starts the game
exactly as the originals do. From then on the launcher is code we can change and test, which
iteration 2's solutions need (D-14), and its signatures are known, which EPIC-03's survey of PP's other adaptations
needs. Asked by Diego, 2026-10-11.

## Scope

- In scope: every program in the launch chain: `START.TOS` and what it unpacks, `LEMMINGS.PCH`,
  `LS2DD.FIC`, `D15R_H5.FIC` (the loader D15R, PP's modded GEMDOS if H-08 holds) and
  `D15R_F5.FIC`, with `GXUT260.PRG` included if the launch depends on it. Also the launcher's
  handling of PP's resident driver, which EPIC-01 found it copies and patches rather than carrying
  a driver of its own. Then our unpackers and packers; vasm sources (D-05) that pass the round-trip
  check (EPIC-00 STORY-03); a build of the launcher files from those sources; and the game booted
  from our build in Hatari.
- Out of scope: PPDRIVER itself beyond the interface the launcher uses (it is `../atari-hd`'s blob,
  C-03); the game's own code (`FILES/CODE`, `FILES/MAIN`) beyond where the launcher hands over; any
  change in behaviour (iteration 2).

## Setups

Hatari: the PPDRIVER reference of EPIC-01 STORY-01 on every setup, for the originals and for our
build, up to the level load of `tools/dev/expect/reference-first-level.exp`. The game itself
stops after "1 PLAYER" in Hatari, on the reference too (EPIC-01 STORY-01). GEMDRIVE runs are only
to show that our build fails the same way as the original.

## Stories

- STORY-01: The launch chain mapped from runs
- STORY-02: Unpackers, proven against Hatari's memory
- STORY-03: A packer the launcher accepts
- STORY-04: Sources for every stage that reassemble
- STORY-05: The disk layer: D15R and the driver it uses, annotated
- STORY-06: Our own launcher build boots the game
- STORY-07: Verification (Diego's checkpoint)

## Notes

Tests H-01, H-02, H-05 and H-08 (`ITERATIONS.md`). The first pass's decoders
(`_archive/2026-04-first-pass/src/tools/`) may be reused once a story has checked them against
Hatari's memory (D-01). Its notes disagree with its own decoder on the LZSS match lengths (+2/+3
in `start_tos.md`, +3/+4 in `depack_start_tos.py`); the memory dump settles it.

What EPIC-01 left for this epic (`src/notes/gemdrive-failure.md` §3-5): the stage addresses (LS2DD
staged at `$81000`, its depacker at `$80100`, unpacked to `$70000`, entered at `$7005A`; D15R at
`$C0100`); the PPHD gate at text+$324 and its fallbacks; the copy of the resident driver to
`$B7180` and the offsets patched in it; `$84` pointing to D15R's `TRAP #1` handler at `$C84A0`.

PP's own material (D-11: cited by URL, never copied here; a name taken from it is used only once
our bytes confirm it):

- `GAMEXdoc.html` describes the Gamex launch with GOS5 step by step: lower phystop, save the TOS
  state, load and depack the packed GOS5, install the hard-disk driver in high RAM (with his own
  driver, just a copy, since it is PC-relative), load the game, and send its floppy requests to the
  modded GEMDOS's file I/O. That RAM map matches EPIC-01's addresses (H-08).
- `GamexLSrc.html`, `GamexLSrc2.html` and `GamexLSrc3.html`: his commented sources (2009) of three
  Gamex launchers of the same family (Castle Master, Sideways, Starglider). The third loads
  `D15R_NG1.FIC`, "Packed GEMDOS, GOS 1.00". They are a guide to structure and names for
  STORY-04, not Lemmings' code.
- If H-08 holds, the TOS 1.04 ROM on this Mac (C-03) holds the unmodified GEMDOS 0.15. D15R's
  source can then start from a disassembly of the ROM's GEMDOS, and its differences are PP's
  changes.

**Done 2026-10-11.** All seven stories done; Diego agreed at the checkpoint (STORY-07). Five
sources in `src/` (`start`, `lemld2`, `ls2dd`, `d15r_h5`, `d15r_f5`), made from their maps by
`tools/dev/mksource.py`, reassemble to PP's bytes and pass a `nop` check;
`tools/build_launcher.sh` builds the launcher from them, and it boots the reference to the level
load with PP's exact disk calls on all three setups. Notes: `src/notes/launch-chain.md`,
`launcher-formats.md`, `disk-layer.md`, `launcher-signatures.md`. H-01, H-02, H-05 confirmed (H-05
with a correction), H-08 confirmed and wider: D15R is TOS 1.04 in RAM. D15R's sources are made
from their maps and not committed (D-13). Committed on `epic-02-recompilable-launcher`, cut from
`main` (`7fcff84`), and merged into `main` at Diego's word.
