#!/usr/bin/env python3
"""Probe the launcher's driver check and what follows it, on
one Hatari setup and disk, with chained single-shot breakpoints.

Usage: gate_probe.py <setup> <disk>      (setup: st-104|ste-162|ste-206)

The launcher's inner program (LEMLD2, text+0x000..) is relocated by START.TOS
to an address that depends on the setup and the disk (the driver's resident
size moves the TPA). It is deterministic per setup and disk: BASES below were
read from the harness's first runs as the PC Hatari reports for the launcher's Dgetpath
trap (the return address) minus 2 minus the trap's text offset $31A. Every
breakpoint below disassembles the live machine (`d pc`), so a wrong base shows
as wrong instructions rather than as a wrong conclusion.

Offsets (text+) come from the first pass's listing and are checked the same
way:
  $324  movea.l $472.w,a1        a1 = hdv_bpb (the resident driver's BPB routine)
  $328  cmpi.l #"PPHD",-8(a1)    the signature 8 bytes before it
  $330  bne.w $482               no signature: the fallback
  $334  primary path: the resident PP driver is reused
  $482  fallback: TOS major < 2 -> raw ACSI ($BC6); else XBIOS DMAread ($49E)
  $BE8  ACSI command submitted through the DMA registers; $C90 polls the MFP
  $CC0  IDE probe, with a bus-error handler at $D2E
  $83C  error exit

Writes the debugger files into tools/dev/builds/gemdrive-failure/<setup>-<disk>/ and
runs tools/dev/hatari_harness.py with them (run folder in tools/dev/logs/).
CPU and I/O tracing are switched on only inside bounded windows, never across
a polling loop.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BASES = {
    ("st-104", "gemdrive"): 0xF196, ("st-104", "ppdriver"): 0x17A88,
    ("ste-162", "gemdrive"): 0xF176, ("ste-162", "ppdriver"): 0x17A68,
    ("ste-206", "gemdrive"): 0x149F2, ("ste-206", "ppdriver"): 0x1D2E4,
}
QUIET = "gemdos,bios,xbios,scsi_cmd"
LOUD = QUIET + ",cpu_disasm,io_read,io_write"


def main() -> int:
    if len(sys.argv) != 3 or (sys.argv[1], sys.argv[2]) not in BASES:
        sys.exit(f"usage: {sys.argv[0]} <st-104|ste-162|ste-206> <gemdrive|ppdriver>")
    setup, disk = sys.argv[1], sys.argv[2]
    base = BASES[(setup, disk)]
    out = REPO / "tools" / "dev" / "builds" / "gemdrive-failure" / f"{setup}-{disk}"
    out.mkdir(parents=True, exist_ok=True)

    def at(off: int) -> str:
        return f"${base + off:x}"

    files = {
        "gate.dbg": [f"b GemdosOpcode = $47 :once :trace :file 1-dgetpath.ini"],
        "1-dgetpath.ini": ["m $472 16", "m $516 4", "m $4c2 4",
                           f"b pc = {at(0x328)} :once :trace :file 2-cmp.ini"],
        "2-cmp.ini": ["r", "d pc 3", "m a1-8 16", f"m {at(0x832)} 8",
                      f"b pc = {at(0x330)} :once :trace :file 3-bne.ini"],
        "3-bne.ini": ["d pc 2", "r",
                      f"b pc = {at(0x334)} :once :trace :file 4-primary.ini",
                      f"b pc = {at(0x482)} :once :trace :file 4-fallback.ini"],
        # Primary path: trace every instruction up to the first Rwabs.
        "4-primary.ini": ["d pc 4", f"trace {LOUD}",
                          "b BiosOpcode = 4 :once :trace :file 9-first-rwabs.ini"],
        "9-first-rwabs.ini": [f"trace {QUIET}", "r", "m $472 16", "m $516 4"],
        # Fallback: trace the decision and the command submission, not the polling.
        "4-fallback.ini": ["d pc 4", f"trace {LOUD}",
                           f"b pc = {at(0x49E)} :once :trace :file 5-dmaread.ini",
                           f"b pc = {at(0xBC6)} :once :trace :file 5-acsi.ini",
                           f"b pc = {at(0x83C)} :once :trace :file 8-error.ini",
                           "b GemdosOpcode = 9 :once :trace :file 9-cconws.ini"],
        "5-dmaread.ini": ["d pc 8",
                          f"b pc = {at(0x4BA)} :once :trace :file 6-off.ini",
                          f"b pc = {at(0x4BC)} :once :trace :file 6-dmaread-back.ini"],
        "6-dmaread-back.ini": [f"trace {LOUD}", "r",
                               f"b pc = {at(0x4CE)} :once :trace :file 7-sum.ini"],
        "5-acsi.ini": ["d pc 8",
                       f"b pc = {at(0xBE8)} :once :trace",
                       f"b pc = {at(0xC68)} :once :trace :file 6-dma-go.ini",
                       f"b pc = {at(0xC90)} :once :trace :file 6-off.ini",
                       f"b pc = {at(0xBD4)} :once :trace :file 6-acsi-back.ini"],
        "6-dma-go.ini": ["r", "d pc 2"],
        "6-off.ini": [f"trace {QUIET}", "r"],
        "6-acsi-back.ini": [f"trace {LOUD}", "r",
                            f"b pc = {at(0xBE0)} :once :trace :file 7-sum.ini"],
        "7-sum.ini": ["r", "d pc 2",
                      f"b pc = {at(0xCC0)} :once :trace :file 7-ide.ini"],
        "7-ide.ini": ["d pc 6", "m $8 4",
                      f"b pc = {at(0xD2E)} :once :trace :file 7-buserr.ini"],
        "7-buserr.ini": ["r", "d pc 4"],
        "8-error.ini": ["r", "d pc 4"],
        "9-cconws.ini": [f"trace {QUIET}", "r"],
    }
    for name, lines in files.items():
        (out / name).write_text("\n".join(lines) + "\n")

    cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"),
           "--setup", setup, "--disk", disk, "--parse", str(out / "gate.dbg"),
           "--expect", str(REPO / "tools" / "dev" / "expect" / "launcher-start.exp"),
           "--name", "gate"]
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
