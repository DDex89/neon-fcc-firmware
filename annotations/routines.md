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
when knock sensing is disabled by BitFlags71 bit 7). The value feeds CalculateKnockRetard_MM.

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
the request bits in SubLoopRequests are scanned from bit 0 upward and the first set bit is cleared and its
routine is called, so the slower jobs are spread over consecutive passes. Finally it measures how
long the pass took (LoopTimeLast, worst case in LoopTimeWorst) and waits until TCNT reaches the next slot stored
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
  when BitFlags71 bit 1 requests it.
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

Not called: execution falls into this code from the end of CrankInterrupt_CalculateFuel, so the
running pulse width is computed once per cylinder event, at the 9 degree BTDC slot, from factors
that the main loop prepares every 10.75 ms.

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
Cranking fuel: pulse width from coolant temperature, engine position pulses, RPM and baro. [reviewed - data flow]

Runs in the main loop. Uses STRTFL (vs coolant, limited by STRLMT), STFTMP/STFTM2, EPPMUL (vs engine
position pulses since start), STFBAR (baro) and the RPM factors STFLID (closed throttle) / STFLOI
(open throttle): start fuel = [STRTFL^2 x (1 - STFBAR - STFTMP) x EPPMUL + BATOFF x 4] x 4 us. It also
sets Factor_StartFuelDecayIntoRunFuel from SFDCAY, applies the heat-soak correction
(AllowForHeatSoakAfterStall) and cuts fuel while the throttle is opened more than UNLOAD above MINTHR
("clear flood", ThrottleFlooredWhileStarting_UnloadFuel).

## 76A1 CalculateSumOfAllFuelModifiers_MM
Product of all slow fuel corrections, stored in SumOfFuelModifiers. [reviewed - partially]

Cold enrichment from the 3D tables CLDLDP (off idle) / CLDLDI (idle) and CURV3D (coolant x time since
start, with heat-soak correction after a stall), barometric compensation BAROCP, barometric
enrichment BARENR x BARMAP x BARRPM, charge-air temperature enrichment AIRTMP x AIRMAP x AIRRPM,
and the closed-loop/adaptive factor.

## 6D87 CalculatePartThrottleTransientFuel
Transient fuel: accelerator-pump style enrichment and deceleration lean-out. [reviewed - data flow]

Runs in the main loop. Compares MAP and TPS with their filtered averages (time constants AETIME,
THRTCN, LMAPTC, LOTIME vs coolant). A rise above MAPTRG / POSTRG (limited by MAPMAX / THRMAX) gives an
additive pulse Pulsewidth_PartThrottleEnrichment_HB = delta x AESLOP or POSSLP (vs coolant). A fall
gives the lean-out factors (LOTTHR, NEGSL2, triggers LOTTRG/LOTRG2/DECTRG with hysteresis, minimum
RPM LOTRPM) and inhibits the O2 controller for DCELTM afterwards. AIS motor steps also produce a
small enrichment or enleanment pulse (AISPL1/AISPL2/AISNLC) so idle mixture follows the air change.

## 72F8 CalculatePartThrottleEnrichmentAndLatency_MM
Throttle enrichment factor (part throttle / WOT) and injector latency. [reviewed - data flow]

Runs in the main loop. Chooses between the part-throttle map PTEADJ (RPM x MAPPTE) and the WOT map
WOTENR (RPM x MAPWOT) using the RPMMAP switch point, and moves ThrottleEnrichmentFactor towards the
target in steps (PTENRP / PTENRN engine pulses per step, PTENRD step size, PTENUM before returning to
the part-throttle spark map). It also looks up the injector latency InjectorLatencyPW from BATOFF vs
battery voltage.

## 704C ControlEngineCutout_MM
Fuel cut-off decisions: rev limiter, speed limiter, overboost/MAP and limp-mode limits. [from name]

Uses REVLMT5/REVLMT6 (normal rev limiter cut/restore), SPDLMH/SPDLML (speed limiter) and the limp-in
rev limits for a failed MAP or TPS sensor. The cut is applied per revolution
(ShutOffEngineForThisRotation).

## 8B38 HandleTransitionFromStartToRun
Blends cranking fuel into running fuel after the engine starts. [reviewed]

While the start flag (BitFlags71 bit 4) is set, the larger of the running pulse width and the
decaying start pulse width (InjectorPulsewidth_HB minus Factor_StartFuelDecayIntoRunFuel) is used.
When the decaying start pulse falls below the running value the flag is cleared and only running fuel
remains. Falls through into IncludeInjectorLatency.

