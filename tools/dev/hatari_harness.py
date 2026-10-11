#!/usr/bin/env python3
"""tools/dev/hatari_harness.py: start the launcher in Hatari on one machine, TOS
and disk setup, headless, record what it does, and end with PASS or FAIL against
a list of expected steps (EPIC-00 STORY-05).

Usage: hatari_harness.py --setup st-104|ste-162|ste-206 --disk gemdrive|ppdriver
                         [--expect FILE] [--parse FILE] [--memsize MB] [--no-auto]
                         [--step-time S] [--name NAME]

Hatari is used as released (C-02). Each run gets a folder under tools/dev/logs/:

  hatari.out   everything Hatari printed: its traces of GEMDOS, BIOS, XBIOS and
               ACSI calls, and the debugger's output
  hatari.log   Hatari's log
  shots/       a screenshot per `shot` step, on failure, and at the end
  drive/ or ppdriver.img
               the run's own copy of the disk setup (tools/dev/make_disks.sh),
               so whatever the program writes stays with the run
  result.txt   PASS or FAIL, the steps reached, the wall time

The expectations file has one step per line; a line starting with '#' is a
comment:

  expect <name> <regex>   a line of Hatari's output matching <regex>
                          (Python syntax), within --step-time seconds
  quiet <name> <seconds>  no new line of output for <seconds>
  key <key>               press and release a key: space, return, esc, f1-f10,
                          0-9, or an ST scan code such as 0x39
  shot <name>             a screenshot, shots/<name>.png
  sleep <seconds>

Without --expect the run waits 20 s and takes a screenshot. Times are host
seconds; Hatari runs fast-forwarded, so the machine sees more.

By default START.TOS starts on its own (--auto C:\\LEMMINGS\\START.TOS); with
--no-auto the machine boots to the desktop. --parse hands Hatari a debugger
script (breakpoints, memory dumps). The script, and every command file it names
with `:file`, are copied into the run folder and run from there, so a relative
path they save to (savebin dump.bin ...) lands in the run folder. At the end of
every run the registers are dumped into hatari.out and the PC goes into
result.txt. After every run the harness checks that
LEMMINGS/ still matches LEMMINGS.sha256 (C-01) and that no Hatari is left.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
from devcfg import cfg  # noqa: E402

SETUPS = {  # name: (Hatari machine, dev.cfg key of the TOS image)
    "st-104": ("st", "TOS_ST_104"),
    "ste-162": ("ste", "TOS_STE_162"),
    "ste-206": ("ste", "TOS_STE_206"),
}
DISKS = ("gemdrive", "ppdriver")
TRACE = "gemdos,bios,xbios,scsi_cmd"
AUTO = "C:\\LEMMINGS\\START.TOS"
KEYS = {"space": 0x39, "return": 0x1C, "esc": 0x01, "backspace": 0x0E, "tab": 0x0F}
KEYS.update({f"f{n}": 0x3A + n for n in range(1, 11)})
KEYS.update({str(n): 0x01 + n for n in range(1, 10)})
KEYS["0"] = 0x0B
DEFAULT_STEPS = [("sleep", "20"), ("shot", "desktop")]
PC_LINE = re.compile(r"^Next PC: [0-9a-fA-F]+")
FILE_OPT = re.compile(r":file\s+(\S+)")


class Output:
    """Hatari's output, read from a pseudo-terminal line by line as it comes
    (a file or pipe would hold it back in stdio buffers)."""

    def __init__(self, fd: int, path: Path):
        self.lines: list[str] = []
        self.last = time.time()
        self.cursor = 0
        self.cond = threading.Condition()
        self.file = open(path, "w", errors="replace")
        threading.Thread(target=self._read, args=(fd,), daemon=True).start()

    def _read(self, fd: int) -> None:
        buf = b""
        while True:
            try:
                chunk = os.read(fd, 65536)
            except OSError:
                chunk = b""
            if not chunk:
                break
            buf += chunk
            *done, buf = buf.split(b"\n")
            with self.cond:
                for raw in done:
                    line = raw.decode("utf-8", "replace").rstrip("\r")
                    self.lines.append(line)
                    self.file.write(line + "\n")
                self.file.flush()
                self.last = time.time()
                self.cond.notify_all()

    def wait_for(self, regex: re.Pattern, timeout: float) -> str | None:
        end = time.time() + timeout
        with self.cond:
            while True:
                while self.cursor < len(self.lines):
                    line = self.lines[self.cursor]
                    self.cursor += 1
                    if regex.search(line):
                        return line
                left = end - time.time()
                if left <= 0:
                    return None
                self.cond.wait(min(left, 0.2))

    def wait_quiet(self, seconds: float, timeout: float) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            with self.cond:
                if time.time() - self.last >= seconds:
                    self.cursor = len(self.lines)
                    return True
            time.sleep(0.1)
        return False


def parse_steps(path: Path) -> list[tuple[str, ...]]:
    steps = []
    for n, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        kind, _, rest = line.partition(" ")
        rest = rest.strip()
        if kind == "expect":
            name, _, regex = rest.partition(" ")
            re.compile(regex)
            steps.append((kind, name, regex.strip()))
        elif kind == "quiet":
            name, _, secs = rest.partition(" ")
            steps.append((kind, name, str(float(secs))))
        elif kind in ("key", "shot", "sleep"):
            if kind == "key":
                keycode(rest)
            if kind == "sleep":
                float(rest)
            steps.append((kind, rest))
        else:
            sys.exit(f"error: {path}:{n}: unknown step {kind!r}")
    return steps


def keycode(key: str) -> int:
    if key.lower() in KEYS:
        return KEYS[key.lower()]
    try:
        return int(key, 0)
    except ValueError:
        sys.exit(f"error: unknown key {key!r}")


def stage_debugger_script(script: Path, run_dir: Path) -> str:
    """Copy a debugger script and the command files it names with :file into
    the run folder, pointing it at the copies: Hatari runs a :file from that
    file's own folder, so relative paths it saves to land in the run folder."""
    text = script.read_text()
    for name in set(FILE_OPT.findall(text)):
        src = Path(name) if Path(name).is_absolute() else script.parent / name
        if not src.is_file():
            sys.exit(f"error: {script}: no such :file {name}")
        shutil.copy(src, run_dir / src.name)
        text = text.replace(f":file {name}", f":file {run_dir / src.name}")
    staged = run_dir / script.name
    staged.write_text(text)
    return str(staged)


