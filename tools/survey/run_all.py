#!/usr/bin/env python3
"""EPIC-03 STORY-05: every game run from Hatari's GEMDOS drive, as it is.

Usage: run_all.py [--jobs N] [--only NAME ...] [--strategy S] [--limit N] [--disk gemdrive|ppdriver]
                  [--setup st-104|ste-162|ste-206] [--redo] [--retry]
       run_all.py --reanalyse [--only NAME ...]   (not while another run_all.py writes runs.tsv)

For every game of src/survey/migration.csv (its main download, unpacked by unpack_games.py), the
harness starts its program from a GEMDOS drive whose C:\\GAME\\ is the game's folder (and whose root holds
what the download keeps beside that folder: Maddog Williams' C:\\PABISYS.FIL), on ST TOS 1.04,
with the largest RAM the list (MinRAM, GX) and the page give, 1 or 2 MB, and a monochrome monitor
when the page or the game's README asks for one. A game that halts, quits, ends on an empty desktop
or a blank screen, or seeks before the start of its floppy image runs again with 2 MB, then 4 MB;
the last run counts, unless it ends as the first did (same proposal and reason): then the first.
The expectation is the same for every game: the program starts; screenshots at 12 s, then after
the space bar, Return and F1, and a last one 4 s after F1 with no key in between. --disk ppdriver
runs the same from a PPDRIVER image (make_disks.sh, one per run).

Runs go to tools/dev/builds/survey/runs/<date>-<setup>-<disk>-<name>/ (the drive copy is removed
afterwards); each run's last screenshot, taken just before Hatari quits, is copied to
tools/dev/builds/survey/snapshots/<row>-<name>.png (sheet.py shows them); every run writes its line
of tools/dev/builds/survey/runs.tsv (one per game, setup and disk), so a stopped run_all resumes
where it stopped (--redo runs every game again, --retry the ones not "as it is"). Each line holds what the trace shows:

  opened      files opened by name after the start; missing: the ones not found that PP's archive
              has (a name nowhere in it is a file the game does without, missing from any disk)
  sectors_c   BIOS Rwabs on C:, the GEMDOS drive: nothing answers them there; a program asking for
              C:'s boot block (Getbpb) 8 times or more reads by sectors too (other letters are RAM
              disks the programs make: Weird Dreams' M:)
  floppy      BIOS Rwabs on A:/B: and XBIOS Floprd
  desktop     GEMDOS calls from the ROM's desktop after the start: the program went back to it
  exit        the start program ended (Pterm0, Pterm or Ptermres: breakpoints on GemdosOpcode print
              the basepage of the process ending, matched to the start program's text, and the
              ROM's desktop takes over right after), or how many other processes ended
  screen      "desktop" when the last screenshot is a TOS desktop, told by its menu bar whatever
              its colours (screens.py); "blank" when the last three are one colour, nothing on them
  halt        Hatari stopped the CPU; faults: address and bus errors in hatari.log
  alive       the last two screenshots differ (the game still moves)

and a proposed verdict (D-14), its rules set with Diego's review of 331 games (src/survey/review.tsv):
"fix" when a GOS launcher quit to the desktop or the program read sectors on C:; "broken" when the
screen ends on an empty desktop (TOS in RAM without its disk); "unsure", with the reason, when the
program quit to the desktop, the CPU halted after the first screenshots, a file was missing, or the
run did not start in time; "as it is" otherwise: the game's screen still moves, or stands still at
a menu or title that is not the desktop, or is TOS in RAM's desktop with its drives (HAGE, HAG2).
Faults and a negative seek in the floppy image are recorded but do not decide by themselves. STORY-05
checks the proposals before they go into migration.csv; Diego's answers override them.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import screens  # noqa: E402
SURVEY = REPO / "tools" / "dev" / "builds" / "survey"
RUNS = SURVEY / "runs"
TSV = SURVEY / "runs.tsv"
SNAPSHOTS = SURVEY / "snapshots"
FIELDS = ["row", "name", "strategy", "setup", "disk", "start", "memsize", "monitor", "run", "result",
          "opened", "missing", "sectors_c", "floppy", "desktop", "exit", "screen", "halt", "faults", "alive",
          "proposal", "reason", "snapshot"]
# Breakpoints on the GEMDOS calls that end a process (Pterm0, Ptermres, Pterm), each printing the
# basepage of the process that calls it (Hatari's debugger, GemdosOpcode)
EXITS = ["b GemdosOpcode = 0x00 :trace :file exit.ini", "b GemdosOpcode = 0x31 :trace :file exit.ini",
         "b GemdosOpcode = 0x4C :trace :file exit.ini"]
LOCK = threading.Lock()


MONO = re.compile(r"only (in )?monochrom|monochrome \(high-res\) video mode|needs monochrome|"
                  r"monochrome mode only|works in monochrome mode|monochrome capable|"
                  r", monochrome\b[^\n]*for atari", re.I)  # PP's title line: "Oxyd 2, monochrome,  For Atari ST"
UTILITY = re.compile(r"(CONV|COPY|HELP|INFO|INSTALL|MUSIC|README|ARCH|SETUP|CONFIG|GXUT|DEMO|FSTE)", re.I)


def megabytes(*values: str) -> int:
    """The largest RAM size among the list's and the page's figures: 1 or 2 (MB)."""
    return 2 if any(v.strip().startswith("2") or "2M" in v for v in values if v) else 1


def plan(game: dict, files: list[dict], record: dict) -> dict | None:
    """Where the game's folder is, the program to start in it, RAM and monitor: the largest RAM of the
    list (MinRAM, GX) and the page, and a monochrome monitor when the page or a README asks for one."""
    # of several programs: RUNME or START, then one a README says to start or run (Heroes of the Lance's
    # HOTL.PRG), then the others; utilities last (F1 GP Ultimate's CONV_IMG.TOS, Space Quest 3's MUSIC.PRG)
    base = SURVEY / "games" / Path(game["download"]).with_suffix("")
    named = {n.upper() for f in base.rglob("*") if f.is_file() and f.suffix.upper() in (".TXT", ".DOC")
             and f.stat().st_size < 50000 for line in f.read_text(encoding="latin-1", errors="replace").splitlines()
             if re.search(r"\b(start|run)", line, re.I) for n in re.findall(r"[\w&-]+\.(?:PRG|TOS|TTP|APP)\b", line, re.I)}

    def rank(f: dict) -> int:
        name = f["path"].rsplit("/", 1)[-1]
        return 0 if re.match(r"(RUNME|START)", name, re.I) else 3 if UTILITY.match(name) else \
            1 if name.upper() in named else 2
    starts = sorted((f for f in files if f["start"]), key=lambda f: (f["start"] != "yes", rank(f), f["path"]))
    if not starts:
        return None
    start = starts[0]["path"]
    root = start.rsplit("/", 1)[0] if "/" in start else ""
    folder = SURVEY / "games" / Path(game["download"]).with_suffix("") / root
    ram = megabytes(record.get("min_ram", ""), record.get("gx", ""), record.get("page_min_ram", ""))
    readme = " ".join(f.read_text(encoding="latin-1", errors="replace") for f in folder.glob("*")
                      if f.is_file() and f.suffix.upper() in (".TXT", ".DOC") and f.stat().st_size < 50000)
    # the page, the README, or the name itself (Super Breakout mono, "(monochrome)" on its page;
    # Oxyd Highres)
    mono = game["monitor"] == "mono only" or bool(MONO.search(readme)) or \
        bool(re.search(r"\bmono\b|monochr|high ?res|hi-res", game["name"], re.I))
    # what the download keeps beside the game's folder goes to the drive's root (Maddog Williams' PABISYS.FIL)
    extra = [e for e in folder.parents[len(Path(root).parts) - 1].iterdir() if e.name != root.split("/")[0]] if root else []
    return {"folder": folder, "start": start[len(root) + 1:] if root else start, "memsize": ram,
            "monitor": "mono" if mono else "", "extra": extra}


def expectation(start: str, path: Path) -> None:
    path.write_text("\n".join([
        f'expect start Pexec\\(0, "C:\\\\GAME\\\\{re.escape(start.replace("/", chr(92)))}"',
        "sleep 12", "shot s12", "key space", "sleep 8", "shot s20", "key return", "sleep 8", "shot s28",
        "key f1", "sleep 6", "shot s34", "sleep 4", "shot s38", ""]))


def in_rom(pc: int) -> bool:
    """TOS in ROM: at $FC0000 on the ST (1.04), at $E00000 on the STE (1.62, 2.06)."""
    return 0xFC0000 <= pc < 0xFF0000 or 0xE00000 <= pc < 0xE40000


def in_desktop(pc: int) -> bool:
    """The ROM's desktop and AES, above its BIOS and GEMDOS: $FD0000 up on the ST, $E10000 up on the STE."""
    return 0xFD0000 <= pc < 0xFF0000 or 0xE10000 <= pc < 0xE40000


