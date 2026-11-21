#!/usr/bin/env python3
"""Generate the vasm source tree (src/) from ROM dumps plus the annotation database.

    python tools/gen_source.py --roms roms/

The generated source is committed to the repository; this tool exists so that
improvements to the annotations (names, routine descriptions, comments) can be
applied consistently and re-verified byte-for-byte with tools/build.py.

Requires: Python 3.8+, capstone (pip install capstone).
"""
import argparse, bisect, json, os, re, sys, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fccdis import Rom, Analysis, VECTORS, BASE, TOP, STOP, CALLS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANN = os.path.join(ROOT, "annotations")
SRC = os.path.join(ROOT, "src")
CODE_RANGES = [(0x1200, 0xB4CD), (0xE229, 0xFFD6)]
CAL_RANGE = (0xB600, 0xE229)            # variant-specific: EEPROM window image + calibration

# Standard Motorola names for the 68HC11 register block at $1000
HC11_REGS = {
    0x00: ("PORTA", "Port A data (timer pins: IC1-IC3, OC2-OC5, PAI)"),
    0x02: ("PIOC", "Parallel I/O control"),
    0x03: ("PORTC", "Port C data"),
    0x04: ("PORTB", "Port B data (output only)"),
    0x05: ("PORTCL", "Port C latched data"),
    0x07: ("DDRC", "Port C data direction"),
    0x08: ("PORTD", "Port D data (SCI/SPI pins)"),
    0x09: ("DDRD", "Port D data direction"),
    0x0A: ("PORTE", "Port E data (A/D inputs)"),
    0x0B: ("CFORC", "Timer compare force"),
    0x0C: ("OC1M", "Output compare 1 mask"),
    0x0D: ("OC1D", "Output compare 1 data"),
    0x0E: ("TCNT", "Free-running timer counter (16 bit)"),
    0x10: ("TIC1", "Input capture 1 (16 bit)"),
    0x12: ("TIC2", "Input capture 2 (16 bit)"),
    0x14: ("TIC3", "Input capture 3 (16 bit)"),
    0x16: ("TOC1", "Output compare 1 (16 bit)"),
    0x18: ("TOC2", "Output compare 2 (16 bit)"),
    0x1A: ("TOC3", "Output compare 3 (16 bit)"),
    0x1C: ("TOC4", "Output compare 4 (16 bit)"),
    0x1E: ("TOC5", "Output compare 5 (16 bit)"),
    0x20: ("TCTL1", "Timer control 1 (OC2-OC5 pin actions)"),
    0x21: ("TCTL2", "Timer control 2 (input capture edges)"),
    0x22: ("TMSK1", "Timer interrupt mask 1 (OC/IC enables)"),
    0x23: ("TFLG1", "Timer interrupt flags 1 (write 1 to clear)"),
    0x24: ("TMSK2", "Timer interrupt mask 2 (TOI, RTII, PAOVI, PAII, prescaler)"),
    0x25: ("TFLG2", "Timer interrupt flags 2"),
    0x26: ("PACTL", "Pulse accumulator control / RTI rate"),
    0x27: ("PACNT", "Pulse accumulator count"),
    0x28: ("SPCR", "SPI control"),
    0x29: ("SPSR", "SPI status"),
    0x2A: ("SPDR", "SPI data"),
    0x2B: ("BAUD", "SCI baud rate"),
    0x2C: ("SCCR1", "SCI control 1"),
    0x2D: ("SCCR2", "SCI control 2"),
    0x2E: ("SCSR", "SCI status"),
    0x2F: ("SCDR", "SCI data"),
    0x30: ("ADCTL", "A/D control and status"),
    0x31: ("ADR1", "A/D result 1"),
    0x32: ("ADR2", "A/D result 2"),
    0x33: ("ADR3", "A/D result 3"),
    0x34: ("ADR4", "A/D result 4"),
    0x35: ("BPROT", "EEPROM block protect"),
    0x39: ("OPTION", "System configuration options"),
    0x3A: ("COPRST", "COP watchdog reset (write $55 then $AA)"),
    0x3B: ("PPROG", "EEPROM programming control"),
    0x3C: ("HPRIO", "Highest priority interrupt / mode select"),
    0x3D: ("INIT", "RAM and register block mapping"),
    0x3E: ("TEST1", "Factory test"),
    0x3F: ("CONFIG", "EEPROM-based configuration"),
}


