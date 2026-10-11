---
id: STORY-02
epic: EPIC-03
title: The catalogue and PP's own classification
status: todo
---

## Goal

Every record of PP's list as a table in this repository, with what each game's page adds, its
terms read with STORY-01's glossary.

## Tasks

- [ ] `tools/survey/catalogue.py` (standard library). It reads the list and each game's page from
      the mirror (STORY-03, D-12), never the site, and writes `src/survey/catalogue.csv`: name,
      source URL, page, downloads (archive names, RAM, machines), the list's RAM and TOS 1.04 /
      TOS 2.06 / Mega STE / Falcon / TT marks, its note, its date, the category code, and the
      page's text on the adaptation. The record count must equal the list's on the mirror's
      date.
- [ ] The category code split into its parts (multipart or singleparted, RAM, TOS dependence, TPA,
      file system, XBIOS or floppy controller), counted over the catalogue and compared with the
      counts in `agcat.html`.
## Acceptance

`src/survey/catalogue.csv` holds every record of the list on the mirror's date, with the code
parsed for every game that has one, and each game's mode as its page names it (STORY-01's
glossary).

## Notes
