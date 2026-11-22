# Input / output map

Reconstructed from the code: register accesses, A/D conversion sequences, the actuator tests
(`ATM_*`, each drives one output) and the routines that drive each output bit. The **Pin** column
is the 60-pin PCM connector ([pinout](pcm_connector.md), from the 1995 Neon wiring diagram, supplied
by the project owner). Confidence: **[code]** = follows directly from the code, **[inferred]** =
likely, still to be confirmed on the board. The internal wiring from a connector pin to the HC11 pin
is not traced, so a link between a connector pin and an HC11 pin is never better than [inferred].

The controller has three groups of I/O: the HC11's own pins, an **SPI output driver** for relays
and solenoids, and an **I/O companion chip** reached over the same SPI port. The companion chip
handles the CCD bus, the idle air stepper, the lamps and the switch inputs; see
[ccd_and_link.md](ccd_and_link.md).

## 68HC11 timer pins (port A)

| HC11 pin | Function | Use | Pin | |
|---|---|---|---|---|
| PA0 | IC3 | Crank sensor, falling edges (slot width) | 25 | [inferred] |
| PA1 | IC2 | Vehicle speed sensor | 5 | [code] |
| PA2 | IC1 | Crank sensor, rising edges: main engine event | 25 | [code] |
| PA3 | OC5 | Ignition coil driver (ATM test `$01`) | 21 or 1 | [code] |
| PA4 | OC4 | Knock window timer; also forced high at the start of an ISO 9141 session | — | [code] |
| PA5 | OC3 | Ignition coil driver (ATM test `$02`) | 1 or 21 | [code] |
| PA6 | OC2 / output | Intake air temperature sensor pull-up range: set selects the cold range (table `TMPTL1`), clear the hot range (`TMPTL2`); switched by `CheckAndFilterChargeTempSensor_SM` | — | [code] |
| PA7 | PAI | Cam sensor, both edges | 26 | [code] |

Which OC pin drives coil #1 (pin 21) and which drives coil #2 (pin 1) is not known yet.

## A/D converter (port E)

Two scan modes are used: `ADCTL = $10` converts AN0-AN3, `ADCTL = $14` converts AN4-AN7. AN4 and AN5
are each fed by a 4-to-1 analog multiplexer; bits 0-1 of I/O register `$0400` select the input of
both at once. Results are stored as 16-bit pairs (ADR1:ADR2 and ADR3:ADR4).

| Channel | Signal | Stored in | Pin | |
|---|---|---|---|---|
| AN0 | MAP sensor (crank-synchronous scan) | `MapVolts` | 29 | [inferred] |
| AN1 | Battery voltage | `BatteryVolts` | 11 (fused B+) | [code] signal, [inferred] pin |
| AN2 | Upstream O2 sensor | `O2SensorVolts` | 8 | [code] |
| AN3 | Knock signal, single conversion in `Isr_TOC4_KnockSample` (`ADCTL = $03`), probably after an interface circuit | | 27 | [code] |
| AN4, select `00` | Coolant temperature; the pull-up range is switched with `$0400` bit 7 | `LastCoolantTempVolts` ($016C) | 28 | [code] |
| AN4, select `01` | Read but never used | `AnalogMux01_AN4` ($016E) | ? | [code] |
| AN4, select `10` | ASD relay output voltage, checked against battery voltage (fault code 42) and used for the injector supply | `AsdOutputVolts` ($0170) | 42 | [inferred] |
| AN4, select `11` | Read but never used | `AnalogMux11_AN4` ($0172) | ? | [code] |
| AN5, select `00` | Intake air temperature (`ChargeTemp` in the original names); the pull-up range is switched with PA6 | `LastChargeTempVolts` ($016D) | 6 | [code] signal, [inferred] pin |
| AN5, select `01` | Downstream O2 sensor | `DownstreamO2Volts` ($016F) | 7 | [code] |
| AN5, select `10` | Temperature input checked by fault code 44 (`AmbientAirTempVolts` in the original names) | ($0171) | 49? | [inferred] |
| AN5, select `11` | Battery temperature (fault code 44) | `BatteryTempVolts` ($0173) | 49 | [inferred] |
| AN6 | Throttle position (TPS) | `LastTpsVolts` ($0174) | 10 | [code] |
| AN7 | Speed control switches (one resistor ladder) | `CruiseControlSwitchStateAnalog` ($0175) | 31 | [code] |