def is_fault(line: str) -> bool:
    """An address error, or a bus error below the I/O area: not the hardware probes (Mega STE, STE,
    Falcon IDE registers) every launcher makes, nor TOS sizing the RAM from the ROM at boot."""
    m = re.search(r"(Address|Bus) Error \w+ at address \$([0-9a-f]+), PC=\$([0-9a-f]+)", line)
    if not m:
        return False
    if m.group(1) == "Address":
        return True
    # a bus error from the ROM is TOS sizing the RAM at boot ($41FFFE with 4 MB), not the game
    return int(m.group(2), 16) & 0xFFFFFF < 0xF00000 and not in_rom(int(m.group(3), 16))


def analyse(run: Path, strategy: str, archive: Path | None = None) -> dict:
    """What a run's trace and screenshots show, and the proposed verdict; archive: the game's unpacked
    download, against which a file not found is checked."""
    text = (run / "hatari.out").read_text(errors="replace").splitlines() if (run / "hatari.out").exists() else []
    # the start: C:\GAME\ on the GEMDOS drive, C:\LEMMINGS\ on a PPDRIVER image (make_disks.sh)
    begin = next((i for i, l in enumerate(text) if l.startswith(('GEMDOS 0x4B Pexec(0, "C:\\GAME',
                                                                  'GEMDOS 0x4B Pexec(0, "C:\\LEMMINGS'))), len(text))
    end = next((i for i, l in enumerate(text) if "Halt dialog" in l or l.startswith("> r")), len(text))
    opened, missing, sectors_c, floppy, desktop, bpb_c = [], [], 0, 0, False, 0
    for i in range(begin, end):
        line = text[i]
        m = re.match(r'GEMDOS 0x3D Fopen\("([^"]*)"', line)
        if m:
            nxt = text[i + 1] if i + 1 < len(text) else ""
            (missing if "didn't find" in nxt or "ERROR -" in nxt else opened).append(m.group(1))
        m = re.match(r"BIOS 0x04 Rwabs\(\d+,0x[0-9a-f]+,\d+,\d+,(\d+)\)", line, re.I)
        if m:
            if int(m.group(1)) == 2:  # C: (Weird Dreams' RAM disk is M:, 12; Pole Position asks 52)
                sectors_c += 1
            elif int(m.group(1)) < 2:
                floppy += 1
        # a program asking again and again for the boot block of C: waits for a disk it reads by
        # sectors (Crystals of Arborea's START.PRG; a GOS4 launcher: Defender 2)
        m = re.match(r"(?:(\d+) repeats of: )?BIOS 0x07 Getbpb\(0x([0-9A-F]+)\)", line, re.I)
        if m and int(m.group(2), 16) == 2:
            bpb_c += int(m.group(1) or 1)
        if line.startswith("XBIOS 0x08 Floprd"):
            floppy += 1
        m = re.match(r"GEMDOS 0x[0-9A-F]+ \w+\(.*\) at PC[ =]0x([0-9A-F]+)", line)
        if m and i > begin + 2 and in_desktop(int(m.group(1), 16)):
            desktop = True
    # HAGA looks for optional files (a state save GSAU.TOS, D15H5.FIC, a cover picture *.HST, PP's
    # STE high-colour pictures: some games have only one of the pair); a name found under another
    # path afterwards (the folder, then C:\GAMEX) is not missing either
    found = {o.replace("\\", "/").rsplit("/", 1)[-1].upper() for o in opened}
    # a high-score file a game creates on its first run is not missing either (Overscan Invaders,
    # Critical Mass's scores.dat)
    missing = [m for m in missing if not re.match(r"(GS..\.TOS|D15H5\.FIC|.*\.HST|.*SCO?RE.*|.*HISC.*|.*\.HI|.*\.HSC)$",
                                                  m.rsplit("\\", 1)[-1], re.I)
               and m.replace("\\", "/").rsplit("/", 1)[-1].upper() not in found]
    # a name that is nowhere in PP's archive is a file the game looks for and does without (a save, a
    # high-score table, another loader: Gobliiins' foader.prg); missing from any disk alike, it does
    # not count: only a file the archive has and the drive did not find does
    if archive:
        there = {f.name.upper() for f in archive.rglob("*")}
        missing = [m for m in missing if m.replace("\\", "/").rsplit("/", 1)[-1].upper() in there]
    # the start program's own text: the PC of its first system call (in RAM, not the ROM or
    # Hatari's cartridge); a breakpoint on Pterm whose process's text holds it is the start
    # program ending
    first_pc = next((int(m.group(1), 16) for l in text[begin + 1:end]
                     if (m := re.search(r" at PC[ =]0x([0-9A-F]+)", l, re.I)) and int(m.group(1), 16) < 0xE00000), None)
    exits, start_exit, opcode = 0, "", ""
    for i in range(begin, end):
        m = re.search(r"GemdosOpcode = \$?(0x)?([0-9a-f]+)", text[i], re.I)
        if m:
            opcode = {"0": "Pterm0", "31": "Ptermres", "4c": "Pterm"}.get(m.group(2).lower().lstrip("0") or "0", m.group(2))
        if text[i].startswith("Process basepage ("):
            info = {k.strip(): v.strip() for k, _, v in (l.lstrip("- ").partition(":") for l in text[i + 1:i + 12])}
            exits += 1
            try:
                seg, size = int(info["Text segment"], 16), int(info["Text size"], 16)
            except (KeyError, ValueError):
                continue
            # the start program's own end gives the machine back to the ROM's desktop, which calls
            # from its own code next; a loader or a game ending under PP's TOS in RAM does not
            # (Eaglestar: its game's Pterm0 under TOS in RAM, at RUNME.TOS's old address)
            back = any(in_desktop(int(m.group(1), 16)) for l in text[i:i + 120]
                       if (m := re.search(r" at PC[ =]0x([0-9A-F]+)", l, re.I)))
            if first_pc is not None and seg <= first_pc < seg + size and back:
                start_exit = opcode or "yes"
    last = next((run / "shots" / f"{n}.png" for n in ("end", "s38", "s34") if (run / "shots" / f"{n}.png").is_file()), None)
    try:
        screen = "desktop" if last and screens.is_desktop(last) else ""
        if screen and screens.desktop_items(last) < 300:
            screen = "empty desktop"  # no drive icon, no window (Diego's review: Laser Chess, Joey)
        elif not screen and last and all(screens.blank(run / "shots" / f"{n}.png") for n in ("s34", "s38", "end")
                                         if (run / "shots" / f"{n}.png").is_file()):
            # one colour, nothing on it, in the last three screenshots (Defender 2: a GOS4 launcher with no
            # disk under it); one blank screenshot alone is a fade or a load (Klax loading KLAR.FIC at the end)
            screen = "blank"
    except ValueError:
        screen = "?"
    # HAGE/HAG2 (PP's floppy image in a window of RAM) asking for a negative position in the image:
    # with too little RAM the window starts before the image (Laser Chess: 1 and 2 MB; 4 MB works)
    negative_seek = any(re.match(r"GEMDOS 0x42 Fseek\(-\d+", l) for l in text[begin:end])
    halt = any("Halt dialog" in l for l in text)
    log = (run / "hatari.log").read_text(errors="replace") if (run / "hatari.log").exists() else ""
    faults = sum(1 for l in log.splitlines() if is_fault(l))
    shots = run / "shots"
    alive = (shots / "s34.png").exists() and (shots / "s38.png").exists() and \
        (shots / "s34.png").read_bytes() != (shots / "s38.png").read_bytes()
    result = (run / "result.txt").read_text().splitlines()[0] if (run / "result.txt").exists() else "no result"
    # Diego's review, 2026-10-12 (331 games): a program quit only when its own exit leaves the desktop on
    # screen (GEM programs call GEMDOS from the ROM's AES all the time: Air Warrior, Mean 18, Trivial
    # Pursuit); a halt after the first screenshots, faults and a negative seek are noted but do not make a
    # game broken by themselves (Glad Killing Impact, Ammotrack, Hunt for Red October); an empty desktop does
    on_desktop = screen.startswith("desktop") or screen.startswith("empty desktop")
    quit = start_exit and on_desktop
    shots_after = [n for n in ("s20", "s28", "s34", "s38") if (run / "shots" / f"{n}.png").is_file()]
    failure = (run / "result.txt").read_text() if (run / "result.txt").exists() else ""
    if "Hatari exited" in failure:  # Pac-Land: "string allocation failed", from both disks
        last_words = next((l for l in reversed(text) if l.strip()), "")[:60]
        proposal, reason = "unsure", f"Hatari itself quit ({last_words})"
    elif not result.startswith("PASS"):
        proposal, reason = "unsure", "the program did not start in time (run again)"
    elif quit and strategy in ("Gamex + GOS4", "Gamex + GOS5"):
        proposal, reason = "fix", "the launcher quit to the desktop (driver checks)"
    # on a PPDRIVER image they are answered; under HAGE's and HAG2's TOS in RAM, PP's floppy-image
    # service answers them (Lords of Conquest: the same 78 reads of D: from both disks)
    elif (sectors_c or bpb_c >= 8) and "-ppdriver-" not in run.name and strategy not in ("HAGE", "HAG2"):
        proposal, reason = "fix", f"{sectors_c} sector reads on C:" if sectors_c else \
            f"{bpb_c} requests for C:'s boot block (Getbpb): it reads the disk by sectors"
    elif screen.startswith("empty desktop"):
        proposal, reason = "broken", "an empty desktop: no drive, no window (TOS in RAM did not get its disk)" + \
            (", after a negative seek in the floppy image" if negative_seek else "")
    elif quit:
        proposal, reason = "unsure", f"the program quit to the desktop ({start_exit})"
    elif halt and not shots_after:
        proposal, reason = "unsure", "the CPU halted after the first screenshot"
    elif halt:
        proposal, reason = "unsure", f"the CPU halted after the {shots_after[-1]} screenshot"
    elif screen.startswith("desktop") and strategy in ("HAGE", "HAG2"):
        # Diego's review, 2026-10-11 (Mindfighter): TOS in RAM's desktop, with the game's floppy image
        # as drive A, is where the game is started from
        proposal, reason = "as it is", "TOS in RAM's desktop: the game starts from it"
    elif screen.startswith("desktop"):
        proposal, reason = "unsure", "a desktop on screen (TOS in RAM's, or the game's own)"
    elif screen == "blank":
        proposal, reason = "unsure", "a blank screen at the end"
    elif missing:
        proposal, reason = "unsure", "not found: " + ", ".join(missing[:3])
    elif not alive:
        # Diego's review, 2026-10-11 (Algebra, ACC-TRIS, Knephren): a still screen that is not the
        # desktop, with no exit and nothing missing, is a menu or a title waiting for a key
        proposal, reason = "as it is", "a still screen, not the desktop: waiting at a menu or title"
    else:
        proposal, reason = "as it is", ""
    return {"result": result, "opened": len(opened), "missing": ";".join(missing[:5]), "sectors_c": sectors_c,
            "floppy": floppy, "desktop": "yes" if desktop else "", "exit": start_exit or (f"{exits} other" if exits else ""),
            "screen": screen + (" negative seek" if negative_seek else ""), "halt": "yes" if halt else "",
            "faults": faults, "alive": "yes" if alive else "", "proposal": proposal, "reason": reason}


