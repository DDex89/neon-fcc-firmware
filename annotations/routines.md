# Routine descriptions

Each `## ADDR Name` section names a routine (the name replaces any earlier label) and gives the text
that `tools/gen_source.py` puts in the routine's header comment. The first sentence is also used as
the inline comment on every `jsr`/`bsr` to that routine.

Status tags used below:
- **[reviewed]** - the code was read and the description checked against it.
- **[from name]** - the description follows the original disassembly's naming and has not been
  re-verified instruction by instruction yet.

Timing assumes the usual 8 MHz crystal (2 MHz E-clock). TMSK2 = $11 selects a /4 timer prescaler,
so one TCNT tick is 2 us. This matches the "x 11 ms" units used by many calibration constants:
the main loop period is $1500 ticks = 10.75 ms.

## 8DEB ResetInterrupt
Power-on / reset entry point. [reviewed]

Disables interrupts, puts the stack at $04FF and programs the 68HC11 system registers: OPTION
($B9: A/D powered, IRQ edge-sensitive, clock monitor on, COP rate select 01), TMSK2 ($11: PAI interrupt enable, timer prescaler /4),
BPROT (EEPROM unprotected), PACTL, HPRIO, OC1M, TCTL1/TCTL2 (output-compare pin actions and input
capture edges) and CFORC.

It then decides between a cold and a warm start. CountRamValuesFrom05to38 sums the RAM that holds
adaptive memory, fault codes and learned values; if that sum matches the stored copy and the
signature $AAA5 is present, the RAM is kept (warm start after a trap). Otherwise RAM is cleared and
defaults are loaded (MINTHR from MTHRMX, default knock average, AIS position, fault codes erased).

Next it initialises the external I/O device at $0400 from the (offset, value) table that follows
the code, sets up the SCI/SPI pins on port D, kicks the COP watchdog, starts the first A/D
conversions (O2, MAP, ...) and falls into the main loop.

## 8D7F Trap_SCI_SPI_RTI
Unexpected-interrupt trap for the SCI, SPI and real-time interrupt vectors (cause code $01). [reviewed]

None of these interrupts is enabled in normal operation. Like all Trap_* stubs it loads its cause
bit into B and joins Trap_IRQ, which records the cause and restarts the controller.

## 8D83 Trap_XIRQ
Unexpected XIRQ trap (cause code $02). [reviewed]

## 8D87 Trap_COP
COP watchdog timeout trap (cause code $04): the main loop stopped kicking COPRST. [reviewed]

## 8D8B Trap_ClockMonitor
Clock monitor failure trap (cause code $08). [reviewed]

## 8D8F Trap_IllegalOpcode
Illegal opcode trap (cause code $10), for example after a jump into data. [reviewed]

## 8D93 Trap_SWI
Software interrupt trap (cause code $20). SWI is not used by the firmware. [reviewed]

## 8D97 Trap_TOC2
Output compare 2 interrupt trap (cause code $40). OC2 is used as an output, not as an interrupt. [reviewed]

## 8D9B Trap_IRQ
Common trap handler; the IRQ pin itself enters here with cause code $80. [reviewed]

ORs the cause bit into BYTE00 and copies a word from the interrupt stack frame (intended as the
interrupted program counter) to BYTE01/BYTE02, so the fault can be read out later. It then resets the stack and repeats the
hardware initialisation of ResetInterrupt; because RAM is not cleared on this path, the warm-start
check keeps adaptive memory and fault codes. (The original disassembly called this routine
"Interrupt_CrankSensor_Signal"; the crank sensor is handled by Isr_TIC1_CrankEvent.)

## 1219 Isr_TOC1_Periodic
Output compare 1 interrupt: periodic tick every $03B9 timer counts (about 1.9 ms). [reviewed]

Re-arms TOC1, clears its flag and runs jobs that need a faster rate than the 10.75 ms main loop,
starting with the alternator field duty-cycle timer (Timer_AlternatorDutyCycle).

## 78EC Isr_PAI_CamPhase
Pulse accumulator input (PA7) edge interrupt: cam sensor edge, used for cylinder identification. [reviewed - partially]

