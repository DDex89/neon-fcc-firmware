# Карта ОЗУ

Генерируется `tools/gen_ram_docs.py`; не редактируйте вручную. Имена берутся из `annotations/ram_symbols.json` (имена вида `Lxxxx` пока неизвестны). **R** и **W** — число инструкций, которые читают и пишут адрес (16-битное обращение считается для обоих байтов); в списках показано до пяти подпрограмм. Обращения через индексный регистр (например, `ldx #$0135`, затем `brset 6,x`) не учитываются, так что малый счёт не значит, что адрес не используется.

Соглашения об именах: описательное имя значит, что смысл известен. `Владелец_xxxx` (например, `MonEvap_0205`, `Iso_0489`) — внутреннее состояние одной подпрограммы или модуля, смысл которого не расшифрован; `Var_xxxx` — переменная, общая для нескольких несвязанных подпрограмм; `BitFlagsxx` — байт, с которым работают только (или в основном) битовыми командами; `Unref_xxxx` — прямых обращений в коде нет. Строки без имени — младшие байты, к которым обращаются только 16-битной командой через предыдущий адрес.

Всего адресов: 657, с именами: 614; временных имён (`Lxxxx`) осталось: 0.

## ОЗУ прямой страницы ($0000-$00FF)

| Адрес | Имя | R | W | Читают | Пишут |
|---|---|---|---|---|---|
| `$0000` | `BYTE00` | 1 | 2 | Trap_IRQ | ResetInterrupt, Trap_IRQ |
| `$0001` | `BYTE01` | 0 | 2 |  | ResetInterrupt, Trap_IRQ |
| `$0002` | `BYTE02` | 0 | 2 |  | ResetInterrupt, Trap_IRQ |
| `$0003` | `BYTE03` | 5 | 3 | ResetInterrupt, StoreMAPVoltsAndCalcMAPValue, Trap_IRQ | GetControlFeedback_DetermineIfShutdownRequired_MM, MainSubLoop, ResetInterrupt |
| `$0004` | `BYTE04` | 6 | 3 | ResetInterrupt, StoreMAPVoltsAndCalcMAPValue, Trap_IRQ | GetControlFeedback_DetermineIfShutdownRequired_MM, MainSubLoop, ResetInterrupt |
| `$0005` | `MINTHR_LowestSessionTPS` | 19 | 7 | CODE2d7b, CODE6b1d, CalculateInjectorPulsewidthForStarting_MM, CalculateKnockRetard_MM, CheckErrorMaskingAndSetCodes_MM … | CheckThrottle_AtFullThrottle, CheckThrottle_ErrorAlreadyFlagged, CheckThrottle_VehicleSpeedStillAboveDecelIdle, DRB_Special2, ResetInterrupt |
| `$0006` | `AverageKnockVolts` | 3 | 3 | CalculateAverageKnockVolts_SM, CalculateKnockRetard_MM | CalculateAverageKnockVolts_SM, ResetInterrupt |
| `$0007` | *без имени* | 2 | 3 | CalculateAverageKnockVolts_SM | CalculateAverageKnockVolts_SM, ResetInterrupt |
| `$0008` | `Timer_DacalCountdown` | 4 | 2 | AIS_Subroutine_12, AisState14_SpeedControl, CalculateAisPosition1, CalculateAisPosition2 | AIS_Subroutine_12, ResetInterrupt |
| `$0009` | `CurrentAisPosition` | 8 | 6 | AIS_Subroutine_12, AisDriveRoutine, AisState1_Cranking, CalculateAisPosition2, MonitorEvapPurgeFlow … | AIS_Subroutine_12, AisDriveRoutine, DRB_Special2, ResetInterrupt |
| `$000A` | `BitFlags_AIS` | 38 | 16 | AIS_Subroutine_12, AdaptiveMemory_DetermineWhichCellApplies_MM, AisDriveRoutine, AisState12_ThrottleOpen, AisState13_ClosedThrottle … | AisDriveRoutine, CODEe72a, CODEe74f_MM, CalculateIdleAdvance, DRB_Special2 … |
| `$000B` | `AsdVolts_000B` | 4 | 2 | CODE7242_SM, CheckStuffAndSetStatusFlags_SM | CODE7242_SM |
| `$000C` | `Var_000C` | 2 | 2 | CheckStuffAndSetStatusFlags_SM, Interrupt_SpeedometerSignal | CheckStuffAndSetStatusFlags_SM, Interrupt_SpeedometerSignal |
| `$000D` | `AutoCalCell0` | 0 | 0 |  |  |
| `$000E` | `AutoCalCell1` | 0 | 0 |  |  |
| `$000F` | `AutoCalCell2` | 0 | 0 |  |  |
| `$0010` | `AutoCalCell3` | 0 | 0 |  |  |
| `$0011` | `AutoCalCell4` | 1 | 0 | CCD_SwitchState |  |
| `$0012` | `AutoCalCell5` | 0 | 0 |  |  |
| `$0013` | `AutoCalCell6` | 0 | 0 |  |  |
| `$0014` | `AutoCalCell7` | 0 | 0 |  |  |
| `$0015` | `AutoCalCell8` | 0 | 0 |  |  |
| `$0016` | `AutoCalCell9` | 0 | 0 |  |  |
| `$0017` | `AutoCalCell10` | 0 | 0 |  |  |
| `$0018` | `AutoCalCell11` | 0 | 0 |  |  |
| `$0019` | `AutoCalCell12idle` | 2 | 0 | IncludeCylTrimWithAdaptiveCells |  |
| `$001A` | `AutoCalCellEnd` | 1 | 1 | IncludeCylTrimWithAdaptiveCells | IncludeCylTrimWithAdaptiveCells |
| `$001B` | `FaultList0` | 0 | 1 |  | EraseErrorCodes |
| `$001C` | `FaultList1` | 0 | 1 |  | EraseErrorCodes |
| `$001D` | `FaultList2` | 0 | 1 |  | EraseErrorCodes |
| `$001E` | `FaultList3` | 0 | 1 |  | EraseErrorCodes |
| `$001F` | `FaultList4` | 0 | 1 |  | EraseErrorCodes |
| `$0020` | `FaultList5` | 1 | 1 | UpdateErrorTimersAndPossiblyClearErrors_MM | EraseErrorCodes |
| `$0021` | `FaultList6` | 3 | 2 | ThrowNonCriticalError, UpdateErrorTimersAndPossiblyClearErrors_MM | EraseErrorCodes, ThrowNonCriticalError |
| `$0022` | `FaultList7` | 3 | 2 | ThrowNonCriticalError, UpdateErrorTimersAndPossiblyClearErrors_MM | EraseErrorCodes, ThrowNonCriticalError |
| `$0023` | `ErrorCodeUpdateKeyOnCount` | 4 | 4 | MUCK_WITH_CEL, ThrowNonCriticalError, UpdateErrorTimersAndPossiblyClearErrors_MM | EraseErrorCodes, ThrowNonCriticalError, UpdateErrorTimersAndPossiblyClearErrors_MM |
| `$0024` | `ErrorCodeUpdateKeyOnCount2` | 1 | 3 | UpdateErrorTimersAndPossiblyClearErrors_MM | EraseErrorCodes, ThrowNonCriticalError, UpdateErrorTimersAndPossiblyClearErrors_MM |
| `$0025` | `ErrorCodeUpdateKeyOnCount3` | 1 | 2 | UpdateErrorTimersAndPossiblyClearErrors_MM | EraseErrorCodes, UpdateErrorTimersAndPossiblyClearErrors_MM |
| `$0026` | `Cyl2_InjPWTrim` | 11 | 1 | AdaptiveMemory_UpdateCellIfRequired, DetermineIndividualInjectorTrims_MM, IncludeCylTrimWithAdaptiveCells, MonitorFuelSystemRich | DRB_Special2 |
| `$0027` | `Cyl1_InjPWTrim` | 10 | 1 | AdaptiveMemory_UpdateCellIfRequired, FindCyl1Trim, IncludeCylTrimWithAdaptiveCells, MonitorFuelSystemRich | DRB_Special2 |
| `$0028` | `Cyl3_InjPWTrim` | 10 | 1 | AdaptiveMemory_UpdateCellIfRequired, FindCyl3Trim, IncludeCylTrimWithAdaptiveCells, MonitorFuelSystemRich | DRB_Special2 |
| `$0029` | `CylTrimFlags` | 12 | 14 | ControlPurgeSolenoid_MM, DetermineIndividualInjectorTrims_MM, FindCyl1Trim, FindCyl3Trim, IncludeCylTrimWithAdaptiveCells … | ControlPurgeSolenoid_MM, DRB_Special2, DetermineIndividualInjectorTrims_MM, FindCyl1Trim, FindCyl3Trim … |
| `$002E` | `Counter_SpeedSensorInterrupt` | 2 | 2 | Interrupt_SpeedometerSignal | Interrupt_SpeedometerSignal |
| `$002F` | *без имени* | 2 | 2 | Interrupt_SpeedometerSignal | Interrupt_SpeedometerSignal |
| `$0030` | `AdaptiveRetardIndex` | 6 | 3 | CODE8235, CalculateInjectorPulsewidthForEngineRunning, CalculateKnockRetard_MM, CheckForOtherRetardFactors, DecrementAdaptiveRetardFactor … | CODE8235, CalculateKnockRetard_MM, DecrementAdaptiveRetardFactor |
| `$0031` | `AISCounterIndex` | 3 | 1 | AisDriveRoutine | AisDriveRoutine |
| `$0032` | `PointlessFuelFactor` | 2 | 1 | CCD_BatVolts, DetermineTargetBatteryVoltage_MM | DRB_SomethingLikeEMR_MM |
| `$0033` | `BaroPressure` | 33 | 3 | AisState14_SpeedControl, CCD_Baro, CODEf101, CalculateInjectorPulsewidthForStarting_MM, CalculateMaxRPMxMaxMAPFraction_MM … | ResetInterrupt, SaveBaroPressure, StoreMAPVoltsAndCalcMAPValue |
| `$0034` | `AISSubIndex` | 4 | 5 | AisState_Unused, ControlAIS_MM, SelectAisStateA, SelectAisStateB | AisState0_EngineStopped, AisState_Unused, ControlAIS_MM, SelectAisStateA, SelectAisStateB |
| `$0035` | `WarmupCycleCount` | 2 | 5 | ObdAutoClearCodes, ObdWarmupCycleCheck | EraseErrorCodes, ObdAutoClearCodes, ObdProcessMonitorResult, ObdWarmupCycleCheck, ThrowNonCriticalError |
| `$0036` | `BitFlags36` | 3 | 4 | StoreVariableRevLimit, TPSandMAP_OK, TurnOnVariableRevLimitNow | StoreMAPVoltsAndCalcMAPValue, StoreVariableRevLimit, TurnOffVariableRevLimit, TurnOnVariableRevLimitNow |
| `$0037` | `BitFlags37` | 8 | 8 | AdaptiveMemory_UpdateCellIfRequired, ClearO2SensorFeedbackCounterSigned_MM, ControlPurgeSolenoid_MM, MonitorEvapPurgeFlow, MonitorO2Response … | ControlPurgeSolenoid_MM, ONTHROTTLE_OR_RPMTOOHIGHFORIDLE |
| `$0038` | `EngineRunningTimeMaxFF` | 6 | 1 | ClearO2SensorFeedbackCounterSigned_MM, IncrementBatteryVoltsOKCounter_MM, IncrementLoopCounters_MM, ObdTripEndLogic, ShutDownSubroutineA | IncrementLoopCounters_MM |
| `$0039` | `Var_0039` | 7 | 3 | CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency, ScheduleIgnitionCoils, StoreMAPVoltsAndCalcMAPValue | IncludeInjectorLatency, ScheduleIgnitionCoils, StoreMAPVoltsAndCalcMAPValue |
| `$003A` | `OutputDriverBits` | 26 | 45 | AIS_Subroutine_12, ATM_ACClutchRelay, ATM_AllSolenoidsRelays, ATM_FanRelay, ActuatorTestMode_MM … | AC_Rout2, AC_Rout5, AC_Rout7, ATM_ACClutchRelay, ATM_ASDRelay … |
| `$003B` | `Var_003B` | 2 | 1 | SendOutputDriverByte | SendOutputDriverByte |
| `$003C` | `CCDFlags3` | 1 | 1 | CODEf101 | SendOutputDriverByte |
| `$003D` | `CruiseStatus_1` | 31 | 19 | CODEf101 | CODEf101, StoreMAPVoltsAndCalcMAPValue |
| `$003E` | `CruiseStatus_2` | 9 | 16 | CODEf101 | CODEf101 |
| `$003F` | `Counter_Cruise_1` | 1 | 18 | CODEf101 | CODEf101, StoreMAPVoltsAndCalcMAPValue |
| `$0040` | `Cruise_0040` | 2 | 1 | ControlCruiseServo0_MM | ControlCruiseServo0_MM |
| `$0041` | `StartupSwitchMirror1` | 13 | 17 | CCD_SwitchState, CODEf0b8, CODEf0c1, CODEf0cd, CODEf0d9 … | CODEf0b0, CODEf0b8, CODEf0c1, CODEf0cd, CODEf0d9 … |
| `$0042` | `Counter_Cruise` | 2 | 8 | CODEf101 | CODEf101 |
| `$0043` | `Counter_TimerRegHalfOverflowBetweenSpeedoPulses` | 4 | 4 | DetermineNumberOfOverflowsBetweenSpeedoPulses_MM, Interrupt_SpeedometerSignal | DetermineNumberOfOverflowsBetweenSpeedoPulses_MM, Interrupt_SpeedometerSignal, StoreMAPVoltsAndCalcMAPValue |
| `$0044` | `PreviousVehicleSpeed_HB` | 3 | 1 | DetermineNumberOfOverflowsBetweenSpeedoPulses_MM, Interrupt_SpeedometerSignal | Interrupt_SpeedometerSignal |
| `$0045` | *без имени* | 3 | 1 | DetermineNumberOfOverflowsBetweenSpeedoPulses_MM, Interrupt_SpeedometerSignal | Interrupt_SpeedometerSignal |
| `$0046` | `TimerOverflowsBetweenSpeedoPulses` | 4 | 4 | CODEf101, DetermineNumberOfOverflowsBetweenSpeedoPulses_MM, Interrupt_SpeedometerSignal | DetermineNumberOfOverflowsBetweenSpeedoPulses_MM, Interrupt_SpeedometerSignal, StoreMAPVoltsAndCalcMAPValue |
| `$0047` | `SpeedoSensorPulsewidth_HB` | 2 | 1 | Interrupt_SpeedometerSignal | Interrupt_SpeedometerSignal |
| `$0048` | *без имени* | 2 | 1 | Interrupt_SpeedometerSignal | Interrupt_SpeedometerSignal |
| `$0049` | `VehicleSpeed_HB` | 62 | 3 | AC_Rout11, AC_Rout8, AIS_Subroutine_12, CCD_VehicleSpeed, CODE1265 … | CODE1265, CODEf101, Interrupt_SpeedometerSignal |
| `$004A` | `VehicleSpeed_LB` | 45 | 3 | AC_Rout11, AC_Rout8, CCD_VehicleSpeed, CODE1265, CODE2609 … | CODE1265, CODEf101, Interrupt_SpeedometerSignal |
| `$004B` | `VehicleSpeedScaled` | 22 | 3 | CODEf101, CalculateAISPosition3, CheckErrorMaskingAndSetCodes_MM, CheckThrottle_AtIdle, ControlCruiseServo1_MM … | CODE1265, CODEf101, Interrupt_SpeedometerSignal |
| `$004C` | `Counter_Cruise_2` | 3 | 5 | CODEf101 | CODEf101 |
| `$004D` | `Counter_Cruise_3` | 5 | 7 | CODEf101 | CODEf101 |
| `$004E` | `CruiseSpeedSetpoint` | 17 | 8 | CCD_ThrottlePos, CODEf101 | CODEf101 |
| `$004F` | `CruiseControlVar0` | 3 | 9 | CODEf101 | CODEf101 |
| `$0050` | `CruiseControlVar1` | 2 | 2 | CODEf101 | CODEf101 |
| `$0051` | `CruiseControlVar2` | 1 | 3 | CODEf101 | CODEf101 |
| `$0052` | `CruiseControlVar3` | 8 | 5 | CODEf101 | CODEf101 |
| `$0053` | `CruiseControlVar4` | 3 | 4 | CODEf101 | CODEf101 |
| `$0054` | `FaultMaturingSlot0` | 3 | 1 | CheckErrorMaskingAndSetCodes_MM, OutputErrorBits, UpdateErrorTimersAndPossiblyClearErrors_MM | UpdateErrorTimersAndPossiblyClearErrors_MM |
| `$0055` | `FaultMaturingSlot1` | 3 | 1 | CheckErrorMaskingAndSetCodes_MM, OutputErrorBits, UpdateErrorTimersAndPossiblyClearErrors_MM | UpdateErrorTimersAndPossiblyClearErrors_MM |
| `$0056` | `FaultMaturingCount0` | 0 | 1 |  | UpdateErrorTimersAndPossiblyClearErrors_MM |
| `$0057` | `FaultMaturingCount1` | 0 | 1 |  | UpdateErrorTimersAndPossiblyClearErrors_MM |
| `$0058` | `b58_IPL1` | 67 | 12 | AisState15_MapLimpIn, CCD_ToggleFlags, CODE2aeb, CODE2bd7, CODE2c0d … | CODE59ea, CheckErrorMaskingAndSetCodes_MM, CheckThrottle_BadTpsSignal, EraseErrorCodes, FurtherMAPAndBaroDiagnostics2_SM … |
| `$0059` | `b59_IPL2` | 11 | 10 | CODE8059_MM, CalculateKnockRetard_MM, CheckErrorMaskingAndSetCodes_MM, DetectAlternatorFault_MM, EmmissionMaintenanceRemider2_MM … | CODE59fd, CODE5a0c, CODE8059_MM, DetectAlternatorFault_MM, EmmissionMaintenanceRemider2_MM … |
| `$005A` | `b5a_IPL3` | 14 | 13 | CODE8059_MM, CheckErrorMaskingAndSetCodes_MM, CrankInterrupt_CalculateFuel, IncrementOrClearDiagFaultCounter_SM, IncrementOrClearNormalOpCounter_SM … | CODE59c2, CODE5ad6, CODE8059_MM, CcdRx_4, EraseErrorCodes … |
| `$005B` | `Var_005B` | 3 | 4 | ProcessErrorBits_WorkWithData_MM | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CrankMapRpmUpdate, ProcessErrorBits_WorkWithData_MM, ScheduleIgnitionCoils |
| `$005C` | `ERRORCODERESETTIMERIN_UN_ERRORCODEIN_LN_VAR` | 3 | 3 | ResetErrorCodeIfTimerExpired, UpdateErrorTimersAndPossiblyClearErrors_MM | ResetErrorCodeIfTimerExpired, SELECT_ERROR_BIT_POSITION_ROUT, UpdateErrorTimersAndPossiblyClearErrors_MM |
| `$005D` | `TimerOverflowsBetweenCamPulses` | 28 | 3 | CODE8235, CODEf101, CalculateSparkScatter, ClearErrorCodes, ControlAsdRelay_MM … | CrankInterrupt_FallingEdge, DetermineNumberOfOverflowsBetweenCamSensorPulses_MM, StoreMAPVoltsAndCalcMAPValue |
| `$005E` | `DistributorFallingEdgePulsewidth_HB` | 26 | 4 | AisState14_SpeedControl, CODE8059_MM, CODE8235, CODEf101, CalculateAisPosition1 … | CrankInterrupt_FallingEdge, CrankMapRpmUpdate |
| `$005F` | *без имени* | 9 | 4 | CODE8059_MM, CODEf101, CrankMapRpmUpdate, Isr_TIC1_CrankEvent, ScheduleIgnitionCoils | CrankInterrupt_FallingEdge, CrankMapRpmUpdate |
| `$0060` | `Counter_TimerPastHalfwayBetweenCamPulses` | 4 | 3 | ControlAsdRelay_MM, DetermineNumberOfOverflowsBetweenCamSensorPulses_MM | CrankInterrupt_FallingEdge, DetermineNumberOfOverflowsBetweenCamSensorPulses_MM, StoreMAPVoltsAndCalcMAPValue |
| `$0061` | `LastCamFallingEdgeTime` | 6 | 3 | CrankInterrupt_CalculateFuel, CrankInterrupt_FallingEdge, CrankInterrupt_HandleCamSensorRisingEdgeA, CrankMapRpmUpdate, DetermineNumberOfOverflowsBetweenCamSensorPulses_MM … | CrankInterrupt_FallingEdge, MUCK_WITH_CEL, StoreMAPVoltsAndCalcMAPValue |
| `$0062` | `BitFlags62` | 6 | 3 | ClearErrorCodes, CrankInterrupt_CalculateFuel, CrankInterrupt_FallingEdge, CrankInterrupt_HandleCamSensorRisingEdgeA, CrankMapRpmUpdate … | ClearErrorCodes, CrankInterrupt_FallingEdge |
| `$0063` | `Crank_0063` | 2 | 1 | CrankInterrupt_HandleCamSensorRisingEdgeA, CrankInterrupt_HandleCamSensorRisingEdgeB | CrankInterrupt_HandleCamSensorRisingEdgeA |
| `$0064` | *без имени* | 2 | 1 | CrankInterrupt_HandleCamSensorRisingEdgeA, CrankInterrupt_HandleCamSensorRisingEdgeB | CrankInterrupt_HandleCamSensorRisingEdgeA |
| `$0065` | `BitFlags65` | 87 | 14 | AIS_Subroutine_12, AdaptiveMemory_DetermineWhichCellApplies_MM, AdaptiveMemory_UpdateCellIfRequired, CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CODE8059_MM … | CalculatePartThrottleEnrichmentAndLatency_MM, CheckThrottle_AtFullThrottle, CheckThrottle_ErrorAlreadyFlagged, CheckThrottle_VehicleSpeedStillAboveDecelIdle, HandleAmTimer_MM … |
| `$0066` | `BitFlags66` | 34 | 21 | AIS_Subroutine_12, AdaptiveMemory_UpdateCellIfRequired, CalculateIdleAdvance, CalculateSumOfAllFuelModifiers_MM, CalculateTargetIdleSpeed_MM … | CalculatePartThrottleEnrichmentAndLatency_MM, ControlCruiseServo1_MM, DRB_Special2, ExhGasRecirc_MM, HandleO2Processing_MM … |
| `$0067` | `BitFlags67` | 18 | 12 | AC_Rout11, AIS_Subroutine_12, AR_Rout4, CODE26ed, CODEe74f_MM … | AIS_Subroutine_12, CODEe72a, CODEe74f_MM, ControlAsdRelay_MM, HandleBaroReadRequirement_MM … |
| `$0068` | `BitFlags68` | 15 | 8 | AIS_Subroutine_12, AisState13_ClosedThrottle, AisState14_SpeedControl, CalculateTargetIdleSpeed_MM, CheckAndFilterCoolantTempSensor_SM … | CODEe74f_MM, CheckAndFilterCoolantTempSensor_SM, CheckThrottle_AtIdle, MultiplyTempvar1ByA_Unsign_A, PrepareCCDDataForXmit_MM_1 |
| `$0069` | `BitFlags69` | 17 | 22 | AisDriveRoutine, CODE59c2, CrankInterrupt_CalculateFuel, CrankInterrupt_HandleCamSensorRisingEdgeA, CrankMapRpmUpdate … | AisDriveRoutine, CODE1265, CODE59c2, ControlEngineCutout_MM, CrankInterrupt_FallingEdge … |
| `$006A` | `BitFlags6a` | 12 | 12 | AIS_Subroutine_12, CODEe74f_MM, CalculateSparkScatter, CheckAndFilterChargeTempSensor_SM, ControlEngineCutout_MM … | AisState12_ThrottleOpen, AisState14_SpeedControl, AisState4_ThrottleOpen, AisState6_SpeedControl, CheckAndFilterChargeTempSensor_SM … |
| `$006B` | `BitFlags6b` | 13 | 18 | AC_Rout11, CODE26ed, CalculateSparkScatter, CalculateTargetIdleSpeed_MM, DRB_SomethingLikeEMR_MM … | AC_Rout11, CODE26ed, CheckThrottle_AtFullThrottle, ControlAsdRelay_MM, DRBIISerialCommunications_MM … |
| `$006C` | `BitFlags6C` | 7 | 6 | CCD_SwitchState | CCD_SwitchState |
| `$006D` | `BitFlags6D` | 9 | 7 | CODEe74f_MM, CalculateAisPosition2, CheckIfCheckEngineLightShouldBeOn_B_MM, MonitorO2Response, SendOutputDriverByte | AIS_Init00DF, CODEe74f_MM, CalculateAisPosition2, CheckIfCheckEngineLightShouldBeOn_B_MM, MonitorO2Response |
| `$006E` | `BitFlags6E` | 11 | 16 | AC_Rout11, CODE26ed, ControlAirConditioning_MM, DecrementCounter01ff_SM, MonitorEgrFlow … | AC_Rout11, CODE2609, CODE26ed, DecrementCounter01ff_SM, MonitorEgrFlow … |
| `$006F` | `IPL1` | 17 | 12 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CCD_ToggleFlags, CODE1998, CODE64ea_SM, CheckForErrorsAndSetCodes_MM … | CODE1998, CODE64ea_SM, CalculateAverageKnockVolts_SM, CheckForErrorsAndSetCodes_MM, CrankInterrupt_CalculateFuel … |
| `$0070` | `IPL2` | 17 | 22 | CODE600e_SM, CalculatePartThrottleEnrichmentAndLatency_MM, CheckAnalog0170Limits2_SM, CheckAnalog0170Limits_SM, CheckConditionsForDeltaRPMRetard … | CODE1998, CODE64ea_SM, CalculatePartThrottleEnrichmentAndLatency_MM, CheckAnalog0170Limits2_SM, CheckAnalog0170Limits_SM … |
| `$0071` | `BitFlags71` | 77 | 15 | AisState0_EngineStopped, AisState1_Cranking, CCD_HandleAlarm, CCD_SwitchState, CODE600e_SM … | CODE8235, ControlCruiseServo1_MM, CrankInterrupt_HandleCamSensorRisingEdgeA, CrankInterrupt_HandleCamSensorRisingEdgeB, IncrementLoopCounters_MM … |
| `$0072` | `BitFlags72` | 31 | 45 | CCD_HandleAlarm, CODE1998, CODE64ea_SM, CODE8059_MM, ControlAlternator … | ATM_AllSolenoidsRelays, CCD_HandleAlarm, CODE1998, CODE8059_MM, ControlAlternator … |
| `$0073` | `BitFlags73` | 9 | 16 | CODE1265, CODEf101, DIDNT_2SCOMPLEMENT_OVERFLOW_UNDERFLOW1, EmmissionMaintenanceRemider1_MM, Interrupt_SpeedometerSignal … | CODEf101, EmmissionMaintenanceRemider1_MM, Interrupt_SpeedometerSignal, SwitchOrStayOpenLoop, VerifyOperationOfASDRelayAndO2Sensor_MM |
| `$0074` | `SyncFlags74` | 24 | 21 | CODE8235, ControlAsdRelay_MM, CrankInterrupt_CalculateFuel, CrankInterrupt_FallingEdge, CrankInterrupt_HandleCamSensorRisingEdgeA … | ControlAsdRelay_MM, CrankInterrupt_FallingEdge, CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency, Isr_PAI_CamPhase … |
| `$0075` | `SyncFlags75` | 13 | 20 | CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency, Interrupt_DwellTimerA, Interrupt_DwellTimerB, Isr_PAI_CamPhase … | CrankInterrupt_CalculateFuel, CrankInterrupt_FallingEdge, CrankInterrupt_HandleCamSensorRisingEdgeA, CrankInterrupt_HandleCamSensorRisingEdgeB, CrankMapRpmUpdate … |
| `$0076` | `BitFlags76` | 5 | 15 | AIS_Subroutine_12, CrankMapRpmUpdate | AIS_Subroutine_12, CODE8235, CheckThrottle_AtIdle, CrankInterrupt_FallingEdge, CrankMapRpmUpdate … |
| `$0077` | `BitFlags77` | 17 | 14 | AIS_Subroutine_12, AR_Rout4, AisState14_SpeedControl, CalculateAisPosition1, CalculateAisPosition2 … | AC_Rout7, CalculateTargetIdleSpeed_MM, DecrementCounter01ff_SM |
| `$0078` | `TargetIdleSpeedHB` | 18 | 2 | AIS_Subroutine_12, AdaptiveMemory_DetermineWhichCellApplies_MM, CCD_EEPromData, CalculateTargetIdleSpeed_MM, ControlCruiseServo1_MM … | CalculateTargetIdleSpeed_MM, ControlCruiseServo1_MM |
| `$0079` | `TargetIdleSpeedLB` | 16 | 2 | AIS_Subroutine_12, CCD_EEPromData, CalculateTargetIdleSpeed_MM, ControlCruiseServo1_MM, Cutout_SpeedIsBelow128Mph … | CalculateTargetIdleSpeed_MM, ControlCruiseServo1_MM |
| `$007A` | `EngineRpm_HB` | 147 | 2 | AC_Rout11, AC_Rout8, AC_Rout9, AIS_Subroutine_12, AR_Rout4 … | CrankMapRpmUpdate, ResetAverageValues_MM |
| `$007B` | `EngineRpm_LB` | 39 | 2 | AC_Rout8, AC_Rout9, AIS_Subroutine_12, AR_Rout4, CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT … | CrankMapRpmUpdate, ResetAverageValues_MM |
| `$007C` | `SignedDeltaRPM` | 9 | 1 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CheckConditionsForDeltaRPMRetard, CrankMapRpmUpdate | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT |
| `$007D` | `EngineRpmDouble_HB` | 5 | 1 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CODE8059_MM, CalculateAisPosition2, ClearKnockVoltsAvgCounter | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT |
| `$007E` | `EngineRpmDouble_LB` | 2 | 1 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT |
| `$007F` | `AverageRPMIncremental` | 3 | 1 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CheckConditionsForDeltaRPMRetard | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT |
| `$0080` | *без имени* | 2 | 1 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT |
| `$0081` | `Timer_BaroReadInterval` | 4 | 3 | HandleBaroReadRequirement_MM | HandleBaroReadRequirement_MM, StoreMAPVoltsAndCalcMAPValue |
| `$0082` | `MapVolts` | 3 | 3 | CrankMapRpmUpdate, HandleBaroReadRequirement_MM, ScheduleIgnitionCoils | ResetInterrupt, ScheduleIgnitionCoils, StoreMAPVoltsAndCalcMAPValue |
| `$0083` | `MapPrevious` | 7 | 5 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CODE8059_MM, CalculatePartThrottleTransientFuel, TransFuel_CalculateDecreasingMAPTransientFuel | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CheckThrottle_AtFullThrottle, ResetInterrupt, StoreMAPVoltsAndCalcMAPValue, TransFuel_CalculateDecreasingMAPTransientFuel |
| `$0084` | *без имени* | 4 | 2 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, TransFuel_CalculateDecreasingMAPTransientFuel | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, TransFuel_CalculateDecreasingMAPTransientFuel |
| `$0085` | `Factor_LeanoutOrEnrichTime_MAP` | 4 | 2 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, TransFuel_CalculateDecreasingMAPTransientFuel | CalculatePartThrottleTransientFuel, TransFuel_CalculateDecreasingMAPTransientFuel |
| `$0086` | `TpsAverageValue_HB` | 6 | 4 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, TransFuel_IncludeTPSTransients, TransFuel_StoreLeanOutFactor | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CheckThrottle_AtFullThrottle, StoreMAPVoltsAndCalcMAPValue, TransFuel_StoreLeanOutFactor |
| `$0087` | *без имени* | 4 | 2 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, TransFuel_StoreLeanOutFactor | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, TransFuel_StoreLeanOutFactor |
| `$0088` | `Factor_LeanoutOrEnrichTime_TPS` | 4 | 2 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, TransFuel_StoreLeanOutFactor | TransFuel_CalculateDecreasingTPSTransientFuel, TransFuel_IncludeTPSTransients |
| `$0089` | `Counter_MINTHR` | 1 | 2 | CheckThrottle_AtFullThrottle | CheckThrottle_AtFullThrottle, StoreMAPVoltsAndCalcMAPValue |
| `$008A` | `TPSOverMINTHR` | 34 | 1 | AC_Rout11, AC_Rout5_25F0, AC_Rout8, AC_Rout9, CCD_ThrottlePos … | CheckThrottle_ErrorAlreadyFlagged |
| `$008B` | `MapValue` | 106 | 3 | AIS_Subroutine_12, AdaptiveMemory_DetermineWhichCellApplies_MM, CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CCD_EngineRPM, CODE6b1d … | CrankMapRpmUpdate, ResetInterrupt, StoreMAPVoltsAndCalcMAPValue |
| `$008C` | `BatteryVolts` | 29 | 3 | AisDriveRoutine, CCD_BatVolts, CODE1998, CODE7242_SM, CalculateTargetIdleSpeed_MM … | A2DAndStoreBatteryVolts_MM, ControlAlternator, ResetInterrupt |
| `$008D` | `O2SensorVolts` | 14 | 2 | DecrementDSO2SensorDiagnosticCounter_MM, HandleO2Processing_MM, MonitorO2Response, O2_UsingFeedback, ObdPid14_O2Sensor1 … | A2DAndStoreBatteryVolts_MM, ResetInterrupt |
| `$008E` | `KnockVolts` | 4 | 2 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CalculateAverageKnockVolts_SM, IncrementOrClearKnockDiagCounter_SM | Isr_TOC4_KnockSample, ResetInterrupt |
| `$008F` | `TpsVolts` | 33 | 2 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CODE2d7b, CODE6b1d, CalculateAverageKnockVolts_SM, CalculateInjectorPulsewidthForStarting_MM … | CheckThrottle_ErrorAlreadyFlagged, StoreMAPVoltsAndCalcMAPValue |
| `$0090` | `CoolantTemp` | 109 | 3 | AC_Rout11, AC_Rout8, AIS_Subroutine_12, AMTimer_EngineRunning, AisState14_SpeedControl … | StoreCoolantTempValue, StoreMAPVoltsAndCalcMAPValue, UseDefaultCoolantTempLimpIn_MM |
| `$0091` | `ChargeTemp` | 11 | 3 | CCD_Baro, CalculateAverageKnockVolts_SM, CalculateIdleAdvance, CalculateSparkAdvance_MM, CalculateSumOfAllFuelModifiers_MM … | StoreChargeTempValue, StoreMAPVoltsAndCalcMAPValue, UseDefaultChargeTempLimpIn_MM |
| `$0092` | `AmbientAirTemp` | 9 | 2 | CCD_CoolantTemp, CalculateTargetIdleSpeed_MM, SomethingWithAmbientSensor_SM, StoreMAPVoltsAndCalcMAPValue, VerifyOperationOfAmbientTempSensor_MM | SomethingWithAmbientSensor_SM, StoreMAPVoltsAndCalcMAPValue |
| `$0093` | `TimeEngineRunningAlt` | 2 | 1 | CalculatePartThrottleEnrichmentAndLatency_MM, CalculateSumOfAllFuelModifiers_MM | CalculatePartThrottleEnrichmentAndLatency_MM |
| `$0094` | `Timer_FuelEnrich` | 3 | 1 | CalculateSumOfAllFuelModifiers_MM, DealWithSpecialIdle_SetBasicTiming_MM, O2_UsingFeedback | LOAD_FUELENRICHVAR |
| `$0095` | `InjectorLatencyPW` | 3 | 1 | CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency, PTELookupLatency | PTELookupLatency |
| `$0096` | `MAPRescaledfor3D` | 3 | 1 | CalculateIdleAdvance, CalculateInjectorPulsewidthForEngineRunning, LookupNormalAdvance | CalculateInjectorPulsewidthForEngineRunning |
| `$0097` | `RPMRescaledfor3D` | 6 | 1 | CalculateIdleAdvance, CalculateInjectorPulsewidthForEngineRunning, CalculatePartThrottleEnrichmentAndLatency_MM, LookupNormalAdvance | RescaleEngineRPM_MM |
| `$0098` | `SumOfFuelModifiers_HB` | 1 | 1 | CalculateInjectorPulsewidthForEngineRunning | CalculateSumOfAllFuelModifiers_MM |
| `$0099` | *без имени* | 1 | 1 | CalculateInjectorPulsewidthForEngineRunning | CalculateSumOfAllFuelModifiers_MM |
| `$009A` | `InjectorPulsewidth_HB` | 10 | 5 | AdaptiveMemory_UpdateCellIfRequired, CrankInterrupt_HandleCamSensorRisingEdgeA, DRB_Special2, HandleTransitionFromStartToRun, IncludeInjectorLatency … | CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency, StoreMAPVoltsAndCalcMAPValue, ThrottleFlooredWhileStarting_UnloadFuel |
| `$009B` | `InjectorPulsewidth_LB` | 10 | 5 | AdaptiveMemory_UpdateCellIfRequired, CrankInterrupt_HandleCamSensorRisingEdgeA, DRB_Special2, HandleTransitionFromStartToRun, IncludeInjectorLatency … | CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency, StoreMAPVoltsAndCalcMAPValue, ThrottleFlooredWhileStarting_UnloadFuel |
| `$009C` | `BaseFuelModifier` | 1 | 1 | CalculateInjectorPulsewidthForEngineRunning | CalculateSumOfAllFuelModifiers_MM |
| `$009D` | *без имени* | 1 | 1 | CalculateInjectorPulsewidthForEngineRunning | CalculateSumOfAllFuelModifiers_MM |
| `$009E` | `ThrottleEnrichmentFactor` | 2 | 1 | CalculateInjectorPulsewidthForEngineRunning | PTEStoreThorttleFactor |
| `$009F` | `BaroCompFactorFuel` | 1 | 1 | CalculateSumOfAllFuelModifiers_MM | CalculateSumOfAllFuelModifiers_MM |
| `$00A0` | `ChargeTempCompFactorFuel` | 0 | 1 |  | CalculateSumOfAllFuelModifiers_MM |
| `$00A1` | `BaseInjectorPulsewidthX` | 2 | 1 | CalculateInjectorPulsewidthForEngineRunning, IncludeCylTrimWithAdaptiveCells | CalculateInjectorPulsewidthForEngineRunning |
| `$00A2` | *без имени* | 2 | 1 | CalculateInjectorPulsewidthForEngineRunning, IncludeCylTrimWithAdaptiveCells | CalculateInjectorPulsewidthForEngineRunning |
| `$00A3` | `Factor_StartFuelDecayIntoRunFuel` | 1 | 1 | HandleTransitionFromStartToRun | ThrottleFlooredWhileStarting_UnloadFuel |
| `$00A4` | `Factor_DecelLeanoutWhenMAPDecreasing` | 4 | 2 | CalculateSumOfAllFuelModifiers_MM, HandleO2Processing_MM, MonitorSecondaryAir, O2_UsingFeedback | TransFuel_IncludeTPSTransients, TransFuel_StoreLeanOutFactor |
| `$00A5` | `Unref_00A5` | 0 | 0 |  |  |
| `$00A6` | `Timer_OffThrottleFuelEnrich` | 9 | 1 | CalculateInjectorPulsewidthForEngineRunning, CalculatePartThrottleEnrichmentAndLatency_MM, CalculateSumOfAllFuelModifiers_MM, HandleO2Processing_MM, LookupNormalAdvance … | CalculatePartThrottleEnrichmentAndLatency_MM |
| `$00A7` | `Timer_O2InhibitSwitchingRichIdleToClosedLoop` | 2 | 3 | CalculatePartThrottleTransientFuel, HandleO2Processing_MM | CalculatePartThrottleTransientFuel, DealWithSpecialIdle_SetBasicTiming_MM, TransFuel_CalculateDecreasingMAPTransientFuel |
| `$00A8` | `Pulsewidth_PartThrottleEnrichment_HB` | 4 | 2 | AC_Rout3, AR_Rout4, AdaptiveMemory_UpdateCellIfRequired, CalculateInjectorPulsewidthForEngineRunning | CalculateInjectorPulsewidthForStarting_MM, TransFuel_StoreLeanOutFactor |
| `$00A9` | *без имени* | 4 | 2 | AC_Rout3, AR_Rout4, AdaptiveMemory_UpdateCellIfRequired, CalculateInjectorPulsewidthForEngineRunning | CalculateInjectorPulsewidthForStarting_MM, TransFuel_StoreLeanOutFactor |
| `$00AA` | `Pulsewidth_AISEnrichment_HB` | 2 | 2 | CalculateInjectorPulsewidthForEngineRunning, IncludeInjectorLatency | IncludeInjectorLatency, TransFuel_StoreLeanOutFactor |
| `$00AB` | *без имени* | 2 | 2 | CalculateInjectorPulsewidthForEngineRunning, IncludeInjectorLatency | IncludeInjectorLatency, TransFuel_StoreLeanOutFactor |
| `$00AC` | `Counter_FallingEdgeEPP_MaxFF` | 2 | 3 | CalculatePartThrottleEnrichmentAndLatency_MM, CrankInterrupt_CalculateFuel | CalculatePartThrottleEnrichmentAndLatency_MM, CrankInterrupt_CalculateFuel |
| `$00AD` | `Counter_EPP_MaxFF` | 3 | 1 | CalculateInjectorPulsewidthForStarting_MM, CrankInterrupt_CalculateFuel | CrankInterrupt_CalculateFuel |
| `$00AE` | `TargetBatteryVolts` | 5 | 1 | CCD_BatVolts, CODE1998, CalculateTargetIdleSpeed_MM, CheckForErrorsAndSetCodes_MM, ControlAlternator | DetermineTargetBatteryVoltage_MM |
| `$00AF` | `Counter_O2SensorFeedbackCount_Signed` | 23 | 12 | AdaptiveMemory_UpdateCellIfRequired, CODE6b1d, CalculateIdleAdvance, CalculateSumOfAllFuelModifiers_MM, CaptureFreezeFrame … | AdaptiveMemory_UpdateCellIfRequired, CalculatePartThrottleEnrichmentAndLatency_MM, ClearO2SensorFeedbackCounterSigned_MM, Cutout_CheckMPHLimitingValues, DIDNT_2SCOMPLEMENT_OVERFLOW_UNDERFLOW1 … |
| `$00B0` | `Timer_CountdownFromStartRunForAisFeedback` | 9 | 3 | AIS_Subroutine_12, CalculateAisPosition2, CheckThrottle_AtFullThrottle, CheckThrottle_VehicleSpeedStillAboveDecelIdle, ControlCruiseServo1_MM … | CODE8235, CheckThrottle_VehicleSpeedStillAboveDecelIdle, ControlCruiseServo1_MM |
| `$00B1` | `KeyOnOrEngineRunningTime` | 35 | 3 | AIS_Subroutine_12, ActuatorTestMode_MM, AisState14_SpeedControl, CCD_SwitchState, CODE8059_MM … | CODE8235, IncrementLoopCounters_MM, SetupATM |
| `$00B2` | `Counter_MainLoop` | 109 | 2 | AC_Rout11, AC_Rout3, AC_Rout5_25F0, AC_Rout8, AIS_Subroutine_12 … | CODE8235, IncrementLoopCounters_MM |
| `$00B3` | `EngineRunningTimeBeforeStall` | 1 | 1 | AllowForHeatSoakAfterStall | IncrementLoopCounters_MM |
| `$00B4` | `Timer_AlternatorDutyCycle` | 5 | 1 | CODE1265, ControlAlternator, TurnAlternatorOff | Isr_TOC1_Periodic |
| `$00B5` | `CountdownTimerFromKeyOn` | 13 | 4 | AisDriveRoutine, CrankMapRpmUpdate, EmmissionMaintenanceRemider2_MM, GetControlFeedback_DetermineIfShutdownRequired_MM, LinkRegisterUpdate … | EmmissionMaintenanceRemider2_MM, GetControlFeedback_DetermineIfShutdownRequired_MM |
| `$00B6` | `Timer_CLTIME_ClosedLoopTimer` | 4 | 7 | HandleO2Processing_MM, O2_InvalidSignal_InMiddleRange, O2_UsingFeedback | HandleAmTimer_MM, HandleO2Processing_MM, O2_InvalidSignal_InMiddleRange, O2_UsingFeedback, UseDefaultCoolantTempLimpIn_MM |
| `$00B7` | `Timer_O2CNTR_CountdownFromAbove196FtoEnableClosedLoop` | 5 | 3 | AMTimer_EngineRunning, CalculateIdleAdvance, O2_UsingFeedback, ObdSaveConditions, ObdSimilarConditions | AMTimer_EngineRunning, HandleAmTimer_MM |
| `$00B8` | `AdaptiveCellUpdateTimer_IncrementedEveryCamRisingEdge` | 2 | 5 | AdaptiveMemory_UpdateCellIfRequired | AdaptiveMemory_UpdateCellIfRequired, CrankMapRpmUpdate, O2_UsingFeedback, ONTHROTTLE_OR_RPMTOOHIGHFORIDLE |
| `$00B9` | `PointerIntoAdaptiveMemory` | 13 | 1 | AdaptiveMemory_DetermineWhichCellApplies_MM, AdaptiveMemory_UpdateCellIfRequired, CalculateSumOfAllFuelModifiers_MM, ControlPurgeSolenoid_MM, MonitorEvapPurgeFlow … | ONTHROTTLE_OR_RPMTOOHIGHFORIDLE |
| `$00BA` | `ValueFromAdaptiveMemory` | 5 | 4 | CalculateSumOfAllFuelModifiers_MM, CaptureFreezeFrame, MonitorFuelSystemLean, MonitorFuelSystemRich, ObdPid07_LongTermTrim | AdaptiveMemory_UpdateCellIfRequired, DRB_Special2 |
| `$00BB` | `Timer_OutOfClosedLoopMode` | 4 | 5 | O2HasNotToggled, SwitchOrStayOpenLoop, WorkWithPrimaryRamp | HandleO2Processing_MM, O2_StopUsingFeedback, SwitchOrStayOpenLoop, WorkWithPrimaryRamp |
| `$00BC` | `Timer_O2ToggleDuration` | 1 | 4 | WorkWithSecondaryRamp | CrankMapRpmUpdate, ModifyO2FeedbackCountVarToMaintainStoich_MM, O2_SensorStuckOnOneSideTooLong, SwitchOrStayOpenLoop |
| `$00BD` | `DesiredNewAisPosition` | 22 | 18 | AIS_Subroutine_12, AdjustAISPosition_A, AdjustAISPosition_B, AisDriveRoutine, AisState1_Cranking … | AIS_Subroutine_12, ATM_AISMotorOpenClose, ATM_AllSolenoidsRelays, AdjustAISPosition_A, AdjustAISPosition_B … |
| `$00BE` | `Counter_AISACCompensation` | 2 | 1 | AIS_Subroutine_12, IncDecAISACCompensationCounter | IncDecAISACCompensationCounter |
| `$00BF` | `Counter_IdleControl` | 3 | 4 | AisState13_ClosedThrottle, CalculateIdleAdvance, SomethingWithAIS_MM | AisState13_ClosedThrottle, CODEe72a, SomethingWithAIS_MM |
| `$00C0` | `BaroAISComp` | 9 | 1 | AIS_Subroutine_12, MultiplyTempvar1ByA_Pos, MultiplyTempvar1ByA_Unsign_A, MultiplyTempvar1ByA_Unsign_C, MultiplyTempvar1ByA_Unsign_D | ControlAIS_MM |
| `$00C1` | `Timer_AisChanges` | 3 | 2 | CalculateAisPosition2, IncrementLoopCounters_MM | CalculateAisPosition2, IncrementLoopCounters_MM |
| `$00C2` | `AISACCompensation` | 6 | 2 | AIS_Subroutine_12, AisState14_SpeedControl, CalculateAISPosition3, MultiplyTempvar1ByA_Unsign_C | AIS_Subroutine_12, StoreMAPVoltsAndCalcMAPValue |
| `$00C3` | `CounterForSomething` | 4 | 3 | CODEe74f_MM | CODEe74f_MM |
| `$00C4` | `Ign_00C4` | 1 | 3 | ScheduleIgnitionCoils | ScheduleIgnitionCoils |
| `$00C5` | `Timer_OverboostCountdown` | 2 | 4 | Cutout_BeginOverboostTimerCountdown, Cutout_BeginOverboostTimerCountdownAgain | Cutout_BeginOverboostTimerCountdown, Cutout_BeginOverboostTimerCountdownAgain |
| `$00C6` | `Counter_KnockVoltsAvg` | 2 | 1 | CalculateAverageKnockVolts_SM, CrankMapRpmUpdate | StoreKnockVoltsAvgCounter |
| `$00C7` | `Timer_Over5PsiBoostMaxFF` | 2 | 1 | CalculateKnockRetard_MM | CalculateKnockRetard_MM |
| `$00C8` | `CalculatedSparkAdvance` | 3 | 1 | CalculateSparkScatter, CrankInterrupt_FallingEdge | CheckAndSetMinSparkAdvance |
| `$00C9` | `KnockRetardSum_AllCyls` | 8 | 2 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CalculateInjectorPulsewidthForEngineRunning, CalculateKnockRetard_MM, CrankInterrupt_FallingEdge | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CalculateKnockRetard_MM |
| `$00CA` | `Var_00CA` | 1 | 1 | CrankInterrupt_FallingEdge | CalculateKnockRetard_MM |
| `$00CB` | `KnockSensorThreshold` | 1 | 1 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT | CalculateKnockRetard_MM |
| `$00CC` | `Timer_O2MiddleDiagnostics` | 2 | 4 | VerifyOperationOfASDRelayAndO2Sensor_MM | VerifyOperationOfASDRelayAndO2Sensor_MM |
| `$00CD` | `InjMaskCD` | 6 | 4 | CODE8235, CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency | CODE8235, CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency |
| `$00CE` | `InjMaskCE` | 6 | 10 | CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency, PTELookupLatency | CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency, PTELookupLatency |
| `$00CF` | `DRBOffsetStored_HB` | 8 | 12 | DRB_SomethingLikeEMR_MM, EmmissionMaintenanceRemider1_MM, EmmissionMaintenanceRemider2_MM | CCD_HandleAlarm, CODE8059_MM, DRB_ResetEMR, DRB_SomethingLikeEMR_MM, DRB_Special2 … |
| `$00D0` | `DRBOffsetStored_LB` | 3 | 11 | EmmissionMaintenanceRemider2_MM | CCD_HandleAlarm, CODE8059_MM, DRB_ResetEMR, DRB_SomethingLikeEMR_MM, DRB_Special2 … |
| `$00D1` | `ATMOffset` | 7 | 6 | ActuatorTestMode_MM, ControlAIS_MM, ControlAirConditioning_MM, ControlAlternator, ControlFan_MM … | ATM_SerialOut, ActuatorTestMode_MM, ControlAsdRelay_MM, Isr_PAI_CamPhase, Isr_TIC1_CrankEvent … |
| `$00D2` | `DRBPointer1` | 9 | 32 | ATM_AllSolenoidsRelays, AltSerialComsRoutine, CalculateTargetIdleSpeed_MM, CheckIfCheckEngineLightShouldBeOn_MM, ControlAsdRelay_MM … | AltSerialComsRoutine, CalculateTargetIdleSpeed_MM, ClearErrorCodes, ControlAsdRelay_MM, DRBIISerialCommunications_MM … |
| `$00D3` | `DRBPointer2` | 23 | 12 | AltSerialComsRoutine, CalculateTargetIdleSpeed_MM, ControlAsdRelay_MM, DRB_ResetEMR, DRB_Special1 … | AltSerialComsRoutine, ControlAsdRelay_MM, DRBIISerialCommunications_MM, MUCK_WITH_CEL, OutputErrorBits … |
| `$00D4` | `DRBPointer3` | 11 | 5 | DRB_ResetEMR, DRB_Special2, DRB_UseRAM2ForSpecialProgramRoutine, EraseErrorCodes, SendConstValues … | DRBIISerialCommunications_MM, DRB_Special2, DRB_UseRAM2ForSpecialProgramRoutine, SendConstValues |
| `$00D5` | `DRBSerialMode` | 13 | 14 | AltSerialComsRoutine, BYTE_MODE_SERIAL_CODE_DOWNLOAD_ROUTINE, CalculateTargetIdleSpeed_MM, ControlAsdRelay_MM, DRBIIOuput_MM … | AltSerialComsRoutine, CODE6c36, CODE6cc4, DRBIISerialCommunications_MM, InitByteModeDownload … |
| `$00D6` | `CCDFlags4` | 3 | 5 | CCD_ToggleFlags | CCD_HandleAlarm, CCD_ToggleFlags, CcdRx_1 |
| `$00D7` | `CCDFlags5` | 11 | 10 | AisDriveRoutine, CCD_HandleAlarm, CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency, PTELookupLatency | AisDriveRoutine, CCD_HandleAlarm, CcdRx_1, PrepareCCDDataForXmit_MM_2 |
| `$00D8` | `CCDFlags6` | 5 | 3 | CCD_HandleAlarm, CcdRx_1 | CCD_HandleAlarm |
| `$00D9` | `CylTrim_Adaptive_Var1` | 5 | 6 | AdaptiveMemory_UpdateCellIfRequired, ControlPurgeSolenoid_MM, MonitorO2Response, O2_UsingFeedback | ControlPurgeSolenoid_MM, DRB_Special2, ONTHROTTLE_OR_RPMTOOHIGHFORIDLE |
| `$00DA` | `CylTrim_Flags_1` | 11 | 11 | ControlPurgeSolenoid_MM, DetermineIndividualInjectorTrims_MM, MonitorEvapPurgeFlow, ONTHROTTLE_OR_RPMTOOHIGHFORIDLE | ControlPurgeSolenoid_MM, DRB_Special2, IncludeCylTrimWithAdaptiveCells, ONTHROTTLE_OR_RPMTOOHIGHFORIDLE |
| `$00DB` | `CylTrim_Flags_2` | 1 | 2 | AdaptiveMemory_UpdateCellIfRequired | AdaptiveMemory_UpdateCellIfRequired |
| `$00DC` | `Counter_FuelEngRunning` | 8 | 14 | CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency | ControlEngineCutout_MM, CrankInterrupt_HandleCamSensorRisingEdgeA, Cutout_CheckRevLimitingValues, IncludeInjectorLatency |
| `$00DD` | `EGRVar2` | 1 | 2 | MonitorEgrFlow | EGR_CheckHiLoLimits, ExhGasRecirc_MM |
| `$00DE` | `MAPReferenceValueAIS` | 4 | 2 | AIS_Subroutine_12, CalculateAisPosition2, MultiplyTempvar1ByA_Unsign_C | AisState14_SpeedControl, CalculateAisPosition1 |
| `$00DF` | `Ais_00DF` | 1 | 2 | CalculateAisPosition2 | AIS_Init00DF, CalculateAisPosition2 |
| `$00E0` | `AisLoadFlagsA` | 60 | 16 | AC_Rout1, AC_Rout10, AC_Rout12, AC_Rout13, AC_Rout15 … | AdjustAISPosition_A, AdjustAISPosition_B, AisState12_ThrottleOpen, AisState13_ClosedThrottle, AisState14_SpeedControl … |
| `$00E1` | `AisLoadFlagsB` | 51 | 21 | AC_Rout1, AC_Rout10, AC_Rout12, AC_Rout13, AC_Rout15 … | AisState12_ThrottleOpen, AisState13_ClosedThrottle, AisState14_SpeedControl, AisState15_MapLimpIn, AisState4_ThrottleOpen … |
| `$00E2` | `TempA` | 4 | 2 | CalculatePartThrottleEnrichmentAndLatency_MM | CalculatePartThrottleEnrichmentAndLatency_MM |
| `$00E3` | `BitFlagsE3` | 8 | 14 | CalculateSumOfAllFuelModifiers_MM, ControlPurgeSolenoid_MM | ControlPurgeSolenoid_MM, IncludeCylTrimWithAdaptiveCells |
| `$00E4` | `Var_00E4` | 2 | 1 | ControlPurgeSolenoid_MM, MonitorEvapPurgeFlow | ControlPurgeSolenoid_MM |
| `$00E5` | `BitFlagsE5` | 9 | 13 | CrankMapRpmUpdate, MonitorMisfire, ResetAverageValues_MM | CheckThrottle_VehicleSpeedStillAboveDecelIdle, CrankMapRpmUpdate, MonitorMisfire, ResetAverageValues_MM, StoreMAPVoltsAndCalcMAPValue |
| `$00E6` | `MisfireCylBits` | 3 | 5 | CrankMapRpmUpdate, MonitorMisfire | CrankMapRpmUpdate, MonitorMisfire |
| `$00E7` | `MisfireCylConfirmed` | 6 | 4 | MonitorMisfire, ObdProcessMonitorResult | MonitorMisfire, ObdProcessMonitorResult |
| `$00E8` | `BatteryTemp` | 4 | 2 | DetermineTargetBatteryVoltage_MM, SomethingWithAmbientSensor_SM | SomethingWithAmbientSensor_SM, StoreMAPVoltsAndCalcMAPValue |
| `$00E9` | `Ac_00E9` | 2 | 2 | AC_Rout3 | AC_Rout2, AC_Rout3 |
| `$00EA` | `LinkRequestFlags` | 16 | 9 | AisDriveRoutine, CCDBusComs, CODE1265, Isr_TOC1_Periodic, LinkRegisterUpdate … | AisDriveRoutine, CCDBusComs, CODE1265, LinkRegisterUpdate, LinkSendFrameC … |
| `$00EB` | `LinkStatusFlags` | 9 | 8 | AisDriveRoutine, CCDBusComs, CODE5a0c, Isr_TOC1_Periodic, LinkRegisterUpdate … | AisDriveRoutine, CCDBusComs, CODE1265, CODE5a0c, LinkRegisterUpdate … |
| `$00EC` | `LinkReg48Data` | 1 | 2 | LinkRegisterUpdate | CheckIfCheckEngineLightShouldBeOn_B_MM |
| `$00ED` | `SwitchInputs` | 15 | 3 | AIS_Subroutine_12, CCD_SwitchState, CODEe74f_MM, CODEf101, CalculateTargetIdleSpeed_MM … | LinkRegisterUpdate, StoreMAPVoltsAndCalcMAPValue |
| `$00EE` | `OutputBits2` | 11 | 30 | ActuatorTestMode_MM, CCD_SwitchState, CheckErrorMaskingAndSetCodes_MM, ControlPurgeSolenoid_MM, LinkRegisterUpdate … | ATM_AllSolenoidsRelays, ATM_PTUIndicator, CODEf101, CheckBatVoltsFlag, CheckIfCheckEngineLightShouldBeOn_B_MM … |
| `$00EF` | `OutputBits2Lo` | 4 | 6 | ATM_FanRelay, CODEf101, LinkRegisterUpdate | ATM_FanRelay, CODEf101, TurnOffCEL_C, TurnOnCEL_C |
| `$00F0` | `LinkInputWordHi` | 4 | 1 | LinkRegisterUpdate, O2LoadTestSample, ShutDownSubroutineA | LinkRegisterUpdate |
| `$00F1` | `LinkInputWordLo` | 1 | 1 | LinkRegisterUpdate | LinkRegisterUpdate |
| `$00F2` | `Var_00F2` | 2 | 3 | CODE1265, Isr_TOC1_Periodic | CODE1265, Isr_TOC1_Periodic, LinkError |
| `$00F3` | `Var_00F3` | 8 | 12 | CODE8059_MM, CrankInterrupt_CalculateFuel, Isr_PAI_CamPhase, Isr_TIC1_CrankEvent, StoreMAPVoltsAndCalcMAPValue | CODE8059_MM, Isr_PAI_CamPhase, Isr_TIC1_CrankEvent, StoreMAPVoltsAndCalcMAPValue |
| `$00F4` | `Temp0` | 122 | 128 | AIS_Subroutine_12, AdaptiveMemory_DetermineWhichCellApplies_MM, AdaptiveMemory_UpdateCellIfRequired, AisState14_SpeedControl, CCD_BatVolts … | AIS_Subroutine_12, AdaptiveMemory_DetermineWhichCellApplies_MM, AdaptiveMemory_UpdateCellIfRequired, AisState14_SpeedControl, CCD_BatVolts … |
| `$00F5` | `Temp1` | 67 | 69 | AIS_Subroutine_12, AisState14_SpeedControl, CODEf101, CaculateChecksum, CalculateInjectorPulsewidthForStarting_MM … | AIS_Subroutine_12, AisState14_SpeedControl, CODEf101, CaculateChecksum, CalculateInjectorPulsewidthForStarting_MM … |
| `$00F6` | `Temp2` | 26 | 22 | CODEf101, CheckConditionsForDeltaRPMRetard, ControlPurgeSolenoid_MM, PTELookupLatency, ResetAverageValues_MM … | CODEf101, CalculatePartThrottleTransientFuel, CheckConditionsForDeltaRPMRetard, IncludeCylTrimWithAdaptiveCells, O2LoadTestSample … |
| `$00F7` | `Temp3` | 19 | 17 | CODEf101, CheckConditionsForDeltaRPMRetard, PTELookupLatency, ProcessErrorBits_WorkWithData_MM, ResetAverageValues_MM … | CODEf101, CalculatePartThrottleTransientFuel, CheckConditionsForDeltaRPMRetard, O2LoadTestSample, PTELookupLatency … |
| `$00F8` | `Temp4` | 26 | 22 | AIS_Subroutine_12, CODEf101, CalculateInjectorPulsewidthForStarting_MM, LookupTableFromVehSpdAndCompareToTPS, MultiplyTempvar1ByA_Pos … | AIS_Subroutine_12, CODEf101, CalculateInjectorPulsewidthForStarting_MM, MultiplyTempvar1ByA_Pos, MultiplyTempvar1ByA_Unsign_A … |
| `$00F9` | `Temp5` | 39 | 24 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CODE8235, CalculateInjectorPulsewidthForEngineRunning, CrankInterrupt_FallingEdge, CrankInterrupt_HandleCamSensorRisingEdgeA … | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CODE8235, CalculateInjectorPulsewidthForEngineRunning, CalculateSparkScatter, CrankInterrupt_FallingEdge … |
| `$00FA` | `Temp6` | 33 | 17 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CODE8235, CalculateInjectorPulsewidthForEngineRunning, CrankInterrupt_FallingEdge, CrankInterrupt_HandleCamSensorRisingEdgeA … | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CODE8235, CalculateInjectorPulsewidthForEngineRunning, CrankInterrupt_FallingEdge, CrankInterrupt_HandleCamSensorRisingEdgeA … |
| `$00FB` | `LastDistributorFallingEdgeTime` | 38 | 17 | CODE8235, CrankInterrupt_CalculateFuel, CrankInterrupt_FallingEdge, CrankInterrupt_HandleCamSensorRisingEdgeA, CrankInterrupt_HandleCamSensorRisingEdgeB … | CODE8235, CrankInterrupt_HandleCamSensorRisingEdgeA, CrankInterrupt_HandleCamSensorRisingEdgeB, DetermineNumberOfOverflowsBetweenSpeedoPulses_MM, IncludeInjectorLatency … |
| `$00FC` | *без имени* | 32 | 12 | CODE8235, CrankInterrupt_CalculateFuel, CrankInterrupt_FallingEdge, CrankInterrupt_HandleCamSensorRisingEdgeA, CrankInterrupt_HandleCamSensorRisingEdgeB … | CODE8235, CrankInterrupt_HandleCamSensorRisingEdgeA, CrankInterrupt_HandleCamSensorRisingEdgeB, IncludeInjectorLatency, Isr_TIC1_CrankEvent … |
| `$00FD` | `InjCylinderMask` | 21 | 19 | CCDBusComs, CODE1265, CrankInterrupt_FallingEdge, IncludeInjectorLatency, LinkSendFrameC … | CCDBusComs, CODE1265, CrankInterrupt_FallingEdge, IncludeInjectorLatency, LinkSendFrameC … |
| `$00FE` | `Toc1_00FE` | 1 | 2 | CODE1265 | CODE1265 |
| `$00FF` | `BitFlagsFF` | 8 | 11 | MonitorO2Response | MonitorO2Response, StoreMAPVoltsAndCalcMAPValue |

