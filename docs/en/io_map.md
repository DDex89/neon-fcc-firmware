# Input / output map

Reconstructed from the code: register accesses, A/D conversion sequences, the actuator tests
(`ATM_*`, each drives one output) and the routines that drive each output bit. The **Pin** column
is the 60-pin PCM connector (pinout from the 1995 Neon wiring diagram, supplied by the project
owner). Confidence: **[code]** = follows directly from the code, **[inferred]** = likely, still to be
confirmed on the board. The internal wiring from a connector pin to the HC11 pin is not traced, so
a link between a connector pin and an HC11 pin is never better than [inferred].

## 68HC11 timer pins (port A)

| HC11 pin | Function | Use | Pin | |
|---|---|---|---|---|
| PA0 | IC3 | Crank sensor, falling edges (slot width) | 25 | [inferred] |
| PA1 | IC2 | Vehicle speed sensor | 5 | [code] |
| PA2 | IC1 | Crank sensor, rising edges: main engine event | 25 | [code] |
| PA3 | OC5 | Ignition coil driver (ATM test `$01`) | 21 or 1 | [code] |
| PA4 | OC4 | Knock window timer; also forced high at the start of an ISO 9141 session | — | [code] |
| PA5 | OC3 | Ignition coil driver (ATM test `$02`) | 1 or 21 | [code] |
| PA6 | OC2 / output | Plain output in the charge-air temperature routines (probably switches a sensor pull-up for two ranges) | — | [inferred] |
| PA7 | PAI | Cam sensor, both edges | 26 | [code] |

Which OC pin drives coil #1 (pin 21) and which drives coil #2 (pin 1) is not known yet.

## A/D converter (port E)

| Channel | Signal | Pin | |
|---|---|---|---|
| AN0 | MAP sensor (read in the crank-synchronous scan, `ADCTL = $10`) | 29 | [inferred] |
| AN1 | Battery voltage | 11 (fused B+) | [code] signal, [inferred] pin |
| AN2 | Upstream O2 sensor | 8 | [code] |
| AN3 | Knock signal, single conversion in `Isr_TOC4_KnockSample` (`ADCTL = $03`), probably after an interface circuit | 27 | [code] |
| AN4 | **Multiplexed input**, selected by bits 0-1 of I/O register `$0400`: `00` coolant temperature (28), `01` speed control switches (31), `10` and `11` intake air temperature (6) and battery temperature (49); which select value is which is not confirmed | see text | [code] |
| AN5 | Read next to the downstream O2 monitor; probably the downstream O2 sensor | 7 | [inferred] |
| AN6 | Throttle position (TPS) | 10 | [code] |
| AN7 | Not read | — | [code] |

Two scan modes are used: `ADCTL = $10` converts AN0-AN3, `ADCTL = $14` converts AN4-AN7. The fuel
level sensor (pin 13) does not appear on any channel read so far; its path is still to be found.

## Serial interfaces

| Interface | Use | Pin | |
|---|---|---|---|
| SCI (PD0/PD1) | Diagnostic link: DRB protocol (7812.5 / 62500 baud), ISO 9141 (10.4 kbaud), code download. See [diagnostics.md](diagnostics.md) | 9 RX, 30 TX | [code] |
| SPI (PD2-PD5) | Talks to external chips: the output driver (see below), the CCD bus interface (`CCDBusComs`) and the AIS stepper path (`AisDriveRoutine`). PD5 is toggled as a chip select by the AIS and CCD routines | — | [code] / [inferred] |

## External I/O device at $0400