Each interrupt flips the armed edge (PACTL PEDGE) so both edges of the cam signal are seen. On the
edge it reads the level of the crank signal on PA2 (the TIC1 pin): that level tells which half of the
engine cycle the cam edge belongs to, and the routine sets the phase index CrankEventCounter ($0449,
= $07 or $0F) and the synchronisation flags SyncFlags74/SyncFlags75. Roles inferred from the code: the
original disassembly called this the crank sensor and TIC1 the cam sensor, but the event dispatching
is done by TIC1 and the phase decision here.

## 7956 Isr_PAOV
Pulse accumulator overflow interrupt: counts overflows in $047B. [reviewed]

## 7965 Isr_TIC3
Input capture 3 interrupt: restarts the timer-overflow count ($0478) used to measure long periods. [reviewed]

Clears $0478, enables the timer overflow interrupt and corrects the count if TCNT has already
wrapped past the TIC3 capture. Together with Isr_TOF this gives a period measurement longer than
one 131 ms timer cycle (needed during cranking).

## 797D Isr_TOF
Timer overflow interrupt: increments the overflow counter $0478 used with input capture 3. [reviewed]

## 798E Isr_TIC1_CrankEvent
Input capture 1 (PA2) interrupt: crank sensor edge - the main engine position event. [reviewed - partially]

Time-stamps the edge (TIC1) and measures it against the last input capture 3 time and the number of
timer overflows since the previous pulse. Reset programs TCTL2 = $1A: IC1 captures rising edges and
IC3 falling edges, so TIC1 - TIC3 is the low time before this rising edge. That separates the slots
inside a group (short low time) from the first edge after the long gap between groups. Each group of
the crank wheel has four rising edges, one per event phase (see docs/en/engine_control.md). When the engine is
synchronised (SyncFlags75 bit 5 or 6, depending on the phase bit in SyncFlags74 bit 7) it increments
CrankEventCounter and calls one of four handlers from CrankPickupIntrAddressTable, selected by the
low two bits of SyncFlags75: CrankInterrupt_FallingEdge, CrankInterrupt_HandleCamSensorRisingEdgeA,
CrankInterrupt_HandleCamSensorRisingEdgeB and CrankInterrupt_CalculateFuel. Fuel and spark for the
next cylinder are scheduled from these handlers.

## AE1D Isr_TOC4_KnockSample
Output compare 4 interrupt: samples the knock sensor at the end of the knock window. [reviewed - partially]

Starts an A/D conversion on channel 3, waits a few cycles and stores ADR1 in KnockVolts (or zero
when knock sensing is disabled by BitFlasg71 bit 7). The value feeds CalculateKnockRetard_MM.

## AC21 Interrupt_DwellTimerA
Output compare 3 (PA5) interrupt: ignition coil channel A. [reviewed - partially]

The Neon 2.0 uses two ignition coils in wasted-spark mode. OC3 and OC5 drive the two coil drivers
directly: the pin action in TCTL1 switches between "start dwell" and "fire", and the compare value
sets the time. The events are armed from ScheduleIgnitionCoils in the crank event handlers.

## AC6F Interrupt_DwellTimerB
Output compare 5 (PA3) interrupt: ignition coil channel B (see Interrupt_DwellTimerA). [reviewed - partially]

## AFFA Interrupt_SpeedometerSignal
Input capture 2 interrupt: vehicle speed sensor pulse; measures the period between pulses. [from name]

## 9280 MainProgramLoop
Main program loop, paced to one pass every $1500 timer ticks (10.75 ms). [reviewed]

Each pass calls MainSubLoop, then runs at most one of the eight sub-loops listed in SubLoopList:
the request bits in L0150 are scanned from bit 0 upward and the first set bit is cleared and its
routine is called, so the slower jobs are spread over consecutive passes. Finally it measures how
long the pass took (L0455, worst case in $0454) and waits until TCNT reaches the next slot stored
in MinimumTimerCountBeforeMainloopCanContinue.

## 92D9 MainSubLoop
Work done on every main-loop pass (10.75 ms). [reviewed]

