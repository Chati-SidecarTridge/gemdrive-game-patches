#!/usr/bin/env bash
#
# tools/site/deploy_site.sh: the website published, with its snapshots, on the gh-pages branch.
#
# Usage: tools/site/deploy_site.sh [--dry-run]
#
# Builds and checks the site (build_site.py --check) with the snapshots of this machine's runs
# (tools/dev/builds/survey/snapshots/), which are not in the repository, into
# tools/dev/builds/site-pages/; then makes one commit of that folder, with no parent, and
# force-pushes it to origin's gh-pages branch, which GitHub Pages serves at the address in CNAME.
# The branch keeps only the latest site, so old snapshots do not pile up in it. Refuses when a
# tracked file has changed, so the site published is the one of a commit. --dry-run stops before
# the push.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
out="$repo/tools/dev/builds/site-pages"
cd "$repo"
git diff --quiet HEAD || { echo "error: tracked files changed; commit them first" >&2; exit 1; }
python3 tools/site/build_site.py --out "$out" --check
touch "$out/.nojekyll"  # serve the folder as it is, without Jekyll
export GIT_INDEX_FILE="$repo/tools/dev/builds/site-pages.index"
git read-tree --empty
git --work-tree="$out" add -A
tree="$(git write-tree)"
commit="$(git commit-tree "$tree" -m "The site, built from $(git rev-parse --short HEAD)")"
echo "gh-pages: $commit, $(git ls-tree -r "$tree" | wc -l | tr -d ' ') files"
[[ "${1:-}" == "--dry-run" ]] && exit 0
git push --force origin "$commit:refs/heads/gh-pages"
