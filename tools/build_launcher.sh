#!/usr/bin/env bash
#
# tools/build_launcher.sh: Lemmings' launcher built from the sources in src/ (EPIC-02 STORY-06).
#
# Usage: tools/build_launcher.sh [<src folder>] [<out folder>]
#
# Assembles every stage (tools/dev/asm.sh): src/start/start.s (the stub), src/lemld2/lemld2.s
# (a GEMDOS program), src/ls2dd/ls2dd.s, src/d15r/d15r_h5.s and d15r_f5.s; packs them
# (tools/pack.py) into START.TOS, LS2DD.FIC, D15R_H5.FIC and D15R_F5.FIC, each padded to PP's
# file's length so the disk layout stays the same; and writes them into <out>/LEMMINGS/ next to
# copies of the files the launcher does not build (FILES/, LEMMINGS.PCH, GXUT260.PRG,
# README.TXT) from LEMMINGS/. The header fields the launcher never reads (the packed files'
# names, LS2DD's +10 long, START.TOS's BSS size) are taken from PP's files.
#
# <src folder> defaults to src/ (another one lets a changed copy be built); <out folder> to
# tools/dev/builds/launcher/. Prints every product with its size and SHA-256, and whether each
# stage unpacks to the same bytes as PP's.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="$(cd "${1:-$repo/src}" && pwd)"
out="${2:-$repo/tools/dev/builds/launcher}"
cd "$repo"
[[ -f "$repo/src/d15r/d15r_h5.s" && -f "$repo/src/d15r/d15r_f5.s" ]] || tools/make_sources.sh  # not committed (D-13)
[[ -f "$src/d15r/d15r_h5.s" ]] || cp "$repo"/src/d15r/*.s "$src/d15r/"
obj="$out/obj"
tree="$out/LEMMINGS"
rm -rf "$out"
mkdir -p "$obj" "$tree"

tools/dev/asm.sh "$src/start/start.s" "$obj/START.text"
tools/dev/asm.sh --tos "$src/lemld2/lemld2.s" "$obj/LEMLD2.TOS"
tools/dev/asm.sh "$src/ls2dd/ls2dd.s" "$obj/LS2DD.bin"
tools/dev/asm.sh "$src/d15r/d15r_h5.s" "$obj/D15R_H5.bin"
tools/dev/asm.sh "$src/d15r/d15r_f5.s" "$obj/D15R_F5.bin"

python3 -I tools/pack.py start "$obj/LEMLD2.TOS" "$tree/START.TOS" LEMMINGS/START.TOS \
  --stub "$obj/START.text" --pad > /dev/null
for f in LS2DD D15R_H5 D15R_F5; do
  python3 -I tools/pack.py fic "$obj/$f.bin" "$tree/$f.FIC" "LEMMINGS/$f.FIC" --pad > /dev/null
done
rsync -a --exclude START.TOS --exclude '*.FIC' --exclude .DS_Store LEMMINGS/ "$tree/"

python3 -I - "$obj" "$tree" <<'EOF'
import hashlib, sys
from pathlib import Path
sys.path.insert(0, "tools")
import unpack
obj, tree = Path(sys.argv[1]), Path(sys.argv[2])
ref = {"LEMLD2.TOS": unpack.unpack_start(Path("LEMMINGS/START.TOS").read_bytes())}
for f in ("LS2DD", "D15R_H5", "D15R_F5"):
    ref[f + ".bin"] = unpack.unpack_fic(Path(f"LEMMINGS/{f}.FIC").read_bytes())
ours = {"LEMLD2.TOS": unpack.unpack_start((tree / "START.TOS").read_bytes())}
for f in ("LS2DD", "D15R_H5", "D15R_F5"):
    ours[f + ".bin"] = unpack.unpack_fic((tree / f"{f}.FIC").read_bytes())
for f in ("START.TOS", "LS2DD.FIC", "D15R_H5.FIC", "D15R_F5.FIC"):
    d = (tree / f).read_bytes()
    print(f"{f:12} {len(d):6} bytes  sha256 {hashlib.sha256(d).hexdigest()[:16]}")
for k in ref:
    print(f"  {k:12} unpacks to {'the same bytes as PP' if ours[k] == ref[k] else 'OTHER bytes than PP'}'s")
EOF
echo "built: $tree"