Kicks the COP watchdog (writes $55/$AA to COPRST), toggles bit 4 of the I/O device register $0409
(external watchdog / heartbeat), updates the cam and vehicle-speed period measurements, samples
battery voltage, TPS and the cruise switch, runs the throttle checks and barometric read logic,
calculates cranking fuel and continues with further always-run tasks (see the call list in the
source).

## 93A1 SubLoopA
Sub-loop A of the round-robin scheduler (one of eight jobs spread over main-loop passes). [from name]

## 93B1 SubLoopB
Sub-loop B of the round-robin scheduler. [from name]

## 93C1 SubLoopC
Sub-loop C of the round-robin scheduler. [from name]

## 93E4 SubLoopD
Sub-loop D of the round-robin scheduler. [from name]

## 93F1 SubLoopE
Sub-loop E of the round-robin scheduler. [from name]

## 93F8 TempSensorSubLoop_F
Sub-loop F: coolant, charge-air and ambient temperature sensor sampling and filtering. [from name]

## 9429 SubLoopG
Sub-loop G of the round-robin scheduler. [from name]

## 9439 SubLoopH
Sub-loop H of the round-robin scheduler. [from name]

## 7B7A ScheduleIgnitionCoils
Arms the coil timers: writes TOC3/TOC5, sets the TCTL1 pin actions, enables OC3I/OC5I in TMSK1 and uses CFORC to force a pin state. [reviewed - partially]

## 7AC8 CrankInterrupt_FallingEdge
Crank event handler, falling edge: period bookkeeping, rev limit, MAP checks, spark scatter, injector hand-off. [reviewed - data flow]

Called from Isr_TIC1_CrankEvent when the event phase (SyncFlags75 low bits) is 0 - most likely the
69 degree BTDC slot, the first of the group. Updates the
overflow counts and the pulse-width / period measurements (TimerOverflowsBetweenCamPulses,
DistributorFallingEdgePulsewidth_HB), checks the normal rev limiter (REVLMT6), runs the MAP sensor
plausibility checks (MPDELT, MPDELA, MPRPML/MPRPMH, MPDAGL/MPDAGH), applies idle spark scatter
(HandleSparkScatter) and writes the injector pulse-width registers for the cylinders due next.

## 7DD3 CrankInterrupt_HandleCamSensorRisingEdgeA
Crank event handler for event phase 1 (49 degree BTDC slot, probable): injector scheduling for the next cylinder group. [reviewed - data flow]

Despite the historical name it runs from the crank event interrupt. It selects the cylinders in
InjCylinderMask, scales the pulse width and writes the injector registers and $0410.

## 8275 CrankInterrupt_HandleCamSensorRisingEdgeB
Crank event handler for event phase 2 (29 degree BTDC slot, probable): injector scheduling, adaptive retard index and running-time counters. [reviewed - data flow]

## 83E4 CrankInterrupt_CalculateFuel
Crank event handler for event phase 3 (9 degree BTDC slot, probable): the main crank-synchronous calculation. [reviewed - partially]

- Engine speed from the measured period (EngineRpm_HB, EngineRpmDouble_HB, AverageRPMIncremental).
- Starts an A/D scan of channels 0-3 (ADCTL = $10) so MAP is sampled at a fixed crank angle.
- Arms the knock window: TOC4 = last edge time + 2 x (edge-to-edge time) x TimeToAngleAdvanceConvFactor
  / 256, i.e. a fixed fraction of the tooth period after the edge; Isr_TOC4_KnockSample reads the
  sensor when it expires.
- Forces the coil output of the active pair through CFORC (FOC3 or FOC5, chosen by SyncFlags74 bit 0)
  when BitFlasg71 bit 1 requests it.
- Calculates the running fuel (MAPHI, PRTTBL, modifiers, transient factors), the per-cylinder knock
  retard (KNKMAP, KNKRPM, MAXRTD, RTRDRT) and writes the injector pulse-width registers.

## 8B4D IncludeInjectorLatency
Final injector pulse width: fuel-pressure factor, injector latency, per-cylinder masks, hand-off to the injector driver. [reviewed - partially]

