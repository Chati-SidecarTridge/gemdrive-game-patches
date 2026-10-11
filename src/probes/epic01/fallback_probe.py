#!/usr/bin/env python3
"""EPIC-01 STORY-03/04: on a GEMDRIVE setup, answer the launcher's sector-0
read by hand and see how far it gets, with the pristine files (nothing on
the disk is patched; the debugger changes registers and memory at run time).

Usage: fallback_probe.py <setup> [--synthetic] [--bpb]   (setup: st-104|ste-162|ste-206)

At the instruction after the fallback's sector read (raw ACSI on TOS 1.x,
XBIOS DMAread on TOS 2.x) the probe sets d0 = 0 (success) and loads a 512-byte
sector into the launcher's buffer whose 16-bit words sum to $1234, the
executable-boot-sector mark the launcher checks for. Then it traces every
instruction (cpu_disasm, io) until the launcher's next OS call or its error
exit, switching the trace off inside the ACSI polling loop. Files go to
tools/dev/builds/epic01/fallback-<setup>/; the run folder to tools/dev/logs/.
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_probe import BASES, LOUD, QUIET  # noqa: E402

REPO = Path(__file__).resolve().parents[3]


def main() -> int:
    if len(sys.argv) < 2 or (sys.argv[1], "gemdrive") not in BASES:
        sys.exit(f"usage: {sys.argv[0]} <st-104|ste-162|ste-206> [--synthetic]")
    setup = sys.argv[1]
    base = BASES[(setup, "gemdrive")]
    out = REPO / "tools" / "dev" / "builds" / "epic01" / f"fallback-{setup}"
    out.mkdir(parents=True, exist_ok=True)

    def at(off: int) -> str:
        return f"${base + off:x}"

    # The answer: by default sector 0 of the PPDRIVER reference image, a real
    # PP boot sector (its words sum to $1234); with --synthetic, a sector whose
    # first word is $1234 and the rest zero, which also passes the sum check.
    if "--synthetic" in sys.argv:
        (out / "boot.bin").write_bytes(b"\x12\x34" + bytes(510))
    else:
        img = REPO / "tools" / "dev" / "builds" / "disks" / "ppdriver.img"
        (out / "boot.bin").write_bytes(img.read_bytes()[:512])
    (out / "bpb.bin").write_bytes(bytes.fromhex("0400 0002 0800 0010 0020 0021 0051 3fd7 0001".replace(" ", "")))
    buf = at(0x8864)
    boot = out / "boot.bin"  # absolute: the harness stages :file names, not loadbin's
    # After the answer: no instruction trace (the launcher goes on for long),
    # but every BIOS/XBIOS return through D15R's trampolines with d0, every
    # raw ACSI request, every exception, and the arguments of Getbpb/Rwabs.
    tracing = [f"trace {QUIET},cpu_exception",
               "b pc = $c83ce :trace :file 7-bios-return.ini",
               "b pc = $c83de :trace :file 7-xbios-return.ini",
               "b pc = $c83cc && BiosOpcode = 7 :trace :file 7-getbpb.ini",
               "b BiosOpcode = 4 :trace :file 7-rwabs.ini",
               # TOS 1.04's exception handler (bombs), reached through vectors
               # whose high byte is the vector number: 2 bus error, 3 address
               # error, 4 illegal instruction. The frame says where.
               "b pc = $2fc0b0a :once :trace :file 7-tos-exception.ini",
               "b pc = $3fc0b0a :once :trace :file 7-tos-exception.ini",
               "b pc = $4fc0b0a :once :trace :file 7-tos-exception.ini",
               "b GemdosOpcode = 9 :once :trace :file 9-cconws.ini",
               f"b pc = {at(0x83C)} :once :trace :file 8-error.ini",
               "b GemdosOpcode = $3d :once :trace :file 9-fopen.ini",
               "b GemdosOpcode = $4c :once :trace :file 9-pterm.ini",
               # every raw ACSI request: d1 = LBA, d2 = count, a1 = buffer
               f"b pc = {at(0xBE8)} :trace :file 5-request.ini"]
    files = {
        "fallback.dbg": ["b GemdosOpcode = $47 :once :trace :file 1-dgetpath.ini"],
        "1-dgetpath.ini": [f"b pc = {at(0x482)} :once :trace :file 2-fallback.ini"],
        "2-fallback.ini": ["d pc 4",
                           f"b pc = {at(0xBD4)} :once :trace :file 3-acsi-answer.ini",
                           f"b pc = {at(0x4BC)} :once :trace :file 3-dmaread-answer.ini"],
        # TOS 1.x: after the raw ACSI read returned (d0 = -1 in GEMDRIVE mode)
        "3-acsi-answer.ini": ["r", "r d0=0", f"loadbin {boot} {buf}", f"m {buf} 16", "r"] + tracing,
        # TOS 2.x: after XBIOS DMAread returned
        "3-dmaread-answer.ini": ["r", "r d0=0", f"loadbin {boot} {buf}", f"m {buf} 16", "r"] + tracing,
        "5-request.ini": ["r"],
        "7-bios-return.ini": ["r"],
        "7-xbios-return.ini": ["r"],
        "7-getbpb.ini": ["m a7 4"] + (
            # --bpb: answer the launcher's Getbpb(2) with PPDRIVER's BPB, read
            # from the reference run (EPIC-01 STORY-04): recsiz 1024, clsiz 2,
            # clsizb 2048, rdlen 16, fsiz 32, fatrec 33, datrec 81, numcl 16343,
            # bflags 1. Only the launcher's calls go through its trampoline at
            # $C83CC; TOS's own Getbpb(0) at boot does not.
            ["b pc = $c83ce :once :trace :file 7-bpb-answer.ini"] if "--bpb" in sys.argv else []),
        "7-bpb-answer.ini": [f"loadbin {out / 'bpb.bin'} $7f000", "r d0=$7f000", "m $7f000 18"],
        "7-tos-exception.ini": ["r", "m a7 16"],
        "7-rwabs.ini": ["m a7 16"],
        "9-pterm.ini": ["r", "m a7 8"],
        "8-error.ini": ["r", "d pc 4"],
        "9-cconws.ini": [f"trace {QUIET}", "r"],
        "9-fopen.ini": [f"trace {QUIET}", "r"],
    }
    for name, lines in files.items():
        (out / name).write_text("\n".join(lines) + "\n")

    cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"),
           "--setup", setup, "--disk", "gemdrive", "--parse", str(out / "fallback.dbg"),
           "--expect", str(REPO / "tools" / "dev" / "expect" / "launcher-start.exp"),
           "--name", "fallback"]
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
