---
id: EPIC-11
iteration: 2
title: The release gate
status: in-progress
---

## Goal

The project released: the repository cleaned and made public (D-15), the website published, and the
release marked. Asked by Diego, 2026-10-26 (D-24); the last epic of iteration 2.

## Scope

To be written with Diego when the epic starts. What is known:

- D-15's clean-up: `LEMMINGS/` and the first pass's binaries in `_archive/` removed from the
  repository and its history (`docs/publication/remove.txt`), checked by
  `tools/site/check_public.py` on a clone.
- The public repository and its remote, on Diego's word (no push until then). Diego, 2026-10-26:
  "the current local git repo we must change the name to gemdrive-games-patches (or reword for
  better english) and created in https://github.com/sidecartridge". The name, Diego, 2026-10-26:
  **`gemdrive-game-patches`** (D-26), `https://github.com/sidecartridge/gemdrive-game-patches`.
  The local folder and the docs that name the repository follow.
- The website published at https://gemdrive.sidecartridge.com/ (`CNAME`, Diego, 2026-10-26;
  GitHub Pages); the snapshots published, the site built on this Mac and
  pushed to `gh-pages` (D-28).
- Every check passing on the clean clone: `tools/dev/all_harness.sh`, `build_site.py --check`.

## Setups

A clean clone of the repository; the published site in Chrome, Safari and Firefox.

## Stories

- STORY-01, the clean-up: what leaves the history, decided (D-25), and a cleaned clone that
  `check_public.py` passes.
- The others written as the epic goes, ending with Diego's checkpoint: the release.

## Notes