The fuel level sensor (pin 13) is not used anywhere in the code. If it is wired to the controller,
the likely places are the two AN4 inputs that are read but never used.

## Discrete inputs

| Input | Where the code reads it | Pin | |
|---|---|---|---|
| Switch byte from the companion chip (reply decoded as register `$48`) | `SwitchInputs` ($00ED). Bit 6 is used by the idle speed target, the AIS state choice, the rev limiter, speed control and the CCD switch message, so it is the park / neutral switch. Bit 5 is used by speed control and the AIS; its meaning is not known | 50 (bit 6) | [inferred] |
| Second input word from the companion chip (reply decoded as register `$50`) | `LinkInputWordHi/Lo` ($00F0/$00F1); bits 0 and 3 confirm `OutputBits2` bits 0 and 3 during the key-off O2 heater test | ? | [code] |
| `$0409` bit 1 | Alternate speed control switch input, used when CONFIG2 bit 5 is set | ? | [code] |
| `$0409` bit 2 | Debounced input in `CODEe74f_MM` (polarity set by CONFIG2 bit 5) and in the idle speed check | ? | [code] |
| `$0400` bit 6 | Read by the shutdown routine (`GetControlFeedback_DetermineIfShutdownRequired_MM`) | ? | [code] |

The brake (32), A/C request (33), reverse lamp (55) and power steering pressure (56) switches are
not mapped yet. They are most likely among the companion chip bits above.

## Serial interfaces

| Interface | Use | Pin | |
|---|---|---|---|
| SCI (PD0/PD1) | Diagnostic link: DRB protocol (7812.5 / 62500 baud), ISO 9141 (10.4 kbaud), code download. See [diagnostics.md](diagnostics.md) | 9 RX, 30 TX | [code] |
| SPI (PD2-PD5) | Master, CPHA = 1, 1 MHz (`SPCR = $54`). Shared by the SPI output driver (chip select `$0403` bit 2) and the companion chip (handshake on `$0400` bit 3 and `$0402` bit 3, PD5 as frame select) | — | [code] |

## External I/O device at $0400

| Register | Bits | Use | |
|---|---|---|---|
| `$0400` (write) | 0-1 | Select for the AN4 / AN5 analog multiplexers | [code] |
| | 2 | Output driven by ATM test `$0D`, latched by a pulse on `$0402` bit 2 | [code], output unknown |
| | 7 | Coolant sensor pull-up range: set selects the cold range (`TMPTL1`), clear the hot range (`TMPTL2`); switched after four readings beyond $40 / $DC | [code] |
| `$0400` (read) | 3 | Companion chip ready: every link byte waits for this bit to clear | [code] |
| | 4 | Injector driver status, checked before each injection command | [code] |
| | 6 | Read by the shutdown routine | [code] |
| `$0401` (read) | | Status read by the tachometer test and the injector driver check | [code] |
| `$0402` | 2 | Strobe for `$0400` bit 2 | [code] |
| | 3 | Clock pulse for each companion chip byte | [code] |
| `$0403` | 0 | Set at reset and after each link frame | [code] |
| | 1 | Tachometer output, pin 48 | [code] |
| | 2 | Chip select of the SPI output driver | [code] |
| | 3 | Knock window gate: set in crank phase 3, cleared when the knock sample is taken | [code] |
| `$0409` | 3 | Companion chip reset: pulsed low after ten failed link frames | [inferred] |
| | 4 | Heartbeat, toggled every main-loop pass (external watchdog) | [code] |
| | 1, 2 (read) | Inputs, see above | [code] |
| `$040E` (read) | 0, 3 | Status bits read by the ISO 9141 routines | [code] |
| `$0410` | | Injector command: `$04` hands the latest pulse widths to the injector timers | [code] |
| `$0424`, `$0428`, `$042C`, `$0430` | 16 bit | Injector pulse width, cylinders 1, 2, 3, 4 (microseconds); pins 4, 23, 3, 24 | [code] |
| `$0404`-`$0408`, `$040A`-`$040D`, `$040F` | | Set once by `InitPeripheralRegisters` ($0407 = $1B, $040D = $33, …); meaning not known without the device's documentation | |

