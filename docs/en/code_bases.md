# FCC code bases

Program versions ("code bases") found in the FCC images collected so far, named by the end
address of the first code section. All images with the same code base have byte-identical program
code (compared over $1200 to the end of code part 1 and $F000-$FFFF); only the calibration differs.
Applications and revision letters come from the "Neon Code Families" spreadsheet.

| Code base | Images | Copyright | Notes |
|---|---|---|---|
| B588 | 1 | 1993 | 94½ generation |
| B559 | 12 | 1994 | The original 1995 part numbers, SOHC and DOHC, all markets; buildable from this repository (`src_b559/`) |
| B4F3 | 3 | 1994 | Later revisions (rev D of 4874154 and 4874156, export automatic) |
| B4C2 | 1 | 1994 | Rev C of 4874154; not listed in the spreadsheet |
| B4CC | 3 (+2 "enh") | 1994 | Mopar Performance SOHC/DOHC and 5269718 (rev B of 4874164); the code base of this repository |

## All images

| Part number | Application | Code base | CONFIG | Notes |
|---|---|---|---|---|
| 5293121 | Not in the spreadsheet; 1993 copyright, automatic | B588 | `$A7` A/C, auto |  |
| 4874154 | SOHC Fed low altitude, manual | B559 | `$87` A/C, manual |  |
| 4874155 | SOHC Fed high altitude & California, manual | B559 | `$C7` A/C, EGR, manual |  |
| 4874156 | SOHC Fed low altitude & Taiwan, automatic | B559 | `$A7` A/C, auto |  |
| 4874157 | SOHC Fed & California, manual, racing | B559 | `$C7` A/C, EGR, manual |  |
| 4874158 | SOHC Fed high altitude, automatic | B559 | `$A7` A/C, auto |  |
| 4874159 | SOHC California, automatic | B559 | `$E7` A/C, EGR, auto |  |
| 4874160 | Export & Mexico, manual, Sport | B559 | `$87` A/C, manual |  |
| 4874161 | Export, manual | B559 | `$87` A/C, manual |  |
| 4874162 | DOHC Fed low altitude, manual | B559 | `$87` A/C, manual |  |
| 4874164 | DOHC Fed & California, manual, racing | B559 | `$C7` A/C, EGR, manual | checksum fails (edited, sums to $9C) |
| 4874165 | DOHC Fed low altitude, automatic | B559 | `$A7` A/C, auto |  |
| 5013113 | FJ 2.0 Fed/Canada, manual, flex head | B559 | `$87` A/C, manual |  |
| 5269709 | SOHC Fed low altitude, manual (4874154 rev D) | B4F3 | `$87` A/C, manual |  |
| 5269712 | SOHC Fed & Taiwan, automatic (4874156 rev D) | B4F3 | `$A7` A/C, auto |  |
| 5269738 | SOHC export, automatic | B4F3 | `$A7` A/C, auto |  |
| 5269646 | SOHC Fed low altitude, manual (4874154 rev C) | B4C2 | `$87` A/C, manual | file was named 5289646 |
| 5007033 | Mopar Performance SOHC, manual | B4CC | `$C7` A/C, EGR, manual | “enh” file; checksum fails (edited, sums to $9C) |
| 5007033 | Mopar Performance SOHC, manual | B4CC | `$C7` A/C, EGR, manual |  |
| 5007034 | Mopar Performance DOHC, manual | B4CC | `$86` A/C, manual | checksum fails (edited, sums to $9C); same code as 5007033, copyright text changed |
| 5007034 | Mopar Performance DOHC, manual | B4CC | `$86` A/C, manual | “enh” file; checksum fails (edited, sums to $9C); same code as 5007033, copyright text changed |
| 5269718 | DOHC Fed & California, manual, racing (4874164 rev B) | B4CC | `$86` A/C, manual | checksum fails (edited, sums to $9C); edited copy; the repository uses a clean one |

### Findings

- **B4C2** is a code base that the spreadsheet does not list (5269646, rev C of 4874154).
- The revision letters are not in code-base order: for 4874154 rev C is on B4C2 and rev D on B4F3,
  so the letter does not tell which program version is newer.
- **Checksum:** five images fail the $B805 checksum. In each of them $FF50 was changed and the
  8-bit sum is $9C, so they were saved by an editor that forces the sum to a constant instead of the
  $B805 byte. On a B559 calibration this sets code 53. The unedited images all pass with $FF50 = $FF.
- **EEPROM window:** several images carry data in $B600-$B7FF. That range is the HC11's internal
  EEPROM, which the CPU sees instead of the chip, so these bytes have no effect; they show that the
  file was read from a programmed ECU or saved by a tool.
