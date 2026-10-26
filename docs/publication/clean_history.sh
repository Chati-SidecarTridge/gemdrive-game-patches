#!/usr/bin/env bash
#
# docs/publication/clean_history.sh: a clone of this repository with remove.txt's must paths taken
# out of every commit of every branch (D-15, D-25), for tools/site/check_public.py and then for
# going public. This working copy is not touched.
#
# Usage: docs/publication/clean_history.sh <out>    (<out>: a folder that does not exist yet)
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
out="${1:?usage: clean_history.sh <out>}"
[[ ! -e "$out" ]] || { echo "error: $out exists" >&2; exit 1; }

paths=()
while read -r kind path _; do
  [[ "$kind" == must ]] && paths+=("$path")
done < "$repo/docs/publication/remove.txt"

git clone -q --no-local "$repo" "$out"
cd "$out"
for b in $(git for-each-ref --format='%(refname:strip=3)' refs/remotes/origin/); do
  [[ "$b" == HEAD ]] || git show-ref -q --verify "refs/heads/$b" || git branch -q "$b" "origin/$b"
done
git remote remove origin

rm_cmd="git rm -r -q --cached --ignore-unmatch --"
for p in "${paths[@]}"; do rm_cmd+=" '$p'"; done
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --prune-empty --index-filter "$rm_cmd" -- --all > /dev/null

git for-each-ref --format='%(refname)' refs/original/ | xargs -n 1 git update-ref -d
git reflog expire --expire=now --all
git gc -q --prune=now
git reset -q --hard
echo "$out: $(git rev-list --all --count) commits, $(git ls-files | wc -l | tr -d ' ') files, removed: ${paths[*]}"
