---
id: STORY-07
epic: EPIC-00
title: Verification (Diego's checkpoint)
status: done
---

## Goal

Diego sees the environment work on this Mac and agrees that EPIC-01 can start.

## Tasks

- [x] Claude runs `tools/dev/all_harness.sh` from a clean `tools/dev/builds/` while Diego
      watches, and shows the table and one run folder.
- [x] Claude shows `git status`, `git log` and `shasum -a 256 -c LEMMINGS.sha256` passing.
- [x] Diego agrees, or the stories to reopen are listed here.

## Acceptance

Diego's agreement, recorded here with the date.

## Notes

**Done 2026-10-11.** Claude ran `tools/dev/all_harness.sh` from an empty `tools/dev/builds/`
(11 checks PASS, 132 s, STORY-06) and reported the table, the run folders' contents, the
baseline commit `54199f4` and `shasum -a 256 -c LEMMINGS.sha256` (76 OK) to Diego, who read the
report rather than watching the run live. Diego's answer: "ok". Committed on
`epic-00-dev-environment` at his request.
