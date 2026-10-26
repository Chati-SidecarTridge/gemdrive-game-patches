# Epics, Stories & Tasks

The backlog for gemdrive-game-patches (D-26), the reverse engineering of PP's Gamex hard-disk loader for
Lemmings on the Atari ST. It follows the same procedure as Diego's other repositories
(`../sidecartos/docs/epics/`, `../sidecartos-config/docs/epics/`,
`../romemul-switcher-rom/docs/epics/`), so all of them track work the same way (D-02). This
repository is not part of their shared product, and nothing here has to stay in sync with them.

See `STATUS.md` for the live cockpit (generated; don't edit it by hand).

## Hierarchy

```
docs/epics/
  cockpit.sh          # regenerates STATUS.md from the files below
  STATUS.md           # generated dashboard (epics grouped by iteration)
  ITERATIONS.md       # iteration narrative: goal, order and why, outcome; the H-NN hypotheses
  DECISIONS.md        # D-NN decisions + C-NN constraints
  templates/          # copy these when adding new work
    epic.md
    story.md
  EPIC-00-<slug>/
    epic.md           # the epic (carries `iteration: N`)
    STORY-01-<slug>.md
    STORY-02-<slug>.md
```

- **Iteration**: a pass with one overarching goal, grouping several epics. Each `epic.md`
  carries `iteration: N`; the cockpit groups epics under it.
- **Epic**: a folder `EPIC-NN-<slug>/` with an `epic.md`. A coarse capability or question.
- **Story**: a file `STORY-NN-<slug>.md` inside an epic folder. A shippable slice of that epic.
- **Task**: a checkbox line inside a story, `- [ ]` open or `- [x]` done. The checkboxes drive the
  percentages in the cockpit.

**Numbers are the execution order**: epics within an iteration, and stories within an epic, are
done in number order, and `ITERATIONS.md` says why the order is what it is. Prefer adding over
renumbering once an epic has started.

Every work epic has the same shape: work stories, then **one verification story, which is
Diego's checkpoint**. Its `## Setups` section says which Hatari machines, TOS versions and disk
setups it covers.

## Status field

```yaml
---
id: STORY-01
epic: EPIC-01
title: <short story title>
status: todo   # todo | in-progress | done | blocked | deferred
---
```

Keep `status` honest relative to the checkboxes: `todo` = no tasks done, `done` = all done,
`in-progress` = some, `blocked` = waiting (say why in the body), `deferred` = consciously postponed
to a later iteration.

## Working rules

- **Strictly sequential**: one epic at a time.
- **Checkpoints**: after each epic, work stops. Diego checks the result and approves before the
  next epic starts.
- **A task is checked only when it was observed**, by whoever the task names. "Decoded" is not
  "matches the bytes Hatari had in memory"; "should boot" is not "booted".
- **The first pass is not evidence** (D-01). A finding from `_archive/` becomes a fact only when
  it is observed again here, and the story notes record how. `ITERATIONS.md` lists them as
  hypotheses (`H-NN`); stories confirm or refute them by number.
- **`LEMMINGS/` is never modified** (C-01). Every run, patch and experiment works on a copy.
- **Before and after numbers** for every story that changes a binary (sizes, hashes) or a
  measured behaviour (where a run stops, how long it takes).
- **Hatari is the test machine** (D-06), always as released: its code is never modified (C-02).
  Every fix lives on the Atari side.
- **Nothing is committed until Diego says so.** Work is left in the working tree; he sequences the
  history. The backlog itself (`docs/`) is committed (D-03).
- **Committed files may cite backlog items** (D-04): `EPIC-NN`, `STORY-NN`, `D-NN`, `C-NN`,
  `H-NN`. Items of another repository are cited with it: `firmware EPIC-11`.
- **Run `./docs/epics/cockpit.sh`** after every change to a story or epic file: `STATUS.md` is the
  dashboard Diego reads.
- No AI attribution anywhere (`CLAUDE.md`).

## Adding work

1. Copy `templates/epic.md` to `EPIC-NN-<slug>/epic.md`; give it an `iteration` and its setups.
2. Copy `templates/story.md` into the epic folder once per slice, in execution order.
3. End the epic with a verification story: Diego's checkpoint.
4. Run `./docs/epics/cockpit.sh`.
