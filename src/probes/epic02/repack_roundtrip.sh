#!/usr/bin/env bash
# EPIC-02 STORY-03: the original files with one stage replaced by its repacked copy
# (tools/pack.py) boot the PPDRIVER reference, and the stage's dump at its entry
# (chain_probe.py) equals the original's.
#
# Usage: src/probes/epic02/repack_roundtrip.sh [<setup>]     (default st-104)
#
# Variants: start (START.TOS), ls2dd (LS2DD.FIC), d15r (D15R_H5.FIC), all (the three).
# Each variant is a copy of LEMLD2's folder under tools/dev/builds/epic02/variants/;
# the disks are rebuilt from it, probed, and rebuilt from LEMMINGS/ at the end.
set -euo pipefail
repo="$(cd "$(dirname "$0")/../../.." && pwd)"
setup="${1:-st-104}"
work="$repo/tools/dev/builds/epic02"
mkdir -p "$work/unpacked" "$work/packed"

python3 -I "$repo/tools/unpack.py" start "$repo/LEMMINGS/START.TOS" "$work/unpacked/LEMLD2.TOS" >/dev/null
for f in LS2DD D15R_H5; do
  python3 -I "$repo/tools/unpack.py" fic "$repo/LEMMINGS/$f.FIC" "$work/unpacked/$f.bin" >/dev/null
  python3 -I "$repo/tools/pack.py" fic "$work/unpacked/$f.bin" "$work/packed/$f.FIC" "$repo/LEMMINGS/$f.FIC"
done
python3 -I "$repo/tools/pack.py" start "$work/unpacked/LEMLD2.TOS" "$work/packed/START.TOS" "$repo/LEMMINGS/START.TOS"

for variant in start ls2dd d15r all; do
  case $variant in
    start) files="START.TOS" ;;
    ls2dd) files="LS2DD.FIC" ;;
    d15r) files="D15R_H5.FIC" ;;
    all) files="START.TOS LS2DD.FIC D15R_H5.FIC" ;;
  esac
  tree="$work/variants/$variant/LEMMINGS"
  rm -rf "$work/variants/$variant"
  mkdir -p "$tree"
  rsync -a "$repo/LEMMINGS/" "$tree/"
  for f in $files; do cp "$work/packed/$f" "$tree/$f"; done
  "$repo/tools/dev/make_disks.sh" "$tree" >/dev/null
  echo "== $variant: $files"
  python3 -I "$repo/src/probes/epic02/chain_probe.py" "$setup" | tail -2 | head -1
done
"$repo/tools/dev/make_disks.sh" >/dev/null
shasum -a 256 -c "$repo/LEMMINGS.sha256" | grep -vc ': OK$' | sed 's/^/LEMMINGS files not OK: /'
