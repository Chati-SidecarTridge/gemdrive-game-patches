---
id: STORY-02
epic: EPIC-10
title: The repository's files, as the other SidecarTridge repositories'
status: done
---

## Goal

Diego, 2026-10-26: "this repo also lacks README.md CHANGELOG.md and other files common in our repos. Review them and add them. Also, populate them as other repos."

## Tasks

- [x] The files the other repositories share, reviewed (md-jackintosh-roms, md-jackintosh, romemul-switcher-rom, md-drives-emulator, magic-c-builder): which this one needs.
- [x] `README.md`: what the project is, the site, the patcher, how to build and test, the layout, the licence.
- [x] `CHANGELOG.md`, `version.txt`, `LICENSE` (GPLv3, as the others), and CI in `.github/workflows` (the site's check).
- [x] Nothing in them refers to the adaptations' author or carries their files (D-11, D-21).

## Acceptance

The repository has the files a SidecarTridge repository has, filled in as theirs are.

## Notes

**2026-10-26.** Reviewed: md-jackintosh-roms, md-jackintosh, romemul-switcher-rom, md-drives-emulator
and magic-c-builder share `README.md`, `CHANGELOG.md`, `LICENSE` (GPLv3), `version.txt` and
`.github/workflows`; the ones with a site add `CNAME`. Added here:

- `README.md`, for developers as md-jackintosh-roms' is: what the project is and found, no original
  files, the pieces, building and testing, the website, the licence; users are sent to the site's
  "Patch a game".
- `CHANGELOG.md`: v1.0.0, unreleased (dated at the release gate), in romemul-switcher-rom's shape.
- `version.txt`: v1.0.0. `LICENSE`: GPLv3, the same file as md-jackintosh-roms', magic-c-builder's and
  md-drives-emulator's.
- `.github/workflows/site.yml`: on pull requests and pushes to main, the pinned toolchain pulled
  and `build_site.py --out _site --no-snapshots --check` run. The Pages workflow stays in
  `docs/publication/` until EPIC-11.
- `CNAME`: gemdrive.sidecartridge.com (Diego, 2026-10-26), copied into the built site; each page's
  canonical link and the README and changelog name it.

Neither file names the adaptations' author or carries their files.
