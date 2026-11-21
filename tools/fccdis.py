#!/usr/bin/env python3
"""fccdis - code/data separation and vasm source generation for the 1995 Neon FCC (68HC11).

Analysis core used by gen_source.py:
  * loads the ROM image (0x1200-0xFFFF)
  * finds code by recursive descent from the interrupt vectors and known entry points
  * decodes each instruction into a structured form that can be printed in vasm syntax
"""
from capstone import Cs, CS_ARCH_M680X, CS_MODE_M680X_6811
from capstone import m680x as X

BASE = 0x1200
TOP = 0x10000

VECTORS = [
    (0xFFD6, "SCI"), (0xFFD8, "SPI"), (0xFFDA, "PAI"), (0xFFDC, "PAOV"), (0xFFDE, "TOF"),
    (0xFFE0, "TOC5"), (0xFFE2, "TOC4"), (0xFFE4, "TOC3"), (0xFFE6, "TOC2"), (0xFFE8, "TOC1"),
    (0xFFEA, "TIC3"), (0xFFEC, "TIC2"), (0xFFEE, "TIC1"), (0xFFF0, "RTI"), (0xFFF2, "IRQ"),
    (0xFFF4, "XIRQ"), (0xFFF6, "SWI"), (0xFFF8, "ILLOP"), (0xFFFA, "COP"), (0xFFFC, "CMF"),
    (0xFFFE, "RESET"),
]

# mnemonics after which execution does not fall through
STOP = {"rts", "rti", "jmp", "bra", "stop", "wai", "swi"}
COND_BR = {"bhi", "bls", "bcc", "bcs", "bne", "beq", "bvc", "bvs", "bpl", "bmi", "bge", "blt",
           "bgt", "ble", "brset", "brclr", "bsr", "brn", "bhs", "blo"}
CALLS = {"jsr", "bsr"}


class Insn:
    __slots__ = ("addr", "size", "mn", "ops", "raw", "target", "imm_bytes")

    def __init__(self, ci):
        self.addr = ci.address
        self.size = ci.size
        self.mn = ci.mnemonic
        self.raw = bytes(ci.bytes)
        self.target = None
        self.ops = []           # list of (kind, value[, extra])
        pre = 2 if self.raw[0] in (0x18, 0x1A, 0xCD) else 1
        imm_bytes = self.size - pre
        for o in ci.operands:
            t = o.type
            if t == X.M680X_OP_REGISTER:
                continue
            if t == X.M680X_OP_IMMEDIATE:
                self.ops.append(["imm", o.imm])
            elif t == X.M680X_OP_DIRECT:
                self.ops.append(["dir", o.direct_addr])
                imm_bytes -= 1
            elif t == X.M680X_OP_EXTENDED:
                self.ops.append(["ext", o.ext.address])
                imm_bytes -= 2
            elif t == X.M680X_OP_INDEXED:
                self.ops.append(["idx", o.idx.offset & 0xFF, ci.reg_name(o.idx.base_reg)])
                imm_bytes -= 1
            elif t == X.M680X_OP_RELATIVE:
                self.ops.append(["rel", o.rel.address & 0xFFFF])
                self.target = o.rel.address & 0xFFFF
                imm_bytes -= 1
            else:
                raise ValueError("unhandled operand type %r at %04X" % (t, self.addr))
        # remaining bytes belong to immediates; bit masks are always one byte
        nimm = sum(1 for op in self.ops if op[0] == "imm")
        for op in self.ops:
            if op[0] == "imm":
                width = 1 if self.mn in ("bset", "bclr", "brset", "brclr") else max(1, imm_bytes // max(1, nimm))
                op.append(width)
                op[1] &= (0xFF if width == 1 else 0xFFFF)
        if self.mn in ("jsr", "jmp"):
            for op in self.ops:
                if op[0] == "ext":
                    self.target = op[1]


class Rom:
    def __init__(self, path):
        self.data = open(path, "rb").read()
        assert len(self.data) == TOP - BASE, "expected a 60928-byte image (0x1200-0xFFFF)"
        self.md = Cs(CS_ARCH_M680X, CS_MODE_M680X_6811)
        self.md.detail = True

    def byte(self, a):
        return self.data[a - BASE]

    def word(self, a):
        return (self.data[a - BASE] << 8) | self.data[a - BASE + 1]

    def decode(self, a):
        if not (BASE <= a < TOP):
            return None
        ci = next(self.md.disasm(self.data[a - BASE:a - BASE + 6], a), None)
        if ci is None or ci.mnemonic in ("fcb", "illgl"):
            return None
        return Insn(ci)


class Analysis:
    """Recursive-descent code discovery with conflict detection."""

    def __init__(self, rom, code_ranges):
        self.rom = rom
        self.code_ranges = code_ranges      # [(lo, hi_exclusive)] where code may live
        self.insn = {}                      # addr -> Insn
        self.owner = {}                     # byte addr -> insn start
        self.entries = {}                   # addr -> reason (call target, vector, table ...)
        self.callers = {}                   # target -> set(caller insn addr)
        self.speculative = set()

    def in_code(self, a):
        return any(lo <= a < hi for lo, hi in self.code_ranges)

    def trace(self, start, reason, speculative=False):
        work = [start]
        self.entries.setdefault(start, reason)
        while work:
            a = work.pop()
            while True:
                if a in self.insn or not self.in_code(a):
                    break
                if a in self.owner:          # jumps into the middle of a decoded instruction
                    break
                ins = self.rom.decode(a)
                if ins is None:
                    break
                if any((a + k) in self.owner for k in range(ins.size)):
                    break
                self.insn[a] = ins
                for k in range(ins.size):
                    self.owner[a + k] = a
                if speculative:
                    self.speculative.add(a)
                if ins.target is not None:
                    t = ins.target
                    self.callers.setdefault(t, set()).add(a)
                    if ins.mn in CALLS:
                        self.entries.setdefault(t, "call")
                    if self.in_code(t):
                        work.append(t)
                if ins.mn in STOP:
                    break
                if ins.mn == "jmp" and any(op[0] == "idx" for op in ins.ops):
                    break
                a += ins.size

    def try_speculative(self, start):
        """Decode a candidate block; keep it only if it is clean (no illegal opcode, no overlap)."""
        a = start
        seen = []
        while self.in_code(a) and a not in self.insn and a not in self.owner:
            ins = self.rom.decode(a)
            if ins is None:
                return False
            seen.append(ins)
            if ins.mn in STOP:
                break
            a += ins.size
        else:
            if not seen:
                return False
        if not seen or seen[-1].mn not in STOP:
            return False
        self.trace(start, "unreached (speculative)", speculative=True)
        return True
