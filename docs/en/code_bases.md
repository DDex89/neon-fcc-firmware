# FCC code bases

Program versions ("code bases") found in the FCC images collected so far, named by the end
address of the first code section. All images with the same code base have byte-identical program
code (compared over $1200 to the end of code part 1 and $F000-$FFFF); only the calibration differs.
Applications and revision letters come from the "Neon Code Families" spreadsheet.

| Code base | Images | Copyright | Notes |
|---|---|---|---|
| B588 | 1 | 1993 | 94½ generation |
| B559 | 12 | 1994 | The original 1995 part numbers, SOHC and DOHC, all markets |
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