## SPI output driver: `OutputDriverBits` ($003A, `PIA2_Buffer` in the original disassembly)

`SendOutputDriverByte` ($5A29) pulls `$0403` bit 2 low, shifts this byte out over SPI and stores
the byte shifted back in (`OutputDriverStatus`), which is the driver's fault status. This behaviour
matches an octal serial low-side switch with diagnostics. [code]

| Bit | Output | Evidence | Pin | |
|---|---|---|---|---|
| 0 | A/C compressor clutch relay | ATM test `$09`, air conditioning routines | 59 | [code] |
| 1 | EGR solenoid | `ExhGasRecirc_MM`, ATM test `$10` | 39 | [code] |
| 2 | ASD relay | Switched together with bit 4 by `ControlAsdRelay_MM`; ATM test `$0A` | 18 | [inferred] |
| 3 | Radiator fan relay | ATM test `$08` | 19 | [code] |
| 4 | Fuel pump relay | Switched together with bit 2 by `ControlAsdRelay_MM` | 38 | [inferred] |
| 5 | Canister purge solenoid; reported as secondary air status by OBD-II PID `$12` on cars with that option | Duty-cycle routine at `$B290`, ATM test `$15`, DRB override target 3 | 16 | [inferred] |
| 6, 7 | Speed control vacuum and vent solenoids (order not confirmed) | Speed control routine, ATM tests `$0C`, `$1A`, `$1B` | 40, 60 | [code] |

## Companion chip outputs: `OutputBits2` ($00EE)

`OutputBits2` (`StartupSwitchMirror2` in the original disassembly) is sent to the companion chip
with register header `$50` by `LinkRegisterUpdate` (see [ccd_and_link.md](ccd_and_link.md#register-frames)). Bit 6 is reported as "lamp on" on CCD when it is clear, so
the outputs may be active low.

| Bit | Output | Pin | |
|---|---|---|---|
| 0 | Power hold after key-off for the O2 heater test (confirmed by `LinkInputWordHi` bit 0) | — | [inferred] |
| 3 | Load switch on the O2 sensor lines for the heater test (confirmed by `LinkInputWordHi` bit 3) | — | [inferred] |
| 4 | Charge indicator lamp (driven by charging-system faults through `$0070` bit 7) | 37 | [inferred] |
| 5 | TCC / PTU solenoid (`PTU_SetPTUBits`, ATM tests `$0F`, `$17`) | 17 | [code] |
| 6 | Check-engine lamp (toggled to blink flash codes) | 36 | [inferred] |
| 7 | Output driven by `$9C6A` (`ControlPurgeSolenoid_MM` in the original disassembly) and DRB override target 1 | ? | |

## Other outputs and supplies

| Output | Driven by | Pin | |
|---|---|---|---|
| Idle air control stepper, 4 drivers | Companion chip, phase commands from `AisDriveRoutine` | 35, 14, 15, 34 (IAC #1-#4) | [inferred] |
| Generator field | `ControlAlternator`, duty cycle timed in `Isr_TOC1_Periodic`; output register not traced | 41 | |
| Sensor supplies | 5 V (43), 8 V (44), sensor ground (51) | | |
| Power and ground | Fused B+ (11), ignition (54), speed control supply (47), grounds (2, 22, 52) | | |
