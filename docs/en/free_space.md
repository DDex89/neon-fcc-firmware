# Free space in ROM, RAM and EEPROM

This is the starting point for changing the firmware: where new code, tables and variables can go
without moving anything that exists. Addresses are for B4CC unless stated; the other code bases
are listed where they differ. "No direct access" means no instruction uses the address as a
direct or extended operand; accesses through an index register are not counted, so each region
below was also checked against the index bases the code loads.

## ROM

| Region | Size | Contents now | Notes |
|---|---|---|---|
| $B4CD-$B5FF | 307 bytes | $FF after the last routine of code part 1 (`RescaleEngineRPM_MM`) | B4F3: $B4F4-$B5FF (268), B4C2: $B4C3-$B5FF (317), B559: $B55A-$B5FF (166). Counted by the checksum. [code] |
| $DA0C-$DFFF | 1,524 bytes | $FF between the end of the fault descriptor table area and the tables at $E000 | B559: $DA12-$DFFF (1,518). No code reference points into it; `ldx #$DDD0` in the cruise code is a constant (a divisor), not an address. Counted by the checksum. [code] |
| $FDDA-$FFA2 | 457 bytes | $FF after `VarRevLimit_Return`, before the copyright text | The same in all four code bases. $FF50 inside it is the spare byte that editors use to fix the checksum, so keep one byte for that. [code] |
| $FFC0-$FFD5 | 22 bytes | $FF between the copyright text and the vectors | [code] |

Together about 2.3 KB. Code part 2 and the calibration area are reached with 16-bit addresses like
everything else, so a new routine can live in any of them; the 68HC11 has no banking here.

Earlier versions of these annotations decoded $FEFD-$FFA2 as code because the table at $8D04 was
taken for code pointers. It holds the injector clear masks FE FD FB F7 FE FD
(`InjCylinderClearMasks`), so that area is plain filler. [code]

## RAM

| Region | Size | Use | Notes |
|---|---|---|---|
| $0220-$03FF | 480 bytes | No direct access in normal running | `DrbRamBuffer` ($021C) is the DRB RAM-program download buffer; a download may fill it up to $0437. So this RAM is free while no DRB RAM program is loaded. In B559 the buffer starts at $021E, so the free part is $0222-$03FF. [code] |
| $04C4-$04FF | 60 bytes | Stack | The reset code sets the stack pointer to $04FF; the deepest stack use is not measured yet. Not free. [code] |
| $000D-$0010, $0012-$0018, $002A-$002D | 15 bytes | No direct access | Direct-page bytes are worth having for bit instructions, but $000D, $002A and $002D are loaded as index bases, so check before using them. |
| $0464-$0467 | 4 bytes | No direct access | |

The RAM fault bitmap at $0135-$0148 has no direct access either, but it is used through the fault
descriptors (offset from $0135), so it is not free. A warm start keeps RAM only if the 16-bit sum of
$0005-$0036 and $0100-$014D matches the stored copy (`CountRamValuesFrom05to38`); a variable placed
in those ranges either has to be included in that sum or not be kept over a warm start. [code]

## EEPROM ($B600-$B7FF, 512 bytes)

Bytes used by the code: $B600-$B611 (`EEPROM1`-`EEPROM3`, including the emission maintenance
reminder records), $B612-$B618 (`EEPROM4`-`EEPROM7a`, configuration and checks read at reset and by
the CCD code), $B61D (`EEPROM8`, read by the crank / fuel code), $B7E0, $B7E1 and $B7EF (`EEPROM10`-
`EEPROM12`) and the part number at $B7F0-$B7F3. Nothing in the code accesses **$B61E-$B7DF** (450
bytes) directly. DRB command $15 can read any EEPROM byte, so a scan tool may still look there.
EEPROM is outside the checksum. Writing it needs the PPROG sequence and about 10 ms per byte, and its
endurance is limited, so it suits learned values saved at key-off rather than live data. [code]

## Processor time

The main loop runs every 10.75 ms and records its longest pass in `LoopTimeWorst` (RAM $0454, in
units of 256 timer ticks, so $15 would mean a full slot). Reading that byte over the DRB link on a
running engine is the simplest way to see how much time is left before adding work to the main
loop. Work in the interrupt handlers (fuel and spark scheduling) is not covered by this number.
