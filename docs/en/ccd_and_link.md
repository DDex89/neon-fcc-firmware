# Companion chip link and CCD bus

Besides the SPI output driver, the HC11 talks over SPI to an **I/O companion chip**. That chip
handles the CCD bus to the instrument cluster and body modules, drives the idle air stepper, the
lamps and the TCC solenoid, and returns the switch inputs. The chip itself is not identified; all of
this is reconstructed from the HC11 side. Confidence: **[code]** = follows directly from the code,
**[inferred]** = likely.

## Timing

The link runs at the end of the periodic TOC1 interrupt (about every 1.9 ms):
`Isr_TOC1_Periodic` → alternator control → DRB fast-logging byte → `AisDriveRoutine`, which makes at
most one AIS step and exchanges **one frame**, then returns from the interrupt. A long frame is
skipped in favour of the 1-byte frame if a crank event is pending (TFLG1 IC1F), so the link never
delays crank processing. [code]

## Byte handshake

Each byte waits until `$0400` bit 3 is clear (chip ready, up to 10 tries), is written to SPDR,
clocked with a pulse on `$0402` bit 3, and the byte shifted back is read from SPDR. PD5 is low for
the whole frame. [code]

## Header byte

| Bits | Meaning |
|---|---|
| 7-6 | Frame type: `10` command frame, `11` CCD frame (`$D0`/`$D8`), `01` register frame (`$48`/`$50`/`$58`) |
| 5-3 | Command or register field |
| 2-0 | Complement of bits 5-3 (check bits); in long frames they carry the low bits of the current stepper command |

The reply header is checked the same way: its bits 2-0 must be the complement of bits 5-3. Bits 7-6
of the reply go to `LinkStatusFlags` bits 2-3. [code]

## Frame types

| Frame | Sent when | Bytes out | Bytes back |
|---|---|---|---|
| Command (1 byte) | Default, every tick | `LinkCommandByte`: stepper phase `$B1`, `$AA`, `$A3`, `$9C` (field 6, 5, 4, 3), hold `$B8` (field 7), `$95` once after start | Status in bits 2-0: 6 sets `BitFlags69` bit 1 (battery volts OK), 5 or 7 set `BitFlags69` bit 4 |
| CCD (5 bytes) | `LinkRequestFlags` bit 7 (`PrepareCCDDataForXmit_MM_1`) | `$D0` (send) or `$D8` (nothing), message ID, 2 data bytes, check | The last received CCD message: ID, 2 data bytes, check |
| Register (4 bytes) | `LinkRequestFlags` bit 6 (`LinkRegisterUpdate`) | `$48`, `$50` or `$58`, 16-bit value, check | 16-bit value of the register |
| Frame C (4 bytes) | `LinkRequestFlags` bit 5 (`CODE1265`) | `LinkFrameCHeader`, 2 data bytes, check | 2 bytes; purpose not decoded |

The check byte is the complement of the sum of the bytes before it; the reply is checked the same
way. After ten failed exchanges in a row `LinkError` pulses `$0409` bit 3, which most likely resets
the chip. [code]

### Register frames

`LinkRegisterUpdate` cycles the header through `$50`, `$58` and `$48`. The data sent with each header
and the use of each reply:

| Header | Data sent | Reply used as |
|---|---|---|
| `$50` | `OutputBits2` and `$00EF`: lamps, TCC solenoid, O2 heater relay ([io_map.md](io_map.md#companion-chip-outputs-outputbits2-00ee)) | `LinkInputWordHi/Lo` ($00F0/$00F1) |
| `$58` | `$0176`/`$0177` | not used |
| `$48` | `$00EC`, `$00` | `SwitchInputs` ($00ED) |

A reply is decoded against `LinkRegLastAddress`, the header of the frame before, so the chip answers
one frame late (a pipelined SPI read). Which header means "write" and which register is read is
therefore not certain; the table shows how the code pairs them. [code]

## CCD messages sent

`PrepareCCDDataForXmit_MM_1` walks a 128-slot schedule (`CCDDataStream_1`, index `CcdTxSlot`). Each
slot routine returns the message ID and two data bytes; the first message after start is `$E0` with
zero data. [code]

| ID | Slots of 128 | Routine | Data byte 1 | Data byte 2 |
|---|---|---|---|---|
| `$E4` | 32 | `CCD_EngineRPM` | Engine RPM (`EngineRpm_HB`) | MAP (`MapValue`) |
| `$24` | 8 | `CCD_VehicleSpeed` | Vehicle speed | Vehicle speed, second scaling |
| `$42` | 8 | `CCD_ThrottlePos` | Throttle (`TPSOverMINTHR`) | Cruise set speed / 2 |
| `$A4` | 8 | `CCD_SwitchState` | Status bits: cruise, P/N (`SwitchInputs` bit 6), A/C clutch, check-engine lamp | Speed control state bits |
| `$D4` | 2 | `CCD_BatVolts` | Battery voltage | Target charging voltage |
| `$8C` | 2 | `CCD_CoolantTemp` | Coolant temperature | Ambient / battery temperature (`AmbientAirTemp`) |
| `$54` | 1 | `CCD_Baro` | Barometric pressure | Intake air temperature |
| `$EC` | 1 | `CCD_ToggleFlags` | Warning flags from the fault state | Calibration bits (`CCDCF3`) |
| `$CC` | 1 | `CCD_EEPromData` | EEPROM word 1 × 4 | Target idle speed × 4 |
| `$AC` | 1 | `CCD_ConfigConst1` | Calibration word `CCDCFG` (vehicle configuration) | |
| — | 64 | `CCD_Blank` | Empty slot (`$D8`) | |

## CCD messages received

`PrepareCCDDataForXmit_MM_2` calls a handler by the **low nibble** of the received ID
(`CCDDataStream_2[CcdRxId & $0F]`). [code]

| ID low nibble | Handler | Action |
|---|---|---|
| 1 | `CcdRx_1` | Theft alarm input (sets `CCDFlags5` bit 6, `CCDFlags4` bit 4) |
| 4 | `CcdRx_4` | Stores data byte 1 in `CcdRxValueA`, restarts the CCD time-out |
| 8 | `CcdRx_8` | Stores data byte 1 in `CcdRxValueB` |
| other | — | Ignored |

If no message with low nibble 4 arrives, `CcdRxTimeout` counts up and at `$75` fault code 66 ("no
CCD messages") is reported. `CCD_HandleAlarm` keeps the theft alarm state in EEPROM4 bits 0-1 and
is skipped when CONFIG bit 2 (alarm disable) is set. Which module sends IDs ending in 4 and 8, and what
`CcdRxValueA/B` mean, is not decoded yet. [code] / [inferred]
