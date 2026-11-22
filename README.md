# neon-fcc-firmware

Reconstructed, buildable and annotated source code of the engine controller firmware used in the
**1995 Dodge / Plymouth Neon** (Chrysler "FCC", Four Cylinder Controller, single 60-pin connector,
Motorola 68HC11).

[Русская версия](README.ru.md)

The source assembles back into the original ROM images **byte for byte**. That is the foundation for
everything else: you can read it, rename things, comment it, and later modify it, always knowing
exactly which change produces which byte.

| Variant | Description | SHA-256 of the rebuilt image |
|---|---|---|
| `5269718` | Chrysler factory calibration, 2.0 DOHC manual "Racing" (rev B of 4874164) | `db0b8819...5669bab7` |
| `5007033` | Mopar Performance calibration, 2.0 SOHC manual | `12182bc2...18c3bdc6` |

Both images share the same program code (code base "B4CC"); only the calibration differs. Most
factory 1995 calibrations (4874154, 4874155, 4874159 ...) use an earlier code base ("B559") that is
not covered yet.

## What is in here

```
src/                      the firmware source (vasm, Motorola syntax, 68HC11)
  fcc_<variant>.asm       top-level file per variant
  inc/                    68HC11 registers, RAM variables, inner labels
  code/NN_*.asm           program code split by subsystem (37 modules, in address order)
  cal/<variant>.asm       calibration data, formatted table by table
annotations/              the knowledge base the source is generated from
  routines.md             hand-written routine descriptions (edit this!)
  comments.txt            per-instruction comments
  *.json                  labels, RAM names, table definitions, code entry points, module layout
tools/
  build.py                assemble + verify against the original hashes
  gen_source.py           regenerate src/ from ROM dumps + annotations
  gen_cal_docs.py         regenerate the calibration reference
  fccdis.py               code/data separation (recursive descent disassembler core)
  import_lloyd.py         one-time import of Robert Lloyd's annotations
docs/en, docs/ru          documentation (English / Russian)
```

## Quick start

1. Build the vasm assembler (6800 family, Motorola syntax) - see [docs/en/building.md](docs/en/building.md).
2. `python tools/build.py` - assembles both variants into `build/` and checks the SHA-256.

Expected output:

```
5269718: OK - byte-identical to the original image (sha256 db0b8819...)
5007033: OK - byte-identical to the original image (sha256 12182bc2...)
```

No ROM dump is needed to build. Dumps are only needed to regenerate the source with
`tools/gen_source.py` (see [roms/README.md](roms/README.md)).

## Documentation

- [Building and verifying](docs/en/building.md)
- [Hardware and firmware architecture](docs/en/architecture.md): memory map, timers, interrupts,
  start-up, main loop, table formats, checksum
- [Engine control algorithms](docs/en/engine_control.md): fuel, spark, knock, idle, closed loop,
  limiters, emissions
- [Calibration table reference](docs/en/calibration_tables.md) (generated)
- [Differences between the two calibrations](docs/en/calibration_variants.md) (generated)

## Status

- Byte-identical rebuild of both variants, checked in CI.
- 19,757 instructions identified; 181 of them in blocks that static analysis cannot reach (indirect
  jumps or dead code), marked as such.
- 613 routine headers with call graph; 90 routines described by hand, 46 of them checked (fully or partly) against the
  code instruction by instruction (`[reviewed]`), the rest based on the original names (`[from name]`).
- 463 calibration tables named and formatted; 3D maps and curves are laid out row by row.
- Many RAM variable names are still tentative or generic (`L0123`).

Help is welcome: improving the knowledge base means editing `annotations/routines.md` or
`annotations/comments.txt`, regenerating and checking that the build is still byte-identical.

## Roadmap

1. Finish annotating the code (fuel and spark scheduling, crank/cam synchronisation, diagnostics).
2. Map the hardware completely: 60-pin connector, port pins, the external I/O device at $0400.
3. Port the annotations to the factory code base B559.
4. "Enhanced Edition": a modified firmware for the same hardware (higher resolution tables, wideband
   input, faster logging, better diagnostics). Built on top of the verified source.

## Credits and legal

- Original firmware and calibrations: (c) 1994 Chrysler Corporation; Mopar Performance calibration
  by Chrysler / Mopar.
- The disassembly this project starts from, including most names, was made by **Robert Lloyd**
  (shelgame, BoostButton LLC, author of Turbonator and co-author of MP Tune), and published for free
  in the Turbonator release folder. Table definitions come from the MP Tune definition files by
  Robert Lloyd and Morris Terveen.
- The restructuring, build system, tools, additional analysis and documentation are this project's.

This repository is a non-commercial, educational and interoperability project for owners of these
cars. It does not claim any rights over Chrysler's or Robert Lloyd's work. The project's own tools
and documentation are released under the MIT license (see [LICENSE](LICENSE)); that license does not
apply to the firmware content. See [NOTICE](NOTICE). Rights holders who object can open an issue and
the material will be removed.

Modifying engine controller firmware can damage an engine and may affect emissions compliance. Use
at your own risk.
