# tools/dev/devcfg.sh: sourced by the tools/dev shell scripts that need
# tools/dev/dev.cfg (EPIC-00 STORY-04). Python scripts read the same file
# through tools/dev/devcfg.py.

DEVCFG="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/dev.cfg"
DEVCFG_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# cfg <KEY>: the value of KEY in dev.cfg, a relative path made absolute against
# the repository root. Stops with a message when dev.cfg or the key is missing.
cfg() {
  local v
  if [[ ! -f "$DEVCFG" ]]; then
    echo "error: $DEVCFG missing: copy tools/dev/dev.cfg.example to it and adjust" >&2
    exit 1
  fi
  v="$(sed -n "s/^$1=//p" "$DEVCFG" | tail -1)"
  if [[ -z "$v" ]]; then
    echo "error: $1 is not set in $DEVCFG" >&2
    exit 1
  fi
  [[ "$v" == /* ]] || v="$DEVCFG_REPO/$v"
  printf '%s' "$v"
}
