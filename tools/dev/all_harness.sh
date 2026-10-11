#!/usr/bin/env bash
#
# tools/dev/all_harness.sh: check the whole development environment in one go
# (EPIC-00 STORY-06).
#
# Usage: tools/dev/all_harness.sh
#
#   1. tools/dev/make_disks.sh: both disk setups from LEMMINGS/
#   2. the round trip: the text of START.TOS disassembled, turned into a vasm
#      source and reassembled to the same 230 bytes
#   3. tools/dev/hatari_harness.py with expect/launcher-start.exp on every
#      setup: ST TOS 1.04, STE TOS 1.62, STE TOS 2.06, each in GEMDRIVE mode
#      and from the PPDRIVER image
#   4. expect/must-fail.exp, which the harness must report as FAIL
#   5. LEMMINGS/ against LEMMINGS.sha256, and no Hatari left running
#
# Prints one line per check and exits 0 only when every check gave what it
# must. Each harness run keeps its folder under tools/dev/logs/.
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$here/../.." && pwd)"
cd "$repo"
work="$here/builds/all"
rm -rf "$work"
mkdir -p "$work"
failures=0
rows=()
t0=$SECONDS

row() {  # row <check> <result> <detail> <seconds>
  rows+=("$(printf '%-28s %-5s %-44s %5ss' "$1" "$2" "$3" "$4")")
  [[ "$2" == PASS ]] || failures=$((failures + 1))
}

# 1. Disks.
t=$SECONDS
if "$here/make_disks.sh" > "$work/make_disks.txt" 2>&1; then
  row "disks" PASS "gemdrive + ppdriver.img, $(grep -c '' < <(sed -n '/^[0-9a-f]\{64\}/p' "$here/builds/disks/SOURCE.txt")) files" $((SECONDS - t))
else
  row "disks" FAIL "see $work/make_disks.txt" $((SECONDS - t))
  printf '%s\n' "${rows[@]}"
  exit 1
fi

# 2. Round trip on the START.TOS text (file offsets 28 to 257).
t=$SECONDS
python3 -I -c 'import sys; open(sys.argv[2], "wb").write(open(sys.argv[1], "rb").read()[28:28 + 0xE6])' \
  LEMMINGS/START.TOS "$work/start_tos.text.bin"
if "$here/disasm.sh" "$work/start_tos.text.bin" 0 "$work/start_tos.text.lst" \
   && python3 -I "$here/listing2vasm.py" "$work/start_tos.text.lst" "$work/start_tos.text.bin" \
        "$work/start_tos.text.s" > "$work/listing2vasm.txt" \
   && "$here/roundtrip.sh" "$work/start_tos.text.s" "$work/start_tos.text.bin" > "$work/roundtrip.txt"; then
  row "round trip START.TOS text" PASS "$(cut -d: -f2 "$work/roundtrip.txt" | cut -c2-44)" $((SECONDS - t))
else
  row "round trip START.TOS text" FAIL "see $work/" $((SECONDS - t))
fi

# 3. The launcher on every setup.
for setup in st-104 ste-162 ste-206; do
  for disk in gemdrive ppdriver; do
    t=$SECONDS
    out="$work/$setup-$disk.txt"
    python3 -I "$here/hatari_harness.py" --setup "$setup" --disk "$disk" \
      --expect "$here/expect/launcher-start.exp" > "$out" 2>&1
    summary="$(grep -E '^(PASS|FAIL) ' "$out" | tail -1)"
    result="${summary%% *}"
    detail="$(sed -E 's/^(PASS|FAIL) [^:]*: //; s/, [0-9.]+ s$//' <<< "$summary")"
    row "$setup $disk" "${result:-FAIL}" "${detail:-see $out}" $((SECONDS - t))
  done
done

# 4. The harness must fail when a step cannot happen.
t=$SECONDS
out="$work/must-fail.txt"
python3 -I "$here/hatari_harness.py" --setup st-104 --disk gemdrive --step-time 10 \
  --expect "$here/expect/must-fail.exp" --name must-fail > "$out" 2>&1
if [[ $? -ne 0 ]] && grep -q "step never" "$out" && grep -q "shots/fail.png" "$out"; then
  row "harness detects a failure" PASS "FAIL at step never, with a screenshot" $((SECONDS - t))
else
  row "harness detects a failure" FAIL "see $out" $((SECONDS - t))
fi

# 5. The evidence, and no Hatari left.
if shasum -a 256 -c LEMMINGS.sha256 > "$work/evidence.txt" 2>&1; then
  row "LEMMINGS.sha256" PASS "$(grep -c ': OK$' "$work/evidence.txt") files unchanged" 0
else
  row "LEMMINGS.sha256" FAIL "see $work/evidence.txt" 0
fi
if pgrep -x hatari > /dev/null; then
  row "no Hatari left" FAIL "$(pgrep -x hatari | wc -l | tr -d ' ') still running" 0
else
  row "no Hatari left" PASS "" 0
fi

printf '%s\n' "${rows[@]}"
echo "total $((SECONDS - t0)) s, $failures failure(s)"
[[ $failures -eq 0 ]]
