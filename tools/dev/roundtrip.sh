#!/usr/bin/env bash
#
# tools/dev/roundtrip.sh: the check every reconstructed source must pass. It
# assembles the source and compares the result with the original bytes.
#
# Usage: tools/dev/roundtrip.sh [--tos] <source.s> <reference.bin>
#
# --tos assembles a GEMDOS program (tools/dev/asm.sh --tos) and compares the
# whole file, header and relocation table included.
#
# Prints PASS, or FAIL with the first differing offset, both bytes there, both
# lengths and both SHA-256. Exit 0 on PASS, 1 on FAIL or when the source does
# not assemble. The assembled binary is kept in tools/dev/builds/roundtrip/.
set -euo pipefail

tos=()
if [[ ${1:-} == --tos ]]; then
  tos=(--tos)
  shift
fi
if [[ $# -ne 2 ]]; then
  echo "usage: $0 [--tos] <source.s> <reference.bin>" >&2
  exit 2
fi
src=$1 ref=$2
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -f "$ref" ]] || { echo "error: no such file: $ref" >&2; exit 2; }

out="$here/builds/roundtrip/$(basename "${src%.*}").bin"
mkdir -p "$(dirname "$out")"
rm -f "$out"
if ! "$here/asm.sh" ${tos[@]+"${tos[@]}"} "$src" "$out"; then
  echo "FAIL $src: does not assemble"
  exit 1
fi

python3 -I - "$src" "$out" "$ref" <<'EOF'
import hashlib, sys
src, out, ref = sys.argv[1:]
a, b = open(out, "rb").read(), open(ref, "rb").read()
if a == b:
    print(f"PASS {src}: {len(a)} bytes, sha256 {hashlib.sha256(a).hexdigest()}")
    sys.exit(0)
n = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
byte = lambda d: f"{d[n]:02x}" if n < len(d) else "(end)"
print(f"FAIL {src}: first difference at offset {n:#x}: assembled {byte(a)}, original {byte(b)}")
print(f"  assembled {len(a)} bytes, sha256 {hashlib.sha256(a).hexdigest()}")
print(f"  original  {len(b)} bytes, sha256 {hashlib.sha256(b).hexdigest()}")
sys.exit(1)
EOF