def reanalysed(row: dict, archive: Path | None) -> dict:
    found = analyse(RUNS / row["run"], row["strategy"], archive)
    found["snapshot"] = snapshot(RUNS / row["run"], row["row"], row["name"], row["setup"], row["disk"])
    return found


def snapshot(run: Path, row: str, name: str, setup: str, disk: str) -> str:
    """The run's last screenshot with something on it (end.png, taken just before Hatari quits, else the
    latest; a blank one is often a fade or a load) copied to snapshots/<row>-<name>[-<setup>-<disk>].png,
    for the website (STORY-07) and the contact sheets."""
    shots = [run / "shots" / f"{n}.png" for n in ("end", "s38", "s34", "s28", "s20", "s12")]
    shots = [s for s in shots if s.is_file()]
    if not shots:
        return ""
    shot = next((s for s in shots if not screens.blank(s)), shots[0])
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:30] or "game"
    extra = "" if (setup, disk) == ("st-104", "gemdrive") else f"-{setup}-{disk}"
    target = SNAPSHOTS / f"{int(row):04d}-{slug}{extra}.png"
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(shot, target)
    return target.name


def run_one(game: dict, p: dict, setup: str, disk: str, links: tuple = ()) -> dict:
    """One run; links: other names the game's folder also has in the drive's root (COMP.ZIP's README
    puts it in C:\\COMP). The download's other entries (plan's extra) are on the GEMDOS drive only."""
    name = re.sub(r"[^a-z0-9]+", "-", game["name"].lower()).strip("-")[:30] or "game"
    with tempfile.TemporaryDirectory(dir=SURVEY) as stage:
        stage = Path(stage)
        (stage / "drive").mkdir()
        (stage / "drive" / "GAME").symlink_to(p["folder"], target_is_directory=True)
        for e in p.get("extra", []):
            if e.name.upper() != "GAME":
                (stage / "drive" / e.name).symlink_to(e, target_is_directory=e.is_dir())
        for link in links:
            (stage / "drive" / link).symlink_to(p["folder"], target_is_directory=True)
        exp = stage / "game.exp"
        expectation(p["start"], exp)
        (stage / "exits.dbg").write_text("\n".join(EXITS) + "\n")
        (stage / "exit.ini").write_text("info basepage\n")
        cmd = [sys.executable, "-I", str(REPO / "tools" / "dev" / "hatari_harness.py"), "--setup", setup,
               "--disk", disk, "--start", "C:\\GAME\\" + p["start"].replace("/", "\\"), "--expect", str(exp),
               "--name", f"{game['row']}-{name}", "--memsize", str(p["memsize"]), "--log-root", str(RUNS),
               "--step-time", "30", "--parse", str(stage / "exits.dbg")]
        made = None
        if disk == "gemdrive":
            cmd += ["--drive", str(stage / "drive")]
        else:  # a game larger than the 32 MB image (Xenon 2) gets no run
            made = subprocess.run([str(REPO / "tools" / "dev" / "make_disks.sh"), str(p["folder"]), str(stage / "disks")],
                                  capture_output=True, text=True)
            cmd += ["--image", str(stage / "disks" / "ppdriver.img")]
            cmd[cmd.index("C:\\GAME\\" + p["start"].replace("/", "\\"))] = "C:\\LEMMINGS\\" + p["start"].replace("/", "\\")
            expectation(p["start"], exp)
            exp.write_text(exp.read_text().replace("GAME", "LEMMINGS"))
        if p["monitor"]:
            cmd += ["--monitor", p["monitor"]]
        out = "no PPDRIVER image: " + made.stderr.strip()[-80:] if made and made.returncode else \
            subprocess.run(cmd, capture_output=True, text=True).stdout
    runs = re.findall(r"run folder (\S+)", out)
    run = Path(runs[0]) if runs else None
    if run and not run.is_absolute():
        run = REPO / run
    row = {"row": game["row"], "name": game["name"], "strategy": game["strategy"], "setup": setup, "disk": disk,
           "start": p["start"], "memsize": p["memsize"], "monitor": p["monitor"], "run": run.name if run else ""}
    if run:
        row.update(analyse(run, game["strategy"], SURVEY / "games" / Path(game["download"]).with_suffix("")))
        row["snapshot"] = snapshot(run, game["row"], game["name"], setup, disk)
        shutil.rmtree(run / "drive", ignore_errors=True)
        for img in run.glob("*.img"):
            img.unlink()
    else:
        row.update({"result": "no run", "proposal": "unsure", "reason": out.strip()[-100:]})
    return row


