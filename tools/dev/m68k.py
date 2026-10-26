"""tools/dev/m68k.py: 68000 instruction lengths and control flow, for tracing code
Not a disassembler: objdump gives the text, this gives where
each instruction ends, where it can go next, and which addresses it refers to.

Besides the 68000 set, the few 68010/68030 forms PP's launcher uses on the Falcon
and the TT are sized: MOVEC (4 bytes) and PMMU instructions ($F000-$F03F with an
extension word). Any other line-F word is one word long.
"""

from __future__ import annotations

from dataclasses import dataclass, field

SIZE = {0: "b", 1: "w", 2: "l"}


@dataclass
class Insn:
    addr: int
    length: int
    kind: str = "next"            # next | branch | jump | call | stop
    target: int | None = None     # branch, jump or call destination, when static
    refs: list[int] = field(default_factory=list)  # PC-relative and absolute.l addresses
    abs_sizes: list[str] = field(default_factory=list)  # "w"/"l" per absolute operand, in order
    pcrel: list[int] = field(default_factory=list)  # the PC-relative targets among refs


def _word(b: bytes, i: int) -> int:
    return b[i] << 8 | b[i + 1]


def _signed16(v: int) -> int:
    return v - 0x10000 if v & 0x8000 else v


class _Decoder:
    def __init__(self, data: bytes, base: int, addr: int):
        self.data, self.base, self.addr = data, base, addr
        self.off = addr - base
        self.pos = 2          # bytes consumed so far
        self.refs: list[int] = []
        self.abs_sizes: list[str] = []
        self.pcrel: list[int] = []
        self.ea_target: int | None = None

    def need(self, n: int) -> None:
        if self.off + self.pos + n > len(self.data):
            raise ValueError("runs past the end")

    def ea(self, mode: int, reg: int, size: str = "w") -> None:
        """Consume the extension words of an effective address."""
        here = self.addr + self.pos
        if mode <= 4:
            return
        if mode in (5, 6):
            self.need(2)
            self.pos += 2
            return
        if mode != 7:
            raise ValueError("bad mode")
        if reg == 0:                                   # abs.w
            self.need(2)
            v = _signed16(_word(self.data, self.off + self.pos)) & 0xFFFFFFFF
            self.ea_target = v
            self.abs_sizes.append("w")
            self.pos += 2
        elif reg == 1:                                 # abs.l
            self.need(4)
            v = _word(self.data, self.off + self.pos) << 16 | _word(self.data, self.off + self.pos + 2)
            self.ea_target = v
            self.refs.append(v)
            self.abs_sizes.append("l")
            self.pos += 4
        elif reg == 2:                                 # (d16,pc)
            self.need(2)
            v = here + _signed16(_word(self.data, self.off + self.pos))
            self.ea_target = v
            self.refs.append(v)
            self.pcrel.append(v)
            self.pos += 2
        elif reg == 3:                                 # (d8,pc,xn): a table base
            self.need(2)
            d8 = self.data[self.off + self.pos + 1]
            self.refs.append(here + (d8 - 256 if d8 & 0x80 else d8))
            self.pcrel.append(self.refs[-1])
            self.ea_target = None
            self.pos += 2
        elif reg == 4:                                 # #imm
            n = 4 if size == "l" else 2
            self.need(n)
            if n == 4:
                v = _word(self.data, self.off + self.pos) << 16 | _word(self.data, self.off + self.pos + 2)
                self.refs.append(v)
            self.pos += n
        else:
            raise ValueError("bad mode 7 register")

    def imm(self, size: str) -> None:
        self.ea(7, 4, size)


def decode(data: bytes, base: int, addr: int) -> Insn | None:
    """The instruction at addr (data is loaded at base), or None if the bytes there
    are not one."""
    try:
        return _decode(data, base, addr)
    except (ValueError, IndexError):
        return None