The injectors are not timed by the HC11 output compares. The final pulse width (in microseconds,
latency added as InjectorLatencyPW x 4) is written as a 16-bit value into the registers of the
external I/O device - $0424 (cylinder 1), $0428 (cylinder 2), $042C (cylinder 3), $0430
(cylinder 4) - for the cylinders selected in InjCylinderMask (bit 0 = cyl 4, bit 1 = cyl 2,
bit 2 = cyl 1, bit 3 = cyl 3, i.e. the 1-3-4-2 firing order). If the pulse is longer than $7D and the
device status bit $10 in $0400 is set, $04 is written to IODev_InjectorCommand ($0410). The device
then produces the injector pulses itself. The AIS-related enrichment/enleanment pulse is handled here too.

## 8A95 CalculateInjectorPulsewidthForEngineRunning
Running fuel: base injector pulse width from MAP and RPM, then all multiplicative corrections. [reviewed]

Speed-density calculation:
1. MAP is rescaled through MAPHI to the row coordinate of the 3D tables (MAPRescaledfor3D).
2. Temp5 = (MAP - MAPMIN) x DFPART / 2: air mass proportional to manifold pressure.
3. PRTTBL (RPM x MAP, 3D) adds a volumetric-efficiency style correction:
   base = Temp5 + Temp5 x PRTTBL / 256 (saturated at $FFFF) -> BaseInjectorPulsewidthX.
4. The throttle-enrichment factor (part throttle / WOT blend, scaled by WOTMUL) is combined with
   BaseFuelModifier, then multiplied by SumOfFuelModifiers (temperature, barometric, charge-air,
   closed-loop and adaptive corrections) and by the base pulse width.
5. During knock or after an off-throttle event, extra enrichment is added from the total knock
   retard (KNNRCH, limited by MAXKNR).
Injector latency (BATOFF vs battery voltage) is added afterwards in IncludeInjectorLatency.

## 6F7F CalculateInjectorPulsewidthForStarting_MM
Cranking fuel: pulse width from coolant temperature, number of engine revolutions and baro. [from name]

Uses STRTFL, STFTMP/STFTM2, EPPMUL and STFBAR (see the calibration reference): start fuel =
[STRTFL^2 x (1 - STFBAR - STFTMP) x EPPMUL + BATOFF x 4] x 4 us. Also handles the "clear flood" case
when the throttle is floored while cranking (ThrottleFlooredWhileStarting_Unload).

## 76A1 CalculateSumOfAllFuelModifiers_MM
Product of all slow fuel corrections, stored in SumOfFuelModifiers. [reviewed - partially]

Cold enrichment from the 3D tables CLDLDP (off idle) / CLDLDI (idle) and CURV3D (coolant x time since
start, with heat-soak correction after a stall), barometric compensation BAROCP, barometric
enrichment BARENR x BARMAP x BARRPM, charge-air temperature enrichment AIRTMP x AIRMAP x AIRRPM,
and the closed-loop/adaptive factor.

## 6D87 CalculatePartThrottleTransientFuel
Transient fuel: accelerator-pump style enrichment and deceleration lean-out. [from name]

MAP-based and TPS-based "pump shot" (MAPTRG/MAPMAX/AESLOP, POSTRG/THRMAX/POSSLP) on tip-in,
lean-out on closing throttle or falling MAP (LOTTHR, DECEL, LOTIME ...). See docs/en/fuel.md.

## 72F8 CalculatePartThrottleEnrichmentAndLatency_MM
Part-throttle / WOT enrichment factor (PTEADJ, WOTENR) and its transition timing. [from name]

## 704C ControlEngineCutout_MM
Fuel cut-off decisions: rev limiter, speed limiter, overboost/MAP and limp-mode limits. [from name]

Uses REVLMT5/REVLMT6 (normal rev limiter cut/restore), SPDLMH/SPDLML (speed limiter) and the limp-in
rev limits for a failed MAP or TPS sensor. The cut is applied per revolution
(ShutOffEngineForThisRotation).

## A74B CalculateSparkAdvance_MM
Spark advance calculation. [reviewed]

