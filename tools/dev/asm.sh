#!/usr/bin/env bash
#
# tools/dev/asm.sh: assemble a vasm (Motorola syntax) source into a raw binary,
# in the pinned toolchain (EPIC-00 STORY-02, D-05).
#
# Usage: tools/dev/asm.sh <source.s> <out.bin> [<listing>]
#
# Always 68000, raw binary output (-Fbin), and no optimisation (-no-opt), so
# every instruction keeps the encoding it was written with. Every error is
# reported, not only the first five. With a third argument, vasm also writes
# its listing there (-L). The source is assembled from a fresh copy
# (tc_stage), with its own folder on the include path.
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "usage: $0 <source.s> <out.bin> [<listing>]" >&2
  exit 2
fi
src=$1 out=$2 lst=${3:-}

source "$(dirname "${BASH_SOURCE[0]}")/toolchain.sh"
tc_require
[[ -f "$src" ]] || { echo "error: no such file: $src" >&2; exit 1; }

args=(-quiet -m68000 -Fbin -no-opt -maxerrors=0 -o "$(tc_path "$out")")
args+=(-I "$(tc_path "$(dirname "$src")/.")")
[[ -n "$lst" ]] && args+=(-L "$(tc_path "$lst")")
trap tc_unstage EXIT
tc_stage "$src"
tc_run vasmm68k_mot "${args[@]}" "$(tc_path "$TC_STAGED")"
