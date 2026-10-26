---
id: STORY-01
epic: EPIC-11
title: The clean-up: what leaves the history, and a cleaned clone
status: done
---

## Goal

D-15's clean-up. Diego, 2026-10-26: "show me what you want to delete", then, on the list and its
recommendations, "go with your recommendations" (D-25).

## Tasks

- [x] The list shown to Diego: what each entry of `docs/publication/remove.txt` matches now and in
      the history (38 commits): `LEMMINGS/` 76 files, `_archive/` 54 (of them PP's patched
      `START.TOS`, 27 unpacked stages, D15R's disassembly), the three launcher sources; the only
      other binaries, the two logos.
- [x] `remove.txt`: every entry `must` (`LEMMINGS/`, `_archive/`, `src/start/*.s`,
      `src/lemld2/*.s`, `src/ls2dd/*.s`, `src/d15r/*.s`), and `keep` for the logos;
      `check_public.py` reads `keep` as a binary allowed in the history.
- [x] `LEMMINGS/`, `_archive/` and the three launcher sources git-ignored and untracked, still on
      disk (`shasum -a 256 -c LEMMINGS.sha256`: 76 OK); `DESKTOP.INF` removed from the root (the
      same bytes as `tools/dev/DESKTOP.INF`).
- [x] `tools/make_sources.sh` makes all five stages from their maps; the three it now makes are
      byte for byte the files that were committed. `build_launcher.sh` and `build_gemdrive.sh`
      call it when a source is missing.
- [x] Setup for a new clone (`tools/dev/README.md`): the user's own `LEMMINGS.ZIP` unpacked as
      `LEMMINGS/`. Checked: the mirror's `LEMMINGS.ZIP` unpacks to `LEMMINGS/` and matches all 76
      hashes.
- [x] `CLAUDE.md`, `README.md`, `src/notes/launch-chain.md`, `docs/publication/README.md` say so.
- [x] `docs/publication/clean_history.sh <out>`: a clone with every branch, the must paths taken
      out of every commit (`git filter-branch`, which comes with git), the old refs and objects
      dropped. Rehearsed on `main` (`tools/dev/builds/public/rehearsal-1`): 38 commits, 210
      files; `check_public.py`: "ready to go public"; none of the 133 removed files' blobs left in
      the clone; `.git` 1.6 MB.
- [x] `tools/dev/all_harness.sh` with the sources made from the maps: 0 failures (363 s).
- [x] Committed on `epic-11-release-gate` (Diego's word, `dfff783`), then the cleaned clone made
      from it (`tools/dev/builds/public/clean`): 39 commits, 11 branches, 211 files;
      `check_public.py`: "ready to go public"; 0 of the 133 removed files' blobs left.
- [x] Every check in the clean clone, set up as a new user would: `dev.cfg`, and the mirror's
      `LEMMINGS.ZIP` unpacked as `LEMMINGS/` (76 hashes OK, `git status` clean);
      `tools/make_sources.sh` made the five sources; `tools/dev/all_harness.sh`: 0 failures
      (760 s).
- [x] The repository's name, Diego: `gemdrive-game-patches` (D-26).

## Notes

- The commits carry Diego's name and Gmail address; the rewrite keeps them unless Diego asks.
- `docs/publication/README.md`'s GitHub Pages section predates the custom domain (`CNAME`) and the
  analytics: for the publishing story.
