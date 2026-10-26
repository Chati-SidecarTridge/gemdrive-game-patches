#!/usr/bin/env python3
"""Every address the CPU executes from LEMLD2's entry to the
level load on the PPDRIVER reference, from Hatari's CPU profiler.

Usage: profile_probe.py <setup>      (setup: st-104|ste-162|ste-206)

Profiling starts at LEMLD2's entry (the stub's second arrival at the text base,
caught as in chain_probe.py). Four profiles are saved, since Hatari starts a new
one whenever it leaves the debugger: "lemld2", to its jump to the block at $80100;
"launch", to the game's first instruction at $400; "intro", to the block's code that patches CODE once it is loaded ($801D0);
"title", to about one second into CODE's title. Hatari prints each one (its disassembly of every executed address,
with counts) into hatari.out after the `profile save` line. The addresses are what
matters: code a static trace cannot reach (vectors, pointers, decrypted protection
code) shows up there. src/probes/stages/profile_addrs.py sorts them by stage.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BASES = {"st-104": 0x17A88, "ste-162": 0x17A68, "ste-206": 0x1D2E4}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in BASES:
        sys.exit(f"usage: {sys.argv[0]} <st-104|ste-162|ste-206>")
    setup = sys.argv[1]
    base = BASES[setup]
    out = REPO / "tools" / "dev" / "builds" / "stages" / f"profile-{setup}"
    out.mkdir(parents=True, exist_ok=True)
    files = {
        "profile.dbg": [f"b pc = ${base:x} :once :trace :file 1-stub.ini"],
        "1-stub.ini": [f"b pc = ${base + 0x8DF2:x} :once :trace :file 2-jmp.ini"],
        "2-jmp.ini": [f"b pc = ${base:x} :once :trace :file 3-on.ini"],
        # Hatari compiles a profile only when it stops in the debugger, and starts
        # a new one each time it leaves it, the harness's own debugger commands
        # included. So the save is a real (not :trace) breakpoint set here: the
        # game's IKBD sender ($21A6, found by gate_probe.py) on its 50th run, at the title.
        # LEMLD2's own window ends where it jumps to the block: after that other code
        # (the game's unpacking) runs where LEMLD2 was.
        "3-on.ini": ["profile on", "b pc = $80100 :once :file save-lemld2.ini"],
        "save-lemld2.ini": ["profile save lemld2.txt", "b pc = $400 :once :file save-launch.ini", "c"],
        # block+$D0 ($801D0) patches CODE once it is loaded (chain_probe.py): after it,
        # the title is CODE's own and its IKBD sender at $21A6 runs once a frame.
        "save-launch.ini": ["profile save launch.txt", "b pc = $801d0 :once :file save-intro.ini", "c"],
        "save-intro.ini": ["profile save intro.txt", "b pc = $21a6 :50 :once :file save-title.ini", "c"],
        "save-title.ini": ["profile save title.txt", "c"],
    }
    for name, lines in files.items():
        (out / name).write_text("\n".join(lines) + "\n")
    exp = (REPO / "tools" / "dev" / "expect" / "reference-first-level.exp").read_text()
    (out / "profile.exp").write_text(exp)
    cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"),
           "--setup", setup, "--disk", "ppdriver", "--parse", str(out / "profile.dbg"),
           "--expect", str(out / "profile.exp"), "--name", "profile"]
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
