"""Parse Robert Lloyd's FCC listing into an address map (code/data/labels/pointer words)."""
import re, json, sys
BASE = 0x1200
def parse(listing, binpath):
    rom = open(binpath, 'rb').read()
    code = {}       # addr -> length
    labels = {}     # addr -> [names]
    words = {}      # addr -> symbol text used in .word
    datab = {}      # addr -> 'byte'|'word'|'str'|'fill'
    equ = {}        # name -> value
    pending = []    # labels waiting for next address
    pc = None
    rx_code = re.compile(r'^([0-9A-F]{4}) ([0-9a-f]+)\s+(?:([A-Za-z_]\w*):)?')
    rx_alab = re.compile(r'^([0-9A-F]{4})\s+([A-Za-z_]\w*):\s*$')
    rx_lab = re.compile(r'^([A-Za-z_]\w*):\s*(?:;.*)?$')
    rx_equ = re.compile(r'^([A-Za-z_]\w*)\s+==\s+0x([0-9a-fA-F]+)')
    rx_org = re.compile(r'^\s*\.org\s+0x([0-9a-fA-F]+)')
    def addlab(a, n):
        labels.setdefault(a, [])
        if n not in labels[a]: labels[a].append(n)
    def flush(a):
        for n in pending: addlab(a, n)
        pending.clear()
    def unesc(s):
        out = bytearray(); i = 0
        while i < len(s):
            c = s[i]
            if c == '\\':
                j = i + 1
                if s[j] in '01234567':
                    k = j
                    while k < len(s) and k < j + 3 and s[k] in '01234567': k += 1
                    out.append(int(s[j:k], 8)); i = k; continue
                out.append(ord({'n': '\n', 't': '\t', 'r': '\r'}.get(s[j], s[j]))); i = j + 1; continue
            out.append(ord(c)); i += 1
        return bytes(out)
    for ln in open(listing, encoding='latin-1'):
        s = ln.rstrip('\r\n')
        m = rx_equ.match(s)
        if m: equ[m.group(1)] = int(m.group(2), 16); continue
        m = rx_org.match(s)
        if m: pc = int(m.group(1), 16); continue
        m = rx_alab.match(s)
        if m:
            pc = int(m.group(1), 16); pending.append(m.group(2)); continue
        m = rx_code.match(s)
        if m:
            a = int(m.group(1), 16); h = bytes.fromhex(m.group(2))
            if m.group(3): pending.append(m.group(3))
            flush(a); code[a] = len(h); pc = a + len(h); continue
        m = rx_lab.match(s)
        if m: pending.append(m.group(1)); continue
        t = s.strip()
        if not t or t.startswith(';') or t.startswith('.title'): continue
        t = t.split(';')[0].strip()
        if t.startswith('.byte'):
            vals = [v.strip() for v in t[5:].split(',')]
            flush(pc)
            for v in vals:
                datab[pc] = 'byte'; pc += 1
            continue
        if t.startswith('.word'):
            vals = [v.strip() for v in t[5:].split(',')]
            flush(pc)
            for v in vals:
                datab[pc] = 'word'; datab[pc + 1] = 'word2'
                if not re.fullmatch(r'0x[0-9a-fA-F]+|\d+', v): words[pc] = v
                pc += 2
            continue
        if t.startswith('ds'):
            n = int(t.split()[1]); flush(pc)
            for _ in range(n): datab[pc] = 'fill'; pc += 1
            continue
        if t.startswith('fs'):
            body = re.match(r'fs\s+"(.*)"\s*$', t).group(1)
            b = unesc(body); flush(pc)
            for _ in b: datab[pc] = 'str'; pc += 1
            continue
        raise ValueError("unparsed line: " + s)
    return rom, code, labels, words, datab, equ
if __name__ == "__main__":
    rom, code, labels, words, datab, equ = parse(sys.argv[1], sys.argv[2])
    cov = bytearray(0x10000)
    for a, n in code.items():
        for k in range(n): cov[a + k] |= 1
    for a in datab: cov[a] |= 2
    both = sum(1 for a in range(BASE, 0x10000) if cov[a] == 3)
    none = [a for a in range(BASE, 0x10000) if cov[a] == 0]
    print("code instr:", len(code), "data bytes:", len(datab), "labels:", sum(len(v) for v in labels.values()), "word syms:", len(words), "equ:", len(equ))
    print("overlap code/data:", both, " uncovered:", len(none))
    # gaps
    g = []; i = 0
    while i < len(none):
        j = i
        while j + 1 < len(none) and none[j + 1] == none[j] + 1: j += 1
        g.append((none[i], none[j])); i = j + 1
    print("uncovered ranges:", " ".join("%04X-%04X" % x for x in g[:40]), "..." if len(g) > 40 else "")
    # verify .word symbols resolve to the right value
    allsym = dict(equ)
    for a, ns in labels.items():
        for n in ns: allsym.setdefault(n, a)
    bad = 0
    for a, v in words.items():
        m = re.fullmatch(r'([A-Za-z_]\w*)([+-]\d+)?', v)
        val = allsym.get(m.group(1)) if m else None
        if val is None: bad += 1; continue
        if m.group(2): val += int(m.group(2))
        if ((rom[a - BASE] << 8) | rom[a - BASE + 1]) != val: bad += 1
    print("pointer words not matching ROM:", bad)
