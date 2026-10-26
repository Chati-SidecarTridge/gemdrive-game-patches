#!/usr/bin/env bash
#
# tools/dev/disasm.sh: disassemble a raw binary loaded at a given address, in
# the pinned toolchain.
#
# Usage: tools/dev/disasm.sh <bin> <vma> <out> [arch]
#
#   bin   raw binary (no header: the bytes as they sit in memory); the container
#         reads a fresh copy of it (tc_stage), so it may be anywhere
#   vma   address of its first byte, e.g. 0x70000
#   out   listing to write (objdump -D -z, GNU syntax; -z so that runs of zero
#         bytes are listed, not hidden behind "...")
#   arch  BFD architecture, default m68k:68000, so that bytes that are not a
#         68000 instruction show as .short; m68k decodes 68020+ too, as the
#         first pass did
set -euo pipefail

if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "usage: $0 <bin> <vma> <out> [arch]" >&2
  exit 2
fi
bin=$1 vma=$2 out=$3 arch=${4:-m68k:68000}

source "$(dirname "${BASH_SOURCE[0]}")/toolchain.sh"
tc_require
[[ -f "$bin" ]] || { echo "error: no such file: $bin" >&2; exit 1; }
trap tc_unstage EXIT
tc_stage "$bin"
inner="$(tc_path "$TC_STAGED")"

# The listing comes back on stdout and is written by the host, with the file
# named as given rather than as staged.
tc_run m68k-atari-mint-objdump -D -z -b binary -m "$arch" --adjust-vma="$vma" "$inner" \
  | sed "s|$inner|$bin|" > "$out"
