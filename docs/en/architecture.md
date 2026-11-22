# Hardware and firmware architecture

Statements marked *(inferred)* come from reading the code and are not yet confirmed on real
hardware.

## The controller

The 1995 Neon controller ("FCC", Four Cylinder Controller) has a single 60-pin connector. From 1996
the Neon uses the SBEC III with two 40-pin connectors, which is different hardware and firmware.

The CPU is a Motorola **68HC11** running in expanded mode. The register layout used by the code
(OPTION at $1039, INIT at $103D, BPROT at $1035, EEPROM window at $B600) matches the 68HC11 A/E
family. The program lives in an external (E)EPROM that fills $1200-$FFFF: 60,928 bytes, exactly the
size of the `.bin` dumps.

## Memory map

| Range | Contents |
|---|---|
| `$0000-$00FF` | Direct-page RAM: the most used variables (8-bit addressing) |
| `$0100-$03FF` | RAM: more variables, fault code data, buffers |
| `$0400-$0437` | External I/O device registers (the original disassembly calls it "PIA"). Initialised from the table after ResetInterrupt. It also drives the **injectors**: per-cylinder pulse widths at `$0424/$0428/$042C/$0430`, command register `$0410`, status in `$0400/$0401`. Register `$0409` bit 4 is toggled every main-loop pass (heartbeat). *(inferred)* |
| `$0438-$04FF` | RAM and the stack (the stack pointer starts at $04FF) *(inferred)* |
| `$1000-$103F` | 68HC11 internal registers (`src/inc/hc11_regs.inc`) |
| `$1200-$B4CC` | Program code, part 1 |
| `$B4CD-$B5FF` | Unused ($FF) |
| `$B600-$B7FF` | Window of the HC11 internal EEPROM. The CPU sees the EEPROM here, not the EPROM image, and the ROM checksum skips this range. |
| `$B800-$E228` | Calibration: header (part number, configuration flags) and about 460 tables and constants |
| `$E229-$FFD5` | Program code, part 2; the copyright string is at $FFA4 |
| `$FFD6-$FFFF` | Interrupt vectors |

### Calibration header

| Address | Meaning |
|---|---|
| `$B800-$B801` | Calibration ID bytes |
| `$B802-$B805` | Part number in BCD, for example `05 00 70 33` = 05007033. **$B805 is also the ROM checksum target.** |
| `$B806` | Revision |
| `$B807-$B80B` | RFI number and revision |
| `$B811` | Configuration flags: bit 7 A/C, bit 6 EGR, bit 5 automatic transmission, bit 2 alarm disable, bit 1 early TPS transient fuel |
| `$B812` | Configuration flags 2 (bit 4 transient fuel, bit 6 O2) |
| `$B813-$B816` | CCD bus configuration |
| `$B817-$B819` | Masks of the faults that light the check-engine lamp |

## Timers and interrupts

The timer runs at E-clock / 4. With the usual 8 MHz crystal (2 MHz E-clock) one TCNT tick is
**2 us** and the counter wraps every 131 ms.

| Vector | Handler | Use |
|---|---|---|
| RESET | `ResetInterrupt` | Start-up |
| PAI (PA7 edge) | `Isr_PAI_CamPhase` | Cam sensor edges (both polarities): cylinder identification from the crank signal level *(inferred)* |
| PAOV | `Isr_PAOV` | Pulse accumulator overflow count |
| TIC1 (PA2) | `Isr_TIC1_CrankEvent` | Crank sensor edges: the main engine event; dispatches the per-edge handlers that schedule fuel and spark *(inferred; Lloyd called it the cam sensor)* |
| TIC2 | `Interrupt_SpeedometerSignal` | Vehicle speed sensor |
| TIC3 (PA0) | `Isr_TIC3` | Other edge of the crank signal (slot width); starts the long period measurement together with TOF *(inferred)* |
| TOF | `Isr_TOF` | Timer overflow count for long periods |
| TOC1 | `Isr_TOC1_Periodic` | Periodic interrupt every $03B9 ticks (about 1.9 ms) |
| TOC3 (PA5) | `Interrupt_DwellTimerA` | Ignition coil A driver: dwell start and spark |
| TOC4 (PA4) | `Isr_TOC4_KnockSample` | End of the knock window: samples the knock sensor through the A/D |
| TOC5 (PA3) | `Interrupt_DwellTimerB` | Ignition coil B driver: dwell start and spark |
| TOC2, IRQ, XIRQ, SWI, illegal opcode, COP, clock monitor, SCI, SPI, RTI | `Trap_*` | Not used: these handlers record the cause and restart the controller |

