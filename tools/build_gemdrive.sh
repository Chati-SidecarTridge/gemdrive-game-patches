#!/usr/bin/env bash
#
# tools/build_gemdrive.sh: Lemmings' launcher from src/, changed so that GOS reads through a GEMDOS
# drive (EPIC-04 STORY-01, solution S1).
#
# Usage: tools/build_gemdrive.sh [<out folder>]
#
# Copies src/ into <out>/src; in the copy of src/lemld2/lemld2.s, puts src/gemdrive/
# lemld2_gemdrive.s before no_pp_driver and sends check_pp_driver's "no PP driver" branch to it
# (gd_start); then builds the copy with tools/build_launcher.sh --allow-longer (its START.TOS
# packs longer than PP's) into <out>/build (the game in <out>/build/LEMMINGS/). GOS (D15R) is not changed. <out> defaults to tools/dev/builds/gemdrive/.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out="${1:-$repo/tools/dev/builds/gemdrive}"
rm -rf "$out"
mkdir -p "$out"
[[ -f "$repo/src/lemld2/lemld2.s" && -f "$repo/src/d15r/d15r_h5.s" && -f "$repo/src/d15r/d15r_f5.s" ]] || "$repo/tools/make_sources.sh"  # D-13, D-25
cp -R "$repo/src" "$out/src"
python3 -I - "$out/src/lemld2/lemld2.s" "$repo/src/gemdrive/lemld2_gemdrive.s" <<'PY'
import sys
from pathlib import Path
src, fragment = Path(sys.argv[1]), Path(sys.argv[2]).read_text()
s = src.read_text()
branch = "\tbne.w\tno_pp_driver\t; $000330\n"
fallback = "; fallback: read the disk's boot sector by itself\nno_pp_driver:\n"
if s.count(branch) != 1 or s.count(fallback) != 1:
    sys.exit(f"error: {src}: not the source this change was written for")
s = s.replace(branch, "\tbne.w\tgd_start\t; $000330 (EPIC-04: was no_pp_driver)\n")
s = s.replace(fallback, fragment + fallback)
src.write_text(s)
PY
"$repo/tools/build_launcher.sh" --allow-longer "$out/src" "$out/build"
