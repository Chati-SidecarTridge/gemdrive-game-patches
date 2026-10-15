---
id: STORY-02
epic: EPIC-04
title: The reference's first level: the address error at $2B10
status: todo
---

## Goal

Know why Lemmings, booted from the PPDRIVER image in Hatari, raises an address error after
loading `LEVEL020`, and get past it, because Lemmings' play session (STORY-03) needs a first
level. This is the candidate found in EPIC-01 STORY-01 (`ITERATIONS.md`).

## Tasks

- [ ] The error again, on ST TOS 1.04 and STE TOS 2.06 from PPDRIVER: `$2B10`,
      `move.l (a0)+,(a1)+`, with `a0 = $3E409` taken from `($36,a3)`.
- [ ] Where `($36,a3)` gets its odd value: the game's code, PP's patches to it (EPIC-02 STORY-04),
      or Hatari. Traced back from the load.
- [ ] What gets past it without changing Hatari (C-02), and its cost; or, if it is Hatari's, the
      evidence for a report (which waits for Diego, D-15).
- [ ] The first level reached from PPDRIVER, and then from the GEMDOS drive with STORY-01's build.

## Acceptance

Lemmings reaches its first level in Hatari from both disks, or the cause is shown in a trace and
Diego decides what to do next.

## Notes
