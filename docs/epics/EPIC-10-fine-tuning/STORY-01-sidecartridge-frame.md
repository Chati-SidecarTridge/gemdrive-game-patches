---
id: STORY-01
epic: EPIC-10
title: The site in SidecarTridge's frame (Diego's UX changes)
status: done
---

## Goal

Diego, 2026-10-26: "1. change Diego's review for human review. 2. Background colors, Sidecartridge logos and back navigation like https://jackintosh.sidecartridge.com/ The background color should be the green color of GEM Atari ST. 3. The cookies banner like https://jackintosh.sidecartridge.com/ 4. Add a link to contact page in the store.sidecartridge.com to ask for something."

## Tasks

- [x] "Diego's review" reads "human review" on the site.
- [x] The desk is GEM's green, the colour of the ST's desktop; the SidecarTridge logo bar and a back link to sidecartridge.com, as on the jackintosh and magic sites.
- [x] The cookie banner of the jackintosh site (cookieconsent v2.9.2, MIT), with its analytics only on sidecartridge.com, after consent.
- [x] A contact link to https://store.sidecartridge.com/pages/contact.
- [x] `build_site.py --check` passes; the site still works from its folder; checked at 1440 px and 390 px.

## Acceptance

The site looks and behaves as the SidecarTridge sites do, in GEM's green.

## Notes

**2026-10-26.**

- "human review" in the catalogue's verdict column (81 games) and in the notes (`solutions.md`,
  `gemdrive-failure.md`); no page names Diego.
- The desk is GEM's green, `#00EE00`: the ST desktop's palette entry 070 as Hatari draws it, read
  from a run's screenshot; an STE colour. The menu bar starts with the SidecarTridge logo mark and
  wordmark (`tools/site/logo.png`, `logo-text.png`, from sidecartridge.com's own images, copied so
  the site loads nothing from another site) linking to sidecartridge.com, as on
  jackintosh.sidecartridge.com, and ends with "← Back" to sidecartridge.com, as on
  magic.sidecartridge.com. The bar drops the title's second half below 1,760 px to stay one line.
- The cookie banner: cookieconsent v2.9.2 (MIT) in `tools/site/vendor/`, its settings in
  `tools/site/consent.js` word for word the jackintosh site's (consent shared with sidecartridge.com
  when served there), and its Google Analytics snippet (the sidecartridge.com property), which runs
  only after consent and loads only on `*.sidecartridge.com`: from the site's folder or a local
  server nothing is sent.
- The footer: "A game missing, a fix that fails, or something else to ask? Contact SidecarTridge",
  to https://store.sidecartridge.com/pages/contact.
- `build_site.py --check`: 7 pages, 0 problems. Seen in Chrome at 1440 px and at 390 px (the bar
  wraps, the banner stacks its buttons), from the site's folder.