Every fourth main-loop pass it counts down AdvanceDownCounter_A. Then, depending on BitFlags65 bit 7:
- set: base advance from BASADV (coolant temperature x MAPMOD 3D table) plus the products
  BASMAP x BASRPM and BASMAP x BASCHG (charge-air temperature), saturated to a signed byte, and
  continues at LookupNormalAdvance;
- clear: warm advance from HOTMRP (RPM x MAP, 3D) with idle corrections IDLIAT/ILDMAP
  (CalculateIdleAdvance).
The result is then limited and corrected for knock, TPS, delta-RPM and speed retard
(CheckForOtherRetardFactors) and stored by STORE_SPARK_ADV.

## A7AC CalculateIdleAdvance
Warm-engine advance from HOTMRP (RPM x MAP) with charge-air and MAP corrections. [reviewed]

Despite the historical name this path is used for all warm part-throttle and idle operation; the
full-throttle table WOTMRP is selected later in LookupNormalAdvance.

## A8C8 LookupNormalAdvance
Applies the WOT advance table (WOTMRP) when the throttle is open and finishes the advance value. [from name]

## ACD9 CalculateKnockRetard_MM
Knock control: compares the sampled knock signal with the average and adjusts retard. [from name]

Knock is declared when the sample exceeds the running average by DLTKNK (vs RPM). Retard grows by
the KNKLIM/INCSRT rules up to MAXRTD/RETMAX (vs MAP) and recovers slowly. The adaptive retard
(ARMAP, ARRPM) learns a long-term retard; ARMPIC = $FF disables it.

## 8926 CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT
Per-cylinder knock retard bookkeeping used when scheduling each spark event. [from name]

## AD7F CalculateAverageKnockVolts_SM
Running average of the knock sensor background level (window: KNAMAP, KNARPM, KNACLT ...). [from name]

## 56E7 CaculateChecksum
ROM self test: 8-bit sum of $1200-$B5FF and $B800-$FFFF must equal the byte at $B805. [reviewed]

The sum skips the $B600-$B7FF window of the internal EEPROM. $B805 is the last byte of the part
number in the calibration header, so the checksum is adjusted with a spare byte (usually $FF50)
whenever the calibration is modified. A mismatch is reported through ThrowNonCriticalError with the
fault descriptor at $D4F3 (code 53, internal controller failure); the engine keeps running.

## 5FEF CountRamValuesFrom05to38
16-bit sum of RAM $0005-$0036 and $0100-$014D, used to validate RAM on a warm start. [reviewed]

## 48E7 HandleO2Processing_MM
Narrow-band O2 feedback: open/closed loop decision and the rich/lean ramp controller. [from name]

The controller kicks the mixture rich or lean (PRIRMP/SECRMP kick tables per RPM x MAP cell) until
the O2 sensor toggles; the secondary ramp also updates the adaptive memory cells. See
docs/en/closed_loop.md.

## 4CA9 AdaptiveMemory_UpdateCellIfRequired
Adaptive (learned) fuel correction: updates the current RPM/MAP cell (AutoCalCell0-12). [from name]

## 32E1 CalculateTargetIdleSpeed_MM
Target idle speed from coolant temperature, gear (P/N or drive) and A/C load (AISPN, AISCLD ...). [from name]

## 3514 ControlAIS_MM
Idle air control: positions the AIS stepper motor to hold the target idle speed. [from name]

## 1563 AisDriveRoutine
Low-level AIS stepper motor phase sequencing. [from name]

## B1C7 ExhGasRecirc_MM
EGR solenoid control: enables EGR within RPM, MAP, coolant and time windows. [reviewed]

Checks the conditions with the EGR21-EGR27 calibration constants (RPM window, MAP window
depending on baro, minimum coolant temperature, time since start) and switches the EGR solenoid.
Setting the thresholds to $FD/$FE keeps EGR permanently off (as Mopar did in 5007033).

## 6AE7 EGR_CheckHiLoLimits
Checks A against the low/high limit pair at 0,X and 1,X; aborts the caller (PULX) if outside. [reviewed]

## 9C6A ControlPurgeSolenoid_MM
Evaporative canister purge solenoid control. [from name]