## 689B TweakInjectorPW
Diagnostic override of the injector pulse width. [reviewed]

If calibration byte $D03E is non-zero and DebugRAM bit 2 is set (through the diagnostic link), the
computed pulse width is replaced by DebugTemp1 (a word, or a byte times 256 if bit 3 is set, then
halved). Normally the routine returns the value unchanged.

## 3997 DecideToUseDecelFuelCut
Decides whether deceleration fuel cut-off is allowed. [reviewed - data flow]

Requires closed-throttle deceleration with RPM between the DCLRPL / DCLRPH limits relative to the
target idle speed, coolant above DCLMCT and running time above DCLMER; sets the decel flags used by the
fuel code. Called from the AIS decel logic.

## 7832 AllowForHeatSoakAfterStall
Raises the effective coolant temperature after a short stall (RUNTMP vs time stopped, limited by RUNLMT). [reviewed]

## 4C69 DetermineRampCellFromRPMandMAP
Selects the O2 ramp cell: 3 RPM bands x 3 MAP bands, or the idle cell. [reviewed]

Closed throttle (neither BitFlags66 bit 6 nor BitFlags65 bit 7 set) selects the idle entry. Otherwise
two RPM breakpoints and two MAP breakpoints stored in the ramp table give cells 0-8; the result is
the offset of the cell's (rich kick, lean kick) pair in PRIRMP or SECRMP.

## 4D8B AdaptiveMemory_DetermineWhichCellApplies_MM
Selects the adaptive memory cell for the current operating point. [reviewed]

- Closed throttle and RPM below target idle + IDLOFS (+ HYTRPM hysteresis when already in an idle
  cell): idle cell 12, or cell 13 when BitFlags_AIS bit 3 is set (a second idle load state).
- Otherwise: six MAP bands separated by MP1..MP5 (hysteresis DLTMAP) times two RPM bands separated by
  R1 (hysteresis DLTRPM) give cells 0-11.
When the cell changes, BitFlags37 bit 7 is set so the controller restarts its averaging.

## A74B CalculateSparkAdvance_MM
Spark advance calculation (main loop). [reviewed]

Every fourth main-loop pass it counts down AdvanceDownCounter_A. Then BitFlags65 bit 7 (throttle
open / off idle - the same flag that selects the idle O2 cell) chooses the path:
- **off idle:** a temperature/charge correction is built first: BASADV (coolant temperature x
  MAPMOD) plus BASMAP x BASRPM plus BASMAP x BASCHG (charge-air temperature), saturated to a signed
  byte in Temp0. LookupNormalAdvance then adds the main map value;
- **idle (closed throttle):** CalculateIdleAdvance.
Both paths end in STORE_SPARK_ADV, which stores CalculatedSparkAdvance.

## A7AC CalculateIdleAdvance
Closed-throttle (idle) spark advance. [reviewed - data flow]

HOTMRP (RPM x MAP) plus the charge-air / MAP correction IDLIAT x ILDMAP, the coolant corrections
IDLADV / IDLAD2, and a closed-loop trim from the O2 feedback counter (ADO2C1 / ADO2C2, limits
ADO2CL / ADO2CH). The fast idle-speed spark corrections (HandleSparkScatter) are applied separately
in the crank interrupt.

## A8C8 LookupNormalAdvance
Off-idle advance: main map, vacuum adder, adaptive retard and the retard functions. [reviewed]

1. MaxAdvanceLookup = WOTMRP(RPM, MAPWOT(MAP)).
2. Wide open throttle (BitFlags65 bit 0): advance = WOTMRP + Temp0.
   Part throttle: advance = HOTMRP + ADOTFN(off-throttle enrichment timer) + Temp0; when MAP is at
   or above the RPMMAP switch point, MaxAdvanceLookup is lowered to this value if it is smaller.
3. ADVNGM adds advance from manifold vacuum relative to baro (when BitFlags66 bit 0 is set).
4. Adaptive retard: (ARRPM + ARMAP) scaled by AdaptiveRetardIndex -> AdaptiveRetardValue_A.
5. Falls into CheckForOtherRetardFactors: TPS retard (TPSRT1 without / TPSRT2 with adaptive retard,
   inside the MAPLMx / RPMRTx / TPSLMx windows), retard from vehicle speed (RETSPD) and the
   delta-RPM (surge) retard, then the minimum-advance clamp (CheckAndSetMinSparkAdvance).
