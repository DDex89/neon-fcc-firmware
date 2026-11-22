# B559-specific routine notes

Same format as annotations/routines.md, keyed by B559 addresses. An entry here replaces the
translated B4CC entry for the same routine.

## 8F58 StoreMAPVoltsAndCalcMAPValue
MAP sensor sampling (synchronised with engine position) and conversion. [from name]

B559 only ($9202-$9224): at reset it sets the purge delay PurgeDelayTimer ($021C) from the start
temperature (BatteryTemp, or AmbientAirTemp when CONFIG2 bit 5 is set). Colder than
PurgeDelayTempCold ($C983) gives $FFFF, colder than PurgeDelayTempWarm ($C984) gives PurgeDelayTime
($C985-$C986), warmer leaves no delay. [reviewed]

## 9CB4 ControlPurgeSolenoid_MM
Evaporative canister purge solenoid control. [from name]

B559 only ($9CF9-$9D1D): while PurgeDelayTimer is non-zero, BitFlags71 bit 7 and BitFlags65 bit 7 are
clear and the car is slower than MPHREF, the timer counts down once per Counter_MainLoop wrap and, if
purge has already been enabled (BitFlagsE3 bit 3), the purge calculation is skipped. Above MPHREF the
normal purge logic runs. Called from MainSubLoop (also in B4F3 and B4C2); B4CC has no call to this routine. [reviewed]

## B238 ExhGasRecirc_MM
EGR solenoid control: enables EGR within RPM, MAP, coolant and time windows. [reviewed]

Checks the conditions with the EGR21-EGR27 calibration constants (RPM window, MAP window
depending on baro, minimum coolant temperature, time since start) and switches the EGR solenoid.
Setting the thresholds to $FD/$FE keeps EGR permanently off (as Mopar did in 5007033).

B559 only ($B257-$B272): an extra temperature gate before the other checks. The temperature
(BatteryTemp, or AmbientAirTemp when CONFIG2 bit 5 is set) must be above EgrTempOn ($CB3C) to enable
EGR; once on, EGR stays on down to EgrTempOff ($CB3B). [reviewed]
