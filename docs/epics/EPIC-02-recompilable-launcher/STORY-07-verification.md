---
id: STORY-07
epic: EPIC-02
title: Verification (Diego's checkpoint)
status: done
---

## Goal

Diego sees the launcher built from our sources boot the game, and agrees the sources are ready to
change in iteration 2 and the signatures ready for EPIC-03's survey.

## Tasks

- [x] Claude builds the launcher from a clean tree and boots the game from it while Diego
      watches, then shows the visible-change proof.
- [x] Diego agrees, or the stories to reopen are listed here.

## Acceptance

Diego's agreement, recorded here with the date.

## Notes

**Done 2026-10-11.** To see it, each one command:

```
tools/build_launcher.sh                                    # from src/, a clean tools/dev/builds/launcher/
tools/dev/make_disks.sh tools/dev/builds/launcher/LEMMINGS # our build onto both disks
python3 tools/dev/hatari_harness.py --setup st-104 --disk ppdriver --expect tools/dev/expect/reference-first-level.exp
tools/dev/make_disks.sh                                    # PP's files back on the disks
tools/dev/all_harness.sh                                   # everything, the sources and the build included
```

The visible-change proof is STORY-06's (`…-183638-st-104-ppdriver-rebuilt/shots/info.png`).
Diego read the report rather than watching live; the first task is taken as done on that basis,
as in EPIC-00 and EPIC-01.

Diego's agreement, 2026-10-11: "story 07 agree", with "commit and merge to main, keep d15r .s
git-ignored" (D-13). No story reopened.
