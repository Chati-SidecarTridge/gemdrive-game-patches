---
id: STORY-03
epic: EPIC-09
title: The program
status: todo
---

## Goal

The program of STORY-01's design: given a folder, it finds the start files, checks each by
signature, replaces the ones it knows with our builds, and says what it did.

## Tasks

- [ ] A known original: replaced, and kept beside it so that the program can put it back.
- [ ] An unknown file, or one that is neither the original nor our build: left as it is, and said.
- [ ] Run twice, it changes nothing the second time; undo gives back the originals byte for byte.
- [ ] A folder in the card's layout (`tools/survey/sdcard.py`) and a download's folder.

## Acceptance

On a copy of the card, every known game replaced, the rest untouched, and undo gives back the card.

## Notes
