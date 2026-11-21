#!/usr/bin/env python3
"""Assemble the firmware and verify it against the known original images.

    python tools/build.py              # build every variant listed in annotations/variants.json
    python tools/build.py 5007033      # build one variant

The assembler is vasm (6800 family backend, Motorola syntax), executable
"vasm6800_mot". It is looked up in $VASM, then tools/bin/, then PATH.
Output goes to build/<partnumber>.bin. The build fails if the SHA-256 of the
result does not match the hash recorded for that variant (byte-identical rebuild),
unless --no-verify is given (use that once you start modifying the code).
"""
import argparse, hashlib, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_vasm():
    cands = [os.environ.get("VASM")]
    for name in ("vasm6800_mot", "vasm6800_mot.exe"):
        cands.append(os.path.join(ROOT, "tools", "bin", name))
        cands.append(shutil.which(name))
    for c in cands:
        if c and os.path.isfile(c):
            return c
    sys.exit("vasm6800_mot not found: set VASM, put it in tools/bin/, or add it to PATH (see docs/en/building.md)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variants", nargs="*")
    ap.add_argument("--no-verify", action="store_true", help="do not compare with the original image hash")
    args = ap.parse_args()
    with open(os.path.join(ROOT, "annotations", "variants.json"), encoding="utf-8") as f:
        variants = json.load(f)
    todo = args.variants or list(variants)
    vasm = find_vasm()
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    ok = True
    for pn in todo:
        if pn not in variants:
            sys.exit("unknown variant " + pn)
        src = os.path.join(ROOT, "src", "fcc_%s.asm" % pn)
        out = os.path.join(ROOT, "build", "%s.bin" % pn)
        lst = os.path.join(ROOT, "build", "%s.lst" % pn)
        cmd = [vasm, "-m68hc11", "-Fbin", "-quiet", "-I", os.path.join(ROOT, "src"), "-L", lst, "-o", out, src]
        r = subprocess.run(cmd)
        if r.returncode != 0:
            print("%s: assembler failed" % pn)
            ok = False
            continue
        data = open(out, "rb").read()
        h = hashlib.sha256(data).hexdigest()
        want = variants[pn].get("sha256")
        if len(data) != variants[pn].get("size", len(data)):
            print("%s: size %d, expected %d" % (pn, len(data), variants[pn]["size"]))
            ok = False
        if args.no_verify:
            print("%s: built %s (%d bytes, sha256 %s)" % (pn, out, len(data), h))
        elif h == want:
            print("%s: OK - byte-identical to the original image (sha256 %s)" % (pn, h))
        else:
            print("%s: MISMATCH - sha256 %s, expected %s" % (pn, h, want))
            ok = False
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