## Внутреннее ОЗУ выше прямой страницы ($0100-$03FF)

| Адрес | Имя | R | W | Читают | Пишут |
|---|---|---|---|---|---|
| `$0100` | `ObdMonitorsComplete` | 1 | 2 | ObdPid01_MonitorStatus | EraseErrorCodes, ResetInterrupt |
| `$0101` | `Code8059_0101` | 2 | 5 | CODE8059_MM, StoreMAPVoltsAndCalcMAPValue | CODE8059_MM, ResetInterrupt, StoreMAPVoltsAndCalcMAPValue |
| `$0102` | `Shutdown_0102` | 2 | 2 | ShutDownSubroutineA | ShutDownSubroutineA |
| `$0103` | `Shutdown_0103` | 2 | 2 | ShutDownSubroutineA | ShutDownSubroutineA |
| `$0104` | `Shutdown_0104` | 2 | 2 | ShutDownSubroutineA | ShutDownSubroutineA |
| `$0105` | `Shutdown_0105` | 2 | 2 | ShutDownSubroutineA | ShutDownSubroutineA |
| `$0106` | `Shutdown_0106` | 1 | 2 | ShutDownSubroutineA | ShutDownSubroutineA |
| `$0107` | `Shutdown_0107` | 1 | 2 | ShutDownSubroutineA | ShutDownSubroutineA |
| `$0108` | `Shutdown_0108` | 2 | 2 | ShutDownSubroutineA | ShutDownSubroutineA |
| `$0109` | `Shutdown_0109` | 9 | 8 | ShutDownSubroutineA | ShutDownSubroutineA |
| `$010A` | `Shutdown_010A` | 1 | 1 | ShutDownSubroutineA | ShutDownSubroutineA |
| `$010B` | *без имени* | 1 | 1 | ShutDownSubroutineA | ShutDownSubroutineA |
| `$010C` | `Shutdown_010C` | 1 | 1 | ShutDownSubroutineA | O2LoadTestSample |
| `$010D` | `ObdDtcCount` | 4 | 2 | CODE1f17, IsoValidateRequest, ObdPid01_MonitorStatus, ThrowNonCriticalError | EraseErrorCodes, ThrowNonCriticalError |
| `$010E` | `ObdMonStatus_O2Response` | 2 | 1 | ControlPurgeSolenoid_MM, EraseErrorCodes | EraseErrorCodes |
| `$010F` | `CatFailCounts` | 7 | 6 | MonitorCatalyst | EraseErrorCodes, MonitorCatalyst |
| `$0110` | `CatPassTrips` | 3 | 5 | MonitorCatalyst | EraseErrorCodes, MonitorCatalyst |
| `$0111` | `ObdMonStatus_Catalyst` | 1 | 1 | EraseErrorCodes | EraseErrorCodes |
| `$0112` | `ObdMonStatus_SecondaryAir` | 13 | 5 | AdaptiveMemory_UpdateCellIfRequired, ControlPurgeSolenoid_MM, DIDNT_2SCOMPLEMENT_OVERFLOW_UNDERFLOW1, EraseErrorCodes, ModifyO2FeedbackCountVarToMaintainStoich_MM … | EraseErrorCodes, MonitorSecondaryAir |
| `$0113` | `ObdMonStatus_O2HeaterUp` | 2 | 1 | EraseErrorCodes, LinkRegisterUpdate | EraseErrorCodes |
| `$0114` | `ObdMonStatus_O2HeaterDown` | 2 | 1 | EraseErrorCodes, LinkRegisterUpdate | EraseErrorCodes |
| `$0115` | `ObdMonStatus_Egr` | 9 | 5 | CODE6b1d, CODE6b91, EGR_CheckHiLoLimits, EGR_ResetEGRVars, EraseErrorCodes … | CODE6b1d, CODE6b91, EGR_CheckHiLoLimits, EGR_ResetEGRVars, EraseErrorCodes |
| `$0116` | `ObdMonStatus_EvapPurge` | 7 | 3 | AIS_Subroutine_12, CODEa344, CalculateAISPosition3, EraseErrorCodes, MonitorEvapPurgeFlow … | CODEa344, EraseErrorCodes, MonitorEvapPurgeFlow |
| `$0117` | `ObdMonStatus_FuelRich` | 13 | 8 | ControlPurgeSolenoid_MM, EraseErrorCodes, MonitorFuelSystemRich, O2_UsingFeedback | EraseErrorCodes, MonitorFuelSystemRich |
| `$0118` | `ObdMonStatus_FuelLean` | 7 | 5 | CODEa68d, EraseErrorCodes, MonitorFuelSystemLean | CODEa68d, EraseErrorCodes, MonitorFuelSystemLean |
| `$0119` | `ObdMonStatus_Misfire` | 6 | 4 | EraseErrorCodes, MonitorMisfire, StoreMAPVoltsAndCalcMAPValue | EraseErrorCodes, MonitorMisfire |
| `$011A` | `ObdStatusFlags` | 12 | 2 | CODE6b91, CODEa68d, MonitorEgrFlow, MonitorEvapPurgeFlow, MonitorFuelSystemLean … | EraseErrorCodes, MonitorMisfire |
| `$011B` | `ObdGoodTripCount` | 4 | 3 | ObdMisfireMilLogic, ObdProcessMonitorResult, ObdTripEndLogic | EraseErrorCodes, ObdProcessMonitorResult |
| `$011C` | `LastEmissionFault` | 3 | 3 | ObdProcessMonitorResult, ObdTripEndLogic | EraseErrorCodes, ObdProcessMonitorResult, ThrowNonCriticalError |
| `$011D` | `ISO_ErrBitStatus` | 3 | 3 | CaptureFreezeFrame, ErrorCodeRoutine_Unused, ObdTripEndLogic | CaptureFreezeFrame, EraseErorrCodes, EraseErrorCodes |
| `$011E` | `ISO_ErrorBitRegister0` | 0 | 0 |  |  |
| `$011F` | `ISO_ErrorBitRegister1` | 1 | 0 | CODE2395 |  |
| `$0120` | `ISO_ErrorBitRegister2` | 1 | 0 | CODE23a6 |  |
| `$0121` | `ISO_ErrorBitRegister3` | 1 | 0 | CODE23b2 |  |
| `$0122` | `ISO_ErrorBitRegister4` | 1 | 0 | CODE23c3 |  |
| `$0123` | `ISO_ErrorBitRegisterStored0` | 1 | 0 | CODE23d6 |  |
| `$0124` | `ISO_ErrorBitRegisterStored1` | 1 | 0 | CODE23e9 |  |
| `$0125` | `ISO_ErrorBitRegisterStored2` | 1 | 0 | CODE23fa |  |
| `$0126` | `ISO_ErrorBitRegisterStored3` | 1 | 0 | CODE2408 |  |
| `$0127` | `ISO_ErrorBitRegisterStored4` | 5 | 7 | CODE1f17, MonitorO2Response, StoreMAPVoltsAndCalcMAPValue | EraseErrorCodes, MonitorO2Response, StoreMAPVoltsAndCalcMAPValue |
| `$0128` | `Var_0128` | 5 | 7 | CODE1f17, MonitorO2Response, StoreMAPVoltsAndCalcMAPValue | EraseErrorCodes, MonitorO2Response, StoreMAPVoltsAndCalcMAPValue |
| `$0129` | `MisfireCondRpm` | 0 | 0 |  |  |
| `$012A` | `MisfireCondMap` | 0 | 0 |  |  |
| `$012B` | `MisfireCondFlags` | 8 | 2 | CrankMapRpmUpdate, MonitorMisfire, ObdMisfireMilLogic | MonitorMisfire |
| `$012C` | `MisfireCondCount` | 3 | 4 | MonitorMisfire | MonitorMisfire |
| `$012D` | `FuelSysCondRpm` | 0 | 0 |  |  |
| `$012E` | `FuelSysCondMap` | 0 | 0 |  |  |
| `$012F` | `FuelSysCondFlags` | 1 | 0 | ObdMisfireMilLogic |  |
| `$0130` | `FuelSysCondCount` | 0 | 4 |  | CODEa68d, MonitorFuelSystemRich |
| `$0131` | `RpmScaleA` | 7 | 5 | CrankMapRpmUpdate, ResetAverageValues_MM, ResetInterrupt | ResetAverageValues_MM, ResetInterrupt |
| `$0132` | `MapRpm_0132` | 5 | 5 | CrankMapRpmUpdate, ResetAverageValues_MM | ResetAverageValues_MM, ResetInterrupt |
| `$0133` | `RpmScaleB` | 3 | 3 | CrankMapRpmUpdate, ResetAverageValues_MM | ResetAverageValues_MM, ResetInterrupt |
| `$0134` | `MapRpm_0134` | 3 | 3 | CrankMapRpmUpdate, ResetAverageValues_MM | ResetAverageValues_MM, ResetInterrupt |
| `$0135` | `FaultBitmap` | 0 | 0 |  |  |
| `$0149` | `MonSecAir_0149` | 1 | 4 | MonitorSecondaryAir | EraseErrorCodes, MonitorSecondaryAir |
| `$014A` | `CoolantTempCopy1` | 2 | 1 | StoreMAPVoltsAndCalcMAPValue | CalculateInjectorPulsewidthForStarting_MM |
| `$014B` | `MapRpm_014B` | 5 | 1 | CrankMapRpmUpdate, ResetAverageValues_MM | ResetAverageValues_MM |
| `$014C` | `MapRpm_014C` | 4 | 1 | CrankMapRpmUpdate, ResetAverageValues_MM | ResetAverageValues_MM |
| `$014D` | `Vss_014D` | 1 | 1 | Interrupt_SpeedometerSignal | Interrupt_SpeedometerSignal |
| `$014E` | `CrankActivityTimer` | 2 | 3 | ControlAsdRelay_MM, IncrementLoopCounters_MM | IncrementLoopCounters_MM, Isr_PAI_CamPhase, Isr_TIC1_CrankEvent |
| `$014F` | `MinimumTimerCountBeforeMainloopCanContinue` | 2 | 1 | MainProgramLoop | SetupMainLoopCounter |
| `$0150` | `SubLoopRequests` | 3 | 2 | IncrementLoopCounters_MM, MainProgramLoop | IncrementLoopCounters_MM, MainProgramLoop |
| `$0151` | `CcdTxHeader` | 1 | 13 | CCDBusComs | CCD_Baro, CCD_BatVolts, CCD_Blank, CCD_ConfigConst1, CCD_CoolantTemp … |
| `$0152` | `CcdTxId` | 1 | 13 | CCDBusComs | CCD_Baro, CCD_BatVolts, CCD_Blank, CCD_ConfigConst1, CCD_CoolantTemp … |
| `$0153` | `CcdTxData1` | 1 | 3 | CCDBusComs | CODE1265, PrepareCCDDataForXmit_MM_1 |
| `$0154` | `CcdTxData2` | 1 | 3 | CCDBusComs | CODE1265, PrepareCCDDataForXmit_MM_1 |
| `$0156` | `CcdRxId` | 2 | 1 | CCDBusComs, PrepareCCDDataForXmit_MM_2 | CCDBusComs |
| `$0157` | `CcdRxData1` | 3 | 1 | CCDBusComs, CcdRx_4, CcdRx_8 | CCDBusComs |
| `$0158` | `CcdRxData2` | 2 | 1 | CCDBusComs, CcdRx_4 | CCDBusComs |
| `$0159` | `LinkRegAddress` | 2 | 3 | LinkRegisterUpdate, LinkSendRegisterFrame | LinkRegisterUpdate |
| `$015A` | `LinkRegDataOutHi` | 1 | 1 | LinkSendRegisterFrame | LinkRegisterUpdate |
| `$015B` | `LinkRegDataOutLo` | 1 | 1 | LinkSendRegisterFrame | LinkRegisterUpdate |
| `$015C` | `LinkRegLastAddress` | 1 | 1 | LinkRegisterUpdate | LinkRegisterUpdate |
| `$015D` | `LinkRegDataInHi` | 3 | 1 | LinkRegisterUpdate, LinkSendRegisterFrame | LinkSendRegisterFrame |
| `$015E` | `LinkRegDataInLo` | 2 | 1 | LinkRegisterUpdate, LinkSendRegisterFrame | LinkSendRegisterFrame |
| `$015F` | `LinkFrameCHeader` | 2 | 2 | Isr_TOC1_Periodic, LinkSendFrameC | CODE1265, LinkError |
| `$0160` | `LinkFrameCData1` | 1 | 1 | LinkSendFrameC | CODE1265 |
| `$0161` | `LinkFrameCData2` | 1 | 1 | LinkSendFrameC | CODE1265 |
| `$0162` | `Var_0162` | 1 | 1 | Isr_TOC1_Periodic | CODE1265 |
| `$0163` | `LinkFrameCReply1` | 1 | 1 | LinkSendFrameC | LinkSendFrameC |
| `$0164` | `LinkFrameCReply2` | 1 | 1 | LinkSendFrameC | LinkSendFrameC |
| `$0165` | `LinkCommandByte` | 5 | 1 | AisDriveRoutine, CCDBusComs, LinkSendFrameC, LinkSendRegisterFrame | AisDriveRoutine |
| `$0166` | `LinkReplyHeader` | 8 | 4 | AisDriveRoutine, CCDBusComs, LinkSendFrameC, LinkSendRegisterFrame | AisDriveRoutine, CCDBusComs, LinkSendFrameC, LinkSendRegisterFrame |
| `$0167` | `LinkRetryCount` | 1 | 2 | LinkError | LinkError, Load05Into0167_SM |
| `$0168` | `AltSerial_0168` | 1 | 2 | CODE6cc4 | CODE6cc4 |
| `$0169` | `AltSerial_0169` | 1 | 2 | CODE6cc4 | CODE6cc4 |
| `$016A` | `AltSerial_016A` | 5 | 3 | CODE6c36, CODE6cc4, EchoSerialData | CODE6c36, CODE6cc4 |
| `$016B` | `AltSerial_016B` | 5 | 3 | CODE6c36, CODE6cc4, EchoSerialData | CODE6c36, CODE6cc4 |
| `$016C` | `LastCoolantTempVolts` | 3 | 2 | CheckAndFilterCoolantTempSensor_SM, UseDefaultCoolantTempLimpIn_MM | A2DAndStoreCoolantAndChargeTempVolts_SM, StoreMAPVoltsAndCalcMAPValue |
| `$016D` | `LastChargeTempVolts` | 4 | 2 | CheckAndFilterChargeTempSensor_SM, StoreMAPVoltsAndCalcMAPValue, UseDefaultChargeTempLimpIn_MM | A2DAndStoreCoolantAndChargeTempVolts_SM, StoreMAPVoltsAndCalcMAPValue |
| `$016E` | `AnalogMux01_AN4` | 0 | 2 |  | A2DAndStoreTPS_and_CruiseVolts_MM, StoreMAPVoltsAndCalcMAPValue |
| `$016F` | `DownstreamO2Volts` | 12 | 2 | MonitorSecondaryAir, ObdPid15_O2Sensor2, SCI_DSO2SensorVolts, SwitchOrStayOpenLoop, VerifyOperationOfASDRelayAndO2Sensor_MM … | A2DAndStoreTPS_and_CruiseVolts_MM, StoreMAPVoltsAndCalcMAPValue |
| `$0170` | `AsdOutputVolts` | 6 | 2 | CODE7242_SM, CheckAnalog0170Limits2_SM, CheckAnalog0170Limits_SM | A2DAndStoreAmbientTempVolts_SM, StoreMAPVoltsAndCalcMAPValue |
| `$0171` | `AmbientAirTempVolts` | 5 | 2 | SomethingWithAmbientSensor_SM, StoreMAPVoltsAndCalcMAPValue | A2DAndStoreAmbientTempVolts_SM, StoreMAPVoltsAndCalcMAPValue |
| `$0172` | `AnalogMux11_AN4` | 0 | 1 |  | CheckAndFilterAmbientTempSensor_SM |
| `$0173` | `BatteryTempVolts` | 3 | 1 | SomethingWithAmbientSensor_SM, StoreMAPVoltsAndCalcMAPValue | CheckAndFilterAmbientTempSensor_SM |
| `$0174` | `LastTpsVolts` | 4 | 2 | CheckThrottleRoutine_MM, FurtherMAPAndBaroDiagnostics2_SM, ObdPid11_Throttle | A2DAndStoreTPS_and_CruiseVolts_MM, StoreMAPVoltsAndCalcMAPValue |
| `$0175` | `CruiseControlSwitchStateAnalog` | 2 | 2 | CCD_SwitchState, ControlCruiseServo0_MM | A2DAndStoreTPS_and_CruiseVolts_MM, StoreMAPVoltsAndCalcMAPValue |
| `$0176` | `LinkReg58Data` | 1 | 4 | LinkRegisterUpdate | ControlPurgeSolenoid_MM |
| `$0177` | `LinkReg58DataLo` | 1 | 4 | LinkRegisterUpdate | ControlPurgeSolenoid_MM |
| `$0178` | `EgrMonSampleCount` | 3 | 4 | CODE6b1d, MonitorEgrFlow | CODE6b1d, CODE6b91, EGR_CheckHiLoLimits, MonitorEgrFlow |
| `$0179` | `MonEgr_0179` | 3 | 4 | CODE6b1d, MonitorEgrFlow | CODE6b1d, CODE6b91, EGR_CheckHiLoLimits, MonitorEgrFlow |
| `$017A` | `EGR_Temp_1` | 4 | 2 | CODE6b1d, EGR_ResetEGRVars, MonitorEgrFlow | EGR_CheckHiLoLimits, MonitorEgrFlow |
| `$017B` | `EGR_Temp_2` | 2 | 2 | CODE6b1d | CODE6b1d, EGR_ResetEGRVars |
| `$017C` | `CcdTxSlot` | 1 | 1 | PrepareCCDDataForXmit_MM_1 | PrepareCCDDataForXmit_MM_1 |
| `$017D` | `Temp0_X` | 0 | 1 |  | HandleBaroReadRequirement_MM |
| `$017E` | `Ign_017E` | 3 | 2 | ScheduleIgnitionCoils | ScheduleIgnitionCoils |
| `$017F` | `Temp1_X` | 1 | 1 | ClearO2SensorFeedbackCounterSigned_MM | TransFuel_IncludeTPSTransients |
| `$0180` | `BatVoltsDiagCounter` | 1 | 2 | CODE1998 | CODE1998 |
| `$0181` | `O2AdvanceIncrement` | 1 | 2 | ControlAlternator | ControlAlternator |
| `$0182` | `Alt_0182` | 1 | 2 | TurnAlternatorOff | TurnAlternatorOff, TurnAlternatorOn |
| `$0183` | `Var_0183` | 7 | 1 | CalculateTargetIdleSpeed_MM, MonitorEvapPurgeFlow, StoreVariableRevLimit, TurnAlternatorOff | TurnAlternatorOff |
| `$0185` | `Factor_DecelLeanoutWhenMAPDecreasing_Temp` | 5 | 2 | CrankMapRpmUpdate, MonitorSecondaryAir, TransFuel_CalculateDecreasingMAPTransientFuel, TransFuel_StoreLeanOutFactor | CalculatePartThrottleTransientFuel, TransFuel_CalculateDecreasingMAPTransientFuel |
| `$0186` | `Timer_OffThrottleFuelEnrich2` | 3 | 2 | CrankMapRpmUpdate, MonitorSecondaryAir, TransFuel_CalculateDecreasingTPSTransientFuel | TransFuel_IncludeTPSTransients, TransFuel_StoreLeanOutFactor |
| `$0187` | `MonFuelSys_0187` | 8 | 6 | CODEa68d, MonitorFuelSystemLean, MonitorFuelSystemRich | CODEa68d, MonitorFuelSystemLean, MonitorFuelSystemRich |
| `$0188` | `FuelSysTrimSum` | 3 | 3 | MonitorFuelSystemLean, MonitorFuelSystemRich | MonitorFuelSystemLean, MonitorFuelSystemRich |
| `$0189` | `MonFuelSys_0189` | 3 | 3 | MonitorFuelSystemLean, MonitorFuelSystemRich | MonitorFuelSystemLean, MonitorFuelSystemRich |
| `$018A` | `FuelSysLeanCount` | 1 | 2 | MonitorFuelSystemLean | CODEa68d, MonitorFuelSystemLean |
| `$018B` | `FuelSysRichCount` | 3 | 4 | MonitorFuelSystemRich | MonitorFuelSystemRich |
| `$018C` | `SparkScatter` | 0 | 2 |  | CalculateSparkScatter |
| `$018D` | `O2AdvanceIncrement_018D` | 0 | 2 |  | CalculateIdleAdvance, SparkAdvance_BadO2 |
| `$018E` | `AdvanceTemporary` | 7 | 1 | CrankInterrupt_HandleCamSensorRisingEdgeA, CrankInterrupt_HandleCamSensorRisingEdgeB, Interrupt_DwellTimerA, Interrupt_DwellTimerB, ObdPid0E_Advance … | ScheduleIgnitionCoils |
| `$018F` | `DistFETimeModified_A` | 5 | 1 | CrankInterrupt_HandleCamSensorRisingEdgeA, CrankInterrupt_HandleCamSensorRisingEdgeB, Interrupt_DwellTimerB, ScheduleIgnitionCoils | StoreMAPVoltsAndCalcMAPValue |
| `$0190` | `DistFETimeModified_B` | 5 | 1 | CODE8235, CrankInterrupt_HandleCamSensorRisingEdgeA, Interrupt_DwellTimerA, ScheduleIgnitionCoils | StoreMAPVoltsAndCalcMAPValue |
| `$0191` | `Knock_0191` | 5 | 1 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CalculateAverageKnockVolts_SM, CheckForOtherRetardFactors | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT |
| `$0192` | `Knock_0192` | 2 | 1 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT |
| `$0193` | `Knock_0193` | 5 | 1 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CalculateAverageKnockVolts_SM, CheckForTPSRetard_NoAR | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT |
| `$0194` | *без имени* | 2 | 1 | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT |
| `$0195` | `MaxAdvanceLookup` | 1 | 2 | LookupNormalAdvance | LookupNormalAdvance |
| `$0196` | `AdaptiveRetardValue_A` | 1 | 1 | CalculateInjectorPulsewidthForEngineRunning | LookupNormalAdvance |
| `$0197` | `Counter_DeltaEngineRPM_1` | 2 | 2 | IncrementDeltaRPMCounter_SM, SparkAdvance_BadO2 | CheckConditionsForDeltaRPMRetard, IncrementDeltaRPMCounter_SM |
| `$0198` | `SparkDrpm_0198` | 2 | 3 | CheckConditionsForDeltaRPMRetard | CheckConditionsForDeltaRPMRetard, SparkAdvance_BadO2 |
| `$0199` | `SparkDrpm_0199` | 2 | 4 | CheckConditionsForDeltaRPMRetard | CheckConditionsForDeltaRPMRetard |
| `$019A` | `FuelLookupValue3D` | 2 | 5 | VerifyOperationOfASDRelayAndO2Sensor_MM | VerifyOperationOfASDRelayAndO2Sensor_MM |
| `$019B` | `PreviousMAPTemp` | 1 | 1 | PTU_Main | PTU_Main |
| `$019C` | `DownCounterUnknown` | 2 | 1 | PTU_SetPTUBits | PTU_SetPTUBits |
| `$019D` | `MisfireEventCount` | 2 | 2 | CrankMapRpmUpdate, MonitorMisfire | CrankMapRpmUpdate, MonitorMisfire |
| `$019E` | `MisfireCount100` | 7 | 6 | CrankMapRpmUpdate, MonitorMisfire | CrankMapRpmUpdate, MonitorMisfire |
| `$019F` | `MisfireBlockCount` | 1 | 2 | MonitorMisfire | MonitorMisfire |
| `$01A0` | `MisfireSum500` | 4 | 4 | CrankMapRpmUpdate, MonitorMisfire | CrankMapRpmUpdate, MonitorMisfire |
| `$01A1` | `MisfireHealEvents` | 4 | 10 | CrankMapRpmUpdate, MonitorMisfire | CrankMapRpmUpdate, MonitorMisfire |
| `$01A2` | `MisfireHealCount` | 5 | 8 | CrankMapRpmUpdate, MonitorMisfire | CrankMapRpmUpdate, MonitorMisfire |
| `$01A3` | `MisfireHealBlocks` | 3 | 6 | CrankMapRpmUpdate, MonitorMisfire | CrankMapRpmUpdate, MonitorMisfire |
| `$01A4` | `MisfireHealSum` | 4 | 6 | CrankMapRpmUpdate, MonitorMisfire | CrankMapRpmUpdate, MonitorMisfire |
| `$01A5` | `MapRpm_01A5` | 5 | 5 | CrankMapRpmUpdate | CrankMapRpmUpdate |
| `$01A6` | `MapRpm_01A6` | 2 | 2 | CrankMapRpmUpdate | CrankMapRpmUpdate |
| `$01A7` | `MapRpm_01A7` | 3 | 2 | CrankMapRpmUpdate, ResetAverageValues_MM | ResetAverageValues_MM, StoreMAPVoltsAndCalcMAPValue |
| `$01A8` | `MapRpm_01A8` | 0 | 1 |  | CrankMapRpmUpdate |
| `$01A9` | `MapRpm_01A9` | 0 | 1 |  | CrankMapRpmUpdate |
| `$01AA` | `StartCoolantTemp` | 3 | 1 | ExhGasRecirc_MM, MonitorMisfire, ObdWarmupCycleCheck | StoreMAPVoltsAndCalcMAPValue |
| `$01AB` | `Var_01AB` | 1 | 1 | CrankMapRpmUpdate | CrankInterrupt_CalculateFuel |
| `$01AC` | `CrankPeriodPrev` | 1 | 2 | AIS_Subroutine_12 | CrankMapRpmUpdate, ResetAverageValues_MM |
| `$01AD` | *без имени* | 1 | 2 | AIS_Subroutine_12 | CrankMapRpmUpdate, ResetAverageValues_MM |
| `$01AE` | `RpmHistory0` | 6 | 2 | AIS_Subroutine_12, CrankMapRpmUpdate, ResetAverageValues_MM | CrankMapRpmUpdate, ResetAverageValues_MM |
| `$01AF` | *без имени* | 6 | 2 | AIS_Subroutine_12, CrankMapRpmUpdate, ResetAverageValues_MM | CrankMapRpmUpdate, ResetAverageValues_MM |
| `$01B0` | `RpmHistory1` | 3 | 2 | CrankMapRpmUpdate, ResetAverageValues_MM | CrankMapRpmUpdate, ResetAverageValues_MM |
| `$01B1` | *без имени* | 3 | 2 | CrankMapRpmUpdate, ResetAverageValues_MM | CrankMapRpmUpdate, ResetAverageValues_MM |
| `$01B2` | `RpmHistory2` | 1 | 2 | CrankMapRpmUpdate | CrankMapRpmUpdate, ResetAverageValues_MM |
| `$01B3` | *без имени* | 1 | 2 | CrankMapRpmUpdate | CrankMapRpmUpdate, ResetAverageValues_MM |
| `$01B8` | `MapRpm_01B8` | 1 | 1 | ResetAverageValues_MM | CrankMapRpmUpdate |
| `$01B9` | `MapRpm_01B9` | 1 | 1 | ResetAverageValues_MM | CrankMapRpmUpdate |
| `$01BA` | `Ais_01BA` | 1 | 1 | AIS_Subroutine_12 | AIS_Subroutine_12 |
| `$01BB` | *без имени* | 1 | 1 | AIS_Subroutine_12 | AIS_Subroutine_12 |
| `$01BC` | `Ais_01BC` | 1 | 1 | AIS_Subroutine_12 | AIS_Subroutine_12 |
| `$01BD` | *без имени* | 1 | 1 | AIS_Subroutine_12 | AIS_Subroutine_12 |
| `$01BE` | `Ais_01BE` | 0 | 1 |  | AIS_Subroutine_12 |
| `$01BF` | *без имени* | 0 | 1 |  | AIS_Subroutine_12 |
| `$01C0` | `ModifiedDeltaRPMFractionReducing` | 2 | 1 | AIS_Subroutine_12, CalculateIdleAdvance | AIS_Subroutine_12 |
| `$01C1` | `Ais_01C1` | 2 | 1 | AIS_Subroutine_12 | AIS_Subroutine_12 |
| `$01C2` | `Ais_01C2` | 2 | 1 | AIS_Subroutine_12 | AIS_Subroutine_12 |
| `$01C3` | `EngineIdleIncrDecrBit7` | 2 | 1 | AIS_Subroutine_12, CalculateSparkScatter | AIS_Subroutine_12 |
| `$01C4` | `Ais_01C4` | 2 | 2 | AIS_Subroutine_12 | AIS_Subroutine_12 |
| `$01C5` | `AisStepDelay` | 1 | 2 | AisDriveRoutine | AisDriveRoutine |
| `$01C6` | `LinkLastStatus` | 1 | 1 | AisDriveRoutine | AisDriveRoutine |
| `$01C7` | `AdvanceDownCounter_A` | 6 | 3 | AisState5_ClosedThrottle, AisState6_SpeedControl, CalculateIdleAdvance, CalculateSparkAdvance_MM, CalculateTargetIdleSpeed_MM … | CODEe72a, CalculateIdleAdvance, CalculateSparkAdvance_MM |
| `$01C8` | `Ais_01C8` | 3 | 9 | AisState4_ThrottleOpen, AisState5_ClosedThrottle, AisState6_SpeedControl | AisState12_ThrottleOpen, AisState13_ClosedThrottle, AisState14_SpeedControl, AisState4_ThrottleOpen, AisState5_ClosedThrottle … |
| `$01C9` | `Ais_01C9` | 2 | 9 | AisState5_ClosedThrottle, AisState6_SpeedControl | AisState12_ThrottleOpen, AisState13_ClosedThrottle, AisState14_SpeedControl, AisState4_ThrottleOpen, AisState5_ClosedThrottle … |
| `$01CA` | `IdleTarget_01CA` | 2 | 2 | CalculateTargetIdleSpeed_MM, IncrementCounters01cb_01ca_MM | CalculateTargetIdleSpeed_MM, IncrementCounters01cb_01ca_MM |
| `$01CB` | `IdleTarget_01CB` | 2 | 2 | CalculateTargetIdleSpeed_MM, IncrementCounters01cb_01ca_MM | CalculateTargetIdleSpeed_MM, IncrementCounters01cb_01ca_MM |
| `$01CC` | `Counter_IdleControl2` | 2 | 4 | CODEe72a, SomethingWithAIS_MM | CODEe72a, SomethingWithAIS_MM |
| `$01CD` | `Var_01CD` | 1 | 1 | CrankMapRpmUpdate | CalculateAisPosition2 |
| `$01CE` | `CruiseControlVar4_01CE` | 2 | 2 | Interrupt_SpeedometerSignal | Interrupt_SpeedometerSignal |
| `$01CF` | `Counter_SomethingWithCamSensor` | 3 | 3 | CrankInterrupt_CalculateFuel, Interrupt_SpeedometerSignal | CrankInterrupt_CalculateFuel, Interrupt_SpeedometerSignal |
| `$01D0` | `ScaledDistPWForCruiseControl` | 8 | 1 | CODEf101, CheckConditionsForDeltaRPMRetard, CheckErrorMaskingAndSetCodes_MM | CODEf101 |
| `$01D1` | `OutputDriverStatus` | 2 | 1 | CODEf101 | SendOutputDriverByte |
| `$01D2` | `FaultMask_01D2` | 8 | 2 | CheckErrorMaskingAndSetCodes_MM | CheckErrorMaskingAndSetCodes_MM |
| `$01D3` | `FaultMask_01D3` | 6 | 2 | CheckErrorMaskingAndSetCodes_MM | CheckErrorMaskingAndSetCodes_MM |
| `$01D4` | `FaultMask_01D4` | 2 | 4 | CheckErrorMaskingAndSetCodes_MM | CheckErrorMaskingAndSetCodes_MM |
| `$01D5` | `FaultMask_01D5` | 2 | 3 | CheckErrorMaskingAndSetCodes_MM | CheckErrorMaskingAndSetCodes_MM |
| `$01D6` | `FaultMask_01D6` | 3 | 1 | CheckErrorMaskingAndSetCodes_MM | CheckErrorMaskingAndSetCodes_MM |
| `$01D7` | `FaultMask_01D7` | 3 | 1 | CheckErrorMaskingAndSetCodes_MM | CheckErrorMaskingAndSetCodes_MM |
| `$01D8` | `FaultMask_01D8` | 2 | 2 | CheckErrorMaskingAndSetCodes_MM | CheckErrorMaskingAndSetCodes_MM |
| `$01D9` | `FaultMask_01D9` | 2 | 4 | CheckErrorMaskingAndSetCodes_MM | CheckErrorMaskingAndSetCodes_MM |
| `$01DA` | `FaultMask_01DA` | 1 | 3 | CheckErrorMaskingAndSetCodes_MM | CheckErrorMaskingAndSetCodes_MM |
| `$01DB` | `Counter_ACControl1` | 2 | 3 | AC_Rout11, CODE26ed | AC_Rout11, CODE26ed, DRB_SomethingLikeEMR_MM |
| `$01DC` | `Var_01DC` | 2 | 0 | CODEe74f_MM, Check01DCStatus_SM |  |
| `$01DF` | `IdleTarget_01DF` | 1 | 2 | CalculateTargetIdleSpeed_MM | CalculateTargetIdleSpeed_MM |
| `$01E1` | `CcdRxValueA` | 4 | 2 | AisState14_SpeedControl, CalculateAisPosition2, CalculateTargetIdleSpeed_MM | CcdRx_4, Set_ErrorBits_3_MM |
| `$01E2` | `CcdRxValueB` | 3 | 1 | CalculateTargetIdleSpeed_MM, SomethingWithAIS_MM | CcdRx_8 |
| `$01E3` | `Var_01E3` | 5 | 2 | MonitorSecondaryAir, PTELookupLatency | PTELookupLatency |
| `$01E4` | *без имени* | 4 | 2 | PTELookupLatency | PTELookupLatency |
| `$01E5` | `Pte_01E5` | 1 | 1 | PTELookupLatency | PTELookupLatency |
| `$01E6` | `Var_01E6` | 1 | 1 | CODE8059_MM | PTELookupLatency |
| `$01E7` | `Var_01E7` | 4 | 4 | ExhGasRecirc_MM, MonitorSecondaryAir | ExhGasRecirc_MM |
| `$01E8` | `Egr_01E8` | 3 | 5 | ExhGasRecirc_MM | ExhGasRecirc_MM |
| `$01E9` | `Egr_01E9` | 2 | 3 | ExhGasRecirc_MM | ExhGasRecirc_MM |
| `$01EA` | `Purge_01EA` | 4 | 3 | ControlPurgeSolenoid_MM | ControlPurgeSolenoid_MM |
| `$01EB` | `Var_01EB` | 4 | 5 | ControlPurgeSolenoid_MM | ControlPurgeSolenoid_MM, IncludeCylTrimWithAdaptiveCells |
| `$01EC` | `Purge_01EC` | 1 | 4 | ControlPurgeSolenoid_MM | ControlPurgeSolenoid_MM |
| `$01ED` | `Var_01ED` | 0 | 1 |  | IncludeCylTrimWithAdaptiveCells |
| `$01EE` | `Unref_01EE` | 0 | 0 |  |  |
| `$01EF` | `Var_01EF` | 3 | 5 | Set_ErrorBits_3_MM, SomethingWithAIS_MM | CODEe72a, CcdRx_4, Set_ErrorBits_3_MM, SomethingWithAIS_MM, StoreMAPVoltsAndCalcMAPValue |
| `$01F0` | `O2RespSpeedTimer` | 2 | 5 | MonitorO2Response | MonitorO2Response |
| `$01F1` | `O2RespSampleCount` | 1 | 2 | MonitorO2Response | MonitorO2Response |
| `$01F2` | `O2RespElapsed` | 6 | 2 | MonitorO2Response | MonitorO2Response |
| `$01F3` | `Var_01F3` | 1 | 3 | MonitorO2Response | MonitorO2Response, SwitchOrStayOpenLoop |
| `$01F4` | `O2RespSwitches` | 2 | 2 | MonitorO2Response | MonitorO2Response |
| `$01F5` | `O2RespSteps` | 2 | 2 | MonitorO2Response | MonitorO2Response |
| `$01F6` | *без имени* | 2 | 2 | MonitorO2Response | MonitorO2Response |
| `$01F7` | `O2RespStepsTotal` | 2 | 3 | MonitorO2Response | MonitorO2Response |
| `$01F8` | `MonO2Resp_01F8` | 2 | 3 | MonitorO2Response | MonitorO2Response |
| `$01F9` | `O2RespSwitchesTotal` | 2 | 3 | MonitorO2Response | MonitorO2Response |
| `$01FA` | `O2RespLastVolts` | 1 | 2 | MonitorO2Response | MonitorO2Response |
| `$01FB` | `CounterX` | 8 | 28 | AisState12_ThrottleOpen, AisState13_ClosedThrottle, AisState14_SpeedControl, ControlFan_MM, IncrementCounter01fb_MM | CODE2bb4, CODE2bca, CODE2cbb, CODE2d51, CODE2dd6 … |
| `$01FC` | `AcState` | 44 | 27 | AC_Rout11, AC_Rout12, AC_Rout13, AC_Rout15, AC_Rout16 … | AC_Rout1, AC_Rout10, AC_Rout11, AC_Rout12, AC_Rout13 … |
| `$01FD` | `CoolantTempStatusFlags` | 25 | 4 | AC_Rout11, AR_Rout4, CODE26ed, CODE2aeb, CODE2b88 … | Check01DCStatus_SM, CheckCoolantTempStatus2_SM, CheckCoolantTempStatus_SM, CheckSpeedStatus_SM |
| `$01FE` | `Fan_01FE` | 2 | 6 | CODE2dd6, ControlFan_MM | CODE2bca, CODE2cbb, CODE2d51, CODE2dd6, ControlFan_MM |
| `$01FF` | `AcTimer` | 5 | 10 | AC_Rout3, AC_Rout8, CODE2609 | AC_Rout3, AC_Rout5, AC_Rout5_25F0, AC_Rout7, AC_Rout8 … |
| `$0200` | `Timer_RadSteamingCountdown` | 1 | 2 | ControlFan_MM | ControlFan_MM, StoreMAPVoltsAndCalcMAPValue |
| `$0201` | `MonEvap_0201` | 4 | 1 | MonitorEvapPurgeFlow | StoreMAPVoltsAndCalcMAPValue |
| `$0202` | `EvapStartDelay` | 1 | 2 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$0203` | `EvapBaselineTime` | 2 | 2 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$0204` | `EvapBaseAisPos` | 1 | 1 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$0205` | `EvapBaseO2Trim` | 3 | 2 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$0206` | `EvapBaseRpm` | 3 | 2 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$0207` | *без имени* | 2 | 2 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$0208` | `EvapTestO2Trim` | 2 | 2 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$0209` | `EvapTestRpm` | 2 | 2 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$020A` | *без имени* | 1 | 2 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$020B` | `EvapPurgeDuty` | 5 | 3 | ControlPurgeSolenoid_MM, MonitorEvapPurgeFlow | ControlPurgeSolenoid_MM, MonitorEvapPurgeFlow |
| `$020C` | `MonEvap_020C` | 3 | 1 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$020D` | `Var_020D` | 3 | 5 | AIS_Subroutine_12, StoreKnockVoltsAvgCounter | AIS_Subroutine_12, CheckAndSetMinSparkAdvance |
| `$020E` | `Timer_DelayBeforeUpdating_MINTHR` | 1 | 3 | CheckThrottle_AtFullThrottle | CheckThrottle_AtFullThrottle, StoreMAPVoltsAndCalcMAPValue |
| `$020F` | `Var_020F` | 1 | 2 | CheckThrottle_AtFullThrottle | CheckThrottle_AtFullThrottle, StoreMAPVoltsAndCalcMAPValue |
| `$0210` | `MonFuelSys_0210` | 1 | 2 | MonitorFuelSystemRich | MonitorFuelSystemRich |
| `$0211` | `Var_0211` | 3 | 2 | CODE7886, CalculatePartThrottleEnrichmentAndLatency_MM | CODE7886 |
| `$0212` | *без имени* | 3 | 2 | CODE7886, CalculatePartThrottleEnrichmentAndLatency_MM | CODE7886 |
| `$0213` | `Code7886_0213` | 1 | 4 | CODE7886 | CODE7886, StoreMAPVoltsAndCalcMAPValue |
| `$0214` | *без имени* | 1 | 4 | CODE7886 | CODE7886, StoreMAPVoltsAndCalcMAPValue |
| `$0215` | `Counter_BatteryVoltsOK` | 2 | 2 | IncrementBatteryVoltsOKCounter_MM | IncrementBatteryVoltsOKCounter_MM |
| `$0216` | `CcdRxTimeout` | 1 | 2 | Set_ErrorBits_3_MM | CcdRx_4, Set_ErrorBits_3_MM |
| `$0217` | `Var_0217` | 2 | 2 | CODEe74f_MM | CODEe74f_MM |
| `$0218` | `Var_0218` | 3 | 2 | CODE600e_SM, CODE7242_SM, CheckStuffAndSetStatusFlags_SM | CODE7242_SM, StoreMAPVoltsAndCalcMAPValue |
| `$0219` | `ObdMapValue` | 2 | 1 | CaptureFreezeFrame, ObdPid0B_Map | TurnAlternatorOff |
| `$021A` | `CoolantTempVolts` | 2 | 2 | CaptureFreezeFrame, ObdPid05_Coolant | CheckAndFilterCoolantTempSensor_SM, StoreMAPVoltsAndCalcMAPValue |
| `$021B` | `ChargeTempVolts` | 1 | 2 | ObdPid0F_IntakeAirTemp | CheckAndFilterChargeTempSensor_SM, StoreMAPVoltsAndCalcMAPValue |
| `$021C` | `DrbRamBuffer` | 0 | 1 |  | DRB_UseRAM2ForSpecialProgramRoutine |
| `$021E` | `DrbRamProgramEntry` | 1 | 0 | DRB_UseRAM2ForSpecialProgramRoutine |  |

