#!/usr/bin/env python3
"""Run one of PP's adaptations from the mirror, as it is, on one disk,
and report how it reached its files.

Usage: mode_probe.py <ZIP> [--disk gemdrive|ppdriver] [--setup st-104|ste-162|ste-206]
                     [--start <program>] [--monitor mono] [--memsize MB]
       mode_probe.py --report <run folder>...

<ZIP> is a file name in the mirror's site/ (dev.cfg MIRROR). The archive is unpacked
into tools/dev/builds/modes/games/<name>/ (its single top folder, if any, dropped), the
disks are built from it (make_disks.sh: it becomes C:\\LEMMINGS) and the harness starts
<program> (default: RUNME.TOS, else START.TOS, else START.PRG, in the game's root) with a
generic expectation: the program starts, then screenshots at 10 s and 30 s, the space
bar, a screenshot 15 s later.

The report, from hatari.out after the program's Pexec: every file opened by name (on the
GEMDOS drive, Hatari also says which ones it did not find), the BIOS Rwabs calls per drive,
the ACSI commands, the exceptions and CPU halts Hatari printed, the address and bus errors in
hatari.log (not the hardware probes at $F00000 and up), and the PC at the end.
"""

from __future__ import annotations

import argparse
import collections
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
GAMES = REPO / "tools" / "dev" / "builds" / "modes" / "games"
STARTS = ("RUNME.TOS", "START.TOS", "START.PRG")


def mirror() -> Path:
    for line in (REPO / "tools" / "dev" / "dev.cfg").read_text().splitlines():
        if line.startswith("MIRROR="):
            return Path(line.split("=", 1)[1].strip())
    sys.exit("error: no MIRROR in tools/dev/dev.cfg")


def unpack(zip_name: str) -> Path:
    """The archive's files under GAMES/<stem>/, without its single top folder."""
    src = mirror() / "site" / zip_name
    out = (GAMES / Path(zip_name).stem.upper()).resolve()
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    zf = zipfile.ZipFile(src)
    names = [n for n in zf.namelist() if not n.endswith("/")]
    tops = {n.split("/")[0] for n in names}
    strip = len(tops) == 1 and all("/" in n for n in names)
    for n in names:
        rel = Path(*Path(n).parts[1:]) if strip else Path(n)
        dest = (out / rel).resolve()
        if not dest.is_relative_to(out):
            sys.exit(f"error: {n} leaves the folder")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(zf.read(n))
    return out


def report(run: Path) -> str:
    text = (run / "hatari.out").read_text(errors="replace").splitlines()
    result = (run / "result.txt").read_text() if (run / "result.txt").exists() else ""
    start = next((i for i, l in enumerate(text) if l.startswith("GEMDOS 0x4B Pexec(0, \"C:\\LEMMINGS")), 0)
    opens, rwabs, acsi, exc = [], collections.Counter(), 0, []
    for i, line in enumerate(text[start:], start):
        m = re.match(r'GEMDOS 0x3D Fopen\("([^"]*)"', line) or re.match(r'GEMDOS 0x4B Pexec\(\d+, "([^"]*)"', line)
        if m:
            nxt = text[i + 1] if i + 1 < len(text) else ""
            missing = "didn't find" in nxt or "ERROR -" in nxt
            opens.append(m.group(1) + (" (not found)" if missing else ""))
        m = re.match(r"BIOS 0x04 Rwabs\((\d+),0x[0-9a-f]+,(\d+),(\d+),(\d+)\)", line, re.I)
        if m:
            rwabs[f"drive {m.group(4)} {'write' if int(m.group(1)) & 1 else 'read'}"] += 1
        if re.search(r"\bACSI\b", line):
            acsi += 1
        if re.search(r"exception|bus error|address error|illegal instruction|halt", line, re.I) and "Setexc" not in line:
            exc.append(line.strip()[:100])
    log = (run / "hatari.log").read_text(errors="replace") if (run / "hatari.log").exists() else ""
    faults = [l.split(":", 1)[1].strip()[:70] for l in log.splitlines()
              if (m := re.search(r"(Address|Bus) Error \w+ at address \$([0-9a-f]+), PC=\$([0-9a-f]+)", l))
              and (m.group(1) == "Address" or (int(m.group(2), 16) & 0xFFFFFF < 0xF00000
                                               and not 0xFC0000 <= int(m.group(3), 16) < 0xFF0000))]
    pc = re.search(r"PC[^\n]*", result)
    lines = [f"run      {run.relative_to(REPO)}",
             f"result   {result.splitlines()[0] if result else '?'}",
             f"opens    {', '.join(opens) or '-'}",
             f"rwabs    {dict(rwabs) or '-'}",
             f"acsi     {acsi}",
             f"except   {'; '.join(exc[:3]) or '-'}{' ...' if len(exc) > 3 else ''}",
             f"faults   {len(faults)}{': ' + faults[-1] if faults else ''}",
             f"end      {pc.group(0) if pc else '?'}"]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("zip", nargs="?")
    ap.add_argument("--disk", default="gemdrive", choices=("gemdrive", "ppdriver"))
    ap.add_argument("--setup", default="st-104")
    ap.add_argument("--start")
    ap.add_argument("--monitor", choices=("mono", "rgb", "vga", "tv"))
    ap.add_argument("--memsize", type=int, default=1)
    ap.add_argument("--report", nargs="+", type=Path)
    args = ap.parse_args()
    if args.report:
        print("\n\n".join(report(r.resolve()) for r in args.report))
        return 0
    if not args.zip:
        ap.error("a ZIP or --report")
    game = unpack(args.zip)
    start = args.start or next((s for s in STARTS if (game / s).is_file()), None)
    if not start:
        sys.exit(f"error: no {'/'.join(STARTS)} in {game}; give --start")
    subprocess.run([str(REPO / "tools" / "dev" / "make_disks.sh"), str(game)], check=True,
                   stdout=subprocess.DEVNULL)
    exp = game.parent / f"{game.name}.exp"
    exp.write_text("\n".join([
        f'expect start Pexec\\(0, "C:\\\\LEMMINGS\\\\{re.escape(start)}"',
        "sleep 10", "shot s10", "sleep 20", "shot s30", "key space", "sleep 15", "shot s45", ""]))
    name = game.name.lower() + (f"-{args.monitor}" if args.monitor else "") + \
        (f"-{args.memsize}mb" if args.memsize != 1 else "")
    cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"),
           "--setup", args.setup, "--disk", args.disk, "--start", f"C:\\LEMMINGS\\{start}",
           "--expect", str(exp), "--name", name, "--memsize", str(args.memsize)] + \
        (["--monitor", args.monitor] if args.monitor else [])
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    runs = re.findall(r"tools/dev/logs/\S+", out)
    if not runs:
        print(out)
        return 1
    print(report(REPO / runs[-1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