Reset sets TCTL2 = $1A (IC1 on rising edges, IC2 and IC3 on falling edges) and TCTL1 = $2A (OC3, OC4
and OC5 clear their pins on compare; OC2 is disconnected from its pin).

The register names in the original disassembly (inherited from the turbo SMEC) call OC3 and OC4
injector drivers and OC2 "wastegate". On the FCC the coils use OC3/OC5 directly, while the four
injectors are timed by the external I/O device (see [engine_control.md](engine_control.md#engine-position-and-event-scheduling)).

## Start-up and recovery

`ResetInterrupt` programs the HC11 system registers within the first 64 cycles, as the HC11
requires for the protected registers. It then checks whether RAM survived:

- `CountRamValuesFrom05to38` sums the RAM that holds adaptive memory, fault codes and learned values
  ($0005-$0036 and $0100-$014D);
- if the sum matches the stored copy and the signature `$AAA5` is present, the RAM is kept (warm start);
- otherwise RAM is cleared and default values are loaded (cold start).

Every unused interrupt vector points to a small `Trap_*` stub. The stub puts a cause bit into
`BYTE00`, then runs the same initialisation as reset **without** clearing RAM, so after a crash,
watchdog timeout or illegal opcode the engine keeps its learned values and fault codes.

| Cause bit | Trap |
|---|---|
| $01 | SCI / SPI / real-time interrupt |
| $02 | XIRQ |
| $04 | COP watchdog |
| $08 | Clock monitor |
| $10 | Illegal opcode |
| $20 | SWI |
| $40 | Output compare 2 |
| $80 | IRQ pin |

## Main loop and scheduler

`MainProgramLoop` runs once every **$1500 ticks = 10.75 ms**. That is the "x 11 ms" unit that
appears in many calibration constants.

1. `MainSubLoop` runs on every pass: COP watchdog kick, heartbeat on $0409, period measurements,
   A/D of battery voltage, TPS and cruise switches, throttle and baro logic, cranking fuel, and
   further always-run tasks.
2. Then at most **one** of the eight sub-loops `SubLoopA`..`SubLoopH` runs. Their request bits are in
   RAM $0150; the lowest pending bit is served and cleared. Slow tasks (temperature sensors,
   diagnostics ...) are spread this way.
3. The loop measures how long the pass took (RAM $0455, worst case in $0454) and waits until TCNT
   reaches the next 10.75 ms slot.

Time-critical work (fuel and spark scheduling relative to crankshaft position, knock sampling, coil
dwell) runs in the interrupt handlers, not in the main loop.

## Table formats

Almost all calibration data uses two formats.

### 2D curves, "point-slope" (`Lookup4ByteTable`, $FA9D)

```
count n
x0, y0, slope0_hi, slope0_lo
x1, y1, slope1_hi, slope1_lo
...
x(n-1), y(n-1)            ; last point has no slope
```

For an input x below x0 the result is y0. Otherwise the routine finds the segment x_i <= x < x_(i+1)
and returns `y_i + (x - x_i) * slope_i / 256`. The slope is stored rather than computed, so editing
a y value without updating the slope gives a wrong curve. MP Tune recalculates slopes automatically.

### 3D maps (`Lookup3DTableRoutine_2`, $B437)

```
rows, cols, sign          ; sign: $00 unsigned, $80/$FF signed
rows x cols bytes, row by row
```

The two inputs are 0-255 coordinates produced by transfer curves: for example `RPMSCL` turns engine
RPM into the column coordinate and `MAPHI` turns MAP into the row coordinate. The coordinate is
spread evenly over the (cols-1) and (rows-1) intervals and the four surrounding cells are
interpolated bilinearly. So the RPM and MAP breakpoints of a map are defined by its transfer curve,
not by the map itself. Changing `RPMSCL` moves every map that uses it.

## ROM checksum

`CaculateChecksum` ($56E7) adds every byte of $1200-$B5FF and $B800-$FFFF (8-bit sum, skipping the
EEPROM window). The result must equal the byte at **$B805**, the last byte of the part number. On a
mismatch fault code 53 (internal controller failure) is stored, but the engine keeps running.

Anyone who changes the calibration should fix the sum with a spare byte. Factory images keep $FF50
at $FF for this. Some images edited with MP Tune that were examined for this project do not pass
this test, so check the sum after using any editor.