## Регистры внешнего устройства ввода-вывода ($0400-$0437)

| Адрес | Имя | R | W | Читают | Пишут |
|---|---|---|---|---|---|
| `$0400` | `SwitchPortAccessReg1` | 12 | 0 | CODE64ea_SM, CODEe74f_MM, CrankInterrupt_HandleCamSensorRisingEdgeA, GetControlFeedback_DetermineIfShutdownRequired_MM, IncludeInjectorLatency … |  |
| `$0401` | `SwitchPortAccessReg2` | 6 | 0 | ATM_Tachometer, PTELookupLatency, VerifyOperationOfFuelInjectorDrivers_MM |  |
| `$0403` | `IODev_0403` | 0 | 1 |  | ATM_Tachometer |
| `$0409` | `IODev_0409` | 4 | 3 | ControlCruiseServo0_MM, IncrementOrClearDiagFaultCounter_SM, MainSubLoop, ResetCOPTimer | MainSubLoop, ResetCOPTimer |
| `$0410` | `IODev_InjectorCommand` | 1 | 4 | VerifyOperationOfFuelInjectorDrivers_MM | CALC_SPARK_RETARD_BASED_ON_KNOCK_VOLT, CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency, VerifyOperationOfFuelInjectorDrivers_MM |
| `$0418` | `IODev_0418` | 0 | 1 |  | CrankMapRpmUpdate |
| `$0419` | *без имени* | 0 | 1 |  | CrankMapRpmUpdate |
| `$0424` | `InjectorPulsewidth_HB_Cyl1` | 1 | 2 | PTELookupLatency | IncludeInjectorLatency, PTELookupLatency |
| `$0425` | *без имени* | 1 | 2 | PTELookupLatency | IncludeInjectorLatency, PTELookupLatency |
| `$0428` | `InjectorPulsewidth_HB_Cyl2` | 1 | 2 | PTELookupLatency | IncludeInjectorLatency, PTELookupLatency |
| `$0429` | *без имени* | 1 | 2 | PTELookupLatency | IncludeInjectorLatency, PTELookupLatency |
| `$042C` | `InjectorPulsewidth_HB_Cyl3` | 1 | 2 | PTELookupLatency | IncludeInjectorLatency, PTELookupLatency |
| `$042D` | *без имени* | 1 | 2 | PTELookupLatency | IncludeInjectorLatency, PTELookupLatency |
| `$0430` | `InjectorPulsewidth_HB_Cyl4` | 1 | 2 | PTELookupLatency | IncludeInjectorLatency, PTELookupLatency |
| `$0431` | *без имени* | 1 | 2 | PTELookupLatency | IncludeInjectorLatency, PTELookupLatency |