- 4874157 (SOHC racing) and 4874164 (DOHC racing) have EGR enabled; their rev B, 5269718, has it off.
- The Mopar 5007033 keeps the EGR bit in CONFIG set, but its EGR windows (`EGR21`, `EGR23`, `EGR27`
  and the byte after it) are set to $FD/$FE, which the engine never reaches, so EGR is never enabled.

The calibration layout differs between code bases (for example the fault descriptor table is at
$D4E9 in B559 and at $D4E3 in B4CC), so tables must not be copied byte for byte between them.

## B559 compared with B4CC

The annotations of this repository were made on B4CC and ported to B559 with
`tools/port_base.py` (see [building.md](building.md#other-code-bases)). The comparison below comes
from that alignment: code part 2 ($E229-$FFD5) is identical, and in code part 1 41,653 of 41,677
B4CC bytes have an exact counterpart in B559. [code]

**B4CC is B559 with calls removed.** The B4CC program is 141 bytes shorter. About 100 of them are the
three temperature features listed below; the rest are `jsr` instructions that B4CC no longer has.
The called routines are still in the B4CC ROM, byte for byte, but nothing reaches them there. [code]

| Routine | Called from (B559) | What B4CC loses |
|---|---|---|
| `ObdMonitorScheduler` | MainSubLoop | All ten OBD-II monitors (see [diagnostics.md](diagnostics.md#obd-ii-monitors)) |
| `ControlPurgeSolenoid_MM` | MainSubLoop | Canister purge control (`OutputBits2` bit 7); only the DRB actuator test drives it |
| `DetermineIndividualInjectorTrims_MM` | MainSubLoop | Individual cylinder fuel trims |
| `CalculateVariableRevLimit_MM` | MainSubLoop | Variable rev limit; `VariableRevLimit` stays at $FF from reset, only the fixed limits act |
| `CheckIfCheckEngineLightShouldBeOn_A_MM`, `_B_MM` | MainSubLoop | Charge-warning lamp logic (`OutputBits2` bit 4); despite the name not the MIL. Only the fan code (with CONFIG2 bit 6 set) and the DRB tests still touch the bit |
| `EmmissionMaintenanceRemider1_MM` | MainSubLoop | Emission maintenance reminder record in EEPROM, code 62 |
| `VerifyOperationOfDownstreamO2Sensor_MM` | MainSubLoop | Downstream O2 sensor check (code 21) |
| `DecrementDSO2SensorDiagnosticCounter_MM` | MainSubLoop | Downstream O2 diagnostic counter |
| `VerifyOperationOfAmbientTempSensor_MM` | MainSubLoop | Ambient / battery temperature plausibility check (code 23) |
| `CheckErrorMaskingAndSetCodes_MM` | SubLoopA | A speed / TPS related check (not decoded yet) |
| `FurtherMAPAndBaroDiagnostics2_SM` | SubLoopC | MAP versus TPS rationality check (code 24) |
| `IncrementOrClearKnockDiagCounter_SM` | SubLoopC | Knock sensor signal check (code 16) |

So the racing / Mopar code base runs without OBD-II monitors, purge, cylinder trims, the variable
rev limit and several sensor checks, which fits its use. The fault descriptors of these checks are
still in the calibration and may be enabled, but nothing reports them. [code]

**Code only in B559.** Three short additions, all using the same start temperature: `BatteryTemp`,
or `AmbientAirTemp` when CONFIG2 bit 5 is set. [code]

| Where (B559) | What it does | Calibration (B559) |
|---|---|---|
| Reset init, $9202-$9224 | Sets the purge delay `PurgeDelayTimer` ($021C): colder than `PurgeDelayTempCold` gives $FFFF, colder than `PurgeDelayTempWarm` gives `PurgeDelayTime`, warmer gives no delay | $C983, $C984, $C985-$C986 |
| `ControlPurgeSolenoid_MM`, $9CF9-$9D1D | While the delay runs and the car is below `MPHREF`, counts the delay down (once per `Counter_MainLoop` wrap) and keeps purge from running | - |
| `ExhGasRecirc_MM`, $B257-$B272 | EGR only above `EgrTempOn`; once on, it stays on down to `EgrTempOff` | $CB3C, $CB3B |

Values in the factory images: $C983-$C986 = `6E 8A 02 21` and $CB3B/$CB3C = `73 74` in all of
4874154-4874165; 5013113 has `6E 84 02 8E` and `7B 7C`. The temperature scale of these inputs is not
decoded yet. [code]

**Layout consequences.** Because of these additions the B559 calibration has 4 extra bytes after the
idle purge table and 2 after the EGR constants: B4CC addresses $C983-$CB36 are 4 higher in B559 and
$CB37-$DFF7 are 6 higher. RAM is the same except the DRB RAM-program buffer, which moved from $021C to
$021E to make room for `PurgeDelayTimer`. [code]
