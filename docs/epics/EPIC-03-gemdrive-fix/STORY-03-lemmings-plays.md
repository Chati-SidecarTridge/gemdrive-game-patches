---
id: STORY-03
epic: EPIC-03
title: Lemmings plays in GEMDRIVE mode
status: todo
---

## Goal

The game keeps working after the first level: everything it loads during play comes through the
fix.

## Tasks

- [ ] A scripted session in GEMDRIVE mode: a level played to its end, the next one loaded, a level
      of each of the four sections entered by number (`README.TXT`), and the music changing.
- [ ] Every file the game opens during that session found in the trace, with no failed access.
- [ ] The same session run from the PPDRIVER reference, for comparison.

## Acceptance

The scripted session PASS in GEMDRIVE mode on every setup, with no failed disk access in its trace.

## Notes