Each addition saturates to a signed byte ($7F / $80).

## ACD9 CalculateKnockRetard_MM
Knock detection: compares the knock sample with the background average (main loop). [reviewed - data flow]

Knock is declared when KnockVolts exceeds the running average (CalculateAverageKnockVolts_SM) by
DLTKNK (vs RPM, MAP above KNKMAP and RPM above KNKRPM). The total retard is limited by RETMAX (vs
MAP). The per-cylinder retard itself is updated in the crank interrupt
(CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT: rate RTRDRT, recovery INCSRT, limit MAXRTD per cylinder) and
its sum also drives the knock enrichment of the fuel (KNNRCH).

## 8926 CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT
Per-cylinder knock retard update in the crank interrupt (part of the phase-3 code path). [reviewed - data flow]

Increases the retard of the cylinder that knocked at RTRDRT, lets it recover otherwise (INCSRT,
INNBNK / INNBSK factors) and limits it per cylinder with MAXRTD (vs MAP). This code shares the
crank-synchronous path with the running fuel calculation.

## AD7F CalculateAverageKnockVolts_SM
Running average of the knock sensor background level (window: KNAMAP, KNARPM, KNACLT ...). [from name]

## 56E7 CaculateChecksum
ROM self test: 8-bit sum of $1200-$B5FF and $B800-$FFFF must equal the byte at $B805. [reviewed]

The sum skips the $B600-$B7FF window of the internal EEPROM. $B805 is the last byte of the part
number in the calibration header, so the checksum is adjusted with a spare byte (usually $FF50)
whenever the calibration is modified. A mismatch is reported through ThrowNonCriticalError with the
fault descriptor at $D4F3 (code 53, internal controller failure). In 5269718 and 5007033 that descriptor is disabled
(flag bit 7 clear), so nothing is stored; the engine runs normally either way.

## 5FEF CountRamValuesFrom05to38
16-bit sum of RAM $0005-$0036 and $0100-$014D, used to validate RAM on a warm start. [reviewed]

## 48E7 HandleO2Processing_MM
Narrow-band O2 feedback: open/closed loop decision and the rich/lean ramp controller. [reviewed - data flow]

The controller kicks the mixture rich or lean (PRIRMP/SECRMP kick tables per RPM x MAP cell) until
the O2 sensor toggles; the secondary ramp also updates the adaptive memory cells. See
docs/en/closed_loop.md.

## 4CA9 AdaptiveMemory_UpdateCellIfRequired
Adaptive (learned) fuel correction: updates the current RPM/MAP cell (AutoCalCell0-12). [from name]

## 32E1 CalculateTargetIdleSpeed_MM
Target idle speed. [reviewed - data flow]

AISPN (park/neutral or manual) or AISCLD (drive, automatic only) vs coolant temperature, with time-
and load-dependent adders (decel airflow curve TIMED2 and further small tables), giving TargetIdleSpeedHB.

## 3514 ControlAIS_MM
Idle air control dispatcher: runs the AIS state in the low nibble of AISSubIndex. [reviewed]

Forces state 0 or 1 while the engine is not running (by RPM against BYTEc581) and state 15 on a
MAP sensor failure, then calls AISSubroutineTable[state]. The running states (4-6 and 12-14) are
chosen by SelectAisStateA/B. State list: docs/en/engine_control.md.

## 1563 AisDriveRoutine
Tail of Isr_TOC1_Periodic: one AIS stepper step and one frame on the SPI link to the I/O companion chip, then RTI. [reviewed]

Steps CurrentAisPosition one step towards DesiredNewAisPosition (not below BTVAIS battery volts,
not during CountdownTimerFromKeyOn), taking the phase command from the four bytes at $1200
($B1, $AA, $A3, $9C) and pacing with AisStepDelay. Without a step the command is $B8 (hold), or
$95 once after start. The command goes into LinkCommandByte. Then one frame is exchanged: a long
frame if LinkRequestFlags asks for one (bit 5 frame C, bit 7 CCD transmit, bit 6 register frame)
and no crank event is pending (TFLG1 IC1F), otherwise the 1-byte command frame. Every link byte
waits for $0400 bit 3 (ready) and is clocked by a pulse on $0402 bit 3. A header byte carries a
3-bit field in bits 3-5 and its complement in bits 0-2; the reply header is checked the same way.
Reply status (bits 0-2): 6 = sets BitFlags69 bit 1 (if battery volts are OK), 5 or 7 = sets
BitFlags69 bit 4. Errors go to LinkError. See docs/en/ccd_and_link.md.

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
Runs the DRB actuator test selected by ATMOffset (set by DRB command $13). [reviewed]

