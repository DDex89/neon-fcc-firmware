# Building and verifying

## What you need

- **Python 3.8 or newer.** The build script uses only the standard library.
- **vasm**, built with the 6800-family backend and the Motorola syntax module. The executable is
  called `vasm6800_mot`. vasm's home page is <http://sun.hasenbraten.de/vasm/>. The CI uses the
  GitHub mirror `StarWolf3000/vasm-mirror`, pinned at commit
  `a13e7e728a3dd5a9ba468bf479119e0bc23e70fd`.
- To regenerate the source (optional): `pip install capstone` and the ROM dumps (see `roms/README.md`).

## Building vasm

### Linux / macOS

```sh
git clone https://github.com/StarWolf3000/vasm-mirror.git vasm
cd vasm
make CPU=6800 SYNTAX=mot
# result: ./vasm6800_mot
```

### Windows (Visual Studio)

Open the "x64 Native Tools Command Prompt for VS" (it comes with any Visual Studio edition that has
the C++ workload), then:

```bat
git clone https://github.com/StarWolf3000/vasm-mirror.git vasm
cd vasm
nmake -f Makefile.Win32 CPU=6800 SYNTAX=mot
rem result: vasm6800_mot.exe
```

## Building the firmware

Tell the build script where vasm is, in one of three ways:

- set the `VASM` environment variable to the full path of the executable;
- copy the executable into `tools/bin/`;
- put it on your `PATH`.

Then:

```sh
python tools/build.py            # all variants
python tools/build.py 5007033    # one variant
```

The images are written to `build/<variant>.bin`, with listings in `build/<variant>.lst`. The script
compares the SHA-256 of each image with the hash recorded in `annotations/variants.json` and fails on
any difference.

When you start changing the code, the hash check will fail by design. Use
`python tools/build.py --no-verify <variant>` for modified builds, and keep the unmodified variants
building byte-identically.

## Working in Visual Studio / VS Code

Use "Open Folder" on the repository. The sources are plain text, and both the build and the
regeneration are command-line Python scripts, so they can run as external tools or tasks. Any editor
with a "Motorola 68000/6800 assembly" syntax mode highlights the files reasonably well.

## How the source is produced

The files in `src/` are generated, and committed so that anyone can read and build them without
extra tools. They are produced from two inputs:

1. A ROM dump of each variant (not included in the repository).
2. The annotation database in `annotations/`:
   - `rom_labels.json`, `ram_symbols.json` - names of code, data and RAM locations;
   - `tables.json` - calibration table definitions (name, type, axes, description);
   - `code_seeds.json` - extra code entry points that static analysis cannot find by itself;
   - `pointer_words.json` - data words that are pointers and should be printed as labels;
   - `modules.json` - how the address space is split into source files;
   - `routines.md` - routine names and descriptions (hand-written);
   - `comments.txt` - per-instruction comments, one per line: `ADDR  text`.

`tools/gen_source.py` disassembles the code by recursive descent: it starts from the interrupt vectors
and the code seeds and follows every branch and call. It then prints every byte as either an
instruction or data, with labels, routine headers and automatic comments: the meaning of a hardware
register or calibration table, and a one-line summary of the called routine.

Recommended workflow:

```sh
# edit annotations/routines.md (for example, describe a routine)
python tools/gen_source.py --roms roms
python tools/gen_cal_docs.py --roms roms
python tools/gen_fault_docs.py --roms roms
python tools/gen_ram_docs.py --roms roms
python tools/build.py           # must still say OK for every variant
```

Never edit `src/` by hand while the annotations are still being developed: the next regeneration
would overwrite the edit. Later, for the modified "Enhanced Edition", the source will be forked and
maintained by hand.

## Other code bases

The factory code base B559 is built the same way from its own generated source in `src_b559/`:

```sh
python tools/build.py --base B559            # all eleven B559 images
python tools/build.py --base B559 4874154    # one image
```

The images go to `build/B559/`. The B559 source is not annotated separately. It is generated from the
same annotation database, with every address moved to B559 through a translation map:

- `annotations/bases/B559/base.json` - code ranges, RAM differences, the variants and their hashes;
- `annotations/bases/B559/map.json` - runs `[lo, hi, delta]` of B4CC addresses and how far they move;
- the same file names as in `annotations/` (`rom_labels.json`, `ram_symbols.json`, `routines.md`,
  `comments.txt`, ...) for names and notes of code that exists only in B559, keyed by B559 addresses.

`tools/port_base.py` builds the map. It aligns the two programs instruction by instruction (ROM
operands masked first, then compared after translation) and derives the calibration runs from the
pairs of calibration addresses that matching instructions use:

```sh
python tools/port_base.py --base B559 --ref roms/5269718.bin --img roms_b559/4874154.bin \
    --cal-img roms_b559/4874164.bin \
    --code-ref 1200:B4CD,E229:FFD6 --code-img 1200:B55A,E229:FFD6
python tools/gen_source.py --roms roms_b559 --base B559
python tools/build.py --base B559
```

The calibration is aligned byte by byte, so `--cal-img` should be a B559 image of the same application
as the reference: 5269718 is rev B of 4874164. (4874164 itself is not among the build variants because
its $FF50 byte was edited, but its calibration is fine for the alignment.)

An annotation added for B4CC therefore appears in B559 at the next regeneration. The generator prints
how many labels, comments and routine notes had no counterpart; for B559 that count is zero. The
differences between the two code bases are described in [code_bases.md](code_bases.md#b559-compared-with-b4cc).

## Why the rebuild is exact

- Every instruction is printed with an explicit addressing mode: `<` forces direct (8-bit) and `>`
  forces extended (16-bit) addressing, so the assembler cannot pick a different encoding.
- Anything that is not decoded as code is emitted as data bytes, so a wrong code/data guess can make
  the source harder to read but never changes the output.
- Labels that point inside an instruction or a data run are defined as absolute equates
  (`src/inc/inner_labels.inc`).
