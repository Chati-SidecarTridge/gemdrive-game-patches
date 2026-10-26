---
id: STORY-03
epic: EPIC-09
title: The patcher in the browser: the ZIP, the build, the download
status: done
---

## Goal

The page's code: it reads the ZIP, checks it, applies the fix in JavaScript and writes the
patched ZIP for the user to download. Standard browser APIs only.

## Tasks

- [x] ZIP reading (stored and deflated entries, `DecompressionStream`) and writing (stored, CRC-32), tested on the mirror's archives.
- [x] The Gamex launchers' unpacker and packer in JavaScript, byte for byte `tools/unpack.py` and `tools/pack.py`.
- [x] The GOS5 and GOS4 builds in JavaScript, byte for byte `tools/build_gos5.py` and `build_gos4.py`, with their blocks assembled from our sources.
- [x] S2, S3, S4 and the second download (D-23).
- [x] Every result checked against our build's SHA-256 before it is offered; an archive that does not match is refused with the reason.

## Acceptance

For every patchable archive, the page's file equals the card build's, byte for byte.

## Notes

**2026-10-26.** `tools/site/patcher.js`: ZIP reading (central directory, stored and deflated entries
through `DecompressionStream('deflate-raw')`, CRC-32 checked) and writing (unchanged entries keep
their compressed bytes, changed and added ones are stored); the unpacker, the packer (the same
optimal parse and tie-breaks as `tools/pack.py`), the stub's in-place margin, the GOS5 and GOS4
searches and build; S2 (our `GDBPB.PRG`), S3 (the bit), S4 and D-23's second download; every file
checked against the table's SHA-256 before and after, refused otherwise. The data, `patch-data.js`,
is written by `build_site.py`: the table and our three blocks in base64 (`gos5_patch.s`,
`gos4_patch.s`, `gdbpb.s`, assembled as the build tools assemble them).

`src/probes/epic09/patch_test.py` runs it in headless Chrome on a local server and checks every
patched ZIP with `zipfile` (every original entry, the same bytes but the fix's file, which must be our
build, and the added files): `tools/dev/builds/epic09/test-20261026-163512`, 230 archives (the 208
fixes and five of each other action) in 30 s, 208 patched, 0 problems; the slowest, AGE.ZIP, 616 ms.
A ZIP not in the table is not known; a truncated one is refused ("this is not a ZIP file"). The
packed results being our builds' SHA-256 shows the JavaScript packer byte for byte the Python one.
