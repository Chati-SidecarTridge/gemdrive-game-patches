#!/usr/bin/env bash
#
# tools/make_sources.sh: the sources of src/ that are not committed, made from their maps
# (EPIC-02, D-13): D15R's two builds, which are mostly TOS 1.04's own code. Unpacks the stages
# from LEMMINGS/ first (tools/unpack_all.sh), then tools/dev/mksource.py for each map.
#
# Usage: tools/make_sources.sh
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo"
tools/unpack_all.sh > /dev/null
for m in src/d15r/d15r_h5 src/d15r/d15r_f5; do
  python3 -I tools/dev/mksource.py "$m.map" "$m.s" | tail -1
done