def _decode(data: bytes, base: int, addr: int) -> Insn:
    if addr & 1:
        raise ValueError("odd address")
    d = _Decoder(data, base, addr)
    d.need(0)
    op = _word(data, addr - base)
    line, mode, reg = op >> 12, (op >> 3) & 7, op & 7
    size_bits = (op >> 6) & 3
    kind, target = "next", None

    def size() -> str:
        if size_bits == 3:
            raise ValueError("bad size")
        return SIZE[size_bits]

    if line == 0:
        if op & 0x0100:
            if mode == 1:                                # MOVEP
                d.need(2)
                d.pos += 2
            else:                                        # BTST/BCHG/BCLR/BSET Dn,<ea>
                d.ea(mode, reg, "b")
        else:
            kind_bits = (op >> 9) & 7
            if op in (0x003C, 0x007C, 0x023C, 0x027C, 0x0A3C, 0x0A7C):
                d.need(2)
                d.pos += 2                               # ORI/ANDI/EORI to CCR/SR
            elif kind_bits == 4:                         # BTST/BCHG/BCLR/BSET #n,<ea>
                d.need(2)
                d.pos += 2
                d.ea(mode, reg, "b")
            elif kind_bits in (0, 1, 2, 3, 5, 6):
                s = size()
                d.imm(s)
                d.ea(mode, reg, s)
            else:
                raise ValueError("bad line 0")
    elif line in (1, 2, 3):                              # MOVE
        s = {1: "b", 3: "w", 2: "l"}[line]
        d.ea(mode, reg, s)
        d.ea((op >> 6) & 7, (op >> 9) & 7, s)
    elif line == 4:
        if op == 0x4AFC:
            kind = "stop"                                # ILLEGAL
        elif op in (0x4E70, 0x4E71, 0x4E76):
            pass                                         # RESET, NOP, TRAPV
        elif op == 0x4E72:
            d.need(2)
            d.pos += 2                                   # STOP
        elif op in (0x4E73, 0x4E75, 0x4E77):
            kind = "stop"                                # RTE, RTS, RTR
        elif 0x4E40 <= op <= 0x4E6F:
            if 0x4E50 <= op <= 0x4E57:
                d.need(2)
                d.pos += 2                               # LINK
        elif op in (0x4E7A, 0x4E7B):
            d.need(2)
            d.pos += 2                                   # MOVEC
        elif (op & 0xFF80) == 0x4E80:                    # JSR, JMP
            d.ea(mode, reg, "l")
            jsr = not op & 0x40
            static = mode == 7 and reg in (0, 1, 2)
            target = d.ea_target if static else None
            kind = "call" if jsr else "jump"
        elif (op & 0xF1C0) == 0x41C0:                    # LEA
            d.ea(mode, reg, "l")
        elif (op & 0xF1C0) == 0x4180:                    # CHK
            d.ea(mode, reg, "w")
        elif (op & 0xFFC0) == 0x4840:                    # SWAP, PEA
            if mode != 0:
                d.ea(mode, reg, "l")
        elif (op & 0xFB80) == 0x4880:                    # EXT, MOVEM
            if mode != 0:
                d.need(2)
                d.pos += 2
                d.ea(mode, reg, "l")
        elif (op & 0xFFC0) in (0x40C0, 0x44C0, 0x46C0):  # MOVE from SR, to CCR, to SR
            d.ea(mode, reg, "w")
        elif (op & 0xFFC0) == 0x4AC0:                    # TAS
            d.ea(mode, reg, "b")
        elif (op & 0xFFC0) == 0x4800:                    # NBCD
            d.ea(mode, reg, "b")
        elif (op & 0xFF00) in (0x4000, 0x4200, 0x4400, 0x4600, 0x4A00):  # NEGX CLR NEG NOT TST
            d.ea(mode, reg, size())
        else:
            raise ValueError("bad line 4")
    elif line == 5:
        if size_bits == 3:
            if mode == 1:                                # DBcc
                d.need(2)
                target = addr + 2 + _signed16(_word(data, addr - base + 2))
                d.pos += 2
                kind = "branch"
            else:                                        # Scc
                d.ea(mode, reg, "b")
        else:                                            # ADDQ, SUBQ
            d.ea(mode, reg, size())
    elif line == 6:                                      # BRA, BSR, Bcc
        disp = op & 0xFF
        if disp == 0:
            d.need(2)
            disp = _signed16(_word(data, addr - base + 2))
            d.pos += 2
        elif disp == 0xFF:
            raise ValueError("32-bit branch")
        else:
            disp = disp - 256 if disp & 0x80 else disp
        target = addr + 2 + disp
        cond = (op >> 8) & 0xF
        kind = "jump" if cond == 0 else "call" if cond == 1 else "branch"
    elif line == 7:                                      # MOVEQ
        if op & 0x0100:
            raise ValueError("bad MOVEQ")
    elif line in (8, 9, 0xB, 0xC, 0xD):
        opmode = (op >> 6) & 7
        if line in (8, 0xC) and opmode in (3, 7):        # DIVU DIVS MULU MULS
            d.ea(mode, reg, "w")
        elif line in (9, 0xB, 0xD) and opmode in (3, 7):  # SUBA CMPA ADDA
            d.ea(mode, reg, "w" if opmode == 3 else "l")
        elif line in (8, 9, 0xC, 0xD) and (op & 0x1F0) == 0x100:
            pass                                         # SBCD SUBX ABCD ADDX (registers)
        elif line in (8, 9, 0xC, 0xD) and (op & 0x1F0) in (0x140, 0x180) and line in (9, 0xD):
            pass                                         # SUBX ADDX .w/.l
        elif line == 0xC and (op & 0x1F8) in (0x140, 0x148, 0x188):
            pass                                         # EXG
        elif line == 0xB and opmode in (4, 5, 6) and mode == 1:
            pass                                         # CMPM
        else:                                            # OR SUB CMP EOR AND ADD
            d.ea(mode, reg, SIZE[opmode & 3])
    elif line == 0xA:
        pass                                             # line A
    elif line == 0xE:
        if size_bits == 3:
            d.ea(mode, reg, "w")                         # memory shift
    elif line == 0xF:
        if (op & 0xFFC0) == 0xF000:                      # PMMU (68030), with an extension word
            d.need(2)
            d.pos += 2
            d.ea(mode, reg, "l")
    return Insn(addr, d.pos, kind, target, d.refs, d.abs_sizes, d.pcrel)
