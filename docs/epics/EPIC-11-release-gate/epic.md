---
id: EPIC-11
iteration: 2
title: The release gate
status: todo
---

## Goal

The project released: the repository cleaned and made public (D-15), the website published, and the
release marked. Asked by Diego, 2026-10-26 (D-24); the last epic of iteration 2.

## Scope

To be written with Diego when the epic starts. What is known:

- D-15's clean-up: `LEMMINGS/` and the first pass's binaries in `_archive/` removed from the
  repository and its history (`docs/publication/remove.txt`), checked by
  `tools/site/check_public.py` on a clone.
- The public repository and its remote, on Diego's word (no push until then).
- The website published (`docs/publication/site.yml`, GitHub Pages, prepared, not in use); whether
  the snapshots are published (D-15, Diego's call).
- Every check passing on the clean clone: `tools/dev/all_harness.sh`, `build_site.py --check`.

## Setups

A clean clone of the repository; the published site in Chrome, Safari and Firefox.

## Stories

Written when the epic starts, ending with Diego's checkpoint: the release.

## Notes
