"""Import Robert Lloyd's FCC annotations (listing labels, equates, symbol types, .mpt table info)."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import re
from parse_lloyd import parse as parse_listing

GENERIC = re.compile(r'^(L[0-9A-Fa-f]{4}|CODE[0-9A-Fa-f]{4}(_\w+)?|TABLE[0-9a-fA-F]{4}|BYTE[0-9a-fA-F]{2,4}|WORD[0-9a-fA-F]{4}|Pointer[0-9a-fA-F]{4})$')


def is_generic(n):
    return bool(GENERIC.match(n))


def best(names):
    named = [n for n in names if not is_generic(n)]
    return (named or names)[0]


def load_symbol2(path):
    out = {}
    for ln in open(path, encoding="latin-1"):
        p = ln.rstrip("\r\n").split("\t")
        if len(p) < 3 or p[0].startswith(";"):
            continue
        try:
            a = int(p[0], 16)
        except ValueError:
            continue
        typ = p[1].strip()
        name = p[2].strip()
        if typ.startswith("T_HEX_BYTE") and not name:
            name = typ[len("T_HEX_BYTE"):].strip()
            typ = "T_HEX_BYTE"
        if name:
            out.setdefault(a, []).append((typ, name))
    return out


def load_mpt(path):
    """addr -> dict(cname, lname, type, xaxis, yaxis, desc, group)"""
    tables = {}
    cur = None
    for ln in open(path, encoding="latin-1"):
        s = ln.strip()
        m = re.match(r";mptbladdr\s+0x([0-9A-Fa-f]+)", s)
        if m:
            cur = {"addr": int(m.group(1), 16)}
            continue
        if cur is None:
            continue
        for key, field in (("mptbltype", "type"), ("mptbllname", "lname"), ("mptblcname", "cname"),
                           ("mpxaxis", "xaxis"), ("mpyaxis", "yaxis"), ("mptbldesc", "desc"), ("mpgrp", "group")):
            if s.startswith(";" + key + " ") or s == ";" + key:
                cur[field] = s.split(None, 1)[1].strip() if " " in s else ""
        if "desc" in cur and "cname" in cur and cur["addr"] not in tables:
            cur["desc"] = cur["desc"].replace("_", " ")
            tables[cur["addr"]] = cur
    return tables


class Lloyd:
    def __init__(self, listing, binpath, symbol2, mpt):
        (self.rom, self.code, labels, self.words, self.datab, self.equ) = parse_listing(listing, binpath)
        self.labels = labels                  # addr -> [names]
        self.sym2 = load_symbol2(symbol2)
        self.tables = load_mpt(mpt)
        # value -> preferred RAM/IO name
        inv = {}
        for n, v in self.equ.items():
            inv.setdefault(v, []).append(n)
        for a, lst in self.sym2.items():
            if a < 0x1200:
                for typ, n in lst:
                    inv.setdefault(a, []).append(n)
        self.ram = {v: best(ns) for v, ns in inv.items()}

    def code_entries(self):
        out = set()
        for a, lst in self.sym2.items():
            for typ, n in lst:
                if typ == "T_CODE":
                    out.add(a)
        return out

    def rom_names(self):
        names = {}
        for a, ns in self.labels.items():
            names[a] = list(ns)
        for a, lst in self.sym2.items():
            if a >= 0x1200:
                for typ, n in lst:
                    names.setdefault(a, [])
                    if n not in names[a]:
                        names[a].append(n)
        return {a: best(ns) for a, ns in names.items()}
