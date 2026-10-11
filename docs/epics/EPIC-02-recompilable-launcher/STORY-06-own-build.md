---
id: STORY-06
epic: EPIC-02
title: Our own launcher build boots the game
status: todo
---

## Goal

One command builds the launcher files from our sources, and the game boots from them in Hatari
exactly as from the originals.

## Tasks

- [ ] `tools/build_launcher.sh`: assembles every stage (`tools/dev/asm.sh`), packs them
      (`tools/pack.py`) and writes the launcher files into a disk tree under
      `tools/dev/builds/`, next to a copy of `FILES/`.
- [ ] Our build boots the PPDRIVER reference to the level load on every setup, with the same
      milestones and the same disk calls as the originals (`reference-first-level.exp`).
- [ ] Our build in GEMDRIVE mode stops where the original stops (EPIC-01 STORY-02).
- [ ] Proof it is ours: a visible change in one source (for example a text on the launcher's
      screen) appears in the run, and reverting it restores the original bytes.
- [ ] Added to `tools/dev/all_harness.sh`.

## Acceptance

`tools/dev/all_harness.sh` builds the launcher from source and boots the game from it on every
reference setup, PASS.

## Notes
