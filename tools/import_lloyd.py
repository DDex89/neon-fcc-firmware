#!/usr/bin/env python3
"""One-time import of Robert Lloyd's FCC disassembly annotations into this project's database.

Usage:
    python tools/import_lloyd.py <lloyd.asm> <rom.bin> <symbol2.txt> <tables.mpt>

Lloyd's files are part of the "jeffball718" package in the Turbonator release folder
(see README). They are not redistributed here; this script turns them into
annotations/*.json, which is everything gen_source.py needs.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lloyd import Lloyd
from fccdis import Rom, Analysis, VECTORS

CODE_RANGES = [(0x1200, 0xB4CD), (0xE229, 0xFFD6)]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    listing, rom_path, sym2, mpt = sys.argv[1:5]
    L = Lloyd(listing, rom_path, sym2, mpt)
    rom = Rom(rom_path)
    an = Analysis(rom, CODE_RANGES)
    seeds = {}
    for va, vn in VECTORS:
        an.trace(rom.word(va), "vector " + vn)
    for a in sorted(L.code_entries()):
        if an.in_code(a):
            an.trace(a, "named entry")
            seeds["%04X" % a] = "named entry"
    for a in sorted(L.words):
        t = rom.word(a)
        if an.in_code(t) and a not in an.owner:
            an.trace(t, "pointer table")
            seeds.setdefault("%04X" % t, "pointer @%04X" % a)
    changed = True
    while changed:
        changed = False
        for a in sorted(L.labels):
            if an.in_code(a) and a not in an.owner and a in L.code and an.try_speculative(a):
                seeds["%04X" % a] = "speculative"
                changed = True
    rom_names = {"%04X" % a: n for a, n in sorted(L.rom_names().items())}
    ram_names = {"%04X" % a: n for a, n in sorted(L.ram.items())}
    tables = {"%04X" % a: {k: v for k, v in t.items() if k != "addr"} for a, t in sorted(L.tables.items())}
    pointer_words = sorted("%04X" % a for a in L.words if a not in an.owner)
    os.makedirs(os.path.join(ROOT, "annotations"), exist_ok=True)
    def dump(name, obj):
        with open(os.path.join(ROOT, "annotations", name), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1, sort_keys=True)
            f.write("\n")
    dump("rom_labels.json", rom_names)
    dump("ram_symbols.json", ram_names)
    dump("tables.json", tables)
    dump("code_seeds.json", seeds)
    dump("pointer_words.json", pointer_words)
    print("rom labels %d, ram symbols %d, tables %d, extra code seeds %d, pointer words %d, insns %d"
          % (len(rom_names), len(ram_names), len(tables), len(seeds), len(pointer_words), len(an.insn)))


if __name__ == "__main__":
    main()
