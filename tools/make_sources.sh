#!/usr/bin/env bash
#
# tools/make_sources.sh: the launcher's sources, made from their maps. None is
# committed: START.TOS's stub, LEMLD2 and LS2DD reassemble to the original files, D15R's
# two builds are mostly TOS 1.04's own code. Unpacks the stages from LEMMINGS/ first
# (tools/unpack_all.sh), then tools/dev/mksource.py for each map.
#
# Usage: tools/make_sources.sh
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo"
tools/unpack_all.sh > /dev/null
for m in src/start/start src/lemld2/lemld2 src/ls2dd/ls2dd src/d15r/d15r_h5 src/d15r/d15r_f5; do
  python3 -I tools/dev/mksource.py "$m.map" "$m.s" | tail -1
done
