# Going public (D-15): prepared, not done

EPIC-03 STORY-07, 2026-10-13. The repository and its website go public only on Diego's word, after
what cannot be published has left the repository and its history. This folder holds what that
needs; nothing here has been run against the repository's history, and there is no remote.

## What has to leave

`remove.txt` is the list, one path or pattern per line, each with its reason. Diego, 2026-10-26,
took the recommendations (D-25):

- **must**: `LEMMINGS/` (the game and PP's files); all of `_archive/`, the first pass (its patched
  `START.TOS`, PP's stages unpacked and disassembled, D15R's disassembly, which is TOS 1.04's code,
  and its notes and tools, superseded); the launcher's sources in `src/start/`, `src/lemld2/` and
  `src/ls2dd/`, which reassemble to PP's bytes; and D15R's sources (never committed, D-13; listed
  so a slip is caught).
- **keep**: the two binary files that stay, SidecarTridge's logos for the site.

Kept: `CLAUDE.md`, the working rules; `LEMMINGS.sha256`, which checks a user's own copy; the maps
and executed-address lists of every stage (names, comments and addresses, no code), from which
`tools/make_sources.sh` makes the sources from the user's `LEMMINGS/`. `DESKTOP.INF` left the root
(the first pass's, the same as `tools/dev/DESKTOP.INF`, which the disks use); its history stays.

`LEMMINGS/` and `_archive/` stay on this Mac, git-ignored, in the working copy.

Other things a reader of the public repository will see, also Diego's call, not on the list
because they are not files to remove:

- The notes quote PP's pages in short passages, each cited by page (`modes.md` §2, his
  categories, quotes most). His pages are linked, never copied (D-11).
- `DECISIONS.md` records how the mirror was made (D-11, D-12).
- The commits carry their author's name and e-mail address.
- The snapshots (each game's last screen, `tools/dev/builds/survey/snapshots/`, 22 MB) are not
  committed: the site built on GitHub has no pictures unless they are committed or published
  another way. They show the games' screens and the TOS desktop.

Kept, as D-11 and D-13 allow: the survey tables (`src/survey/`, PP's list read into this project's
columns, each game with its page's URL), the hashes in `LEMMINGS.sha256`.

## The check

```
python3 tools/site/check_public.py            # a fresh clone of this repository, every branch
python3 tools/site/check_public.py <clone>    # or a clone already cleaned
```

It reports every entry of `remove.txt` still found in the clone's files or in any commit, any
binary file in the history that the list does not name, any commit message with a co-author
trailer, and whether the site builds from the clone. It exits 0 only when there is nothing left
to report.

## The clean-up

On a fresh clone, never on this working copy: `clean_history.sh` clones the repository (every
branch) and removes the `must` paths from every commit with `git filter-branch`, which comes with
git; then `check_public.py <clone>` must say "ready to go public". Every commit's hash changes.
The clone is the repository that goes public; this working copy, with its whole history, stays
here.

```
docs/publication/clean_history.sh <out>       # <out>: a new folder, the cleaned clone
python3 tools/site/check_public.py <out>
```

## GitHub Pages

The site is built, not committed, and published from this Mac, with its snapshots (Diego,
2026-10-26, D-28): the snapshots come from the Hatari runs here and are not in the repository.

```
tools/site/deploy_site.sh [--dry-run]         # build, check, force-push the site to gh-pages
```

A release is `make tag`: it refuses when `version.txt`'s version is already tagged, runs
`deploy_site.sh`, and only then tags the version and pushes the tag. `deploy_site.sh` refuses when a tracked file has changed, builds the site with its snapshots and `--check`
into `tools/dev/builds/site-pages/`, and pushes it as a single commit with no parent to `origin`'s
`gh-pages` branch, so the branch holds only the latest site.

- Repository settings, Pages, "Build and deployment": source **Deploy from a branch**,
  `gh-pages`, `/` (root); custom domain `gemdrive.sidecartridge.com` (`CNAME`, copied into the
  site), whose DNS record already points at `sidecartridge.github.io`; HTTPS enforced.
- `.github/workflows/site.yml` only builds and checks the site, without snapshots, on pull
  requests and pushes to `main`; it publishes nothing.
