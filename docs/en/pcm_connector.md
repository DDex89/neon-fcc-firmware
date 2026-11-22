# PCM connector (60 pins)

Pinout of the 1995 Neon FCC engine controller, from the wiring diagram, supplied by the project owner. Pin 48 (tachometer) was added later and is missing from some diagrams. For the firmware side of each signal see [io_map.md](io_map.md).

| Pin | Circuit | Wire | Function |
|---|---|---|---|
| 1 | K19 | BK/GY | Ignition coil #2 driver |
| 2 | Z12 | BK/TN | Ground |
| 3 | K13 | YL/WT | Injector #3 driver |
| 4 | K11 | WT/DB | Injector #1 driver |
| 5 | G7 | WT/OR | Vehicle speed sensor signal |
| 6 | K21 | BK/RD | Intake air temperature sensor signal |
| 7 | K141 | TN/WT | Downstream O2 sensor signal |
| 8 | K41 | BK/DG | Upstream O2 sensor signal |
| 9 | D20 | LG | SCI receive |
| 10 | K22 | OR/DB | Throttle position sensor signal |
| 11 | A14 | RD/WT | Fused B+ |
| 12 |  |  | Empty |
| 13 | G4 | DB | Fuel level sensor signal |
| 14 | K60 | YL/BK | IAC #2 driver |
| 15 | K39 | GY/RD | IAC #3 driver |
| 16 | K52 | PK/BK | EVAP purge solenoid control |
| 17 | K54 | OR/BK | TCC solenoid control |
| 18 | K51 | DB/YL | ASD relay control |
| 19 | C27 | DB/PK | Radiator fan relay control |
| 20 |  |  | Empty |
| 21 | K17 | DB/TN | Ignition coil #1 driver |
| 22 | Z12 | BK/TN | Ground |
| 23 | K12 | TN | Injector #2 driver |
| 24 | K14 | LB/BR | Injector #4 driver |
| 25 | K24 | GY/BK | Crankshaft position sensor signal |
| 26 | K44 | TN/YL | Camshaft position sensor signal |
| 27 | K42 | DB/LG | Knock sensor signal |
| 28 | K2 | TN/DB | Coolant temperature sensor signal |
| 29 | K1 | DG/RD | MAP sensor signal |
| 30 | D21 | PK | SCI transmit |
| 31 | V37 | RD/LG | Speed control switch signal |
| 32 | K29 | WT/PK | Brake switch sense |
| 33 | C20 | BR/OR | A/C switch sense |
| 34 | K59 | VT | IAC #4 driver |
| 35 | K40 | BR/WT | IAC #1 driver |
| 36 | G3 | BK/PK | Malfunction indicator lamp driver |
| 37 | G12 | TN/BK | Charge indicator lamp driver |
| 38 | K31 | BR | Fuel pump relay control |
| 39 | K35 | GY/YL | EGR solenoid control |
| 40 | K36 | TN/RD | Speed control vacuum solenoid control |
| 41 | K20 | DG | Generator field driver |
| 42 | A142 | DG/OR | ASD relay output |
| 43 | K6 | VT/WT | 5 V supply |
| 44 | K7 | OR | 8 V supply |
| 45 |  |  | Empty |
| 46 |  |  | Empty |
| 47 | V32 | YL/RD | Speed control power supply |
| 48 | G21 | GY/LB | Tachometer signal |
| 49 | G31 | VT/LG | Battery temperature sensor signal |
| 50 | T41 | BR/YL | Park/neutral position switch sense |
| 51 | K4 | BK/LB | Sensor ground |
| 52 | Z11 | BK/WT | Ground |
| 53 |  |  | Empty |
| 54 | F18 | LG/BK | Fused ignition switch output |
| 55 | L1 | VT/BK | Reverse lamp sense |
| 56 | K10 | WT | Power steering pressure switch sense |
| 57 |  |  | Empty |
| 58 |  |  | Empty |
| 59 | C28 | DB/OR | A/C compressor clutch relay control |
| 60 | V35 | LG/RD | Speed control vent solenoid control |
