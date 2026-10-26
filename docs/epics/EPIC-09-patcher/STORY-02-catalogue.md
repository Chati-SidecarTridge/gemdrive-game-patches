---
id: STORY-02
epic: EPIC-09
title: The catalogue: every archive, its check and what the page does
status: done
---

## Goal

A table of every archive in the mirror, generated from what the repository holds: the
archive's name, size and SHA-256, its games and verdicts, and what the page does with it.

## Tasks

- [x] Every archive of the mirror in it: name, size, SHA-256, the games it holds (`migration.csv`).
- [x] Its action: nothing to patch (as it is), a fix (S1 with its tool and options, S2, S3, S4), a second download (D-23), or no file and the reason (not feasible, unsure, fails, no build).
- [x] For a fix: the file it changes, that file's SHA-256 in the original, and our build's SHA-256.
- [x] Regenerated from scratch, the same table; no byte of the adaptations in it.

## Acceptance

Every archive in the table with an action; every fix's expected result is the card build's.

## Notes

**2026-10-26.** `tools/survey/patch_table.py` writes `src/survey/patches.tsv`: 2,074 archives (every
ZIP under the mirror's `site/`), each with its size and SHA-256, its rows, its start program and an
action: none 1,606, gos5 85, gos4 117, gdbpb 3 (ARBOTARG.ZIP holds two games), fastload 2, rody2 1,
refuse 14 (10 unsure, 3 built but failing, 1 not feasible), other 196 (another download of a game),
notgame 50. Aquanaut is refused (`ports.tsv`: fails). A fix's result comes from `sdcard.py`'s own
build on a copy of the unpacked download; the 208 results equal the card build `sdcard-1245b` file
for file. Every fix's target is in its ZIP at the table's path with the table's SHA-256, and every
second download's files likewise (no target is inside a nested ZIP). Run again from scratch, the same
table byte for byte (16:38:42 against 16:30). The table holds names, sizes and hashes only.
