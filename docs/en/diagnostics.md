# Diagnostics and communication

The controller has two diagnostic links on the same SCI port (connector pins 9 receive and 30
transmit). One is the Chrysler DRB protocol, used by the DRB II/III scan tool, MP Scan-type loggers
and code download. The other is ISO 9141 for generic OBD-II scan tools. The fault codes themselves are
listed in [fault_codes.md](fault_codes.md).

Confidence: **[code]** = follows directly from the code, **[inferred]** = likely, not yet confirmed.

## Serial settings

| Mode | `BAUD` | Rate (8 MHz crystal, E = 2 MHz) | |
|---|---|---|---|
| DRB normal | `$22` | 7812.5 baud | [code] |
| DRB high speed (command `$12`) | `$01` | 62500 baud | [code] |
| ISO 9141 | `$12` | 10417 baud (10.4 kbaud) | [code] |

The rates match the known Chrysler SCI and ISO 9141-2 rates, which also confirms the 8 MHz crystal.

## DRB protocol

`DRBIISerialCommunications_MM` ($4FDB) runs from the main loop. It echoes every received byte. A
command byte from `$10` to `$25` is kept in `DRBPointer1`. `DRBSerialToggles` says how many parameter
bytes follow (one or two), and these go to `DRBPointer2` and `DRBPointer3`. `DRBIIOuput_MM` ($5061) then
calls `DRBFunctionTable[command - $10]`.

| Cmd | Handler | Function | |
|---|---|---|---|
| `$10` | `OutputErrorCodes` | Sends the stored fault list (`$001B`-`$0022`, flash codes), `$FE` marks the end | [code] |
| `$11` | `OutputErrorBits` | Sends fault bitmap bytes | [inferred] |
| `$12` | `SetupHiSpeedDataTransfer` | Switches the SCI to 62500 baud for fast logging | [code] |
| `$13` | `SetupATM` | Starts actuator test *n* (parameter, up to `$40`); refused while the engine runs | [code] |
| `$14` | `SendDiagnosticDataToSCI` | Sends a live data value by ID (parameter below `$40`) | [code] |
| `$15` | `SendECUIDToSCI` | Reads an EEPROM byte (address from the two parameters) | [code] |
| `$16` | `SendConstValues` | Constant / EEPROM values; parameter `$80` checks `PPROG` | [inferred] |
| `$17` | `ClearErrorCodes` | Clears the stored faults and the freeze frame | [code] |
| `$18`, `$19`, `$24` | `DRB_Return` | No function | [code] |
| `$1A` | `SwitchTest` | Sends one of six input or output bytes: switch inputs, `OutputDriverBits`, `$00EE`, … | [code] |
| `$1B` | `InitByteModeDownload` | Enters byte-mode code download | [code] |
| `$1C` | `DRB_ResetEMR` | Stores an address for a later write (answers `$E2`); the original name says emission maintenance reminder reset | [inferred] |
| `$1D`, `$1E` | `DRB_UseRAM…SpecialProgramRoutine` | Writes a byte into RAM at an offset from `$0000` or `$0438` (answers `$E5`) | [code] |
| `$1F`, `$20` | `L52E9`, `L5312` | Builds and checks a block at `$021C` with a sum; part of the RAM program loader | [inferred] |
| `$21`, `$22` | `DRB_Special1`, `DRB_Special2` | Requests a special mode; `$21` answers `$02` (refused) with the throttle open, `$03` when `BitFlags_AIS` bit 3 is set, otherwise `$01` | [code] |
| `$23` | `L53AB` | Sub-commands `$01`-`$04`, `$0B`, engine stopped only; function not decoded | |
| `$25` | `L54E4` | Output override: target 1-4 in `DrbOverrideTarget`, state in `DrbOverrideState`. Target 1 is the output in `$00EE` bit 7, target 3 is the purge solenoid | [code] |

## Actuator tests (command `$13`)

The test number is the parameter of command `$13`. `ActuatorTestMode_MM` ($552D) uses entry *n − 1*
of `ATMFunctionTable` and toggles the output at a few hertz until the test times out. The output bits
are listed in the [input / output map](io_map.md).