| Register | Bits | Use | |
|---|---|---|---|
| `$0400` (write) | 0-1 | Analog multiplexer select for AN4 | [code] |
| | 2 | Output driven by ATM test `$0D`, latched by a pulse on `$0402` bit 2 | [code], output unknown |
| `$0400` / `$0401` (read) | | Switch inputs and status (`SwitchPortAccessReg` in the original disassembly). Bit 4 of `$0400` is an injector-driver status bit checked before each injection command. The switch inputs on the connector are brake (32), A/C request (33), park/neutral (50), reverse lamp (55), power steering pressure (56) and the ASD relay output sense (42); their bits are not mapped yet | [code] / [inferred] |
| `$0403` | 0 | Set at reset | [code] |
| | 1 | Tachometer output, pin 48 | [code] |
| | 2 | Chip select of the SPI output driver | [code] |
| | 3 | Knock window gate: set in crank phase 3, cleared when the knock sample is taken | [code] |
| `$0409` | 3 | Toggled by the fault code-53 path | [code] |
| | 4 | Heartbeat, toggled every main-loop pass (external watchdog) | [code] |
| `$0410` | | Injector command: `$04` hands the latest pulse widths to the injector timers | [code] |
| `$0424`, `$0428`, `$042C`, `$0430` | 16 bit | Injector pulse width, cylinders 1, 2, 3, 4 (microseconds); pins 4, 23, 3, 24 | [code] |
| `$0402`, `$0404`-`$040F` | | Configured by `DealWithConfigurationAndPulseAccumulator_MM` and at reset; function not yet decoded | |

## SPI output driver: `PIA2_Buffer` ($003A)

`SendOutputDriverByte` ($5A29) pulls `$0403` bit 2 low, shifts this byte out over SPI and stores
the byte shifted back in (`CCDFlagsX`), which is the driver's fault status. This behaviour matches
an octal serial low-side switch with diagnostics. [code]

| Bit | Output | Evidence | Pin | |
|---|---|---|---|---|
| 0 | A/C compressor clutch relay | ATM test `$09`, air conditioning routines | 59 | [code] |
| 1 | EGR solenoid | `ExhGasRecirc_MM`, ATM test `$10` | 39 | [code] |
| 2 | ASD relay | Switched together with bit 4 by `ControlAsdRelay_MM`; ATM test `$0A` | 18 | [inferred] |
| 3 | Radiator fan relay | ATM test `$08` | 19 | [code] |
| 4 | Fuel pump relay | Switched together with bit 2 by `ControlAsdRelay_MM` | 38 | [inferred] |
| 5 | Canister purge solenoid | Duty-cycle routine at `$B290`, ATM test `$15`, DRB override target 3 | 16 | [inferred] |
| 6, 7 | Speed control vacuum and vent solenoids (order not confirmed) | Speed control routine, ATM tests `$0C`, `$1A`, `$1B` | 40, 60 | [code] |

## Second output byte: `$00EE`

`$00EE` (named `StartupSwitchMirror2` in the original disassembly) holds more outputs. It is sent
out in a frame with the address bytes `$48`/`$50`/`$58` together with `$0176` and `$00EC`; the
receiving chip is not identified yet.

| Bit | Output | Pin | |
|---|---|---|---|
| 4 | Charge indicator lamp (driven by charging-system faults through `$0070` bit 7) | 37 | [inferred] |
| 5 | TCC / PTU solenoid (`PTU_SetPTUBits`, ATM tests `$0F`, `$17`) | 17 | [code] |
| 6 | Check-engine lamp (toggled to blink flash codes) | 36 | [inferred] |
| 7 | Output driven by `$9C6A` (`ControlPurgeSolenoid_MM` in the original disassembly) and DRB override target 1 | ? | |
| 0, 3 | Switched by the ASD / O2 heater checks and the shutdown routine | ? | |

## Other outputs and supplies

| Output | Driven by | Pin | |
|---|---|---|---|
| Idle air control stepper, 4 drivers | SPI path, `AisDriveRoutine` | 35, 14, 15, 34 (IAC #1-#4) | [inferred] |
| Generator field | `ControlAlternator`, duty cycle timed in `Isr_TOC1_Periodic`; output register not traced | 41 | |
| Sensor supplies | 5 V (43), 8 V (44), sensor ground (51) | | |
| Power and ground | Fused B+ (11), ignition (54), speed control supply (47), grounds (2, 22, 52) | | |
