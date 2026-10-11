#!/usr/bin/env bash
#
# tools/dev/make_disks.sh: build the two disk setups the harness boots, from a
# copy of the game folder and never from LEMMINGS/ itself (EPIC-00 STORY-04,
# C-01).
#
# Usage: tools/dev/make_disks.sh [<game folder>]
#
#   <game folder>  default LEMMINGS/; or a patched or rebuilt tree with the
#                  same layout
#
# Writes tools/dev/builds/disks/ (emptied first):
#   gemdrive/LEMMINGS/  the folder Hatari mounts as drive C: in GEMDRIVE mode
#                       (--harddrive gemdrive)
#   ppdriver.img        the working reference (D-09): a 32 MB ACSI image with
#                       one partition, booted by PPDRIVER, made by ../atari-hd
#                       --ppdriver-bootable, with the same folder copied in
#   SOURCE.txt          where the game came from, and the SHA-256 of every file
#
# Both disks also get tools/dev/DESKTOP.INF at their root: a TOS 1.04 desktop
# that opens a window on C:\LEMMINGS (the first pass's DESKTOP.INF, unchanged).
#
# macOS files (.DS_Store) are left out. File dates are kept. The image is
# checked by copying everything back out and comparing every SHA-256.
set -euo pipefail

if [[ $# -gt 1 ]]; then
  echo "usage: $0 [<game folder>]" >&2
  exit 2
fi
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$here/../.." && pwd)"
source "$here/devcfg.sh"
src="$(cd "${1:-$repo/LEMMINGS}" && pwd)"
atari_hd="$(cfg ATARI_HD)"
[[ -f "$atari_hd/atari_hd.py" ]] || { echo "error: no atari_hd.py in $atari_hd" >&2; exit 1; }
for tool in mcopy mdir rsync; do
  command -v "$tool" >/dev/null || { echo "error: $tool not found (mtools, rsync)" >&2; exit 1; }
done
export MTOOLS_SKIP_CHECK=1

out="$repo/tools/dev/builds/disks"
rm -rf "$out"
mkdir -p "$out/gemdrive"

# GEMDRIVE: the folder, as it is on a disk.
rsync -a --exclude .DS_Store "$src/" "$out/gemdrive/LEMMINGS/"
cp "$here/DESKTOP.INF" "$out/gemdrive/DESKTOP.INF"
(cd "$out/gemdrive" && find LEMMINGS -type f | LC_ALL=C sort | xargs shasum -a 256) > "$out/SOURCE.sha256"
{
  echo "source: $src"
  echo "built:  $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "files:  $(wc -l < "$out/SOURCE.sha256" | tr -d ' ')"
} > "$out/SOURCE.txt"
cat "$out/SOURCE.sha256" >> "$out/SOURCE.txt"
rm "$out/SOURCE.sha256"

# PPDRIVER: atari-hd asks for the file name and a confirmation even without
# its TUI; one 32 MB partition (512-byte DOS sectors, 1024-byte TOS sectors).
(cd "$out" && printf 'ppdriver.img\ny\n' | python3 -I "$atari_hd/atari_hd.py" --no-tui \
  --ppdriver-bootable --size 32 --auto default --auto-n 1 > atari-hd.log)
# The partition's first sector, from the MBR's first entry (little-endian).
lba=$(python3 -I -c 'import sys; d = open(sys.argv[1], "rb").read(512)
assert d[510:512] == b"\x55\xaa", "no MBR"
print(int.from_bytes(d[0x1C6:0x1CA], "little"))' "$out/ppdriver.img")
img="$out/ppdriver.img@@$((lba * 512))"
mcopy -s -m -i "$img" "$out/gemdrive/LEMMINGS" "$out/gemdrive/DESKTOP.INF" ::/

# Check: everything back out of the image, compared file by file.
check="$out/check"
mkdir -p "$check"
mcopy -s -n -i "$img" ::/LEMMINGS "$check/"
if ! diff <(cd "$out/gemdrive" && find LEMMINGS -type f | LC_ALL=C sort | xargs shasum -a 256) \
          <(cd "$check" && find LEMMINGS -type f | LC_ALL=C sort | xargs shasum -a 256); then
  echo "error: the image does not hold the same files as gemdrive/LEMMINGS" >&2
  exit 1
fi
rm -rf "$check"

n=$(cd "$out/gemdrive" && find LEMMINGS -type f | wc -l | tr -d ' ')
echo "gemdrive: $out/gemdrive (C:\\LEMMINGS, $n files)"
echo "ppdriver: $out/ppdriver.img (partition at LBA $lba, same $n files, checked)"