def hx(v, w):
    return ("$%0" + str(2 * w) + "X") % v


def regname(off):
    if off in HC11_REGS:
        return HC11_REGS[off][0]
    if off - 1 in HC11_REGS and HC11_REGS[off - 1][1].endswith("(16 bit)"):
        return HC11_REGS[off - 1][0] + "+1"
    return None


def load_json(name, default=None):
    p = os.path.join(ANN, name)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_routines():
    """annotations/routines.md: '## XXXX Name' headers followed by description text."""
    out = {}
    p = os.path.join(ANN, "routines.md")
    if not os.path.exists(p):
        return out
    cur = None
    for ln in open(p, encoding="utf-8"):
        m = re.match(r"^##\s+([0-9A-Fa-f]{4})\s+(\S+)\s*$", ln)
        if m:
            cur = int(m.group(1), 16)
            out[cur] = {"name": m.group(2), "text": []}
            continue
        if cur is not None and not ln.startswith("#"):
            out[cur]["text"].append(ln.rstrip("\n"))
    for v in out.values():
        while v["text"] and not v["text"][-1].strip():
            v["text"].pop()
        while v["text"] and not v["text"][0].strip():
            v["text"].pop(0)
    return out


def load_inline():
    """annotations/comments.txt: 'XXXX  comment' lines (instruction comments)."""
    out = {}
    p = os.path.join(ANN, "comments.txt")
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            m = re.match(r"^([0-9A-Fa-f]{4})\s+(.+?)\s*$", ln)
            if m:
                out[int(m.group(1), 16)] = m.group(2)
    return out


def summary(text_lines):
    t = " ".join(l.strip() for l in text_lines if l.strip())
    m = re.match(r"(.+?[.!?])(\s|$)", t)
    return (m.group(1) if m else t)[:90]


