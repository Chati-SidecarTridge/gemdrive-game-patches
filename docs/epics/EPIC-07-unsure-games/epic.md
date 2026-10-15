---
id: EPIC-07
iteration: 2
title: The unsure games settled (UNSURE, Little Puff in Dragonland first)
status: todo
---

## Goal

Each of the ten games in the card's `UNSURE` folder gets a cause and a verdict: **fix**, with the
fix built and run here, or **not feasible**, with the reason. They fail from Hatari's GEMDOS drive
and, by Diego's test (2026-10-15), from the Multidevice's too. EPIC-03 did not find out why
(`hd-strategies.md` §3.6). Little Puff in Dragonland is the first test game: it runs from
PPDRIVER and fails only from the GEMDOS drive, so a trace of each run should show the difference.
Chosen by Diego, 2026-10-15 (D-16). The not-feasible game, Great Giana Sisters STE (`NOFIX`),
stays out.

## Scope

- In scope:
  - The three games that fail only from the GEMDOS drive: Super Breakout mono, 9 Lives and Little
    Puff in Dragonland, all HAGA.
  - The six that fail from PPDRIVER too: Lords of Doom, Substation, Roger, Zero-5, Spitting Images
    and Utopos. Is it Hatari, PP's files, or the machine?
  - Ice and Fire, which has only floppy images, run with a virtual floppy driver from the GEMDOS
    drive.
  - Each game's fix, if it has one, built, run and handed to the user like EPIC-06's. Then the
    verdicts, the card and the site.
- Out of scope:
  - A change to Hatari (C-02).
  - Great Giana Sisters STE.

## Setups

As EPIC-04: Hatari's three setups, in GEMDRIVE mode and from PPDRIVER, at more RAM where a game
asks for it. At the checkpoint, Diego's Multidevice, from a card.

## Stories

- STORY-01: The three that fail only from the GEMDOS drive (Little Puff in Dragonland first)
- STORY-02: The six that fail from PPDRIVER too
- STORY-03: Ice and Fire from floppy images
- STORY-04: The fixes, the verdicts, the card and the site
- STORY-05: Verification (Diego's checkpoint)

## Notes
