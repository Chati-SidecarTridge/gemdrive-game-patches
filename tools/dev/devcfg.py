"""tools/dev/devcfg.py: read tools/dev/dev.cfg from Python, as devcfg.sh does
from the shell."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def cfg(key: str) -> str:
    """The value of key in dev.cfg, a relative path made absolute against the
    repository root. Stops with a message when dev.cfg or the key is missing."""
    path = HERE / "dev.cfg"
    if not path.is_file():
        sys.exit(f"error: {path} missing: copy tools/dev/dev.cfg.example to it and adjust")
    value = None
    for line in path.read_text().splitlines():
        if line.startswith(key + "="):
            value = line[len(key) + 1:]
    if not value:
        sys.exit(f"error: {key} is not set in {path}")
    return value if value.startswith("/") else str(REPO / value)
