#!/usr/bin/env bash
#
# tools/unpack_all.sh: every launcher stage unpacked from LEMLD2's files in LEMMINGS/ into
# tools/dev/builds/stages/unpacked/, where the maps of src/ read them.
#
# Usage: tools/unpack_all.sh
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out="$repo/tools/dev/builds/stages/unpacked"
mkdir -p "$out"
cd "$repo"
python3 -I tools/unpack.py text LEMMINGS/START.TOS "$out/START.text"
python3 -I tools/unpack.py start LEMMINGS/START.TOS "$out/LEMLD2.TOS"
for f in LS2DD D15R_H5 D15R_F5; do
  python3 -I tools/unpack.py fic "LEMMINGS/$f.FIC" "$out/$f.bin"
done
