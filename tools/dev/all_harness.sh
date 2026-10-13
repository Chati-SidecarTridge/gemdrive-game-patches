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
#   2b. the launcher's sources (EPIC-02 STORY-04): each reassembles to the
#      stage tools/unpack.py takes out of LEMMINGS/ (tools/dev/roundtrip.sh),
#      and still says the same with a nop inserted (tools/dev/shiftcheck.py)
#   3. tools/dev/hatari_harness.py with expect/launcher-start.exp on every
#      setup: ST TOS 1.04, STE TOS 1.62, STE TOS 2.06, each in GEMDRIVE mode
#      and from the PPDRIVER image
#   4. expect/must-fail.exp, which the harness must report as FAIL
#   5. the launcher built from src/ (tools/build_launcher.sh, EPIC-02 STORY-06): every stage
#      unpacks to PP's bytes, and it boots the PPDRIVER reference to the level load on ST TOS
#      1.04 (expect/reference-first-level.exp); the disks are rebuilt from LEMMINGS/ after
#   6. LEMMINGS/ against LEMMINGS.sha256, and no Hatari left running
#   7. the website (EPIC-03 STORY-07): tools/site/build_site.py --check from the working tree,
#      and from a fresh clone of the last commit without the snapshots
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

# 2b. The launcher's sources: round trip and nop check for every stage. D15R's are not
# committed (D-13): made from their maps first.
"$repo/tools/make_sources.sh" > "$work/make-sources.txt" 2>&1 || row "D15R's sources made" FAIL "see $work/make-sources.txt" 0
refs="$work/refs"
mkdir -p "$refs"
python3 -I tools/unpack.py text LEMMINGS/START.TOS "$refs/START.text" > /dev/null
python3 -I tools/unpack.py start LEMMINGS/START.TOS "$refs/LEMLD2.TOS" > /dev/null
for f in LS2DD D15R_H5 D15R_F5; do
  python3 -I tools/unpack.py fic "LEMMINGS/$f.FIC" "$refs/$f.bin" > /dev/null
done
for stage in "start src/start/start.s START.text 0" \
             "lemld2 src/lemld2/lemld2.s LEMLD2.TOS 0 --tos" \
             "ls2dd src/ls2dd/ls2dd.s LS2DD.bin 0x70000" \
             "d15r_h5 src/d15r/d15r_h5.s D15R_H5.bin 0xc0100" \
             "d15r_f5 src/d15r/d15r_f5.s D15R_F5.bin 0xc0100"; do
  read -r name src ref origin tos <<< "$stage"
  t=$SECONDS
  if "$here/roundtrip.sh" $tos "$src" "$refs/$ref" > "$work/rt-$name.txt" 2>&1 \
     && python3 -I "$here/shiftcheck.py" $tos "$src" "$origin" > "$work/shift-$name.txt" 2>&1; then
    row "source $name" PASS "$(sed -E 's/^PASS [^:]*: ([0-9]+) bytes.*/\1 bytes/' "$work/rt-$name.txt"), nop check: every reference moves" $((SECONDS - t))
  else
    row "source $name" FAIL "see $work/rt-$name.txt, shift-$name.txt" $((SECONDS - t))
  fi
done

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

# 5. The launcher built from the sources boots the reference.
t=$SECONDS
out="$work/build-launcher.txt"
if "$repo/tools/build_launcher.sh" > "$out" 2>&1 && [[ $(grep -c "the same bytes as PP" "$out") -eq 4 ]] \
   && "$here/make_disks.sh" "$here/builds/launcher/LEMMINGS" > /dev/null 2>&1; then
  python3 -I "$here/hatari_harness.py" --setup st-104 --disk ppdriver --name built \
    --expect "$here/expect/reference-first-level.exp" > "$work/built-run.txt" 2>&1
  summary="$(grep -E '^(PASS|FAIL) ' "$work/built-run.txt" | tail -1)"
  result="${summary%% *}"
  detail="$(sed -E 's/^(PASS|FAIL) [^:]*: //; s/, [0-9.]+ s$//' <<< "$summary")"
  row "launcher built from src/" "${result:-FAIL}" "4 stages as PP's; st-104: ${detail:-see $work/built-run.txt}" $((SECONDS - t))
else
  row "launcher built from src/" FAIL "see $out" $((SECONDS - t))
fi
"$here/make_disks.sh" > /dev/null 2>&1 || row "disks back from LEMMINGS/" FAIL "make_disks.sh" 0

# 6. The evidence, and no Hatari left.
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

# 7. The website, from the working tree and from a fresh clone.
site_detail() { sed -nE 's/^check: ([0-9]+ pages), [0-9]+ links, ([0-9]+ of [0-9]+ games), 0 problem.*/\1, \2/p' "$1"; }
t=$SECONDS
if python3 -I tools/site/build_site.py --check > "$work/site.txt" 2>&1; then
  row "site" PASS "$(site_detail "$work/site.txt")" $((SECONDS - t))
else
  row "site" FAIL "see $work/site.txt" $((SECONDS - t))
fi
t=$SECONDS
if git clone -q --no-local "$repo" "$work/clone" > "$work/clone-site.txt" 2>&1 \
   && python3 -I "$work/clone/tools/site/build_site.py" --out "$work/clone-site" --no-snapshots --check \
        >> "$work/clone-site.txt" 2>&1; then
  row "site from a fresh clone" PASS "$(site_detail "$work/clone-site.txt"), last commit" $((SECONDS - t))
else
  row "site from a fresh clone" FAIL "see $work/clone-site.txt" $((SECONDS - t))
fi

printf '%s\n' "${rows[@]}"
echo "total $((SECONDS - t0)) s, $failures failure(s)"
[[ $failures -eq 0 ]]
