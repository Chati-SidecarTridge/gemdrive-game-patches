#!/usr/bin/env python3
"""In GEMDRIVE mode, with the pristine files, answer by hand
everything the launcher asks of the disk, one BIOS Rwabs at a time, until it
reaches the title screen or asks for something that cannot be answered.

Usage: serve_rwabs.py <setup> [--max N] [--reset]     (setup: st-104 only for now)

Each run answers, through chained single-shot breakpoints at the launcher's
BIOS trampoline ($C83CC trap, $C83CE return), the sector-0 read (fallback_probe),
every Getbpb(2) (PPDRIVER's BPB) and the first N Rwabs reads with the sectors
they ask for, taken from the PPDRIVER reference image (logical sector n of
1,024 bytes = DOS sectors 2n+1 and 2n+2 of the partition at LBA 63). The run's
trace then shows the (N+1)-th request, which the next run answers too. The
list of answered requests is kept in tools/dev/builds/gemdrive-failure/serve-<setup>/
requests.txt; --reset starts over. Stops when a run asks for nothing new.
"""

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_probe import BASES, QUIET  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
IMAGE = REPO / "tools" / "dev" / "builds" / "disks" / "ppdriver.img"
PART = 63 * 512
RWABS = re.compile(r"BIOS 0x04 Rwabs\((\d+),0x([0-9a-f]+),(\d+),(\d+),(\d+)\) at PC 0xC83CE")
BPB = bytes.fromhex("0400 0002 0800 0010 0020 0021 0051 3fd7 0001".replace(" ", ""))


def sector_bytes(img: bytes, recno: int, count: int) -> bytes:
    off = PART + (2 * recno + 1) * 512
    return img[off:off + count * 1024]


def write_chain(out: Path, base: int, requests: list[tuple[int, int, int]]) -> None:
    def at(off: int) -> str:
        return f"${base + off:x}"
    boot = out / "boot.bin"
    boot.write_bytes(IMAGE.read_bytes()[:512])
    (out / "bpb.bin").write_bytes(BPB)
    files = {
        "serve.dbg": ["b GemdosOpcode = $47 :once :trace :file 1-dgetpath.ini"],
        "1-dgetpath.ini": [f"b pc = {at(0xBD4)} :once :trace :file 2-sector0.ini"],
        "2-sector0.ini": ["r d0=0", f"loadbin {boot} {at(0x8864)}",
                          f"trace {QUIET},cpu_exception",
                          "b pc = $c83cc && BiosOpcode = 7 :trace :file 3-getbpb.ini",
                          # Mediach(2): TOS without a driver answers an error; PPDRIVER
                          # answers 0 (no change), which D15R expects before each read
                          "b pc = $c83cc && BiosOpcode = 9 :trace :file 3-mediach.ini",
                          "b pc = $c83cc && BiosOpcode = 4 :once :trace :file rw-1.ini",
                          "b pc = $2fc0b0a :once :trace :file 9-exception.ini",
                          "b pc = $3fc0b0a :once :trace :file 9-exception.ini",
                          "b pc = $4fc0b0a :once :trace :file 9-exception.ini",
                          "b GemdosOpcode = $4c :once :trace :file 9-pterm.ini"],
        "3-getbpb.ini": ["b pc = $c83ce :once :trace :file 3-bpb-answer.ini"],
        "3-bpb-answer.ini": [f"loadbin {out / 'bpb.bin'} $7f000", "r d0=$7f000"],
        "3-mediach.ini": ["b pc = $c83ce :once :trace :file 3-mediach-answer.ini"],
        "3-mediach-answer.ini": ["r d0=0"],
        "9-exception.ini": ["r", "m a7 16"],
        "9-pterm.ini": ["r"],
    }
    img = IMAGE.read_bytes()
    for n, (buf, count, recno) in enumerate(requests, 1):
        data = out / f"sec-{n}.bin"
        data.write_bytes(sector_bytes(img, recno, count))
        files[f"rw-{n}.ini"] = ["m a7 16", f"b pc = $c83ce :once :trace :file ans-{n}.ini",
                                f"b pc = $c83cc && BiosOpcode = 4 :once :trace :file rw-{n + 1}.ini"]
        files[f"ans-{n}.ini"] = [f"loadbin {data} ${buf:x}", "r d0=0", "r"]
    n = len(requests) + 1
    files[f"rw-{n}.ini"] = ["m a7 16", f"b pc = $c83ce :once :trace :file unanswered-{n}.ini"]
    files[f"unanswered-{n}.ini"] = ["r"]
    for name, lines in files.items():
        (out / name).write_text("\n".join(lines) + "\n")


def main() -> int:
    argv = sys.argv[1:]
    if "--max" in argv:
        del argv[argv.index("--max"):argv.index("--max") + 2]
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1 or (args[0], "gemdrive") not in BASES:
        sys.exit(f"usage: {sys.argv[0]} <setup> [--max N] [--reset]")
    setup = args[0]
    base = BASES[(setup, "gemdrive")]
    limit = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 60
    out = REPO / "tools" / "dev" / "builds" / "gemdrive-failure" / f"serve-{setup}"
    out.mkdir(parents=True, exist_ok=True)
    reqfile = out / "requests.txt"
    if "--reset" in sys.argv or not reqfile.exists():
        reqfile.write_text("")
    requests = [tuple(int(x, 16) for x in l.split()) for l in reqfile.read_text().splitlines() if l]

    for _ in range(limit):
        write_chain(out, base, requests)
        expect = out / "serve.exp"
        expect.write_text('expect files-dir Dsetpath\\("FILES"\\)\nsleep 25\nshot end-of-run\n')
        cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"),
               "--setup", setup, "--disk", "gemdrive", "--parse", str(out / "serve.dbg"),
               "--expect", str(expect), "--name", f"serve-{len(requests):02d}"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        run = re.search(r"run folder (\S+)", res.stdout)
        if not run:
            sys.exit(res.stdout + res.stderr)
        run_dir = REPO / run.group(1)
        text = (run_dir / "hatari.out").read_text(errors="replace")
        seen = [(int(m.group(2), 16), int(m.group(3)), int(m.group(4))) for m in RWABS.finditer(text)
                if m.group(1) == "0" and m.group(5) == "2"]
        # Hatari folds identical consecutive lines into "N repeats of: ..."; a
        # repeated request is a retry of the same read, answered once already.
        pterm = "Pterm(-1)" in text
        halted = "Halt dialog" in text or "Bus error" in text
        print(f"run {len(requests):02d}: {len(seen)} Rwabs seen, answered {len(requests)}, "
              f"{'crashed (Pterm -1)' if pterm else 'halted (bus error)' if halted else 'no crash'}, "
              f"{run.group(1)}", flush=True)
        if len(seen) <= len(requests):
            print("nothing new asked: done")
            return 0
        new = seen[len(requests)]
        print(f"   new request: buf ${new[0]:x} count {new[1]} recno {new[2]}", flush=True)
        requests.append(new)
        reqfile.write_text("".join(f"{b:x} {c:x} {r:x}\n" for b, c, r in requests))
    print("limit reached")
    return 1


if __name__ == "__main__":
    sys.exit(main())