def run_game(game: dict, p: dict, setup: str, disk: str, links: tuple = ()) -> dict:
    """run_one, again with more RAM while the run ends in trouble."""
    row = run_one(game, p, setup, disk, links)
    # some need more RAM in Hatari than their page says: Vector Invaders 2 MB, Laser Chess 4 MB;
    # when more RAM does not help (the same halt at 1, 2 and 4 MB), the first run counts
    first = row
    for more in (2, 4):
        trouble = row.get("halt") or "empty desktop" in row.get("screen", "") or row.get("screen") == "blank" or \
            "negative seek" in row.get("screen", "") or row.get("proposal") == "unsure" and "quit" in row.get("reason", "")
        if row["proposal"] in ("as it is", "fix") or not trouble or p["memsize"] >= more:
            continue
        p["memsize"] = more
        row = run_one(game, p, setup, disk, links)
    if row is not first and row["proposal"] == first["proposal"] and row.get("reason") == first.get("reason"):
        row = first
        row["snapshot"] = snapshot(RUNS / row["run"], row["row"], row["name"], setup, disk)
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=5)
    ap.add_argument("--only", nargs="+", default=[])
    ap.add_argument("--strategy")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--disk", default="gemdrive", choices=("gemdrive", "ppdriver"))
    ap.add_argument("--setup", default="st-104")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--retry", action="store_true", help="run again the games done whose proposal is not "
                    "'as it is' (GOS4/GOS5 'fix' apart), replacing their line")
    ap.add_argument("--reanalyse", action="store_true", help="recompute runs.tsv from the run folders")
    args = ap.parse_args()
    if args.reanalyse:
        rows = list(csv.DictReader(TSV.open(), delimiter="\t"))
        archives = {g["row"]: SURVEY / "games" / Path(g["download"]).with_suffix("")
                    for g in csv.DictReader((REPO / "src" / "survey" / "migration.csv").open())}
        todo = [r for r in rows if r["run"] and (RUNS / r["run"]).is_dir() and (not args.only or r["name"] in args.only)]
        with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:  # PNGs decoded in Python: slow
            for row, found in zip(todo, pool.map(reanalysed, todo, [archives.get(r["row"]) for r in todo], chunksize=8)):
                row.update(found)
        TSV.write_text("\t".join(FIELDS) + "\n" + "".join(
            "\t".join(str(r.get(k, "")).replace("\t", " ") for k in FIELDS) + "\n" for r in rows))
        print(f"{len(todo)} runs analysed again")
        return 0
    games = list(csv.DictReader((REPO / "src" / "survey" / "migration.csv").open()))
    files: dict[str, list[dict]] = {}
    for f in csv.DictReader((REPO / "src" / "survey" / "files.csv").open()):
        files.setdefault(f["archive"], []).append(f)
    records = {r["row"]: r for r in csv.DictReader((REPO / "src" / "survey" / "catalogue.csv").open())}
    done = set()
    if TSV.exists() and not args.redo:
        for r in csv.DictReader(TSV.open(), delimiter="\t"):
            if args.retry and r["proposal"] != "as it is" and not (
                    r["proposal"] == "fix" and r["strategy"] in ("Gamex + GOS4", "Gamex + GOS5")):
                continue
            done.add((r["row"], r["setup"], r["disk"]))
    if args.retry:
        tried = {r["row"] for r in csv.DictReader(TSV.open(), delimiter="\t")}
        games = [g for g in games if g["row"] in tried]
    todo = [g for g in games if (not args.only or g["name"] in args.only)
            and (not args.strategy or g["strategy"] == args.strategy)
            and (g["row"], args.setup, args.disk) not in done]
    todo = todo[:args.limit] if args.limit else todo
    RUNS.mkdir(parents=True, exist_ok=True)
    if not TSV.exists():
        TSV.write_text("\t".join(FIELDS) + "\n")
    print(f"{len(todo)} games to run ({len(done)} done), {args.jobs} at a time", flush=True)
    started = time.time()

    def work(game: dict) -> dict:
        p = plan(game, files.get(game["download"], []), records.get(game["row"], {}))
        if p is None:
            row = {"row": game["row"], "name": game["name"], "strategy": game["strategy"], "setup": args.setup,
                   "disk": args.disk, "proposal": "unsure", "reason": "no program to start in PP's archive"}
        else:
            row = run_game(game, p, args.setup, args.disk)
        line = "\t".join(str(row.get(k, "")).replace("\t", " ") for k in FIELDS) + "\n"
        key = (row["row"], row["setup"], row["disk"])
        with LOCK:  # one line per game, setup and disk: a new run replaces the old line
            lines = TSV.read_text().splitlines(keepends=True)
            kept = [l for l in lines[1:] if tuple(l.split("\t")[i] for i in (0, 3, 4)) != key]
            TSV.write_text(lines[0] + "".join(kept) + line)
        return row

    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        for n, row in enumerate(pool.map(work, todo), 1):
            print(f"{n:5}/{len(todo)} {time.time() - started:7.0f}s  {row['proposal']:9} {row['strategy']:16} "
                  f"{row['name'][:30]:30} {row.get('reason', '')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
