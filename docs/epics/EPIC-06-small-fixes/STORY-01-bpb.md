---
id: STORY-01
epic: EPIC-06
title: S2: a BPB for the GEMDOS drive (Crystals of Arborea first)
status: todo
---

## Goal

A resident program, run from `C:\AUTO\`, makes the four Silmarils games run from the GEMDOS drive.

## Tasks

- [ ] The program, in vasm source (D-05). It hooks `hdv_bpb` with XBRA. For the GEMDOS drive's
      number it returns an 18-byte BPB, and for any other drive it chains to the routine before
      it, as the trial's 22-byte routine did (`hd-strategies.md` §3.2). It stays resident in
      about 100 bytes.
- [ ] Crystals of Arborea from the GEMDOS drive with the program in `C:\AUTO\`, on the three
      setups: it plays, with no `Rwabs` on C: and its files opened by name.
- [ ] Targhan, Robinsons Requiem and Storm Master, the same.
- [ ] A game that does not need the program (a HAGA game) still runs with the program installed.

## Acceptance

The four games run from the GEMDOS drive with the program, on the three setups.

## Notes
