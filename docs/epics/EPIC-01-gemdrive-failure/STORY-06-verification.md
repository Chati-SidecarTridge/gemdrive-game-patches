---
id: STORY-06
epic: EPIC-01
title: Verification (Diego's checkpoint)
status: done
---

## Goal

Diego agrees with the cause and the list of dependencies, seen in Hatari.

## Tasks

- [x] Claude reruns the reference, a failing GEMDRIVE run and the furthest patched probe while
      Diego watches, and walks him through the write-up.
- [x] Diego agrees, or the stories to reopen are listed here.

## Acceptance

Diego's agreement, recorded here with the date.

## Notes

**Done 2026-10-11.** The runs to show, each one command:

```
python3 tools/dev/hatari_harness.py --setup st-104 --disk ppdriver --expect tools/dev/expect/reference-first-level.exp
python3 tools/dev/hatari_harness.py --setup st-104 --disk gemdrive --expect tools/dev/expect/launcher-start.exp
python3 src/probes/epic01/gate_probe.py st-104 gemdrive      # then src/probes/epic01/read_probe.py <run>
python3 src/probes/epic01/fallback_probe.py st-104 --bpb     # sector 0 and the BPB answered by hand
```

Diego read the report rather than watching live; the first task is taken as done on that basis,
as in EPIC-00 STORY-07.

Diego's agreement, 2026-10-11: "the problem is we are running in hatari GEMDRIVE mode and ppera
driver expects a native driver", then, after the report, "please concrete the pending task of
epic 1". No story reopened.
