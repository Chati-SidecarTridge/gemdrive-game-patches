---
id: STORY-06
epic: EPIC-04
title: The instructions, the card and the site
status: todo
---

## Goal

A user can patch their own copy of a GOS5 game and run it from a GEMDOS drive. Diego's test card
and the website show the result.

## Tasks

- [ ] A README a user can follow on a fresh copy: what the patch changes, how to run the tool,
      and how to undo it.
- [ ] `tools/survey/sdcard.py`: the card holds the patched GOS5 games, under the verdict they
      have now.
- [ ] The site: the GOS5 band, the catalogue's verdicts, and the solution's page updated.
      `build_site.py --check` passes.

## Acceptance

The README, followed on a fresh copy of a GOS5 game, gives a game that runs from the GEMDOS
drive. The card and the site show the new verdicts.

## Notes
