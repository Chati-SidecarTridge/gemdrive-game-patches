#!/usr/bin/env python3
"""tools/unpack.py: the Gamex launcher's formats, unpacked on the host.

    unpack.py start <START.TOS> <out.prg>          the program packed in START.TOS (LEMLD2.TOS)
    unpack.py fic <file.FIC> <out.bin>             a .FIC payload (LS2DD, D15R_H5, D15R_F5)
    unpack.py relocate <prog.prg> <base> <out.bin> a GEMDOS program's header, text and data as
                                                   they sit in memory at text base <base>
    unpack.py text <prog.prg> <out.bin>            a GEMDOS program's text section (START.TOS's
                                                   stub)

The packer (src/notes/launcher-formats.md): a byte stream read by the same routine in
START.TOS's stub (text+$32) and in LEMLD2 (text+$B32). A control byte c:
  c = 0              end of stream
  1 <= c <= $7F      c literal bytes follow
  $80 <= c <= $BF    match: one offset byte d, copy (c & $3F) + 3 bytes from d bytes back
  $C0 <= c <= $FF    match: offset bytes hi, lo, copy (c & $3F) + 4 bytes from hi*256+lo back
A packed file starts with a 32-byte header that the unpacking code never reads: "C3", then the
packed size (long at +2), the unpacked size (+6), a long at +10 (the program's BSS size in
START.TOS, 0 in D15R, $7A007C00 in LS2DD) and a name at +16.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

HEADER = 32


def depack(src: bytes, start: int = 0) -> bytes:
    """Unpack the stream at src[start:] up to its end byte."""
    out = bytearray()
    i = start
    while True:
        c = src[i]
        i += 1
        if c == 0:
            return bytes(out)
        if c < 0x80:
            out += src[i:i + c]
            i += c
            continue
        if c & 0x40:
            dist = src[i] << 8 | src[i + 1]
            i += 2
            length = (c & 0x3F) + 4
        else:
            dist = src[i]
            i += 1
            length = (c & 0x3F) + 3
        if not 0 < dist <= len(out):
            sys.exit(f"error: match at stream offset {i:#x} reaches before the output")
        for _ in range(length):  # byte by byte: a match may overlap its own output
            out.append(out[-dist])


def fic_header(data: bytes) -> tuple[int, int, int, str]:
    """Packed size, unpacked size, BSS size and name of a 32-byte "C3" header."""
    if data[:2] != b"C3":
        sys.exit("error: no 'C3' header")
    packed, unpacked, bss = struct.unpack(">III", data[2:14])
    name = data[16:32].split(b"\0")[0].decode("latin-1")
    return packed, unpacked, bss, name


def unpack_fic(data: bytes) -> bytes:
    packed, unpacked, _, _ = fic_header(data)
    if len(data) < HEADER + packed or any(data[HEADER + packed:]):
        sys.exit(f"error: file is {len(data)} bytes, header says {HEADER} + {packed} (and zeros after)")
    out = depack(data, HEADER)
    if len(out) != unpacked:
        sys.exit(f"error: unpacked {len(out)} bytes, header says {unpacked}")
    return out


def unpack_start(data: bytes) -> bytes:
    """START.TOS: a GEMDOS program whose data section is a packed program."""
    magic, tlen, dlen = struct.unpack(">HII", data[:10])
    if magic != 0x601A:
        sys.exit("error: not a GEMDOS program")
    payload = data[28 + tlen:28 + tlen + dlen]
    packed = fic_header(payload)[0]
    pad = payload[HEADER + packed:]
    if len(pad) > 3 or any(pad):  # zeros up to an even length (Lemmings) or a multiple of 4
        sys.exit(f"error: {len(pad)} unexpected bytes after the packed program")
    return unpack_fic(payload[:HEADER + packed])


def relocate(prog: bytes, base: int) -> bytes:
    """Header, text and data of a GEMDOS program with its relocations applied for text base
    `base`, as TOS (or START.TOS's stub) leaves them in memory."""
    magic, tlen, dlen, _, slen = struct.unpack(">HIIII", prog[:18])
    if magic != 0x601A:
        sys.exit("error: not a GEMDOS program")
    image = bytearray(prog[:28 + tlen + dlen])
    table = 28 + tlen + dlen + slen
    first = struct.unpack(">I", prog[table:table + 4])[0]
    if first:
        pos, i = first, table + 4
        while True:
            value = struct.unpack(">I", image[28 + pos:32 + pos])[0]
            image[28 + pos:32 + pos] = struct.pack(">I", (value + base) & 0xFFFFFFFF)
            step = prog[i]
            i += 1
            while step == 1:
                pos += 254
                step = prog[i]
                i += 1
            if step == 0:
                break
            pos += step
    return bytes(image)


def main() -> None:
    args = sys.argv[1:]
    if len(args) == 3 and args[0] in ("start", "fic"):
        data = Path(args[1]).read_bytes()
        out = unpack_start(data) if args[0] == "start" else unpack_fic(data)
        Path(args[2]).write_bytes(out)
        print(f"{args[2]}: {len(out)} bytes")
    elif len(args) == 3 and args[0] == "text":
        data = Path(args[1]).read_bytes()
        magic, tlen = struct.unpack(">HI", data[:6])
        if magic != 0x601A:
            sys.exit("error: not a GEMDOS program")
        Path(args[2]).write_bytes(data[28:28 + tlen])
        print(f"{args[2]}: {tlen} bytes")
    elif len(args) == 4 and args[0] == "relocate":
        out = relocate(Path(args[1]).read_bytes(), int(args[2], 0))
        Path(args[3]).write_bytes(out)
        print(f"{args[3]}: {len(out)} bytes at {int(args[2], 0):#x}")
    else:
        sys.exit(__doc__.split("\n\n")[1])


if __name__ == "__main__":
    main()