## 9F68 DetermineIndividualInjectorTrims_MM
Individual cylinder fuel trims (CL1PTR..CLTRP4). [from name]

## A677 ControlPTU_MM
Torque converter lock-up (part-throttle unlock, PTU) control for automatic transmissions. [from name]

## 29EB ControlFan_MM
Radiator fan relay control from coolant temperature, vehicle speed and A/C state. [from name]

## 250E ControlAirConditioning_MM
A/C compressor clutch relay control, including cut-out at wide open throttle. [from name]

## 1A1F ControlAsdRelay_MM
Auto shutdown (ASD) relay: powers fuel pump, injectors and coils while the engine turns. [from name]

## 131E ControlAlternator
Alternator field control (the controller regulates charging voltage directly). [from name]

## FA9D Lookup4ByteTable
2D table lookup with linear interpolation ("point-slope" format). [reviewed]

Input: A = x, X = table. Table: count n, then n-1 records (x_i, y_i, slope_hi, slope_lo) and a final
(x_n, y_n). Returns y_0 for x <= x_0; otherwise finds the segment with x_i <= x < x_(i+1) and
returns y_i + (x - x_i) x slope / 256 in A (and B). Slope is a 16-bit value in 1/256 units.

## FBF2 Lookup5ByteTable
2D lookup for tables with 5-byte records (16-bit outputs). [from name]

## B3CA Lookup3DTableRoutine
3D table lookup (bilinear interpolation), variant 1. [from name]

## B437 Lookup3DTableRoutine_2
3D table lookup with bilinear interpolation. [reviewed]

Input: A = row coordinate (0-255, e.g. MAPRescaledfor3D), B = column coordinate (0-255, e.g.
RPMRescaledfor3D), X = table. Table header: rows, cols, sign flag ($00 unsigned, $80/$FF signed),
then rows x cols bytes. The coordinates are spread over (rows-1) and (cols-1) intervals; the four
neighbouring cells are interpolated with InterpSigned or InterpUnsigned. Result in A.

## B4A8 InterpSigned
Signed interpolation step used by the 3D lookups. [from name]

## B4AC InterpUnsigned
Unsigned interpolation step used by the 3D lookups. [from name]

## B4BB RescaleEngineRPM_MM
Converts engine RPM to the 3D-table column coordinate through RPMSCL (RPMRescaledfor3D). [from name]

## FACF ScaleYbyA
D = Y x A / 256 (unsigned fractional multiply). [from name]

## FC0E ScaleYbyD_resultD
D = Y x D / 256 style 16-bit fractional multiply used to chain fuel factors. [from name]

## FADF ScaleXbyB_addingA_intoD
Fractional multiply-accumulate helper used by the fuel modifier code. [from name]

## FBD5 ResetCOPTimer
Kicks the COP watchdog (writes $55, $AA to COPRST). [from name]

## E229 A2DAndStoreBatteryVolts_MM
Battery voltage A/D conversion and storage. [from name]

## E8DF ConvertMAPVoltsToValue
Converts the MAP sensor voltage to the internal MAP value. [from name]

## 8F58 StoreMAPVoltsAndCalcMAPValue
MAP sensor sampling (synchronised with engine position) and conversion. [from name]

## E85D HandleBaroReadRequirement_MM
Barometric pressure update: reads MAP as baro at key-on and at wide open throttle, low RPM. [from name]

## E4F7 CheckThrottleRoutine_MM
Throttle position processing: minimum-throttle learning (MINTHR), idle / WOT detection, TPS faults. [from name]

## FC69 CalculateVariableRevLimit_MM
Variable rev limiter (rev limit that depends on vehicle speed / TPS / MAP state). [from name]

## 552D ActuatorTestMode_MM
DRB actuator tests: drives relays, injectors, coils, AIS and solenoids on request. [from name]

## 4FDB DRBIISerialCommunications_MM
DRB II / SCI diagnostic protocol: fault codes, live data, memory read-out, special modes. [from name]

## 542C EraseErrorCodes
Clears all stored fault codes. [from name]

## 5B0A ThrowNonCriticalError
Records a fault from the descriptor at 0,Y (code number, counters, lamp behaviour). [from name]
