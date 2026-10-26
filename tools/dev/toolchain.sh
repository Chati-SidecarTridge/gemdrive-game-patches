# tools/dev/toolchain.sh: sourced by every tools/dev script that runs the 68000
# toolchain. The pinned image and the helpers around it, kept in one place
# The same arrangement as the sibling repositories'
# tools/dev/toolchain.sh.

# Diego's atarist-toolkit-docker, pinned by tag and digest (the tag the
# siblings pin): vasm 2.0f (vasmm68k_mot), vlink 0.18a, binutils 2.30
# (m68k-atari-mint-objdump). `stcmd` is not used: it follows `latest`.
ATARI_IMAGE="logronoide/atarist-toolkit-docker-x86_64:1.4.0@sha256:016434131cf53f627c365e55262845fba53f30a7de87a1f122d58f8fa6aeeebe"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# tc_require: stop with a message when Docker or the pinned image is missing.
tc_require() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "error: docker not found: install Docker Desktop" >&2
    exit 1
  fi
  if ! docker info >/dev/null 2>&1; then
    echo "error: Docker is not running: start Docker Desktop" >&2
    exit 1
  fi
  if ! docker image inspect "$ATARI_IMAGE" >/dev/null 2>&1; then
    echo "error: image missing: docker pull ${ATARI_IMAGE%@*}" >&2
    exit 1
  fi
}

# tc_path <host path>: the same path inside the container, under /work. The
# file need not exist yet, but its folder must, and it must be inside the
# repository, which is the only folder the container sees.
tc_path() {
  local dir abs
  dir="$(cd "$(dirname "$1")" 2>/dev/null && pwd)" || {
    echo "error: no such folder: $(dirname "$1")" >&2
    return 1
  }
  abs="$dir/$(basename "$1")"
  case "$abs" in
    "$REPO"/*) printf '/work/%s' "${abs#"$REPO"/}" ;;
    *)
      echo "error: $1 is outside the repository ($REPO)" >&2
      return 1
      ;;
  esac
}

# tc_stage <host file>: copy the file, for a container to read, to a fresh name
# in tools/dev/builds/.stage/, and leave its path in TC_STAGED (not printed:
# called in $(...) the list would be lost to the subshell). Docker Desktop's
# file sharing can serve a container a file the host has just rewritten in
# place at its old length, cut short (seen 2026-10-11: vasm assembled a source
# truncated mid-line); a file no container has seen sidesteps it. Never next
# to the original, which may be one of the original files, never modified. tc_unstage removes the copy.
TC_STAGED=""
tc_stage() {
  mkdir -p "$REPO/tools/dev/builds/.stage"
  TC_STAGED="$REPO/tools/dev/builds/.stage/$$.$RANDOM.$(basename "$1")"
  cp "$1" "$TC_STAGED"
}
tc_unstage() {
  [[ -z "$TC_STAGED" ]] || rm -f "$TC_STAGED"
}

# tc_run <tool> [args...]: run a tool of the image with the repository mounted
# at /work, as the calling user.
tc_run() {
  docker run --rm --platform linux/x86_64 -v "$REPO:/work" -w /work \
    --user "$(id -u):$(id -g)" "$ATARI_IMAGE" "$@"
}
