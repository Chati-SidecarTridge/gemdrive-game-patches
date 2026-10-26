#!/usr/bin/env python3
"""What the SidecarTridge Multidevice's GEMDRIVE would find in RAM when GOS's
file requests reach it, from Hatari's GEMDOS drive (which needs none of it).

Usage: multidevice_probe.py [<setup>] [--memsize N] [--stack ADDR ...]
       (setup: st-104|ste-162|ste-206, default ste-162)

The Multidevice's TRAP #1 handler (../md-drives-emulator/target/atarist/src/gemdrive.s) reads,
for a call it serves: _dskbufp ($4C6), and writes 20 bytes at its target + $100 (Fread);
_sysbase ($4F2), the OS header's os_beg and os_run, and the basepage os_run points to (Fopen,
Fcreate); the current drive, with a nested Dgetdrv (Dsetpath, and Fopen with no drive letter);
and it runs on a 1 KB stack it Mallocs at boot, near _membot. So the probe logs:
  entry   START.TOS's first instruction: the machine's _membot, _memtop, _drvbits, _dskbufp,
          _sysbase, TRAP #1
  fwd     gd_forward ($B7180), each call: the registers, the call on the stack, and the same
          variables in GOS's image, then in low RAM, with the OS header and the basepage
and gemdrive-first-level.exp runs to the first level's load. The log is tools/dev/logs/<run>/
hatari.out. With --stack, each call also dumps the 1 KB at ADDR and then fills it with ILLEGAL
($4AFC): what GEMDRIVE's own stack, if it were there, could leave in the game's RAM, at worst.
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("setup", nargs="?", default="ste-162", choices=("st-104", "ste-162", "ste-206"))
    ap.add_argument("--memsize", type=int, default=1)
    ap.add_argument("--stack", action="append", default=[], type=lambda v: int(v, 0))
    a = ap.parse_args()
    out = REPO / "tools" / "dev" / "builds" / "gos5" / f"multidevice-{a.setup}"
    out.mkdir(parents=True, exist_ok=True)
    junk = out / "illegal.bin"
    junk.write_bytes(b"\x4a\xfc" * 512)
    stacks = [line for addr in a.stack for line in (f"m ${addr:x} 1024", f"l {junk} ${addr:x}")]
    build = REPO / "tools" / "dev" / "builds" / "gemdrive"
    subprocess.run([str(REPO / "tools" / "build_gemdrive.sh"), str(build)], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run([str(REPO / "tools" / "dev" / "make_disks.sh"), str(build / "build" / "LEMMINGS"),
                    str(out / "disks")], check=True, stdout=subprocess.DEVNULL)
    variables = ["m $430 8", "m $4c0 8", "m $4f0 4", "m $84 4", "m $59e 2"]
    files = {
        "calls.dbg": ["b GemdosOpcode = 0x4B && OsCallParam = 0x0 :once :file pexec.ini",
                      "b pc = $b7180 :trace :file fwd.ini"],
        "pexec.ini": ["b pc = TEXT :once :file entry.ini"],
        "entry.ini": variables,
        "fwd.ini": ["r", "m a7 16", *variables,
                    'm "($4f2).l" 48',            # the OS header _sysbase points to
                    'm "(($4f2).l+8).l" 48',      # os_beg's
                    'm "(((($4f2).l+8).l+$28).l).l" 64',  # the basepage at os_run
                    *stacks],
    }
    for name, lines in files.items():
        (out / name).write_text("\n".join(lines) + "\n")
    cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"),
           "--setup", a.setup, "--disk", "gemdrive", "--drive", str(out / "disks" / "gemdrive"),
           "--memsize", str(a.memsize), "--parse", str(out / "calls.dbg"),
           "--expect", str(REPO / "tools" / "dev" / "expect" / "gemdrive-first-level.exp"),
           "--name", "multidevice" + ("-stack" if a.stack else "")]
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
