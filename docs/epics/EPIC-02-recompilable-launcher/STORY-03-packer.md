---
id: STORY-03
epic: EPIC-02
title: A packer the launcher accepts
status: todo
---

## Goal

`tools/pack.py` turns an unpacked stage back into a launcher file that the original launcher code
unpacks correctly, so a stage rebuilt from source can go back on the disk.

## Tasks

- [ ] `tools/pack.py` for each packed format, standard library only.
- [ ] Round trip on the host: `unpack(pack(x)) == x` for every stage.
- [ ] Round trip in Hatari: the original files with one stage replaced by its repacked copy boot
      the reference to the level load (`reference-first-level.exp`); the dump at that stage's entry equals the original's.
- [ ] Sizes before and after for every repacked file. Byte-identical packed files are not
      required, since PP's packer is unknown; the same unpacked bytes are.

## Acceptance

Every stage repacked by our packer boots in the reference with the same memory as the original.

## Notes
