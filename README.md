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
  gen_fault_docs.py       regenerate the fault code reference
  gen_ram_docs.py         regenerate the RAM map
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
- [Input / output map](docs/en/io_map.md): port pins, A/D channels, the I/O device at $0400, the SPI
  output driver
- [PCM connector pinout](docs/en/pcm_connector.md)
- [Diagnostics and communication](docs/en/diagnostics.md): DRB commands, actuator tests, ISO 9141, lamps
- [Fault codes](docs/en/fault_codes.md) (generated): all 160 fault descriptors with flash and OBD-II codes
- [RAM map](docs/en/ram_map.md) (generated): every RAM and I/O address with its readers and writers
- [Calibration table reference](docs/en/calibration_tables.md) (generated)
- [Differences between the two calibrations](docs/en/calibration_variants.md) (generated)

## Status

- Byte-identical rebuild of both variants, checked in CI.
- 20,075 instructions identified. All code reached through pointer tables is now traced; only 7
  instructions in four unreferenced fragments remain, marked as dead code.
- 614 routine headers with call graph; 123 routines described by hand, 87 of them checked (fully or partly) against the
  code instruction by instruction (`[reviewed]`), the rest based on the original names (`[from name]`).
- 463 calibration tables named and formatted; 3D maps and curves are laid out row by row.
- RAM map with readers and writers of every address; 239 of 612 addresses still have a placeholder
  name (`L0123`).

Help is welcome: improving the knowledge base means editing `annotations/routines.md` or
`annotations/comments.txt`, regenerating and checking that the build is still byte-identical.

## Roadmap

1. Finish annotating the code. Done: engine position and scheduling, fuel, spark, knock, idle,
   fault codes, DRB / ISO protocols. Open: CCD messages, ISO 9141 services, the remaining RAM names.
2. Map the hardware completely. Done: connector pinout, timer pins, A/D channels, output drivers.
   Open: switch input bits, fuel level input, the receiver of the second output byte, the registers
   $0402-$040F.
3. Port the annotations to the factory code base B559.
4. "Enhanced Edition": a modified firmware for the same hardware (higher resolution tables, wideband
   input, faster logging, better diagnostics). Built on top of the verified source. The OBD-II
   monitors already in the code but never scheduled are the natural starting point for OBD-II.

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
