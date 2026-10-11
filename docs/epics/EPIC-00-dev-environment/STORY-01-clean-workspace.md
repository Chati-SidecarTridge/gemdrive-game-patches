---
id: STORY-01
epic: EPIC-00
title: A clean workspace: the first pass archived, the evidence pristine, git
status: done
---

## Goal

`LEMMINGS/` holds only PP's original files and a manifest proves it; everything the first pass
produced sits under `_archive/2026-04-first-pass/`, untouched and out of the way (D-01); the
repository is under git with the pristine evidence as its first commit (D-03).

## Tasks

- [x] Before touching anything: the file list and SHA-256 of every file under `LEMMINGS/`,
      `src/` and the repository root, recorded in these notes.
- [x] `src/` (without `__pycache__`) moved to `_archive/2026-04-first-pass/src/`, `trace.log`
      to `_archive/2026-04-first-pass/trace.log`.
- [x] The first pass's builds moved out of `LEMMINGS/` into
      `_archive/2026-04-first-pass/lemmings-patched/`: `START.TOS` (35,230 bytes, the
      `minimal_install` build, equal to `src/unpacked/start_tos.inner.minimal.prg`),
      `START2.TOS` and `START_bare.TOS`.
- [x] `LEMMINGS/START.TOS` restored from `START.TOS.orig` (9,106 bytes, GEMDOS header
      `tsize=0xE6 dsize=0x228C`), `LEMMINGS/LS2DD.FIC` from `LS2DD.FIC.orig` (byte-identical
      today; the `.orig` keeps its 2011 date). No `.orig` left in `LEMMINGS/`.
- [x] `LEMMINGS.sha256` at the root lists every file under `LEMMINGS/`;
      `shasum -a 256 -c LEMMINGS.sha256` passes (C-01).
- [x] An empty `src/` for the new work, and `.gitignore`: `.DS_Store`, `__pycache__/`, `*.log`,
      `tools/dev/builds/`, `tools/dev/logs/`, `tools/dev/dev.cfg`,
      `.claude/settings.local.json`.
- [x] `git init` on `main`; the first commit holds `LEMMINGS/`, `LEMMINGS.sha256`,
      `DESKTOP.INF`, `CLAUDE.md`, `docs/` and `_archive/` (not `trace.log`), with no AI
      attribution (D-03).

## Acceptance

Every file recorded before the move is found again, with the same SHA-256, either in
`LEMMINGS/` or under `_archive/`; `shasum -a 256 -c LEMMINGS.sha256` passes; `git status` is
clean after the first commit.

## Notes

`DESKTOP.INF` at the root is the first pass's emulated `C:` desktop (it opens a window on
`C:\LEMMINGS\*.*`), so the first pass pointed a Hatari GEMDOS drive at this repository's root
(C-01). It stays as evidence of that setup; STORY-04 builds its own drive.

**Done 2026-10-11.**

- Before the move: 134 files hashed (`LEMMINGS/` and `src/` without `.DS_Store`, plus
  `CLAUDE.md`, `DESKTOP.INF` and `trace.log` in the root), kept as
  `_archive/2026-04-first-pass/MANIFEST.before.sha256`. The patched `LEMMINGS/START.TOS` was
  `6dad7b5f…e3a3`, the original `START.TOS.orig` `59c6e445…02c8`; `LS2DD.FIC` and
  `LS2DD.FIC.orig` were both `0f9e22d0…2092`.
- After the move, 131 of the 134 are found again with the same SHA-256 under `LEMMINGS/` or
  `_archive/`. The other three: `CLAUDE.md` and `DESKTOP.INF` are unchanged in the root (checked
  against the manifest), and `src/tools/__pycache__/repack_start_tos.cpython-314.pyc` was
  deleted on purpose (a Python cache).
- `LEMMINGS.sha256`: 76 files (7 in `LEMMINGS/`, 69 in `LEMMINGS/FILES/`); `shasum -a 256 -c`
  reports 76 OK. `LEMMINGS/.DS_Store` is Finder noise, left in place, ignored and not listed.
- This Mac's git is 2.23.0, which has no `git init -b`: `main` set with
  `git symbolic-ref HEAD refs/heads/main`.
- Baseline commit `54199f4` on `main`, 170 files, authored by Diego Parrilla, no AI attribution.
  `trace.log` and the `.DS_Store` files ignored. The rest of EPIC-00 continues on
  `epic-00-dev-environment` (D-07, proposed), cut from `54199f4`, uncommitted.
