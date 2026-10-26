---
id: STORY-02
epic: EPIC-11
title: The repository on GitHub, private until the release
status: done
---

## Goal

The cleaned working copy pushed to `https://github.com/sidecartridge/gemdrive-game-patches`.
Diego, 2026-10-26: private until the release, every branch, the author's address kept (D-27).

## Tasks

- [x] `gh repo create sidecartridge/gemdrive-game-patches --private`; `origin` added, `main` and
      every branch pushed (11: `main` and the ten epic branches); `main` is the default branch.
- [x] A mirror clone of the remote has the same 11 branch heads as the working copy.
- [x] `check_public.py` on a clone of the remote: "ready to go public" (234 paths in the history
      of every branch; site check, 1831 of 1831 games, 0 problems).
- [x] `CLAUDE.md`'s push rule says so.

## Notes

- Made public at the release, with the site (a story to come).
