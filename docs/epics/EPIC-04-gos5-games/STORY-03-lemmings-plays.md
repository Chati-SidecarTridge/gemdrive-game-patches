---
id: STORY-03
epic: EPIC-04
title: Lemmings plays from the GEMDOS drive
status: done
---

## Goal

A scripted play session of Lemmings from the GEMDOS drive on the three setups, with every file it
opens found in the trace. This is what was the Lemmings fix's acceptance (D-14, kept in git at
`7fcff84`).

## Tasks

- [x] Lemmings played, for a long time, on Diego's STE (TOS 1.62, 4 MB) from the Multidevice's
      GEMDRIVE, with the build of `START.TOS` `27c534e8…` (Diego, 2026-10-15).
- [x] In Hatari from the GEMDOS drive (STE TOS 1.62, 4 MB): level 1 ("Just dig!") entered from the
      title and played to its end ("Your time is up!"), every file in the trace (`level018`,
      `objects1`, `ground1`, `mountain`), no `Rwabs`, no crash.
- [x] From PPDRIVER: PP's own launcher stops at the first level (STORY-02), and stays so (D-17).

## Acceptance

The session passes on the three setups from the GEMDOS drive and from PPDRIVER, with its
screenshots and traces.

## Notes

### Closed on Diego's play (2026-10-15)

Diego: "i have been testing the game playing for a long time and it works in physical with
multidevice. move on." The scripted session first planned (a level to its end, the next one, a
level of each section entered by its code, the music changing; an expectation file) was not built.
What the exploration found, for whoever scripts it (`tools/dev/builds/epic04/session-1925/`):

- "1 PLAYER" is at the harness's `mouse 25 150` on the title; one more click starts the level after
  its preview. With no input, level 1 runs to "Your time is up!" in about 20 s of Hatari's time
  ("Press left button to try again, right button for menu").
- In a level, the pointer is drawn at about the mouse position + (8, 6), and the IKBD keeps y at
  most 155: the skill panel (screen y 176 to 198) is out of the `mouse` step's reach. F10
  (scan code `$44`) does not select the digger. Reaching the panel, or the key that selects a skill,
  is still to be found.

