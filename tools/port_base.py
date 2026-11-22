#!/usr/bin/env python3
"""Build an address map from the reference code base (B4CC) to another code base.

The two images are normalised (a linear disassembly in which every 16-bit operand
that points into the ROM is masked, because those are exactly the bytes that change
when code moves), then matched with unique k-byte anchors (patience-diff style).
Between two anchors the span is mapped with one offset when both sides have the
same length; otherwise the gap is matched again with difflib.

Usage:
  python3 tools/port_base.py --base B559 --ref roms/5269718.bin --img <B559 image>
          [--cal-ref roms/5269718.bin --cal-img <B559 image of the same application>]

The calibration is aligned byte by byte, so it should be compared with an image of the same
application: for 5269718 (rev B of 4874164) that is 4874164. With an unrelated calibration the
split points can land a few bytes off where the values happen to match.
Writes annotations/bases/<base>/map.json and prints a coverage report.
"""
import argparse, bisect, difflib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from fccdis import Rom, BASE

K = 10


def normalise(rom, lo, hi):
    """Linear sweep of [lo, hi): returns (bytes, list of addresses), ROM pointers masked."""
    out, addr = bytearray(), []
    a = lo
    while a < hi:
        ins = rom.decode(a) if rom.byte(a) != 0xFF else None
        if ins is None or a + ins.size > hi:
            out.append(rom.byte(a)); addr.append(a); a += 1
            continue
        raw = bytearray(ins.raw)
        for op in ins.ops:
            if op[0] == "ext" or (op[0] == "imm" and len(op) > 2 and op[2] == 2):
                if 0x1200 <= op[1] <= 0xFFFF:
                    i = raw.find(bytes([op[1] >> 8, op[1] & 0xFF]), 1)
                    if i > 0:
                        raw[i] = raw[i + 1] = 0xEE
        out += raw; addr += range(a, a + ins.size); a += ins.size
    return bytes(out), addr


def translated(rom, lo, hi, mapf):
    """Linear sweep of the reference with every ROM pointer replaced by its mapped value."""
    out, addr = bytearray(), []
    a = lo
    while a < hi:
        ins = rom.decode(a) if rom.byte(a) != 0xFF else None
        if ins is None or a + ins.size > hi:
            out.append(rom.byte(a)); addr.append(a); a += 1
            continue
        raw = bytearray(ins.raw)
        for op in ins.ops:
            if op[0] == "ext" or (op[0] == "imm" and len(op) > 2 and op[2] == 2):
                if 0x1200 <= op[1] <= 0xFFFF:
                    i = raw.find(bytes([op[1] >> 8, op[1] & 0xFF]), 1)
                    m = mapf(op[1])
                    if i > 0:
                        raw[i], raw[i + 1] = (m >> 8, m & 0xFF) if m is not None else (0xEE, 0xEE)
            if op[0] == "rel":
                m, here = mapf(op[1]), mapf(a)
                if m is not None and here is not None:
                    off = m - (here + ins.size)
                    if -128 <= off <= 127:
                        raw[-1] = off & 0xFF
        out += raw; addr += range(a, a + ins.size); a += ins.size
    return bytes(out), addr


def mapper(runs):
    runs = sorted(runs)
    los = [r[0] for r in runs]
    def f(a):
        i = bisect.bisect_right(los, a) - 1
        if i >= 0 and runs[i][0] <= a < runs[i][1]:
            return a + runs[i][2]
        return None
    return f


def anchors(x, y):
    def grams(s):
        c = {}
        for i in range(len(s) - K + 1):
            g = s[i:i + K]
            c[g] = -1 if g in c else i
        return c
    gx, gy = grams(x), grams(y)
    pairs = sorted((i, gy[g]) for g, i in gx.items() if i >= 0 and gy.get(g, -1) >= 0)
    # longest increasing subsequence on the second coordinate
    tails, prev, idx = [], [None] * len(pairs), []
    for n, (_, j) in enumerate(pairs):
        k = bisect.bisect_left(tails, j)
        if k == len(tails):
            tails.append(j); idx.append(n)
        else:
            tails[k] = j; idx[k] = n
        prev[n] = idx[k - 1] if k else None
    seq, n = [], (idx[-1] if idx else None)
    while n is not None:
        seq.append(pairs[n]); n = prev[n]
    return seq[::-1]


def match(x, y):
    """Return list of matched index pairs (i, j)."""
    res = []
    an = anchors(x, y)
    pi, pj = 0, 0
    for i, j in an + [(len(x), len(y))]:
        if i < pi or j < pj:
            continue
        gx, gy = x[pi:i], y[pj:j]
        if len(gx) == len(gy):
            res += [(pi + k, pj + k) for k in range(len(gx))]
        elif gx and gy and len(gx) * len(gy) < 4_000_000:
            sm = difflib.SequenceMatcher(None, gx, gy, autojunk=False)
            for b in sm.get_matching_blocks():
                res += [(pi + b.a + k, pj + b.b + k) for k in range(b.size)]
        if i < len(x):
            res += [(i + k, j + k) for k in range(K)]
        pi, pj = i + (K if i < len(x) else 0), j + (K if i < len(x) else 0)
    return sorted(set(res))


def ranges(pairs, ax, ay):
    """Compress matched address pairs into [lo, hi, delta] runs (reference addresses)."""
    out = []
    for i, j in pairs:
        a, b = ax[i], ay[j]
        d = b - a
        if out and out[-1][1] == a and out[-1][2] == d:
            out[-1][1] = a + 1
        else:
            out.append([a, a + 1, d])
    return out


