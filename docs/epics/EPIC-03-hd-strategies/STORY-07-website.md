---
id: STORY-07
epic: EPIC-03
title: The website: the documentation and the catalogue, for the internet
status: done
---

## Goal

Everything this project documents, published as a website with the repository: the story of the
work (why Lemmings fails from a GEMDOS drive, PP's launcher, its disk layer), PP's modes and
strategies, the catalogue of his adaptations with each game's strategy and verdict, and the
solutions proposed. Designed with the frontend-design skill. Asked by Diego, 2026-10-11.

## Tasks

- [x] The design, with the frontend-design skill: the site's look, its pages and its navigation
      (the project, the findings, PP's modes, the catalogue, the strategies and solutions, the
      tools), and the catalogue's table: searchable and filterable by strategy, verdict, PP's
      category, RAM and machine, each game linking to its page on PP's site.
- [x] `tools/site/build_site.py` (standard library, D-05) builds the site into the git-ignored
      `tools/dev/builds/site/` from what the repository holds: the notes in `src/notes/`, the
      tables in `src/survey/`, the backlog's state. No external services or CDNs: it works from a
      file folder and from GitHub Pages alike.
- [x] What goes on the site is the project's own work: PP credited and linked on every page that
      uses his material, his files and pages never copied (D-11), no TOS code (D-13), no game
      files. Images are this project's own Hatari screenshots, or none; which ones is Diego's call.
- [x] Checks: every internal link resolves, every game of `migration.csv` has its row, the site
      builds from a fresh clone; `tools/dev/all_harness.sh` builds it.
- [x] Publication prepared, not done (D-15): the list of what has to leave the repository and its
      history before it goes public (`LEMMINGS/`, `_archive/`'s binaries, anything else found), a
      script that checks a clone against it, and the GitHub Pages settings the site needs.
- [x] Every game's page or row shows its snapshot from STORY-05 (`run_all.py` copies each run's
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

### Done (2026-10-13)

`python3 tools/site/build_site.py`, then open `tools/dev/builds/site/index.html`.

**The design** (frontend-design skill). The plan, kept for the next pass:

- The one picture is the data: on the home page every game is a square, in a band per strategy,
  coloured by verdict, the bands read in one after the other when the page loads (not with
  reduced motion). The GOS4 and GOS5 bands are the solid amber ones: the finding at a glance.
  A square links to the game's row; a band to the catalogue filtered on its strategy.
- Colours the STE could show (each channel a multiple of `0x11`): paper `#FFFFFF`, ink `#000000`,
  grey `#444444`, rules `#BBBBBB`, code `#EEEEEE`, links `#0000AA`; as it is `#008844`, fix
  `#FFAA00`, not feasible `#CC2211`, unsure an outlined square (told apart by fill as well as hue).
- Type from the system, no font files and no CDN: DIN (`DIN Alternate`, Bahnschrift) for headings,
  Charter for the text, the system's monospace for code.
- The top bar is GEM's menu bar: the current section shown selected, in reverse. The section's
  pages and the page's headings are in a rail beside the text, above it on narrow screens.
- Reviewed in screenshots from headless Chrome at 1440, 1100 and 900 pixels, and at 375 inside
  an iframe (headless Chrome keeps windows 500 pixels wide or more).

**The pages** (11): the project (the map, why some games do not run, the solutions, the epics and
their tasks from `docs/epics/`), the five findings of EPIC-01 and EPIC-02, PP's modes, the verdicts
and solutions with the strategies, the catalogue, and the tools (`tools/dev/README.md` and every
script's docstring). The notes are rendered by the builder's own Markdown (the subset they use); a
note named in another (`strategies.md`) links to its page, a page of PP's (`agcat.html`) to his
site.

**The catalogue**: one row per game of `migration.csv` (`id` `g-0695` for row 695), with its
snapshot (1,814 games; the 17 others halted before Hatari took a screen), its name linking to its
page on PP's site, its download and the reason, the solution for a fix, its strategy, PP's
category code, RAM, the machines PP's list gives, and the verdict with where it comes from. Filters
for the name, the verdict, the strategy, PP's category, RAM and machine; they live in the address
(`catalogue.html#v=fix&s=Gamex%20%2B%20GOS5`), so a link opens the catalogue filtered. A snapshot
opens at full size.

**What is on it**: the credit to PP, with a link to his site, on every page; his pages linked,
none copied; no code of PP's or of TOS and no game file. The snapshots go in when they are on this
Mac, and `--no-snapshots` leaves them out: which, for publication, is Diego's call (STORY-08).

**Checks** (`--check`): 11 pages, 7,614 links and anchors, every one resolved; 1,831 of 1,831
games with their row; nothing loaded from another site. From a fresh clone with this story's files
(no snapshots: git-ignored): 3,986 links, 0 problems. `all_harness.sh` builds it from the working
tree and from a fresh clone of the last commit: after this story's commit (`4106b06`) the clone
builds with 3,986 links, 0 problems; `all_harness.sh`: 0 failures (222 s). `check_public.py`'s
own clone, in a macOS temporary folder (`/var` is a link to `/private/var`), found the builder
naming itself by an unresolved path; it resolves it now.

**Publication, prepared** (`docs/publication/`): `remove.txt` (must: `LEMMINGS/`, the first
pass's patched `START.TOS`, its unpacked stages and D15R's disassembly; review, Diego's call: the
rest of `_archive/`, the launcher's sources in `src/`, `CLAUDE.md`), `README.md` (what else a
reader would see, the clean-up steps, the Pages settings) and `site.yml`, the Pages workflow, to
move into `.github/workflows/` when going public. `tools/site/check_public.py` checks a clone:
the files and the history of every branch against the list, binary files the list does not name,
co-author trailers, and the site's build. On a fresh clone today it reports the nine entries of
the list (nothing has been removed); on a throwaway repository without them, "ready to go public";
with a binary file and a trailer added to it, both reported. The history holds 19 paths no longer
in the tree: earlier backlog files only.

