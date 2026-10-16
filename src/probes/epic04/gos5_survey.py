#!/usr/bin/env python3
"""EPIC-04 STORY-04: what the launcher change needs, in each of the card's 87 FIXGOS5 games.

Usage: gos5_survey.py [<card>]    (default tools/dev/builds/sdcard, tools/survey/sdcard.py's)

For each game in INDEX.TXT's FIXGOS5 lines: its start program unpacked (tools/unpack.py's
unpack_start), its layout (text, data, BSS, relocations), and in it the places gd_start uses:
  check   movea.l $472.w,a1 / cmpi.l #'PPHD',-8(a1) / bne.w  -> no_pp_driver, the bne's target
  start   lea $FFFAA,a1 / lea $C0100,a0 / moveq #0,d0 / move.w 6(a0),d0 / adda.l d0,a0 / jsr (a0)
  image   movea.l ($C07E6).l,a6 / adda.l #$C0800,a6 (reuse_pp_driver's), and its constants
and each D15R*.FIC beside it unpacked: its entry table and file_io's first bytes (gd_quiet
expects lea (sr_save,pc),a0 / move.w sr,(a0)). Prints one line per game and a summary;
writes the table to tools/dev/builds/epic04/gos5-survey.tsv. Reads the card only.
"""

import hashlib
import re
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))
import unpack  # noqa: E402

CHECK = re.compile(rb"\x22\x78\x04\x72\x0c\xa9PPHD\xff\xf8\x66\x00(..)", re.S)
START = re.compile(rb"\x43\xf9\x00\x0f\xff\xaa\x41\xf9\x00\x0c\x01\x00\x70\x00\x30\x28\x00\x06"
                   rb"\xd1\xc0\x4e\x90")
IMAGE = re.compile(rb"\x2c\x79(....)\xdd\xfc(....)", re.S)


def even(pattern: re.Pattern, data: bytes) -> list[re.Match]:
    return [m for m in pattern.finditer(data) if m.start() % 2 == 0]


def program(prog: bytes) -> dict:
    _, tlen, dlen, blen, slen = struct.unpack(">HIIII", prog[:18])
    body = prog[28:28 + tlen + dlen]
    table = 28 + tlen + dlen + slen
    relocs = 0
    if struct.unpack(">I", prog[table:table + 4])[0]:
        relocs = 1 + sum(1 for b in prog[table + 4:] if b not in (0, 1))
    row = {"text": tlen, "data": dlen, "bss": blen, "relocs": relocs,
           "prog_sha": hashlib.sha256(prog).hexdigest()[:12]}
    checks = even(CHECK, body)
    row["check"] = ",".join(f"${m.start():X}" for m in checks) or "-"
    row["no_pp"] = ",".join(f"${m.start() + 12 + 2 + struct.unpack('>h', m.group(1))[0]:X}"
                            for m in checks) or "-"
    starts = even(START, body)
    row["start_d15r"] = ",".join(f"${m.start():X}" for m in starts) or "-"
    images = [m for m in even(IMAGE, body)
              if struct.unpack(">I", m.group(1))[0] >> 16 in (0x000B, 0x000C, 0x000D)]
    row["image"] = ",".join(f"${m.start():X}:({struct.unpack('>I', m.group(1))[0]:X})+"
                            f"{struct.unpack('>I', m.group(2))[0]:X}" for m in images) or "-"
    return row


def d15r(path: Path) -> str:
    raw = path.read_bytes()
    try:
        data = unpack.unpack_fic(raw)
    except SystemExit as e:
        return f"{path.name}:unpack-error({e})"
    table = struct.unpack(">5H", data[:10])
    fio = table[2]
    head = data[fio:fio + 6]
    ok = head[:2] == b"\x41\xfa" and head[4:6] == b"\x40\xd0"
    save = 0xC0100 + fio + 2 + struct.unpack(">h", head[2:4])[0] if ok else 0
    name = unpack.fic_header(raw)[3]
    return (f"{path.name}[{name}]:table={'.'.join(f'{w:04X}' for w in table)}"
            f":file_io=${0xC0100 + fio:X}:{head.hex()}" + (f":sr_save=${save:X}" if ok else ":UNEXPECTED"))


def main() -> int:
    card = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "tools" / "dev" / "builds" / "sdcard"
    lines = [l for l in (card / "INDEX.TXT").read_text(encoding="latin-1").splitlines()
             if l.startswith("FIXGOS5\\")]
    rows = []
    for line in lines:
        rel = line.split("  ")[0]
        start = card.joinpath(*rel.split("\\"))
        game = start.parent
        row = {"game": game.name, "start": start.name}
        try:
            row.update(program(unpack.unpack_start(start.read_bytes())))
        except SystemExit as e:
            row["error"] = str(e)
        fics = sorted(p for p in game.rglob("*") if p.is_file() and p.name.upper().startswith("D15R")
                      and p.suffix.upper() == ".FIC")
        row["d15r"] = " ".join(d15r(p) for p in fics) or "-"
        rows.append(row)
    keys = ["game", "start", "text", "data", "bss", "relocs", "prog_sha", "check", "no_pp",
            "start_d15r", "image", "d15r", "error"]
    out = REPO / "tools" / "dev" / "builds" / "epic04" / "gos5-survey.tsv"
    out.write_text("\n".join("\t".join(str(r.get(k, "")) for k in keys) for r in [dict(zip(keys, keys))] + rows) + "\n")
    for r in rows:
        print(" ".join(f"{k}={r.get(k, '')}" for k in keys if r.get(k, "") != ""))
    print(f"\n{len(rows)} games; programs: {len(set(r.get('prog_sha') for r in rows))} distinct")
    for k in ("check", "start_d15r", "image", "data", "bss"):
        print(k, Counter("found" if r.get(k) not in (None, "-", 0) and k in ("check", "start_d15r", "image")
                         else r.get(k) for r in rows).most_common(6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
