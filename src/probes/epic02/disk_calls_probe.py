#!/usr/bin/env python3
"""EPIC-02 STORY-05: every call into the disk layer from the hand-over to the level load,
on the PPDRIVER reference.

Usage: disk_calls_probe.py [<setup>]      (setup: st-104|ste-162|ste-206, default st-104)

From the game's first instruction ($400) on, :trace breakpoints log, each time:
  loader     $85000  PP's loader (src/lemld2/lemld2.s `loader`): the name at a0, a1, d1
  file_io    $C0170  D15R's entry 2: its parameters at $C0730
  file_io_2  $C02CA  D15R's entry 4: the same
  hdv_bpb    $B718C  the driver copy's entries (EPIC-01: the copy at $B7180), with the
  hdv_rw     $B71C2  stack: hdv_rw's (rwflag, buffer, count, recno, drive)
  hdv_media  $B75BE
and reference-first-level.exp runs to the level load. tools/dev/logs/<run>/hatari.out holds
the log; disk_calls_report.py turns it into a table.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BASES = {"st-104": 0x17A88, "ste-162": 0x17A68, "ste-206": 0x1D2E4}


def main() -> int:
    setup = sys.argv[1] if len(sys.argv) > 1 else "st-104"
    if setup not in BASES:
        sys.exit(f"usage: {sys.argv[0]} [st-104|ste-162|ste-206]")
    out = REPO / "tools" / "dev" / "builds" / "epic02" / f"disk-calls-{setup}"
    out.mkdir(parents=True, exist_ok=True)
    files = {
        "calls.dbg": ["b pc = $400 :once :trace :file arm.ini"],
        "arm.ini": ["b pc = $85000 :trace :file loader.ini",
                    "b pc = $c0170 :trace :file file_io.ini",
                    "b pc = $c02ca :trace :file file_io_2.ini",
                    "b pc = $b718c :trace :file hdv_bpb.ini",
                    "b pc = $b71c2 :trace :file hdv_rw.ini",
                    "b pc = $b75be :trace :file hdv_media.ini"],
        "loader.ini": ["r", "m a0 16"],
        "file_io.ini": ["m $c0730 64"],
        "file_io_2.ini": ["m $c0730 64"],
        "hdv_bpb.ini": ["m a7 8"],
        "hdv_rw.ini": ["m a7 16"],
        "hdv_media.ini": ["m a7 8"],
    }
    for name, lines in files.items():
        (out / name).write_text("\n".join(lines) + "\n")
    cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"),
           "--setup", setup, "--disk", "ppdriver", "--parse", str(out / "calls.dbg"),
           "--expect", str(REPO / "tools" / "dev" / "expect" / "reference-first-level.exp"),
           "--name", "disk-calls", "--step-time", "120"]
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