class Gen:
    def __init__(self, code_rom):
        self.rom = code_rom
        self.an = Analysis(code_rom, CODE_RANGES)
        self.rom_labels = {int(k, 16): v for k, v in load_json("rom_labels.json", {}).items()}
        self.ram = {int(k, 16): v for k, v in load_json("ram_symbols.json", {}).items()}
        self.tables = {int(k, 16): v for k, v in load_json("tables.json", {}).items()}
        self.seeds = {int(k, 16): v for k, v in load_json("code_seeds.json", {}).items()}
        self.pwords = {int(a, 16) for a in load_json("pointer_words.json", [])}
        self.routines = load_routines()
        self.inline = load_inline()
        for off, (n, _) in HC11_REGS.items():          # standard register names
            self.ram[0x1000 + off] = n
        self.emitted = set()

    # ------------------------------------------------------------------ analysis
    def analyse(self):
        an, rom = self.an, self.rom
        for va, vn in VECTORS:
            an.trace(rom.word(va), "vector " + vn)
        for a, why in sorted(self.seeds.items()):
            if why == "speculative":
                continue
            an.trace(a, why)
        for a, why in sorted(self.seeds.items()):
            if why == "speculative":
                an.trace(a, "unreached (speculative)", speculative=True)
        # unique names
        seen = {"REGS"}
        for v in sorted(self.ram):
            n = re.sub(r"\W", "_", self.ram[v])
            if n in seen:
                n = "%s_%04X" % (n, v)
            seen.add(n)
            self.ram[v] = n
        names = dict(self.rom_labels)
        for a, r in self.routines.items():
            names[a] = r["name"]
        targets = {i.target for i in an.insn.values() if i.target is not None}
        self.names = {}
        for a in sorted(set(names) | set(an.entries) | targets):
            if not (BASE <= a < TOP):
                continue
            n = names.get(a) or (("sub_%04X" if an.entries.get(a) == "call" else "L%04X") % a)
            n = re.sub(r"\W", "_", n)
            if n in seen:
                n = "%s_%04X" % (n, a)
            seen.add(n)
            self.names[a] = n
        vt = {}
        for va, vn in VECTORS:
            vt.setdefault(rom.word(va), []).append(vn)
        self.vector_of = vt
        self.data_labels = sorted(a for a in self.names if not an.in_code(a))
        # routine entries = vectors, calls, named entries, pointer targets, speculative starts
        ent = set(an.entries) | set(vt) | {a for a in self.routines}
        self.entry_list = sorted(a for a in ent if a in an.insn)
        # callers per entry
        self.callers = {}
        for i in an.insn.values():
            if i.mn in CALLS and i.target is not None:
                self.callers.setdefault(i.target, set()).add(i.addr)

    def routine_of(self, addr):
        i = bisect.bisect_right(self.entry_list, addr) - 1
        return self.entry_list[i] if i >= 0 else None

    # ------------------------------------------------------------------ references
    def data_ref(self, a):
        if a in self.names:
            return self.names[a]
        i = bisect.bisect_right(self.data_labels, a) - 1
        if i >= 0:
            b = self.data_labels[i]
            if a - b < 64 and not self.an.in_code(a):
                return "%s+%d" % (self.names[b], a - b)
        return None

    def ref(self, a, width):
        if a < 0x1200:
            n = self.ram.get(a)
            return n if n else hx(a, width)
        n = self.data_ref(a)
        return n if n else hx(a, 2)

    def table_of(self, a):
        if a in self.tables:
            return a
        ks = sorted(self.tables)
        i = bisect.bisect_right(ks, a) - 1
        if i >= 0 and a - ks[i] < 64:
            return ks[i]
        return None

    def operands(self, ins):
        out = []
        for op in ins.ops:
            k = op[0]
            if k == "imm":
                v, w = op[1], op[2]
                s = "#" + hx(v, w)
                if w == 2 and ins.mn in ("ldx", "ldy", "cpx", "cpy", "lds") and v >= 0x1000:
                    if v == 0x1000:
                        s = "#REGS"
                    elif v in self.names:
                        s = "#" + self.names[v]
                out.append(s)
            elif k == "dir":
                out.append("<" + self.ref(op[1], 1))
            elif k == "ext":
                out.append(">" + self.ref(op[1], 2))
            elif k == "idx":
                out.append("%s,%s" % (hx(op[1], 1), op[2]))
            elif k == "rel":
                out.append(self.names.get(op[1], hx(op[1], 2)))
        return ",".join(out)

    def auto_comment(self, ins, xregs, yregs):
        """Short automatic comment: table meaning, register name, callee summary."""
        if ins.addr in self.inline:
            return self.inline[ins.addr]
        for op in ins.ops:
            if op[0] == "idx" and ((op[2] == "x" and xregs) or (op[2] == "y" and yregs)):
                rn = regname(op[1])
                if rn:
                    base = rn.split("+")[0]
                    desc = next((d for o, (n, d) in HC11_REGS.items() if n == base), "")
                    return "%s: %s" % (rn, desc)
        for op in ins.ops:
            if op[0] in ("ext", "imm") and op[1] >= 0xB800 and not self.an.in_code(op[1]):
                t = self.table_of(op[1])
                if t is not None:
                    d = self.tables[t].get("desc", "")
                    if d and d.lower() not in ("desc", "description", "detailed description", "desc."):
                        return "%s: %s" % (self.tables[t]["cname"], d[:70])
                    return "%s (%s)" % (self.tables[t]["cname"], self.tables[t].get("lname", ""))
        if ins.mn in CALLS and ins.target in self.routines:
            s = summary(self.routines[ins.target]["text"])
            if s:
                return s
        return None

    def routine_header(self, a):
        r = self.routines.get(a)
        lines = [";" + "-" * 99]
        title = "%s  ($%04X)" % (self.names.get(a, "sub_%04X" % a), a)
        if a in self.vector_of:
            title += "  -- interrupt vector: " + ", ".join(self.vector_of[a])
        lines.append("; " + title)
        if r and r["text"]:
            lines.append(";")
            # join wrapped source lines into paragraphs; list items start a new paragraph
            paras, cur = [], []
            for t in r["text"]:
                s = t.strip()
                if not s:
                    if cur:
                        paras.append(cur)
                    paras.append(None)
                    cur = []
                elif re.match(r"^(\d+\.|-)\s", s) and cur:
                    paras.append(cur)
                    cur = [s]
                else:
                    cur.append(s)
            if cur:
                paras.append(cur)
            for p in paras:
                if p is None:
                    lines.append(";")
                    continue
                text = " ".join(p)
                lead = re.match(r"^(\d+\.|-)\s", text)
                indent = " " * (len(lead.group(0)) if lead else 0)
                for k, w in enumerate(textwrap.wrap(text, 96, break_long_words=False,
                                                     subsequent_indent=indent)):
                    lines.append("; " + w)
        elif a in self.an.speculative:
            lines.append(";")
            lines.append("; Not reached by static analysis: called through a computed jump, or dead code.")
        # call graph
        cs = sorted(self.callers.get(a, []))
        if cs:
            who = sorted({self.names.get(self.routine_of(c), "?") for c in cs})
            lines.append(";")
            lines.append("; Called from: " + ", ".join(who[:8]) + (" ... (%d total)" % len(who) if len(who) > 8 else ""))
        lines.append(";" + "-" * 99)
        return lines

    # ------------------------------------------------------------------ emission
    def emit_range(self, rom, lo, hi, cal=False):
        an = self.an
        out = []
        a = lo
        pend = []
        xregs = yregs = False

        def flush():
            while pend:
                chunk = pend[:8]
                del pend[:8]
                out.append("        dc.b    " + ",".join(hx(b, 1) for b in chunk))

        while a < hi:
            in_code = a in an.insn and not cal
            if a in self.names:
                flush()
                xregs = yregs = False
                if in_code and a in self.entry_list:
                    out.append("")
                    out += self.routine_header(a)
                elif cal and a in self.tables:
                    out += self.table_header(a)
                elif not in_code and not cal and self.names[a] and not self.names[a].startswith("L"):
                    out.append("")
                out.append("%s:" % self.names[a])
                self.emitted.add(a)
            if in_code:
                flush()
                ins = an.insn[a]
                assert a + ins.size <= hi, "instruction crosses module boundary at %04X" % a
                text = "        %-7s %s" % (ins.mn, self.operands(ins))
                c = self.auto_comment(ins, xregs, yregs)
                if c:
                    text = "%-52s ; %s" % (text.rstrip(), c)
                out.append(text.rstrip())
                # track X/Y = register block base
                if ins.mn == "ldx":
                    xregs = any(op[0] == "imm" and op[1] == 0x1000 for op in ins.ops)
                elif ins.mn in ("pulx", "inx", "dex", "xgdx", "abx", "tsx", "ldx"):
                    xregs = False
                if ins.mn == "ldy":
                    yregs = any(op[0] == "imm" and op[1] == 0x1000 for op in ins.ops)
                elif ins.mn in ("puly", "iny", "dey", "xgdy", "aby", "tsy"):
                    yregs = False
                if ins.mn in STOP:
                    out.append("")
                a += ins.size
                continue
            if cal:
                n = self.cal_object(rom, a, hi, out, flush, pend)
                if n:
                    a += n
                    continue
            if a in self.pwords and a + 1 < hi and a + 1 not in self.names:
                t = rom.word(a)
                n = self.data_ref(t) if t >= 0x1200 else None
                if n and "+" not in n:
                    flush()
                    out.append("        dc.w    %s" % n)
                    a += 2
                    continue
            run = 0
            while (a + run < hi and rom.byte(a + run) == 0xFF and (a + run) not in an.insn
                   and (run == 0 or (a + run) not in self.names)):
                run += 1
            if run >= 16:
                flush()
                out.append("        dcb.b   %d,$FF" % run)
                a += run
                continue
            pend.append(rom.byte(a))
            a += 1
        flush()
        return out

    # ------------------------------------------------------------------ calibration formatting
    def table_header(self, a):
        t = self.tables[a]
        lines = ["", "; " + "=" * 98]
        lines.append("; %s - %s" % (t["cname"], t.get("lname", "")))
        d = t.get("desc", "")
        if d and d.lower() not in ("desc", "description", "detailed description", "desc."):
            for w in textwrap.wrap(d, 94):
                lines.append(";   " + w)
        g = t.get("group", "").replace("_", " ").replace("\\", " / ").strip(" /")
        if g:
            lines.append(";   group: " + g)
        if t.get("xaxis") or t.get("yaxis"):
            lines.append(";   axes: x = %s | y = %s" % (t.get("xaxis", ""), t.get("yaxis", "")))
        m = re.match(r"^\S+\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(\S+)", t.get("yaxis", ""))
        if m and m.group(3).lower() not in ("out", "in", "y", "count", "scale", "steps"):
            lo, hi = float(m.group(1)), float(m.group(2))
            if hi > lo:
                step = (hi - lo) / 256.0
                off = "" if lo == 0 or lo < 0 and t.get("type") in ("7",) else " %+g" % lo
                lines.append(";   value scale (MP Tune display, approximate): raw x %.4g%s %s"
                             % (step, off, m.group(3)))
        lines.append("; " + "=" * 98)
        return lines

    def next_label(self, a, hi):
        i = bisect.bisect_right(self.data_labels, a)
        n = self.data_labels[i] if i < len(self.data_labels) else hi
        return min(n, hi)

    def cal_object(self, rom, a, hi, out, flush, pend):
        """Format a known calibration table; return number of bytes consumed (0 = not handled)."""
        if a not in self.tables or pend:
            return 0
        t = self.tables[a]
        typ = t.get("type", "")
        end = self.next_label(a, hi)
        size = end - a
        b = [rom.byte(a + k) for k in range(size)]
        if typ == "7" and size >= 3:
            rows, cols, sign = b[0], b[1], b[2]
            if rows and cols and 3 + rows * cols <= size:
                out.append("        dc.b    %s,%s,%s%s; %d rows x %d cols, %s" % (
                    hx(rows, 1), hx(cols, 1), hx(sign, 1), " " * 8, rows, cols,
                    "signed" if sign else "unsigned"))
                for r in range(rows):
                    row = b[3 + r * cols: 3 + (r + 1) * cols]
                    out.append("        dc.b    " + ",".join(hx(v, 1) for v in row) + "   ; row %d" % r)
                rest = b[3 + rows * cols:]
                for k in range(0, len(rest), 8):
                    out.append("        dc.b    " + ",".join(hx(v, 1) for v in rest[k:k + 8]))
                return size
        if typ == "0" and size >= 3:
            n = b[0]
            need = 1 + 4 * (n - 1) + 2 if n >= 1 else 0
            if 1 <= n <= 32 and need <= size:
                out.append("        dc.b    %s%s; %d breakpoints (x, y, slope16 ... last x, y)" % (hx(n, 1), " " * 21, n))
                p = 1
                for k in range(n - 1):
                    x, y, s = b[p], b[p + 1], (b[p + 2] << 8) | b[p + 3]
                    out.append("        dc.b    %s,%s,%s,%s            ; x=%3d y=%3d slope=%s" % (
                        hx(x, 1), hx(y, 1), hx(b[p + 2], 1), hx(b[p + 3], 1), x, y, hx(s, 2)))
                    p += 4
                out.append("        dc.b    %s,%s                    ; x=%3d y=%3d (end)" % (hx(b[p], 1), hx(b[p + 1], 1), b[p], b[p + 1]))
                p += 2
                rest = b[p:]
                run = 0
                while run < len(rest) and rest[run] == 0xFF:
                    run += 1
                if run == len(rest) and run >= 16:
                    out.append("        dcb.b   %d,$FF" % run)
                else:
                    for k in range(0, len(rest), 8):
                        out.append("        dc.b    " + ",".join(hx(v, 1) for v in rest[k:k + 8]))
                return size
        if typ in ("3", "5") and size >= 1:
            v = b[0]
            out.append("        dc.b    %s%s; %d" % (hx(v, 1), " " * 25, v))
            return 1
        if typ == "4" and size >= 2:
            out.append("        dc.w    %s%s; %d" % (hx((b[0] << 8) | b[1], 2), " " * 23, (b[0] << 8) | b[1]))
            return 2
        return 0