def cal_pointer_pairs(ref, img, mapf):
    """(reference address, image address) of calibration operands of matching instructions."""
    pairs = {}
    a = 0x1200
    for lo, hi in ((0x1200, 0xB4CD), (0xE229, 0xFFD6)):
        a = lo
        while a < hi:
            i = ref.decode(a)
            if i is None:
                a += 1; continue
            b = mapf(a)
            j = img.decode(b) if b is not None else None
            if j is not None and j.mn == i.mn and len(j.ops) == len(i.ops) and j.mn in LOADS:
                for o1, o2 in zip(i.ops, j.ops):
                    if o1[0] in ("ext", "imm") and 0xB800 <= o1[1] < 0xE229 and o2[0] == o1[0]:
                        pairs.setdefault(o1[1], set()).add(o2[1])
            a += i.size
    return {k: next(iter(v)) for k, v in pairs.items() if len(v) == 1}


LOADS = {"ldaa", "ldab", "ldd", "ldx", "ldy", "cmpa", "cmpb", "cpd", "cpx", "cpy", "adda", "addb",
         "addd", "suba", "subb", "subd", "anda", "andb", "oraa", "orab", "eora", "eorb", "bita",
         "bitb", "adca", "adcb", "sbca", "sbcb", "tst", "staa", "stab", "std", "jsr", "jmp"}


def clean_cal(runs, pairs):
    """Keep calibration runs whose offset is confirmed by code pointers; extend them over gaps."""
    pts = sorted((a, b - a) for a, b in pairs.items())
    # offsets that occur for a single address only are 16-bit constants, not pointers
    good = [(a, d) for k, (a, d) in enumerate(pts)
            if (k > 0 and pts[k - 1][1] == d) or (k + 1 < len(pts) and pts[k + 1][1] == d)]
    out = []
    for lo, hi, d in runs:
        support = [a for a, dd in good if lo <= a < hi and dd == d]
        if support or hi - lo >= 256:
            out.append([lo, hi, d])
    merged = []
    for lo, hi, d in sorted(out):
        if merged and merged[-1][2] == d:
            merged[-1][1] = hi
        else:
            merged.append([lo, hi, d])
    for k in range(len(merged) - 1):                      # close gaps between different offsets
        if merged[k][1] < merged[k + 1][0]:
            merged[k][1] = merged[k + 1][0]
    bad = [(a, d) for a, d in good if not any(lo <= a < hi and dd == d for lo, hi, dd in merged)]
    print("calibration pointers: %d confirm the map, %d disagree" % (len(good) - len(bad), len(bad)))
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--img", required=True)
    ap.add_argument("--cal-ref", help="image whose calibration is aligned (default: --ref)")
    ap.add_argument("--cal-img", help="image whose calibration is aligned (default: --img)")
    ap.add_argument("--code-ref", default="1200:B4CD,E229:FFD6")
    ap.add_argument("--code-img", default="1200:B55A,E229:FFD6")
    args = ap.parse_args()
    ref, img = Rom(args.ref), Rom(args.img)
    rr = [tuple(int(v, 16) for v in s.split(":")) for s in args.code_ref.split(",")]
    ri = [tuple(int(v, 16) for v in s.split(":")) for s in args.code_img.split(",")]
    code = []
    for (lo1, hi1), (lo2, hi2) in zip(rr, ri):          # pass 1: ROM pointers masked
        x, ax = normalise(ref, lo1, hi1)
        y, ay = normalise(img, lo2, hi2)
        code += ranges(match(x, y), ax, ay)
    for npass in (2, 3):                                 # passes 2-3: pointers translated, exact bytes
        f = mapper(code)
        code = []
        for (lo1, hi1), (lo2, hi2) in zip(rr, ri):
            x, ax = translated(ref, lo1, hi1, f)
            y = img.data[lo2 - BASE:hi2 - BASE]; ay = list(range(lo2, hi2))
            p = match(x, y)
            r = ranges(p, ax, ay)
            code += r
            print("pass %d code %04X-%04X -> %04X-%04X: %d of %d bytes matched, %d runs"
                  % (npass, lo1, hi1 - 1, lo2, hi2 - 1, len(p), hi1 - lo1, len(r)))
    allr = list(code)
    if True:
        cr, ci = Rom(args.cal_ref or args.ref), Rom(args.cal_img or args.img)
        x = cr.data[0xB800 - BASE:0xE229 - BASE]; y = ci.data[0xB800 - BASE:0xE229 - BASE]
        p = match(x, y)
        r = ranges(p, list(range(0xB800, 0xE229)), list(range(0xB800, 0xE229)))
        r = clean_cal(r, cal_pointer_pairs(ref, img, mapper(code)))
        allr += r
        print("calibration: %d of %d bytes matched, %d runs after cleaning" % (len(p), len(x), len(r)))
    allr.sort()
    d = os.path.join(ROOT, "annotations", "bases", args.base)
    os.makedirs(d, exist_ok=True)
    json.dump({"reference": "B4CC", "base": args.base,
               "runs": [["%04X" % lo, "%04X" % hi, d] for lo, hi, d in allr]},
              open(os.path.join(d, "map.json"), "w"), indent=0)
    print("wrote", os.path.join(d, "map.json"), len(allr), "runs")


if __name__ == "__main__":
    main()
