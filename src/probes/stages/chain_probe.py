#!/usr/bin/env python3
"""The launch chain on the PPDRIVER reference, one memory
dump per stage at its entry.

Usage: chain_probe.py <setup>      (setup: st-104|ste-162|ste-206)

The stages and how each is caught (addresses from gate_probe.py's runs and from the stub's
own code, tools/dev/builds/stages/start_text.lst):
  stub     START.TOS's text, entered at the text base (BASES, as in gate_probe.py)
  jmp      the stub's unpacker copies itself to text+$8D40 and jumps into the
           unpacked program from text+$8DF2 (its `jmp (a0)`)
  lemld2   the unpacked program, at the same text base, its header 28 bytes
           below
  d15r     the first instruction run in D15R ($C0100-$D6543, 91,460 bytes)
  block    $80100, 1,600 bytes LEMLD2 copies from its text+$604: unpacks LS2DD
           from $81000, copies the loader to $85000, patches LS2DD, starts it
  ls2dd    $7005A, LS2DD's entry ($70000, 7,168 bytes)
  loader   $85000, 904 bytes from block+$30E, PP's replacement for the game's
           floppy loader
  handover the first instruction below $12000 after LS2DD started: the game
           (found at $400, in what was TOS's system variables)

Each dump is a savebin into the run folder; tools/dev/logs/<run>/hatari.out
holds the registers at every stop. Runs the reference expectations
(reference-first-level.exp), so the run also says how far the boot went.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BASES = {"st-104": 0x17A88, "ste-162": 0x17A68, "ste-206": 0x1D2E4}
QUIET = "gemdos,bios,xbios,scsi_cmd"


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in BASES:
        sys.exit(f"usage: {sys.argv[0]} <st-104|ste-162|ste-206>")
    setup = sys.argv[1]
    base = BASES[setup]
    out = REPO / "tools" / "dev" / "builds" / "stages" / f"chain-{setup}"
    out.mkdir(parents=True, exist_ok=True)
    h = lambda v: f"${v:x}"  # noqa: E731

    files = {
        "chain.dbg": [f"b pc = {h(base)} :once :trace :file 1-stub.ini"],
        "1-stub.ini": ["r", f"savebin stub-basepage.bin {h(base - 256)} 256",
                       f"savebin stub.bin {h(base)} 9074",
                       f"b pc = {h(base + 0x8DF2)} :once :trace :file 2-jmp.ini"],
        "2-jmp.ini": ["r", "d pc 1",
                      f"b pc = {h(base)} :once :trace :file 3-lemld2.ini"],
        "3-lemld2.ini": ["r", f"savebin lemld2-basepage.bin {h(base - 256)} 256",
                         f"savebin lemld2.bin {h(base - 28)} {28 + 34910}",
                         "b pc > $c00ff && pc < $d6544 :once :trace :file 4-d15r.ini",
                         "b pc = $80100 :once :trace :file 5-block.ini",
                         "b pc = $85000 :once :trace :file 5-loader.ini",
                         "b pc = $7005a :once :trace :file 6-ls2dd.ini"],
        "4-d15r.ini": ["r", "d pc 4", "savebin d15r.bin $c0100 91460",
                       "savebin lowmem-d15r.bin 0 $1000"],
        "5-block.ini": ["r", "d pc 8", "savebin block.bin $80100 1600",
                         "savebin ls2dd-packed.bin $81000 4929"],
        "5-loader.ini": ["r", "d pc 8", "savebin loader.bin $85000 904"],
        "6-ls2dd.ini": ["r", "d pc 4", "savebin ls2dd.bin $70000 7168",
                        "savebin lowmem-ls2dd.bin 0 $1000",
                        "b pc = $8014c :once :trace :file 6-start-game.ini",
                        "b pc < $12000 :once :trace :file 7-handover.ini"],
        "6-start-game.ini": ["r", "d pc 4"],
        "7-handover.ini": ["r", "d pc 8", "savebin lowmem-handover.bin 0 $1000",
                           "savebin game-handover.bin $a00 $5f600",
                           "savebin high-handover.bin $af000 $28000"],
    }
    for name, lines in files.items():
        (out / name).write_text("\n".join(lines) + "\n")

    cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"),
           "--setup", setup, "--disk", "ppdriver", "--parse", str(out / "chain.dbg"),
           "--expect", str(REPO / "tools" / "dev" / "expect" / "reference-first-level.exp"),
           "--name", "chain"]
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
