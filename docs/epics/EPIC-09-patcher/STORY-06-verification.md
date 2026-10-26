---
id: STORY-06
epic: EPIC-09
title: Verification (Diego's checkpoint)
status: done
---

## Goal

Diego patches games with the page and runs them on his machines.

## Tasks

- [x] Claude runs the sample of STORY-04 on the three setups.
- [x] Diego patches games with the page and tests them from the card. A game that disagrees is listed here.
- [x] Diego agrees, or the stories to reopen are listed here.

## Acceptance

Diego's agreement, recorded with the date.

## Notes

Claude's runs: STORY-04 (`tools/dev/builds/epic09/runs-1653/`, six fixes on the three setups).

**Diego, 2026-10-26**: the page with the three original downloads (`10THFRAM.ZIP` nothing to patch,
`LEMMINGS.ZIP` patched, `AQUAN.ZIP` no fix): "uploading is working for the three games". A URL field
was asked for and dropped the same day: the 8bitchip.info website sends no CORS header, so a page
cannot read its downloads ("it is ok").

**Diego, 2026-10-26**: `LEMMINGS-GEMDRIVE.ZIP` from the page, unpacked, its `LEMMINGS` folder copied
to the card and started on his machine with the Multidevice: "it works".

**Diego agrees, 2026-10-26**: "close and commit". The patcher page checks all 2,074 archives, patches
the 208 with a built fix byte for byte as the card build, and the patched Lemmings runs on his machine.