| Test | Output | |
|---|---|---|
| `$01` | Ignition coil on OC5 (PA3), single spark | [code] |
| `$02` | Ignition coil on OC3 (PA5), single spark | [code] |
| `$04`, `$05`, `$06`, `$1D` | Injector cylinder 4, 3, 2, 1 (500 µs pulse) | [code] |
| `$07` | AIS motor, open / close | [code] |
| `$08` | Radiator fan relay | [code] |
| `$09` | A/C clutch relay | [code] |
| `$0A` | ASD relay (coil outputs forced off) | [inferred] |
| `$0C` | Speed control servo, vacuum and vent sequence | [code] |
| `$0D` | Output on `$0400` bit 2, latched by a pulse on `$0402` bit 2 | [code], output unknown |
| `$0E` | Tachometer | [code] |
| `$0F`, `$17` | TCC / PTU solenoid (`$00EE` bit 5) | [code] |
| `$10` | EGR solenoid | [code] |
| `$14` | All solenoids and relays together | [code] |
| `$15` | Purge solenoid | [inferred] |
| `$1A`, `$1B` | Speed control solenoids, one at a time | [code] |
| `$1C` | Clears `OutputDriverBits` bit 4 (fuel pump relay) | [inferred] |
| other | No output | [code] |

## OBD-II monitors

The code contains a complete set of OBD-II monitors driven from a table, `ObdMonitorTable` at $E939: ten
records of 14 bytes. Each record holds the monitor routine, its status byte in RAM, a scheduling mask, the
fault descriptor it reports and three calibration pointers for its enable conditions. `ObdMonitorScheduler`
($E9C5) walks the table, checks the enable conditions and calls each monitor whose status byte allows it.
`ObdMonitorInit` ($E8EA) prepares the status bytes; it is called (from `StoreMAPVoltsAndCalcMAPValue`). [code]

**Nothing calls `ObdMonitorScheduler` in this code base.** There is no JSR, JMP or pointer to $E9C5 anywhere
in the ROM, so in 5269718 and 5007033 none of these monitors runs, although most of their fault descriptors
are enabled. [code] This is the main piece of work for an OBD-II "Enhanced Edition": the monitors exist,
they only need to be scheduled, checked against the calibration and tested.

| # | Routine | Address | Monitor | Fault | Status byte |
|---|---|---|---|---|---|
| 0 | `MonitorO2HeaterUp` | $9449 | Upstream O2 heater | P0135 | `$0113` |
| 1 | `MonitorO2HeaterDown` | $945E | Downstream O2 heater | P0141 | `$0114` |
| 2 | `MonitorO2Response` | $9881 | Upstream O2 response | P0133 | `$010E` |
| 3 | `MonitorSecondaryAir` | $2F58 | Secondary air | P0411 | `$0112` |
| 4 | `MonitorEvapPurgeFlow` | $A118 | EVAP purge flow | P0441 | `$0116` |
| 5 | `MonitorCatalyst` | $428A | Catalyst efficiency | P0422 | `$0111` |
| 6 | `MonitorEgrFlow` | $6A22 | EGR flow | P0401 | `$0115` |
| 7 | `MonitorFuelSystemRich` | $A337 | Fuel system rich | P0172 | `$0117` |
| 8 | `MonitorFuelSystemLean` | $A55F | Fuel system lean | P0171 | `$0118` |
| 9 | `MonitorMisfire` | $AE3F | Misfire | P0300-P0304 | `$0119` |

## ISO 9141 (generic OBD-II)

`HanldeISODiagnosticComs` ($1ABA) is a state machine of 20 steps (`DiagnosticRoutineTable`). At the
start of a session it sets the SCI to 10.4 kbaud, forces OC4 (PA4) high and sends `$55`, the
ISO 9141-2 sync byte. The handlers read the stored faults, the freeze frame (`ISO_ErrorBitRegister0`
at `$011E`) and `ObdDtcCount` (`$010D`). That matches the service-1 "number of codes", service-2
"freeze frame" and service-3 "stored codes" requests of a generic scan tool. [inferred] The service
numbers and the message layout are not decoded yet.

## Lamps

The check-engine lamp (pin 36) and the charge indicator lamp (pin 37) are controlled through bits 6
and 4 of `$00EE` (`OutputBits2`, called `StartupSwitchMirror2` in the original disassembly). Flash codes are
blinked by toggling bit 6, so bit 6 is the check-engine lamp. [inferred] Bit 4 is set from `$0070` bit 7,
which only charging-system faults set (flag bit 5), so bit 4 is most likely the charge lamp.
[inferred] `$00EE` is sent out as part of a frame with the address bytes `$48`, `$50` and `$58`, together
with `$0176` and `$00EC`. The chip that receives these frames is not identified yet.