## Внешнее ОЗУ (от $0438)

| Адрес | Имя | R | W | Читают | Пишут |
|---|---|---|---|---|---|
| `$0438` | `MonMisfire_0438` | 3 | 2 | ObdMisfireMilLogic | ObdMisfireMilLogic |
| `$0439` | `MonMisfire_0439` | 3 | 3 | ObdMisfireMilLogic | ObdMisfireMilLogic |
| `$043B` | `FuelSystemStatus` | 2 | 5 | CaptureFreezeFrame, ObdPid03_FuelSystem | HandleAmTimer_MM, HandleO2Processing_MM, O2_UsingFeedback, SwitchOrStayOpenLoop |
| `$043C` | `MaxRPMxMaxMAPFraction` | 2 | 1 | CaptureFreezeFrame, ObdPid04_Load | CalculateMaxRPMxMaxMAPFraction_MM |
| `$043E` | `CatTestTimer` | 1 | 2 | MonitorCatalyst | MonitorCatalyst |
| `$043F` | *без имени* | 1 | 2 | MonitorCatalyst | MonitorCatalyst |
| `$0440` | `CatSettleTimer` | 1 | 3 | MonitorCatalyst | MonitorCatalyst |
| `$0441` | *без имени* | 1 | 3 | MonitorCatalyst | MonitorCatalyst |
| `$0442` | `CatWarmupEstimate` | 2 | 2 | MonitorCatalyst | MonitorCatalyst |
| `$0443` | `Var_0443` | 1 | 2 | SwitchOrStayOpenLoop | MonitorCatalyst, SwitchOrStayOpenLoop |
| `$0444` | `Var_0444` | 1 | 2 | SwitchOrStayOpenLoop | MonitorCatalyst, SwitchOrStayOpenLoop |
| `$0445` | `Var_0445` | 2 | 2 | MonitorCatalyst, SwitchOrStayOpenLoop | MonitorCatalyst, SwitchOrStayOpenLoop |
| `$0446` | `Var_0446` | 2 | 2 | MonitorCatalyst, SwitchOrStayOpenLoop | MonitorCatalyst, SwitchOrStayOpenLoop |
| `$0447` | `Crank_0447` | 7 | 2 | CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency | IncludeInjectorLatency, StoreMAPVoltsAndCalcMAPValue |
| `$0448` | `Var_0448` | 1 | 1 | IncludeInjectorLatency | PTELookupLatency |
| `$0449` | `CrankEventCounter` | 3 | 5 | CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency, Isr_PAI_CamPhase | CrankInterrupt_FallingEdge, Isr_PAI_CamPhase, Isr_TIC1_CrankEvent |
| `$044A` | `Pte_044A` | 1 | 1 | PTELookupLatency | PTELookupLatency |
| `$044B` | `Pte_044B` | 1 | 1 | PTELookupLatency | PTELookupLatency |
| `$044C` | `MAPTemp44c` | 2 | 2 | PTELookupLatency | PTELookupLatency, StoreMAPVoltsAndCalcMAPValue |
| `$044D` | `Pte_044D` | 2 | 1 | PTELookupLatency | PTELookupLatency |
| `$044E` | `Var_044E` | 1 | 1 | VerifyOperationOfFuelInjectorDrivers_MM | CrankInterrupt_HandleCamSensorRisingEdgeA |
| `$044F` | `AISEnleanmentPW` | 1 | 2 | IncludeInjectorLatency | TransFuel_StoreLeanOutFactor |
| `$0450` | `Counter_FuelEngRunning_0450` | 3 | 5 | CrankInterrupt_CalculateFuel, CrankInterrupt_HandleCamSensorRisingEdgeA, IncludeInjectorLatency | ControlEngineCutout_MM, CrankInterrupt_CalculateFuel, CrankInterrupt_FallingEdge, Cutout_CheckRevLimitingValues, ShutOffEngineForThisRotation |
| `$0451` | `DeltaToDesiredAISPos` | 2 | 2 | TransFuel_StoreLeanOutFactor | TransFuel_StoreLeanOutFactor |
| `$0452` | `FuelPressureFactor` | 2 | 1 | IncludeInjectorLatency, PTELookupLatency | CalculateSumOfAllFuelModifiers_MM |
| `$0453` | `Toc1_0453` | 2 | 1 | CODE1265 | CODE1265 |
| `$0454` | `LoopTimeWorst` | 1 | 1 | MainProgramLoop | MainProgramLoop |
| `$0455` | `LoopTimeLast` | 0 | 1 |  | MainProgramLoop |
| `$0456` | `Var_0456` | 2 | 2 | CrankMapRpmUpdate, HandleO2Processing_MM | CrankMapRpmUpdate |
| `$0457` | `MapRpm_0457` | 1 | 2 | CrankMapRpmUpdate | CrankMapRpmUpdate |
| `$0458` | `MapRpm_0458` | 4 | 2 | CrankMapRpmUpdate | CrankMapRpmUpdate |
| `$0459` | `O2RespAcDelay` | 1 | 2 | MonitorO2Response | MonitorO2Response |
| `$045A` | `ObdTrimSettleTimer` | 2 | 3 | CrankInterrupt_CalculateFuel, MonitorFuelSystemRich | CODE6b1d, CODE6b91, CrankInterrupt_CalculateFuel |
| `$045B` | `DsO2_045B` | 2 | 6 | VerifyOperationOfDownstreamO2Sensor_MM | VerifyOperationOfDownstreamO2Sensor_MM |
| `$045C` | `Var_045C` | 3 | 2 | CODE1f17, VerifyOperationOfDownstreamO2Sensor_MM | VerifyOperationOfDownstreamO2Sensor_MM |
| `$045D` | `MAPTemp_A` | 3 | 5 | HandleBaroReadRequirement_MM, ScheduleIgnitionCoils, TurnAlternatorOff | ResetInterrupt, ScheduleIgnitionCoils, StoreMAPVoltsAndCalcMAPValue, TurnAlternatorOff |
| `$045E` | `MAPTemp_B` | 3 | 4 | HandleBaroReadRequirement_MM, ScheduleIgnitionCoils, TurnAlternatorOff | ResetInterrupt, ScheduleIgnitionCoils, StoreMAPVoltsAndCalcMAPValue, TurnAlternatorOff |
| `$045F` | `Var_045F` | 3 | 3 | ExhGasRecirc_MM, ScheduleIgnitionCoils | ExhGasRecirc_MM, ScheduleIgnitionCoils |
| `$0460` | `Egr_0460` | 1 | 2 | ExhGasRecirc_MM | ExhGasRecirc_MM, StoreMAPVoltsAndCalcMAPValue |
| `$0461` | `BadMAPCOunter` | 2 | 1 | CheckForBadMAP, IncrementBadMAPCounter_MM | IncrementBadMAPCounter_MM |
| `$0462` | `MonFuelSys_0462` | 1 | 2 | MonitorFuelSystemRich | MonitorFuelSystemRich |
| `$0463` | `MonEvap_0463` | 3 | 3 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$0468` | `EvapStartBattVolts` | 1 | 1 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$0469` | `EvapStartVar0183` | 1 | 1 | MonitorEvapPurgeFlow | MonitorEvapPurgeFlow |
| `$046C` | `Var_046C` | 1 | 1 | CODEa373 | CODEa373 |
| `$046D` | `SomethingForCruise` | 2 | 3 | CODEf101 | CODEf101 |
| `$046E` | `Ais_046E` | 5 | 1 | AIS_Subroutine_12, AisState14_SpeedControl, CalculateAISPosition3, CalculateAisPosition1 | ControlAIS_MM |
| `$046F` | `Var_046F` | 3 | 1 | ControlAIS_MM, Cutout_UseHysteresisToDetermineWhenToTurnFuelBackOn, TurnAlternatorOff | TurnAlternatorOff |
| `$0470` | `Var_0470` | 1 | 3 | CalculateSumOfAllFuelModifiers_MM | CalculateSumOfAllFuelModifiers_MM, IncludeCylTrimWithAdaptiveCells |
| `$0471` | `Var_0471` | 2 | 2 | CalculateSumOfAllFuelModifiers_MM | CalculateSumOfAllFuelModifiers_MM, IncludeCylTrimWithAdaptiveCells |
| `$0472` | `Var_0472` | 2 | 2 | CalculateSumOfAllFuelModifiers_MM | CalculateSumOfAllFuelModifiers_MM, IncludeCylTrimWithAdaptiveCells |
| `$0473` | `Fan_0473` | 1 | 5 | CODE2aeb | CODE2aeb, CODE2c0d, CODE2ce5 |
| `$0474` | `ValueFromAdaptiveMemory_0474` | 2 | 1 | CalculateSumOfAllFuelModifiers_MM | CalculateSumOfAllFuelModifiers_MM |
| `$0475` | `MapRpm_0475` | 1 | 2 | CrankMapRpmUpdate | CrankMapRpmUpdate |
| `$0476` | `Var_0476` | 3 | 1 | CrankMapRpmUpdate | LookupValueFor0476_SM |
| `$0477` | `Code8059_0477` | 5 | 1 | CODE8059_MM | CODE8059_MM |
| `$0478` | `Crank_0478` | 4 | 9 | CrankInterrupt_FallingEdge, CrankInterrupt_HandleCamSensorRisingEdgeA, Isr_TIC1_CrankEvent | CrankInterrupt_FallingEdge, Isr_TIC1_CrankEvent, Isr_TIC3, Isr_TOF |
| `$0479` | `Crank_0479` | 2 | 2 | CrankInterrupt_HandleCamSensorRisingEdgeA, Isr_TIC1_CrankEvent | CrankInterrupt_FallingEdge, Isr_TIC1_CrankEvent |
| `$047A` | *без имени* | 2 | 2 | CrankInterrupt_HandleCamSensorRisingEdgeA, Isr_TIC1_CrankEvent | CrankInterrupt_FallingEdge, Isr_TIC1_CrankEvent |
| `$047B` | `Crank_047B` | 4 | 6 | CODE8059_MM, CrankInterrupt_CalculateFuel, CrankInterrupt_FallingEdge | CODE8059_MM, CrankInterrupt_CalculateFuel, CrankInterrupt_FallingEdge, Isr_PAOV |
| `$047C` | *без имени* | 1 | 1 | CODE8059_MM | CrankInterrupt_FallingEdge |
| `$047D` | `Var_047D` | 1 | 1 | Set_ErrorBits_20_MM | CrankInterrupt_CalculateFuel |
| `$047E` | `CounterOperatingNormal` | 1 | 2 | IncrementOrClearNormalOpCounter_SM | IncrementOrClearNormalOpCounter_SM |
| `$0480` | `AltSerial_0480` | 1 | 2 | CODE6cc4 | AltSerialComsRoutine, CODE6cc4 |
| `$0481` | `DrbOverrideTarget` | 4 | 4 | ControlPurgeSolenoid_MM, ExhGasRecirc_MM, MonitorEgrFlow | EraseErrorCodes, IncrementCounter0483_MM |
| `$0482` | `DrbOverrideState` | 4 | 4 | ControlPurgeSolenoid_MM, ExhGasRecirc_MM, MonitorEgrFlow | EraseErrorCodes, IncrementCounter0483_MM |
| `$0483` | `Var_0483` | 1 | 2 | IncrementCounter0483_MM | EraseErrorCodes, IncrementCounter0483_MM |
| `$0484` | `Var_0484` | 0 | 1 |  | O2_UsingFeedback |
| `$0485` | `IsoStep` | 1 | 32 | ISODiagnosticComs_18 | ISODiagnosticComs_1, ISODiagnosticComs_10, ISODiagnosticComs_11, ISODiagnosticComs_12, ISODiagnosticComs_13 … |
| `$0486` | `ISODiagTestOffset` | 1 | 29 | HanldeISODiagnosticComs | ISODiagnosticComs_1, ISODiagnosticComs_10, ISODiagnosticComs_11, ISODiagnosticComs_12, ISODiagnosticComs_13 … |
| `$0487` | `IsoRxEndPtr` | 8 | 2 | ISODiagnosticComs_18, IsoValidateRequest | ISODiagnosticComs_1, ISODiagnosticComs_18 |
| `$0488` | *без имени* | 8 | 2 | ISODiagnosticComs_18, IsoValidateRequest | ISODiagnosticComs_1, ISODiagnosticComs_18 |
| `$0489` | `Iso_0489` | 1 | 2 | ISODiagnosticComs_9 | CODE1f17, ISODiagnosticComs_9 |
| `$048A` | *без имени* | 1 | 2 | ISODiagnosticComs_9 | CODE1f17, ISODiagnosticComs_9 |
| `$048B` | `Iso_048B` | 3 | 1 | CODE1f17, ISODiagnosticComs_9 | CODE1f17 |
| `$048C` | *без имени* | 3 | 1 | CODE1f17, ISODiagnosticComs_9 | CODE1f17 |
| `$048D` | `IsoTimer` | 3 | 4 | DecrementCounter048D_SM, ISODiagnosticComs_1, ISODiagnosticComs_14 | DecrementCounter048D_SM, ISODiagnosticComs_18, ISODiagnosticComs_2, ISODiagnosticComs_9 |
| `$048E` | `IsoReqHeader1` | 3 | 5 | ISODiagnosticComs_13, IsoValidateRequest | ISODiagnosticComs_11, ISODiagnosticComs_13, ISODiagnosticComs_14, IsoBuildResponse |
| `$048F` | `IsoReqHeader2` | 4 | 6 | ISODiagnosticComs_11, ISODiagnosticComs_12, IsoValidateRequest | ISODiagnosticComs_11, ISODiagnosticComs_12, ISODiagnosticComs_13, IsoBuildResponse |
| `$0490` | `IsoReqSource` | 2 | 3 | ISODiagnosticComs_12, IsoValidateRequest | ISODiagnosticComs_11, ISODiagnosticComs_12, IsoBuildResponse |
| `$0491` | `IsoReqService` | 4 | 9 | ISODiagnosticComs_12, ISODiagnosticComs_18, IsoBuildResponse, IsoValidateRequest | CODE1f17, ISODiagnosticComs_11, ISODiagnosticComs_12, ISODiagnosticComs_9 |
| `$0492` | `IsoReqPid` | 6 | 11 | CODE1f17, ISODiagnosticComs_12, IsoValidateRequest | CODE1f17, ISODiagnosticComs_11, ISODiagnosticComs_12 |
| `$0493` | `IsoRespData1` | 8 | 28 | CODE1f17, IsoValidateRequest | CODE1f17, ObdPid00_Supported, ObdPid01_MonitorStatus, ObdPid03_FuelSystem, ObdPid04_Load … |
| `$0494` | `IsoRespData2` | 0 | 26 |  | CODE1f17, CODE2395, CODE23a6, CODE23b2, CODE23c3 … |
| `$0495` | `IsoRespData3` | 0 | 16 |  | CODE1f17, CODE2395, CODE23fa, ErrorCodeRoutine_Unused, ObdFfPid00_Supported … |
| `$0496` | `IsoRespData4` | 0 | 12 |  | CODE1f17, ObdFfPid00_Supported, ObdPid00_Supported, ObdPid01_MonitorStatus |
| `$0497` | `IsoRespData5` | 0 | 6 |  | CODE1f17, ObdFfPid00_Supported |
| `$0498` | `Iso_0498` | 1 | 1 | ErrorCodeRoutine_Unused | ErrorCodeRoutine_Unused |
| `$0499` | `Iso_0499` | 9 | 6 | CODE1f17, ErrorCodeRoutine_Unused | CODE1f17, ErrorCodeRoutine_Unused |
| `$049A` | `Iso_049A` | 2 | 5 | CODE1f17, ISODiagnosticComs_9 | CODE1f17, ISODiagnosticComs_11 |
| `$049B` | `DrbIII_049B` | 1 | 3 | XmitRequestedRamLocation_DRBIII | XmitRequestedRamLocation_DRBIII |
| `$049C` | `DrbIII_049C` | 1 | 2 | XmitRequestedRamLocation_DRBIII | XmitRequestedRamLocation_DRBIII |
| `$049D` | `DrbIII_049D` | 1 | 1 | XmitRequestedRamLocation_DRBIII | XmitRequestedRamLocation_DRBIII |
| `$049E` | `BitFlags049E` | 26 | 14 | AdaptiveMemory_UpdateCellIfRequired, CheckSpeedAndSomething_SM, CheckThrottleRoutine_MM, DIDNT_2SCOMPLEMENT_OVERFLOW_UNDERFLOW1, DRBIISerialCommunications_MM … | CheckSpeedAndSomething_SM, FurtherMAPAndBaroDiagnostics2_SM, ISODiagnosticComs_14, MonitorSecondaryAir, O2_UsingFeedback … |
| `$049F` | `DiagCounter_FaultCondition` | 1 | 2 | IncrementOrClearDiagFaultCounter_SM | IncrementOrClearDiagFaultCounter_SM |
| `$04A0` | `Var_04A0` | 0 | 2 |  | FurtherMAPAndBaroDiagnostics2_SM |
| `$04A1` | `MonSecAir_04A1` | 1 | 3 | MonitorSecondaryAir | MonitorSecondaryAir |
| `$04A2` | `MonSecAir_04A2` | 1 | 3 | MonitorSecondaryAir | MonitorSecondaryAir |
| `$04A3` | `MonSecAir_04A3` | 4 | 9 | MonitorSecondaryAir | MonitorSecondaryAir |
| `$04A4` | `MonSecAir_04A4` | 4 | 9 | MonitorSecondaryAir | MonitorSecondaryAir |
| `$04A5` | `MonSecAir_04A5` | 2 | 24 | MonitorSecondaryAir | MonitorSecondaryAir |
| `$04A6` | `MonSecAir_04A6` | 4 | 10 | MonitorSecondaryAir | MonitorSecondaryAir |
| `$04A7` | `MonSecAir_04A7` | 4 | 7 | MonitorSecondaryAir | MonitorSecondaryAir |
| `$04A8` | `MonSecAir_04A8` | 1 | 4 | MonitorSecondaryAir | MonitorSecondaryAir |
| `$04A9` | `PreviousInjectorPWMaybe` | 1 | 1 | MonitorSecondaryAir | MonitorSecondaryAir |
| `$04AA` | *без имени* | 1 | 1 | MonitorSecondaryAir | MonitorSecondaryAir |
| `$04AB` | `MonSecAir_04AB` | 2 | 3 | MonitorSecondaryAir | MonitorSecondaryAir |
| `$04AD` | `Var_04AD` | 2 | 2 | CrankInterrupt_CalculateFuel, MonitorSecondaryAir | CrankInterrupt_CalculateFuel, MonitorSecondaryAir |
| `$04AE` | `Var_04AE` | 2 | 2 | AC_Rout7, DecrementCounter04ae_SM | DecideToUseDecelFuelCut, DecrementCounter04ae_SM |
| `$04AF` | `EgrMonFailCount` | 1 | 1 | CODE6b91 | CODE6b91 |
| `$04B0` | `FuelSysHealCounter` | 2 | 9 | MonitorFuelSystemLean, MonitorFuelSystemRich | CODEa68d, MonitorFuelSystemLean, MonitorFuelSystemRich |
| `$04B1` | `Pte_04B1` | 4 | 2 | CalculatePartThrottleEnrichmentAndLatency_MM | CalculatePartThrottleEnrichmentAndLatency_MM |
| `$04B2` | `Var_04B2` | 2 | 0 | DIDNT_2SCOMPLEMENT_OVERFLOW_UNDERFLOW1 |  |
| `$04B3` | `DiagCounter_DSO2SensorSigned` | 4 | 2 | DIDNT_2SCOMPLEMENT_OVERFLOW_UNDERFLOW1, DecrementDSO2SensorDiagnosticCounter_MM, MonitorSecondaryAir | DecrementDSO2SensorDiagnosticCounter_MM, MonitorSecondaryAir |
| `$04B4` | `DiagCounter_DSO2SensorDiagnostics` | 1 | 3 | DecrementDSO2SensorDiagnosticCounter_MM | DecrementDSO2SensorDiagnosticCounter_MM, MonitorSecondaryAir |
| `$04B5` | `DiagCounter_KnockSensorActive` | 1 | 2 | IncrementOrClearKnockDiagCounter_SM | IncrementOrClearKnockDiagCounter_SM |
| `$04B6` | `SystemStatusFlag_4b6` | 27 | 15 | CODE600e_SM, CODE7242_SM, CalculateTargetIdleSpeed_MM, CalculateVariableRevLimit_MM, CheckAnalog0170Limits2_SM … | CODE7242_SM, CalculateTargetIdleSpeed_MM, CheckAnalog0170Limits2_SM, CheckAnalog0170Limits_SM, CheckStuffAndSetStatusFlags_SM … |
| `$04B7` | `VarRevLimitCounterA` | 1 | 3 | StoreVariableRevLimit | StoreVariableRevLimit, TurnOffVariableRevLimit |
| `$04B8` | `VarRevLimitCounterB` | 1 | 2 | StoreVariableRevLimit | StoreVariableRevLimit, TurnOffVariableRevLimit |
| `$04B9` | `VariableRevLimit` | 2 | 9 | Cutout_DetermineLimpModeCutoutRPM, Cutout_SetOBCodeAndShutdown | CalculateVariableRevLimit_MM, StoreMAPVoltsAndCalcMAPValue, StoreVariableRevLimit, TurnOffVariableRevLimit, TurnOffVariableRevLimit2 … |
| `$04BA` | `VarRevLimitMAPRef` | 3 | 1 | StoreVariableRevLimit, TPSandMAP_OK, TurnOnVariableRevLimitNow | CalculateVariableRevLimit_MM |
| `$04BB` | `AsdVolts_04BB` | 4 | 3 | CODE7242_SM, CheckStuffAndSetStatusFlags_SM | CODE7242_SM |
| `$04BC` | `AsdVolts_04BC` | 1 | 2 | CheckStuffAndSetStatusFlags_SM | CODE7242_SM |
| `$04BD` | `AsdVolts_04BD` | 1 | 1 | CheckStuffAndSetStatusFlags_SM | CODE7242_SM |
| `$04BE` | `Timer_ThermostatDiagnostics` | 1 | 3 | VerifyOperationOfThermostat_MM | StoreMAPVoltsAndCalcMAPValue, UseDefaultCoolantTempLimpIn_MM, VerifyOperationOfThermostat_MM |
| `$04BF` | `DebugRAM` | 2 | 0 | AltSerialComsRoutine, TweakInjectorPW |  |
| `$04C0` | `DebugTemp0` | 1 | 0 | AltSerialComsRoutine |  |
| `$04C1` | `DebugTemp1` | 2 | 0 | TweakInjectorPW |  |
| `$04C2` | `DebugTemp2` | 1 | 0 | TweakInjectorPW |  |
| `$04C3` | `DebugTemp3` | 1 | 2 | AltSerialComsRoutine | AltSerialComsRoutine |
| `$04C4` | `DebugTemp4Counter` | 0 | 0 |  |  |
| `$083E` | `Unref_083E` | 0 | 0 |  |  |
