---
id: STORY-02
epic: EPIC-03
title: Lemmings boots in GEMDRIVE mode
status: todo
---

## Goal

The chosen approach, built from source, takes Lemmings from a Hatari GEMDOS drive to its first
level on every setup, while the PPDRIVER reference keeps working.

## Tasks

- [ ] The fix built from source by `tools/build_launcher.sh` (or its own build script), into a
      disk tree under `tools/dev/builds/`.
- [ ] GEMDRIVE runs on every setup reach the first level, with the reference's milestones.
- [ ] The PPDRIVER reference, with the fix in place where it applies, still boots on every
      setup.
- [ ] Memory: what the fix occupies and where, before and after, against the launcher's own
      layout.
- [ ] Added to `tools/dev/all_harness.sh`.

## Acceptance

`tools/dev/all_harness.sh` shows PASS to the first level in GEMDRIVE mode on every setup, and the
PPDRIVER reference still PASS.

## Notes
