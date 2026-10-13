# Going public (D-15): prepared, not done

EPIC-03 STORY-07, 2026-10-13. The repository and its website go public only on Diego's word, after
what cannot be published has left the repository and its history. This folder holds what that
needs; nothing here has been run against the repository's history, and there is no remote.

## What has to leave

`remove.txt` is the list, one path or pattern per line, each with its reason:

- **must**: `LEMMINGS/` (the game and PP's files), the first pass's binaries in `_archive/` (PP's
  patched `START.TOS`, the unpacked stages, D15R's disassembly, which is TOS 1.04's code), and
  D15R's sources (never committed, D-13; listed so a slip is caught).
- **review**, Diego's call, keep or remove: the rest of `_archive/` (the first pass, superseded by
  this one, D-01); the launcher's sources in `src/start/`, `src/lemld2/` and `src/ls2dd/`, which
  reassemble to PP's bytes; `CLAUDE.md`.

Other things a reader of the public repository will see, also Diego's call, not on the list
because they are not files to remove:

- The notes quote PP's pages in short passages, each cited by page (`pp-modes.md` §2, his
  categories, quotes most). His pages are linked, never copied (D-11).
- `DECISIONS.md` records how the mirror was made (D-11, D-12).
- The commits carry their author's name and e-mail address.
- The snapshots (each game's last screen, `tools/dev/builds/survey/snapshots/`, 22 MB) are not
  committed: the site built on GitHub has no pictures unless they are committed or published
  another way. They show the games' screens and the TOS desktop.

Kept, as D-11 and D-13 allow: the survey tables (`src/survey/`, PP's list read into this project's
columns, each game with its page's URL), D15R's maps (names, comments and addresses, no code), the
hashes in `LEMMINGS.sha256`.

Once `LEMMINGS/` has gone, the checks that rebuild the launcher (`tools/make_sources.sh`,
`tools/dev/all_harness.sh`) need PP's files from the user's own copy of `LEMMINGS.ZIP`.

## The check

```
python3 tools/site/check_public.py            # a fresh clone of this repository, every branch
python3 tools/site/check_public.py <clone>    # or a clone already cleaned
```

It reports every entry of `remove.txt` still found in the clone's files or in any commit, any
binary file in the history that the list does not name, any commit message with a co-author
trailer, and whether the site builds from the clone. It exits 0 only when there is nothing left
to report. Today it reports the list itself: nothing has been removed.

## The clean-up, when Diego decides

On a fresh clone, never on this working copy: remove the `must` paths, and the `review` paths
decided against, from every commit (for example `git filter-repo --invert-paths --path LEMMINGS/
--path …`), run `check_public.py <clone>` until it says "ready to go public", then add the remote
and push the clone.

## GitHub Pages

The site is built, not committed: `tools/site/build_site.py` writes it from the repository, and
every link in it is relative, so it works from `https://<user>.github.io/<repository>/`.

- Repository settings, Pages, "Build and deployment": source **GitHub Actions**.
- The workflow: `site.yml` here, moved to `.github/workflows/site.yml` when the repository goes
  public. On every push to `main` it builds the site with `--no-snapshots --check` and deploys it.
- No custom domain, nothing else to configure: the site uses no external services, fonts or
  scripts.