Called every main loop. Loads A = OutputDriverBits and B = OutputBits2, then jumps through
ATMFunctionTable with test number n using entry n-1 (the table base is loaded as $4EB9). Each test
toggles one output with Counter_MainLoop as the clock, so the output pulses at a few hertz. The test
ends when KeyOnOrEngineRunningTime reaches $99. Test numbers and outputs: docs/en/diagnostics.md.

## 4FDB DRBIISerialCommunications_MM
Receives DRB / SCI command bytes (7812.5 baud, BAUD = $22) and echoes each byte back. [reviewed]

A command byte $10-$25 is stored in DRBPointer1; DRBSerialToggles (indexed by command - $13) says
whether one or two parameter bytes follow (bit 5 / bits 4-5), which are stored in DRBPointer2 and
DRBPointer3. DRBIIOuput_MM then runs the handler. The routine also runs the alternate serial and
byte-mode download handlers first, and does nothing while a high-speed or download mode is active
(DRBSerialMode bits 6-7).

## 542C EraseErrorCodes
Clears all stored fault codes. [from name]

## 5A29 SendOutputDriverByte
Sends the relay/solenoid command byte to the SPI output driver and reads back its status. [reviewed]

Pulls $0403 bit 2 (chip select) low, writes OutputDriverBits to SPDR, waits for the transfer, releases the
chip select and stores the returned byte in OutputDriverStatus (the driver's fault status). OutputDriverBits bits:
0 A/C clutch relay, 3 radiator fan relay, 5 purge solenoid, 6-7 speed control solenoids (see
docs/en/io_map.md).

## 5B0A ThrowNonCriticalError
Reports a failed test for the fault descriptor at 0,Y; stores the fault when it has matured. [reviewed]

Descriptor (8 bytes at $D4E3 + index*8): index, maturing count, flash code, flags, bit mask, bitmap
offset, OBD-II code (BCD). Flags: bit7 enabled (when clear the routine returns at once with carry
clear), bit6 emission related, bit5 lamp request ($0070 bit7), bit4 always count, bit3 store at
once, bits 0-2 freeze frame priority. Faults that need maturing use one of two slots at $0054/$0055
with counters at $0056/$0057. A stored fault sets its bit at $0135 + offset, enters the list of the
last eight faults at $001B-$0022 and, if emission related, increments ObdDtcCount on first setting
and captures a freeze frame (CaptureFreezeFrame). Returns carry set when the fault was stored. See
docs/en/fault_codes.md.

## 5061 DRBIIOuput_MM
Dispatches the received DRB command: handler = DRBFunctionTable[command - $10]. [reviewed]

Waits until all parameter bytes have arrived (DRBSerialMode bits 4-5 clear). The command list is in
docs/en/diagnostics.md.

## EC86 CaptureFreezeFrame
Stores an OBD-II freeze frame for fault A at $011E-$0126 if its priority B is higher than the stored one. [reviewed]

Saves the fault index, $043B, MaxRPMxMaxMAPFraction (load), CoolantTempVolts, the O2 feedback
counter (short-term trim), ValueFromAdaptiveMemory (long-term trim), $0219, EngineRpm_HB and
VehicleSpeed_HB. The priority is kept in ISO_ErrBitStatus. EraseErorrCodes clears the frame.

## 9449 MonitorO2HeaterUp
OBD-II monitor: upstream O2 sensor heater (P0135). Status byte ObdMonStatus_O2HeaterUp. [reviewed - table entry]

Entry 0 of the OBD-II monitor table at $E939, run only by ObdMonitorScheduler. In this code base
the scheduler is never called, so this monitor does not run (see docs/en/diagnostics.md).

## 945E MonitorO2HeaterDown
OBD-II monitor: downstream O2 sensor heater (P0141). Status byte ObdMonStatus_O2HeaterDown. [reviewed - table entry]

Entry 1 of the OBD-II monitor table at $E939, run only by ObdMonitorScheduler. In this code base
the scheduler is never called, so this monitor does not run (see docs/en/diagnostics.md).

## 9881 MonitorO2Response
OBD-II monitor: upstream O2 sensor response (P0133). Status byte ObdMonStatus_O2Response. [reviewed - table entry]

Entry 2 of the OBD-II monitor table at $E939, run only by ObdMonitorScheduler. In this code base
the scheduler is never called, so this monitor does not run (see docs/en/diagnostics.md).

## 2F58 MonitorSecondaryAir
OBD-II monitor: secondary air system (P0411). Status byte ObdMonStatus_SecondaryAir. [reviewed - table entry]

Entry 3 of the OBD-II monitor table at $E939, run only by ObdMonitorScheduler. In this code base
the scheduler is never called, so this monitor does not run (see docs/en/diagnostics.md).

## A118 MonitorEvapPurgeFlow
OBD-II monitor: EVAP purge flow (P0441). Status byte ObdMonStatus_EvapPurge. [reviewed - table entry]

Entry 4 of the OBD-II monitor table at $E939, run only by ObdMonitorScheduler. In this code base
the scheduler is never called, so this monitor does not run (see docs/en/diagnostics.md).

## 428A MonitorCatalyst
OBD-II monitor: catalyst efficiency (P0422). Status byte ObdMonStatus_Catalyst. [reviewed - table entry]

Entry 5 of the OBD-II monitor table at $E939, run only by ObdMonitorScheduler. In this code base
the scheduler is never called, so this monitor does not run (see docs/en/diagnostics.md).

## 6A22 MonitorEgrFlow
OBD-II monitor: EGR flow (P0401). Status byte ObdMonStatus_Egr. [reviewed - table entry]

Entry 6 of the OBD-II monitor table at $E939, run only by ObdMonitorScheduler. In this code base
the scheduler is never called, so this monitor does not run (see docs/en/diagnostics.md).

## A337 MonitorFuelSystemRich
OBD-II monitor: fuel system rich (P0172). Status byte ObdMonStatus_FuelRich. [reviewed - table entry]

Entry 7 of the OBD-II monitor table at $E939, run only by ObdMonitorScheduler. In this code base
the scheduler is never called, so this monitor does not run (see docs/en/diagnostics.md).

## A55F MonitorFuelSystemLean
OBD-II monitor: fuel system lean (P0171). Status byte ObdMonStatus_FuelLean. [reviewed - table entry]

Entry 8 of the OBD-II monitor table at $E939, run only by ObdMonitorScheduler. In this code base
the scheduler is never called, so this monitor does not run (see docs/en/diagnostics.md).

## AE3F MonitorMisfire
OBD-II monitor: misfire (P0300-P0304). Status byte ObdMonStatus_Misfire. [reviewed - table entry]

Entry 9 of the OBD-II monitor table at $E939, run only by ObdMonitorScheduler. In this code base
the scheduler is never called, so this monitor does not run (see docs/en/diagnostics.md).

## E9C5 ObdMonitorScheduler
Runs the ten OBD-II monitors from the table at $E939. Not called anywhere in this code base. [reviewed]

Table: 10 records of 14 bytes from $E939 to $E9C4: +0 monitor routine, +2 status byte in RAM
($010E-$0119), +4 pointer to a scheduling mask ($E931-$E937, tested against Counter_MainLoop), +6
fault descriptor, +8/+10/+12 calibration pointers of three enable conditions (evaluated by
CalculateSomething; the results go to ObdStatusFlags bits 0-1). A monitor runs when its status
byte has bit 7 set and the mask allows this pass; when it sets bit 6 the scheduler sets bit 1 and
calls LEABA. After the loop it runs LED24, LEDAD, LEDD0, LEED3, LEE14 and LEFD1. No JSR, JMP or
pointer anywhere in the ROM reaches $E9C5, so in 5269718 and 5007033 the whole monitor set is
dormant even though ObdMonitorInit prepares the status bytes.

## E8EA ObdMonitorInit
Prepares the status bytes of the ten OBD-II monitors (table at $E939). [reviewed]

For each record: clears bit 2 of the status byte, clears bits 0, 3 and 6 (the two heater monitors
keep them if bit 6 is set) and sets bit 7 when the monitor's fault descriptor is enabled. Then it
clears ObdStatusFlags bits 0-6 and bit 7 of $0130 and $012C. Called from
StoreMAPVoltsAndCalcMAPValue.

## 3593 AisState_Unused
States 2, 3 and 7-11: not used; clear the state nibble back to state 0. [reviewed - data flow]

## 359A AisState0_EngineStopped
State 0, key on with the engine stopped: holds BYTEc580 + CALPOS (with BaroAISComp); moves to state 1 once RPM reaches BYTEc581. [reviewed - data flow]

## 35AD AisState1_Cranking
State 1, cranking / start: AISTRT (coolant temperature) + CALPOS with baro compensation; hands over to the running states through SelectAisStateA when the motor has reached its target. [reviewed - data flow]

## 35FE AisState4_ThrottleOpen
State 4, throttle open: position from CalculateAISPosition3 (speed MPHPOS, RPM RPMPOS, 3D table, cold CLDPOS, throttle THRPOS). [reviewed - data flow]

## 3864 AisState5_ClosedThrottle
State 5, throttle closed: closed-loop idle speed control (CalculateAisPosition1), A/C compensation, decel fuel cut decision, load steps. [reviewed - data flow]

## 3EB1 AisState6_SpeedControl
State 6, speed control active (BitFlags66 bit 6, set by ControlCruiseServo1_MM). [reviewed - data flow]

## 367D AisState12_ThrottleOpen
State 12: as state 4, and applies the load-step records (AdjustAISPosition_A/B). [reviewed - data flow]

## 38CE AisState13_ClosedThrottle
State 13: as state 5, with the load-step records. [reviewed - data flow]

## 3F16 AisState14_SpeedControl
State 14: as state 6, with the load-step records. [reviewed - data flow]

## 35EB AisState15_MapLimpIn
State 15, MAP sensor failure (b58_IPL1 bit 5 or 7, set by VerifyOperationOfMapSensor_MM): fixed position of $20 steps, load flags cleared. [reviewed - data flow]

## 4192 SelectAisStateA
Picks the running AIS state from the set 12-14 and stores it in the low nibble of AISSubIndex. [reviewed]

12 when BitFlags68 bit 5 is set, 14 when speed control is active (BitFlags66 bit 6), 13 with the
throttle closed (BitFlags65 bit 7 clear). With the throttle open: 13 if SwitchInputs bit 6 is set
and RPM is above TABLEc681(TPS), otherwise 12.

## 41C4 SelectAisStateB
Same as SelectAisStateA, but picks from the set 4-6. [reviewed]

The running state routines call A when AisLoadFlagsA equals AisLoadFlagsB and B when they
differ.

## 41F6 AdjustAISPosition_A
Applies one AIS load-step record (X): adds the step returned by the record's getter. [reviewed]

Record (10 bytes, eight of them at $37DE-$382D): +0 value that A must match, +1 mask of
AisLoadFlagsA|B bits that block the step, +2 mask of bits that must already be set, +3 bits to
set in AisLoadFlagsA, +4 getter routine (returns the step in A, $382E-$3863), +6 calibration byte
added to the scaled position, +8 RAM result (always $01C8). The step is added to
DesiredNewAisPosition, limited by AISHLM. Returns carry set when the record applied.

## 4241 AdjustAISPosition_B
Same as AdjustAISPosition_A but removes the step and clears the +3 bits in AisLoadFlagsA. [reviewed]

## 3F15 Dead_3F15
Lone RTS just before AisState14_SpeedControl; nothing references it (dead). [reviewed]

## 5B01 Dead_5B01
Short delay loop (Y = 7); nothing references it (dead). [reviewed]

## 68BD Dead_68BD
Lone RTS; nothing references it (dead). [reviewed]

## FBC6 Dead_FBC6
JMP back into the serial wait loop; nothing references it (dead). [reviewed]

## 1788 CCDBusComs
Sends the prepared CCD message (CcdTxHeader, CcdTxId, CcdTxData1/2) to the link chip and reads the received CCD message back. [reviewed]

5-byte frame: header ($D0 = transmit, $D8 = nothing to send, with the low 3 bits of
LinkCommandByte), ID, two data bytes, complement of the sum. The reply (LinkReplyHeader, CcdRxId,
CcdRxData1, CcdRxData2, checksum) is checked; bits 6-7 of the reply header go to LinkStatusFlags
bits 2-3 and LinkStatusFlags bit 7 is set (a message was received).

## 187F LinkSendRegisterFrame
Writes a 16-bit register of the link chip and reads one back: header LinkRegAddress ($48, $50 or $58), data LinkRegDataOut. [reviewed]

4-byte frame (header, two data bytes, complement of the sum). The reply goes to LinkRegDataIn.
Sets LinkStatusFlags bit 6, which LinkRegisterUpdate then processes. Also clears LinkRequestFlags
bit 2 unless one of the O2 heater monitors is active.

## 16B7 LinkSendFrameC
Third long frame type: header LinkFrameCHeader, data LinkFrameCData1/2; reply into LinkFrameCReply1/2. [reviewed]

Requested by LinkRequestFlags bit 5 (set in CODE1265). Purpose not decoded.

## 1961 LinkError
Error exit of the link exchange: flushes the SPI, raises PD5 and counts LinkRetryCount down. [reviewed]

After ten failed exchanges in a row it pulses $0409 bit 3 low, which most likely resets the link
chip, and clears $00F2 and LinkFrameCHeader.

## 58A1 LinkRegisterUpdate
Processes the reply of a register frame and prepares the next one. [reviewed]

The reply is decoded against LinkRegLastAddress (the header of the frame before, the chip answers
one frame late): $48 gives the switch input byte (SwitchInputs), $50 a 16-bit input word
(LinkInputWordHi/Lo). Then the header cycles $50 (data OutputBits2/$00EF), $58 ($0176/$0177) and
$48 ($00EC, 0), and LinkRequestFlags bit 6 is set. Original name
ErrorCodeProcessingSomething_MM.

## 45D2 PrepareCCDDataForXmit_MM_1
Builds the next CCD message from the 128-slot schedule CCDDataStream_1 (index CcdTxSlot). [reviewed]

The first message after start is $E0 with zero data. Each slot routine stores header and ID in
CcdTxHeader/CcdTxId and returns the two data bytes in D. Sets LinkRequestFlags bit 7 so the next
TOC1 tick sends the frame. Message list: docs/en/ccd_and_link.md.

## 4602 PrepareCCDDataForXmit_MM_2
Handles a received CCD message: calls CCDDataStream_2[CcdRxId & $0F]. [reviewed]

Handlers exist for low nibbles 1 (CcdRx_1), 4 (CcdRx_4) and 8 (CcdRx_8). Afterwards, if the
theft alarm is not disabled (CONFIG bit 2), it runs CCD_HandleAlarm.

## 4703 CcdRx_1
Received CCD message with ID low nibble 1: sets CCDFlags5 bit 6 (and CCDFlags4 bit 4 unless CCDFlags6 bit 7). Used by the theft alarm logic. [reviewed]

## 4710 CcdRx_4
Received CCD message with ID low nibble 4: stores data byte 1 in CcdRxValueA and restarts the CCD time-out (CcdRxTimeout). [reviewed]

Set_ErrorBits_3_MM counts CcdRxTimeout up; at $75 it reports code 66 (no CCD messages).

## 4728 CcdRx_8
Received CCD message with ID low nibble 8: stores data byte 1 in CcdRxValueB. [reviewed]

## 4629 CCD_HandleAlarm
Vehicle theft alarm logic over CCD, kept in EEPROM4 bits 0-1. [reviewed - data flow]

Runs only when the alarm is not disabled by CONFIG bit 2. Counts in CCDFlags6 and arms or disarms
using the messages handled by CcdRx_1.

## 476E CCD_EngineRPM
CCD message $E4: EngineRpm_HB, MapValue. [reviewed]

## 4785 CCD_CoolantTemp
CCD message $8C: CoolantTemp, AmbientAirTemp. [reviewed]

## 4791 CCD_BatVolts
CCD message $D4: battery volts and target battery volts (scaled). [reviewed]

## 47BE CCD_ThrottlePos
CCD message $42: TPSOverMINTHR, cruise set speed / 2. [reviewed]

## 47CB CCD_Baro
CCD message $54: BaroPressure, ChargeTemp. [reviewed]

## 47D7 CCD_VehicleSpeed
CCD message $24: vehicle speed in two scalings. [reviewed]

## 47F5 CCD_ToggleFlags
CCD message $EC: fault and warning flags (from b58_IPL1, IPL1, CCDFlags4) and CCDCF3 bits. [reviewed]

## 4836 CCD_SwitchState
CCD message $A4: cruise, P/N, A/C clutch, check-engine lamp state and cruise status bits. [reviewed]

## 48C7 CCD_EEPromData
CCD message $CC: EEPROM1 and TargetIdleSpeedHB, both scaled by 4. [reviewed]

## 477A CCD_ConfigConst1
CCD message $AC: calibration word CCDCFG. [reviewed]

## 4767 CCD_Blank
CCD message $D8 header: nothing (empty slot). [reviewed]

## 1E18 IsoValidateRequest
Checks a received SAE J1979 request in the buffer at $048E: header $68 $6A $Fx, sum checksum, service and length. [reviewed]

Service 1: PID table at $1AEA (PIDs $00-$15, PID $12 only with CONFIG2 bit 5). Service 2: table
at $1B16 (PIDs $00-$0C), frame 0 only. Service 3: only when ObdDtcCount is not zero. Service 4:
only with the engine stopped. Service 5: test IDs for O2 sensors 1 and 2. Returns carry set when
the request is valid.

## 1EEB IsoBuildResponse
Builds the J1979 response (header $48 $6B $40) for the service in the request and runs the PID handler. [reviewed]

Service 4 calls EraseErrorCodes. See docs/en/diagnostics.md.

## 21CF ObdPid00_Supported
Service 1 PID $00: supported PIDs $BE $3E $B8 $00 (PID $12 added with CONFIG2 bit 5). [reviewed]

## 21F4 ObdPid01_MonitorStatus
Service 1 PID $01: DTC count with the MIL bit (ObdStatusFlags bit 7), monitor support from calibration bytes $B81F/$B820 and completion from $0100. [reviewed]

## 2221 ObdPid03_FuelSystem
Service 1 PID $03: FuelSystemStatus. [reviewed]

## 2232 ObdPid04_Load
Service 1 PID $04: MaxRPMxMaxMAPFraction. [reviewed]

## 223E ObdPid05_Coolant
Service 1 PID $05: coolant temperature (CoolantTempVolts - $58). [reviewed]

## 224F ObdPid06_ShortTermTrim
Service 1 PID $06: short-term fuel trim from the O2 feedback counter. [reviewed]

## 2261 ObdPid07_LongTermTrim
Service 1 PID $07: long-term fuel trim (ValueFromAdaptiveMemory). [reviewed]

## 2273 ObdPid0B_Map
Service 1 PID $0B: MAP ($0219 × $69 / 256). [reviewed]

## 2284 ObdPid0C_Rpm
Service 1 PID $0C: engine RPM. [reviewed]

## 2290 ObdPid0D_Speed
Service 1 PID $0D: vehicle speed. [reviewed]

## 22A7 ObdPid0E_Advance
Service 1 PID $0E: spark advance (AdvanceTemporary + $80). [reviewed]

## 22B5 ObdPid0F_IntakeAirTemp
Service 1 PID $0F: charge air temperature (ChargeTempVolts - $58). [reviewed]

## 22C6 ObdPid11_Throttle
Service 1 PID $11: LastTpsVolts. [reviewed]

## 22D2 ObdPid12_SecondaryAir
Service 1 PID $12: secondary air status from OutputDriverBits bit 5 (1 or 4). [reviewed]

## 22E5 ObdPid13_O2Present
Service 1 PID $13: O2 sensors present, fixed $03 (bank 1 sensors 1 and 2). [reviewed]

## 22F0 ObdPid14_O2Sensor1
Service 1 PID $14: upstream O2 voltage. [reviewed]

## 231D ObdPid15_O2Sensor2
Service 1 PID $15: downstream O2 voltage. [reviewed]

## 234A ObdFfPid00_Supported
Service 2 PID $00: supported freeze frame PIDs. [reviewed]

## 672B InitPeripheralRegisters
Initialises HC11 peripherals and the I/O device registers. [reviewed]

HC11: DDRD = $3A, OC1M = 0, TCTL2 = $1A, SPCR = $54 (SPI master, CPHA = 1, E/2 = 1 MHz), SCCR1/2 =
$00/$0C, OPTION = $B9, HPRIO = $2B. I/O device: clears $0402 bits 4 and 6, $0403 bits 4-7, $0404,
$040B, $040C and $040F bits 4-7; $0407 = $1B, $0408 bits 4-7 set, $040A bits 0/1/3/4 set and
2/5/7 cleared, $040D = $33. The meaning of the device registers is not known.

## 84F6 CrankMapRpmUpdate
Crank-synchronous update: converts the MAP sample to MapValue and computes engine RPM from the period between edges. [reviewed - data flow]

Called with A = previous MAP volts (averaged with MapVolts). Keeps the last three RPM values in
RpmHistory0-2 and the previous period in CrankPeriodPrev, which the (dormant) misfire monitor uses.
RPM = RpmScaleA/B (or calibration $CB94/$CB96 when SyncFlags74 bit 0 is set) divided by the period.
Original name GET_AVERAGE_MAP_READING.

