# Input / output map

Reconstructed from the code: register accesses, A/D conversion sequences and the actuator-test
routines (`ATM_*`), which each drive one output and so reveal its bit. Confidence:
**[code]** = follows directly from the code, **[inferred]** = likely, still to be confirmed on the board.
The connector pin numbers are not mapped yet.

## 68HC11 timer pins (port A)

| Pin | Function | Use | |
|---|---|---|---|
| PA0 | IC3 | Crank sensor, falling edges (slot width) | [inferred] |
| PA1 | IC2 | Vehicle speed sensor | [code] |
| PA2 | IC1 | Crank sensor, rising edges: main engine event | [code] |
| PA3 | OC5 | Ignition coil B driver | [code] |
| PA4 | OC4 | Knock window timer (pin action "clear" is set, use of the pin itself unknown) | [code] |
| PA5 | OC3 | Ignition coil A driver | [code] |
| PA6 | OC2 / output | Used as a plain output in the charge-air temperature routines (switching a sensor pull-up for two measuring ranges) | [inferred] |
| PA7 | PAI | Cam sensor, both edges | [code] |

## A/D converter (port E)

| Channel | Signal | |
|---|---|---|
| AN0 | MAP sensor (read in the crank-synchronous scan, `ADCTL = $10`) | [inferred] |
| AN1 | Battery voltage | [code] |
| AN2 | Upstream O2 sensor | [code] |
| AN3 | Knock signal, single conversion in `Isr_TOC4_KnockSample` (`ADCTL = $03`) | [code] |
| AN4 | **Multiplexed input**, selected by bits 0-1 of I/O register `$0400`: `00` coolant temperature, `01` cruise switches, `10` and `11` ambient air and battery temperature (the code uses both names; which select value is which is not confirmed) | [code] |
| AN5 | Read in the sub-loop code next to the downstream O2 monitor; probably the downstream O2 sensor | [inferred] |
| AN6 | Throttle position (TPS) | [code] |
| AN7 | Not read | [code] |

Two scan modes are used: `ADCTL = $10` converts AN0-AN3, `ADCTL = $14` converts AN4-AN7.

## Serial interfaces

| Interface | Use | |
|---|---|---|
| SCI (PD0/PD1) | Diagnostic link (DRB II/III protocol, MP Scan logging, code download); the baud rate is switched at run time | [code] |
| SPI (PD2-PD5) | Talks to external chips: the output driver (see below), the CCD bus interface (`CCDBusComs`) and the AIS stepper path (`AisDriveRoutine`). PD5 is toggled as a chip select by the AIS and CCD routines | [code] / [inferred] |

## External I/O device at $0400

| Register | Bits | Use | |
|---|---|---|---|
| `$0400` (write) | 0-1 | Analog multiplexer select for AN4 | [code] |
| `$0400` / `$0401` (read) | | Switch inputs and status (the original disassembly calls them "SwitchPortAccessReg"); bit 4 of `$0400` is an injector-driver status bit checked before each injection command | [code] |
| `$0403` | 0 | Set at reset | [code] |
| | 1 | Tachometer output (toggled by the tach actuator test) | [code] |
| | 2 | Chip select of the SPI output driver | [code] |
| | 3 | Knock window gate: set in crank phase 3, cleared when the knock sample is taken | [code] |
| `$0409` | 3 | Toggled by the fault code-53 path | [code] |
| | 4 | Heartbeat, toggled every main-loop pass (external watchdog) | [code] |
| `$0410` | | Injector command: `$04` hands the latest pulse widths to the injector timers | [code] |
| `$0424`, `$0428`, `$042C`, `$0430` | 16 bit | Injector pulse width, cylinders 1, 2, 3, 4 (microseconds) | [code] |
| `$0402`, `$0404`-`$040F` | | Configured by `DealWithConfigurationAndPulseAccumulator_MM` and at reset; function not yet decoded | |

## SPI output driver (relays and solenoids)

The RAM byte `PIA2_Buffer` ($003A) is the output command. `SendOutputDriverByte` ($5A29) pulls `$0403` bit 2 low, shifts the
byte out over SPI and stores the byte shifted back in (`CCDFlagsX`), which is the driver's fault
status. This behaviour matches an octal serial low-side switch with diagnostics. [code]

| Bit | Output (from the actuator tests) | |
|---|---|---|
| 0 | A/C compressor clutch relay | [code] |
| 1 | Solenoid driven by an unnamed actuator test (EGR solenoid likely) | [inferred] |
| 2 | ASD relay (the ASD test also forces the coil outputs) | [inferred] |
| 3 | Radiator fan relay | [code] |
| 4 | Not seen in the tests | |
| 5 | Canister purge solenoid | [code] |
| 6-7 | Speed control servo vacuum and vent solenoids | [code] |

## Other outputs

| Output | Driven by | |
|---|---|---|
| Ignition coils A / B | OC3 / OC5 | [code] |
| Injectors 1-4 | External I/O device injector timers | [code] |
| Tachometer | `$0403` bit 1 | [code] |
| AIS stepper motor | SPI path, `AisDriveRoutine` | [inferred] |
| Check-engine lamp, PTU (lock-up) indicator | Lamp routines (`TurnCheckEngineLightOn/Off`, `ATM_PTUIndicator`); output register not yet traced | |
| Alternator field | `ControlAlternator`, duty cycle timed in `Isr_TOC1_Periodic`; output not yet traced | |
