---
id: STORY-03
epic: EPIC-11
title: The website published, with its snapshots, on gh-pages
status: in-progress
---

## Goal

The site at https://gemdrive.sidecartridge.com/ (`CNAME`), with each game's snapshot. Diego,
2026-10-26: built on this Mac and pushed to `gh-pages` (D-28).

## Tasks

- [x] `tools/site/deploy_site.sh [--dry-run]`: refuses on changed tracked files; builds and checks
      the site with the snapshots into `tools/dev/builds/site-pages/`; one parentless commit,
      force-pushed to `origin` `gh-pages`. Dry run: 7 pages, 7902 links, 1831 of 1831 games,
      1816 snapshots, 0 problems; 1834 files, 23 MB.
- [x] The Actions deploy dropped (`docs/publication/site.yml`); `docs/publication/README.md`,
      `README.md`, `CLAUDE.md` and the CI workflow's comment say how the site is published.
- [x] `gh-pages` pushed: `89411f9`, built from `6f0c28a` (`git ls-remote origin gh-pages`).
- [ ] Pages on, from `gh-pages` `/`, custom domain `gemdrive.sidecartridge.com` (its DNS already
      points at `sidecartridge.github.io`), HTTPS; on Diego's word, since the site is then public.
- [ ] The published site in Chrome, Safari and Firefox: every page, the snapshots, the patcher.