def evidence_ok() -> tuple[bool, str]:
    """Whether every file listed in LEMMINGS.sha256 still has its hash (C-01)."""
    bad = []
    for line in (REPO / "LEMMINGS.sha256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        p = REPO / name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
            bad.append(name)
    return not bad, ", ".join(bad)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--setup", required=True, choices=sorted(SETUPS))
    ap.add_argument("--disk", required=True, choices=DISKS)
    ap.add_argument("--expect", type=Path, help="expectations file")
    ap.add_argument("--parse", type=Path, help="Hatari debugger script")
    ap.add_argument("--memsize", type=int, default=1, help="ST RAM in MB, at least 1 (C-04)")
    ap.add_argument("--no-auto", action="store_true", help="boot to the desktop only")
    ap.add_argument("--step-time", type=float, default=60, help="seconds per step")
    ap.add_argument("--name", default="", help="suffix for the run folder")
    args = ap.parse_args()

    if not 1 <= args.memsize <= 14:
        sys.exit("error: --memsize is in MB, 1 to 14 (README.TXT asks for 1 MB at least)")
    steps = parse_steps(args.expect) if args.expect else DEFAULT_STEPS
    machine, tos_key = SETUPS[args.setup]
    hatari, tos = cfg("HATARI"), cfg(tos_key)
    for p in (hatari, tos):
        if not Path(p).is_file():
            sys.exit(f"error: not found: {p} (tools/dev/dev.cfg)")
    disks = HERE / "builds" / "disks"
    if not (disks / "gemdrive" / "LEMMINGS").is_dir() or not (disks / "ppdriver.img").is_file():
        sys.exit("error: no disk setups: run tools/dev/make_disks.sh first")

    stamp = time.strftime("%Y%m%d-%H%M%S")
    label = f"{args.setup}-{args.disk}" + (f"-{args.name}" if args.name else "")
    run_dir = HERE / "logs" / f"{stamp}-{label}"
    (run_dir / "shots").mkdir(parents=True)
    (run_dir / "home").mkdir()

    cmd = [hatari, "--machine", machine, "--tos", tos, "--memsize", str(args.memsize),
           "--sound", "off", "--confirm-quit", "false", "--fast-forward", "yes",
           "--statusbar", "false", "--drive-led", "false",
           "--log-file", str(run_dir / "hatari.log"), "--screenshot-dir", str(run_dir / "shots"),
           "--trace", TRACE]
    if args.disk == "gemdrive":
        shutil.copytree(disks / "gemdrive", run_dir / "drive", copy_function=shutil.copy2)
        cmd += ["--harddrive", str(run_dir / "drive")]
    else:
        subprocess.run(["cp", "-c", str(disks / "ppdriver.img"), str(run_dir)], check=True)
        cmd += ["--acsi", f"0={run_dir / 'ppdriver.img'}"]
    if not args.no_auto:
        cmd += ["--auto", AUTO]
    if args.parse:
        cmd += ["--parse", stage_debugger_script(args.parse, run_dir)]
    shutil.copy(disks / "SOURCE.txt", run_dir / "SOURCE.txt")

    # macOS caps a Unix socket path at 104 bytes; the run folder's can be longer.
    sock_dir = tempfile.mkdtemp(prefix="hh", dir="/tmp")
    sock_path = os.path.join(sock_dir, "ctl.sock")
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(sock_path)
    server.listen(1)
    server.settimeout(20)
    cmd += ["--control-socket", sock_path]

    # A clean HOME, or Hatari loads the user's saved configuration; headless.
    env = dict(os.environ, HOME=str(run_dir / "home"), SDL_VIDEODRIVER="dummy",
               SDL_AUDIODRIVER="dummy")
    (run_dir / "command.txt").write_text(" ".join(f"'{c}'" if " " in c else c for c in cmd) + "\n")
    master, slave = os.openpty()
    start = time.time()
    proc = subprocess.Popen(cmd, env=env, cwd=run_dir, stdin=subprocess.DEVNULL,
                            stdout=slave, stderr=slave)
    os.close(slave)
    out = Output(master, run_dir / "hatari.out")
    print(f"{label}: run folder {run_dir.relative_to(REPO)}", flush=True)

    reached: list[str] = []
    failure = None
    conn = None
    pc_line = None

    def say(text: str) -> None:
        print(f"  [{time.time() - start:6.1f}s] {text}", flush=True)

    def command(text: str) -> None:
        conn.sendall((text + "\n").encode())

    def shot(name: str) -> Path | None:
        shots = run_dir / "shots"
        before = set(os.listdir(shots))
        time.sleep(0.3)  # fast-forward skips frames: let one render
        command("hatari-shortcut screenshot")
        end = time.time() + 5
        while time.time() < end:
            new = [f for f in os.listdir(shots) if f not in before]
            if new:
                time.sleep(0.2)
                path = shots / f"{name}.png"
                os.replace(shots / new[0], path)
                return path
            time.sleep(0.05)
        return None

    try:
        conn, _ = server.accept()
        for step in steps:
            kind = step[0]
            if proc.poll() is not None:
                failure = f"Hatari exited ({proc.returncode}) before step {' '.join(step)}"
                break
            if kind == "expect":
                _, name, regex = step
                line = out.wait_for(re.compile(regex), args.step_time)
                if line is None:
                    failure = f"step {name}: no line matching {regex!r} within {args.step_time:g} s"
                    break
                reached.append(name)
                say(f"{name}: {line.strip()[:110]}")
            elif kind == "quiet":
                _, name, secs = step
                if not out.wait_quiet(float(secs), args.step_time):
                    failure = f"step {name}: output never stopped for {secs} s"
                    break
                reached.append(name)
                say(f"{name}: no output for {float(secs):g} s")
            elif kind == "key":
                # Always in hex: Hatari takes a single character as that
                # character, not as a scan code ("1" would type the digit 1).
                code = f"0x{keycode(step[1]):02x}"
                command(f"hatari-event keydown {code}")
                time.sleep(0.1)
                command(f"hatari-event keyup {code}")
                say(f"key {step[1]}")
            elif kind == "shot":
                path = shot(step[1])
                say(f"screenshot {path.relative_to(REPO) if path else '(none)'}")
            elif kind == "sleep":
                time.sleep(float(step[1]))
    except (OSError, socket.timeout) as err:
        failure = f"control socket: {err}"
    finally:
        if conn is not None:
            try:
                if failure:
                    path = shot("fail")
                    if path:
                        failure += f"; screenshot {path.relative_to(REPO)}"
                shot("end")
                out.cursor = len(out.lines)
                command("hatari-debug r")  # the registers, the PC among them
                pc_line = out.wait_for(PC_LINE, 5)
                command("hatari-shortcut quit")
            except OSError:
                pass
        try:
            proc.wait(10)
        except subprocess.TimeoutExpired:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(5)
        server.close()
        shutil.rmtree(sock_dir, ignore_errors=True)
        time.sleep(0.3)  # the reader's last lines

    left = proc.poll() is None
    ok, bad = evidence_ok()
    if left:
        failure = (failure + "; " if failure else "") + "Hatari still running"
    if not ok:
        failure = (failure + "; " if failure else "") + f"LEMMINGS/ changed: {bad}"
    wall = time.time() - start
    expected = [s[1] for s in steps if s[0] in ("expect", "quiet")]
    verdict = "FAIL" if failure else "PASS"
    summary = (f"{verdict} {label}: {len(reached)}/{len(expected)} steps"
               + (f", last {reached[-1]}" if reached else "") + f", {wall:.1f} s")
    (run_dir / "result.txt").write_text(
        summary + "\n" + (f"failure: {failure}\n" if failure else "")
        + "".join(f"reached: {r}\n" for r in reached)
        + (f"at the end: {pc_line.strip()}\n" if pc_line else ""))
    print(summary)
    if failure:
        print(f"  {failure}")
    print(f"  {run_dir.relative_to(REPO)}")
    return 1 if failure else 0


if __name__ == "__main__":
    sys.exit(main())
