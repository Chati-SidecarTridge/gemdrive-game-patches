---
id: STORY-07
epic: EPIC-03
title: The website: the documentation and the catalogue, for the internet
status: todo
---

## Goal

Everything this project documents, published as a website with the repository: the story of the
work (why Lemmings fails from a GEMDOS drive, PP's launcher, its disk layer), PP's modes and
strategies, the catalogue of his adaptations with each game's strategy and verdict, and the
solutions proposed. Designed with the frontend-design skill. Asked by Diego, 2026-10-11.

## Tasks

- [ ] The design, with the frontend-design skill: the site's look, its pages and its navigation
      (the project, the findings, PP's modes, the catalogue, the strategies and solutions, the
      tools), and the catalogue's table: searchable and filterable by strategy, verdict, PP's
      category, RAM and machine, each game linking to its page on PP's site.
- [ ] `tools/site/build_site.py` (standard library, D-05) builds the site into the git-ignored
      `tools/dev/builds/site/` from what the repository holds: the notes in `src/notes/`, the
      tables in `src/survey/`, the backlog's state. No external services or CDNs: it works from a
      file folder and from GitHub Pages alike.
- [ ] What goes on the site is the project's own work: PP credited and linked on every page that
      uses his material, his files and pages never copied (D-11), no TOS code (D-13), no game
      files. Images are this project's own Hatari screenshots, or none; which ones is Diego's call.
- [ ] Checks: every internal link resolves, every game of `migration.csv` has its row, the site
      builds from a fresh clone; `tools/dev/all_harness.sh` builds it.
- [ ] Publication prepared, not done (D-15): the list of what has to leave the repository and its
      history before it goes public (`LEMMINGS/`, `_archive/`'s binaries, anything else found), a
      script that checks a clone against it, and the GitHub Pages settings the site needs.
- [ ] Every game's page or row shows its snapshot from STORY-05 (`run_all.py` copies each run's
      last screen, taken just before Hatari quits, to `tools/dev/builds/survey/snapshots/`), with
      the run's verdict. Asked by Diego, 2026-10-11.

## Acceptance

The site, built from a fresh clone by one command, opened from its folder on this Mac: every page
and every game reachable, nothing of PP's or Atari's in it but links and credits, and the
removal list of D-15 ready.

## Notes

The snapshots are this project's own captures, but they show the games' screens: whether they are
published with the site is part of the D-15 review before going public (Diego's call); until then
they are git-ignored, under `tools/dev/builds/survey/snapshots/`.