# ---------------------------------------------------------------------- module layout
def load_modules():
    mods = load_json("modules.json")
    return [(int(m["start"], 16), m["file"], m["title"]) for m in mods]


def write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines).rstrip() + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roms", default=os.path.join(ROOT, "roms"), help="directory with <partnumber>.bin dumps")
    args = ap.parse_args()
    variants = load_json("variants.json")
    roms = {}
    for pn in variants:
        p = os.path.join(args.roms, pn + ".bin")
        if os.path.exists(p):
            roms[pn] = Rom(p)
    if not roms:
        sys.exit("no ROM dumps found in " + args.roms)
    code_pn = next(pn for pn in variants if pn in roms)
    code_rom = roms[code_pn]
    for pn, r in roms.items():
        for lo, hi in CODE_RANGES + [(0xFFD6, 0x10000), (0x1200, 0xB600)]:
            assert r.data[lo - BASE:hi - BASE] == code_rom.data[lo - BASE:hi - BASE], \
                "%s: code differs from %s in %04X-%04X" % (pn, code_pn, lo, hi)
    g = Gen(code_rom)
    g.analyse()
    mods = load_modules()
    banner = [
        "; Dodge/Plymouth Neon 1995 FCC engine controller (68HC11) - reconstructed source",
        "; Code base: B4CC (Chrysler 5269718 / Mopar Performance 5007033).",
        "; Original firmware (c) 1994 Chrysler Corp. Disassembly annotations derived from",
        "; the work of Robert Lloyd (BoostButton). Generated by tools/gen_source.py -",
        "; edit annotations/*.md and regenerate rather than editing by hand.",
    ]
    # code modules
    bounds = [m[0] for m in mods] + [0x10000]
    includes = []
    for k, (start, fname, title) in enumerate(mods):
        end = bounds[k + 1]
        if fname == "@cal":
            includes.append("@cal")
            continue
        body = g.emit_range(code_rom, start, end)
        hdr = banner + [";", "; %s  ($%04X-$%04X)" % (title, start, end - 1), ""]
        write(os.path.join(SRC, fname), hdr + ["        org     $%04X" % start, ""] + body)
        includes.append(fname)
    # calibration per variant
    cal_start = next(m[0] for m in mods if m[1] == "@cal")
    cal_end = bounds[[m[1] for m in mods].index("@cal") + 1]
    emitted_before_cal = set(g.emitted)
    cal_emitted = None
    for pn, r in roms.items():
        g.emitted = set(emitted_before_cal)
        body = g.emit_range(r, cal_start, cal_end, cal=True)
        if cal_emitted is None:
            cal_emitted = set(g.emitted)
        assert g.emitted == cal_emitted, "calibration label sets differ between variants"
        hdr = banner + [";", "; Calibration for %s: %s" % (pn, variants[pn]["description"]),
                        "; $B600-$B7FF is the window of the HC11 internal EEPROM: the CPU does not see these",
                        "; dump bytes at run time and the ROM checksum skips them.", ""]
        write(os.path.join(SRC, "cal", pn + ".asm"), hdr + ["        org     $%04X" % cal_start, ""] + body)
    g.emitted = cal_emitted
    # include files
    inc = banner + ["", "; 68HC11 register block (INIT maps it to $1000)", "REGS    equ     $1000", ""]
    for off, (n, d) in sorted(HC11_REGS.items()):
        inc.append("%-8s equ     $%04X        ; %s" % (n, 0x1000 + off, d))
    write(os.path.join(SRC, "inc", "hc11_regs.inc"), inc)
    ram = banner + ["", "; RAM variables. Names come from the original disassembly; many are still tentative.", ""]
    for v, n in sorted(g.ram.items()):
        if 0x1000 <= v < 0x1040:
            continue
        ram.append("%-44s equ $%04X" % (n, v))
    write(os.path.join(SRC, "inc", "ram.inc"), ram)
    orph = banner + ["", "; Labels that point inside another instruction or data object.", ""]
    for a, n in sorted(g.names.items()):
        if a not in g.emitted:
            orph.append("%-44s equ $%04X" % (n, a))
    write(os.path.join(SRC, "inc", "inner_labels.inc"), orph)
    # top-level files
    for pn in roms:
        top = banner + ["", "; Top-level file for %s. Build: python tools/build.py %s" % (pn, pn), "",
                        '        include "inc/hc11_regs.inc"', '        include "inc/ram.inc"',
                        '        include "inc/inner_labels.inc"', ""]
        for f in includes:
            top.append('        include "%s"' % ("cal/%s.asm" % pn if f == "@cal" else f))
        write(os.path.join(SRC, "fcc_%s.asm" % pn), top)
    st = g.an
    print("modules %d, instructions %d (speculative %d), labels %d, routines described %d, variants %s"
          % (len(mods), len(st.insn), len(st.speculative), len(g.names), len(g.routines), ",".join(roms)))


if __name__ == "__main__":
    main()
