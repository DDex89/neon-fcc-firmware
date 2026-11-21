# Различия калибровок: 5269718 и 5007033

5269718: Chrysler factory 1995 Neon 2.0 DOHC manual 'Racing' calibration (rev B of 4874164)  
5007033: Mopar Performance 1995 Neon SOHC manual-transmission calibration

Код программы у обеих прошивок одинаковый, отличается только область калибровок. Ниже таблицы, в которых отличается хотя бы один байт.

| Адрес | Таблица | Изменено байт | Описание |
|---|---|---|---|
| `$B803` | `PARTNO2` | 1 | Part Number prefix. The 1st 4 digits of the Mopar PN for this ECU. |
| `$B804` | `PARTNO1` | 1 | Part Number prefix. The 1st 4 digits of the Mopar PN for this ECU. |
| `$B805` | `PARTNO0` | 1 | Part Number prefix. The 1st 4 digits of the Mopar PN for this ECU. |
| `$B806` | `PARTREV` | 1 | Revision Level |
| `$B808` | `RFINO2` | 1 | RFINO2 |
| `$B809` | `RFINO1` | 1 | RFINO1 |
| `$B80A` | `RFINO0` | 1 | RFINO0 |
| `$B80B` | `RFIREV` | 1 | RFIRevision |
| `$B80C` | `BITSUM` | 1 | ChecksumValue |
| `$B80D` | `CODE13` | 1 | CODE13 |
| `$B80F` | `CODE11_` | 1 | CODE11  |
| `$B811` | `CONFIG` | 1 | These are the factory configuration options. |
| `$B817` | `IPLMSK1` | 1 | Illuminate PowerLoss Light Mask1. These errors alert the driver. |
| `$B818` | `IPLMSK2` | 1 | Illuminate PowerLoss Light Mask2. These errors alert the driver. |
| `$B819` | `IPLMSK3` | 4 | Illuminate PowerLoss Light Mask3. These errors alert the driver. |
| `$B829` | `HOTMRP` | 245 | AdvanceFromMAPAndRPMWarmIdlePart |
| `$B94D` | `BASADV` | 36 | BaseAdvanceFromMAPandCoolant3D |
| `$B9D6` | `IDLADV` | 3 | IdleAdvanceFromCoolantTemp |
| `$B9E5` | `IDLAD2` | 6 | IdleAdvanceFromCoolantTemp2 |
| `$B9F9` | `SPKADD` | 13 | This is how much advance is added to increase engine speed. |
| `$BA0C` | `SPKRET` | 14 | This is how much advance is added to increase engine speed. |
| `$BA1F` | `SPKAD2` | 8 | This is how much advance is added to increase engine speed. |
| `$BA32` | `SPKRT2` | 6 | This is how much advance is added to increase engine speed. |
| `$BA5E` | `ADO2C2` | 6 | AdvanceAddedFromO2FeedbackCounter2 |
| `$BA8C` | `BASCHG` | 12 | Product is added to the coolant temp base advance. |
| `$BA9B` | `BASMAP` | 5 | Product is added to the coolant temp base advance. |
| `$BAAA` | `BASRPM` | 22 | Product is added to the coolant temp base advance. |
| `$BAC8` | `ILDMAP` | 6 | IdlePWFactorFromMAP |
| `$BACF` | `ADOTFN` | 10 | Added to the total advance. |
| `$BAE6` | `WOTMRP` | 144 | AdvanceFromMAPAndRPMWarmFull |
| `$BB89` | `KNARPM` | 1 | MinRPMForAverageKnockVoltCalc |
| `$BB8A` | `KNARPX` | 1 | MaxRPMForAverageKnockVoltCalc |
| `$BB8B` | `KNACLT` | 1 | MinCoolantTempForAverageKnockVoltCalc |
| `$BB8C` | `KNAIAT` | 1 | MinChargeTempForAverageKnockVoltCalc |
| `$BB93` | `DLTKNK` | 17 | Input from the knock sensor that is above this voltage is considered Knock. |
| `$BBB6` | `INNBNK` | 1 | KnockRetardIncrProduct NoBoostNoKnock |
| `$BBBE` | `MAXRTD` | 7 | MaximumKnockRetardPerCylinder |
| `$BBC9` | `RETMAX` | 7 | Maximum Knock Retard from Map |
| `$BBD4` | `ARMAP` | 6 | This table is reduced by the value in #002b (0, 1/4, 1/2, 3/4, or 1) depending on the boost control routine. And the result is subtracted from the advance calculated by 8010 or 805b |
| `$BBEF` | `ARRPM` | 6 | The result of this table is multiplied by #002b (0, 1/4, 1/2, 3/4, or 1) and subtracted from the table at #8098 |
| `$BC0A` | `ARMPIC` | 1 | ff disables the Adaptive Knock Retard |
| `$BC0B` | `ARINDX` | 1 | AdaptiveRetardIndexBase 80 |
| `$BC0E` | `ARTM5P` | 1 | AdaptiveRetardTimeOver5psiBoost |
| `$BC0F` | `TOTKRT` | 1 | TotalKnockRetardRef |
| `$BC10` | `ARMINT` | 1 | AdaptiveRetardMinimumTemp |
| `$BC24` | `RPMRT2` | 1 | RPMLimitForTPSRetard WithAR |
| `$BC27` | `TPSRT2` | 6 | Retard from deltaTPS. |
| `$BC33` | `MMPDRE` | 1 | MinimumMAPForDeltaRPMEvaluation |
| `$BC35` | `MSPDRE` | 1 | MinimumMPHForDeltaRPMEvaluation |
| `$BC3B` | `ICCNT2` | 101 | IdleControlCounterInit2 |
| `$BD6A` | `RETSPD` | 1 | Retard from Speed. |
| `$BDBC` | `STRTFL` | 10 | Start fuel uSec = [ STRTFL * STRTFL * (1 - STFBAR - STFTMP) * EPPMUL + (BATOFF * 4) ] * 4 |
| `$BDE3` | `STRLMT` | 1 | Coldest temperature accepted as input to STRTFL table - anything below this value will be replaced with this value |
| `$BDE4` | `STFLOI` | 6 | StartFuelOffIdleFactor fromRPM |
| `$BE0B` | `STFLID` | 6 | StartFuelIdleFactor fromRPM |
| `$BE41` | `EPPMUL` | 5 | Start fuel uSec = [ STRTFL * STRTFL * (1 - STFBAR - STFTMP) * EPPMUL + (BATOFF * 4) ] * 4. This table decreases fuel for each engine rotation while starting |
| `$BE96` | `SFDCAY` | 3 | Start fuel uSec = [ STRTFL * STRTFL * (1 - STFBAR - STFTMP) * EPPMUL + (BATOFF * 4) ] * 4. This allows fuel to decay gradually after the start-run transition. |
| `$BEA5` | `BATOFF` | 12 | Compensates for slower opening times of injectors with lower voltage. |
| `$BEC9` | `PRTTBL` | 279 | FuelFromRPMAndMAP |
| `$BFED` | `PTEADJ` | 107 | EnrichAdjust FromMap |
| `$C089` | `PTENRP` | 1 | EPP per amount for increasing multiplier |
| `$C08D` | `PTENUM` | 1 | No of PTENRD below PTELMT that PT enrich must be to return to HOTMAP spark advance after maxed out |
| `$C091` | `RPMMAP` | 4 | EPP Control toggle |
| `$C0A9` | `DLTPRP` | 1 | Throttle self calibration |
| `$C0B4` | `UNLOAD` | 17 | DeltaThrottleFrom MINTHR ToUnloadCrankingFuel |
| `$C0CA` | `WOTENR` | 152 | WOTEnrichmentFromRPMAndMAP |
| `$C166` | `CURV3D` | 69 | Fuel Modifier from coolant temp and time. |
| `$C1C3` | `CLDLDP` | 68 | Base Fuel Modifier for Off-Idle |
| `$C220` | `CLDLDI` | 68 | Base Fuel Modifier for Idle |
| `$C28D` | `BARENR` | 8 | Baro enrichment factor |
| `$C29C` | `BARMAP` | 5 | Baro enrichment factor multiplier from MAP |
| `$C2CA` | `AIRTMP` | 8 | Charge Temp Factor. Note that this is an unfiltered charge temp voltage, so higher numbers are lower temps |
| `$C2DD` | `AIRMAP` | 10 | Charge temp enrichment factor multiplier from MAP |
| `$C2E8` | `AIRRPM` | 6 | Charge temp enrichment factor multiplier from RPM |
| `$C2F5` | `POSSLP` | 4 | Throttle Transient Enrich PW Addition |
| `$C307` | `AESLOP` | 4 | Transient Enrichment PW Addition |
| `$C316` | `LOTTHR` | 4 | Decel leanout factor - THR based. When Y is zero, factor is 1.00 |
| `$C328` | `DECEL` | 8 | DecelLeanoutFactorMAP FromTemp |
| `$C457` | `CLTEMP` | 1 | Temperature to start CLTIME Timer - $94 = 70degreesF |
| `$C477` | `PRIRMP` | 32 | Lower RPM Boundary - RPM/32 |
| `$C4A3` | `SECRMP` | 21 | Lower RPM Boundary - RPM/32 |
| `$C4E0` | `MP2` | 1 | AutoCalMapCellBoundary1 |
| `$C4E1` | `MP3` | 1 | AutoCalMapCellBoundary1 |
| `$C4E3` | `MP5` | 1 | AutoCalMapCellBoundary1 |
| `$C4E4` | `DLTMAP` | 1 | Map Hysteresis At Map Cell Boundaries |
| `$C4EF` | `MAPDEC` | 1 | No Cell Update And O2CNTR Held Below This Map. Set to 0xff to disable O2 feedback. |
| `$C4F9` | `PEFMUL` | 13 | Pumping Efficiency multiplier from MAP |
| `$C51F` | `KNNRCH` | 1 | Multiplied by total knock to calculate knock enrich factor. |
| `$C520` | `MAXKNR` | 2 | Maximum knock enrich factor. |
| `$C528` | `DFS20M` | 1 | 20MPHDecelFuelShutoffSpeedLimitOFF |
| `$C529` | `DFS20L` | 1 | 20MPHDecelFuelShutoffSpeedLimitON |
| `$C53E` | `DFRPMX` | 9 | DecelFuelShutoffTurnonLimitFrom0x046f |
| `$C569` | `SPDLMH` | 1 | SpeedLimitFuelShutoff254mph |
| `$C56A` | `SPDLML` | 1 | SpeedLimitFuelShutoffRestore253mph |
| `$C56B` | `SPDRPM` | 1 | EngineSpeedHighLimitToEnableOverspeed |
| `$C56C` | `SPDRPM2` | 1 | EngineSpeedLowLimitToDisableOverspeed |
| `$C56F` | `REVLMT3` | 1 | MapAbove75PctAndIdleSwitchClosed2000 |
| `$C570` | `REVLMT4` | 1 | MapAbove75PctAndThrLimpin2000 |
| `$C571` | `REVLMT5` | 1 | RPMLimiterNormalOnRPM |
| `$C572` | `REVLMT6` | 1 | RPMLimiterNormalOffRPM |
| `$C574` | `RVLSPD` | 1 | CarSpeedForRevLimitWithTBOff |
| `$C578` | `DCLRPL` | 1 | Low RPM to activate decel fuel shutoff. Should be lower than shutoff RPM On point. |
| `$C57B` | `DFRPM1` | 2 | 2050RPM DecelFuelShutoffTurnonLimit |
| `$C57E` | `DLYRPM` | 1 | Decel AIS RPM trigger (third AIS delay) |
| `$C5A5` | `AISPN` | 5 | Idle Speed From Temp in park/neutral or manual trans |
| `$C5B0` | `AISCLD` | 9 | Idle Speed From temp in Drive, auto trans only |
| `$C64C` | `CLDPOS` | 13 | Cold OffIdle AIS Positioning, Increases instantly, decreases after DLYOFI |
| `$C672` | `BARAIS` | 12 | Barometric compensation factor for AIS control |
| `$C6AC` | `ACCTBL` | 14 | ACOffIdleDelta FromSpeed |
| `$C6BF` | `PERKCK` | 1 | AcClutchAisAdjustmentConstant |
| `$C6C0` | `OFFPER2` | 1 | AisInstantlyClosesWhenAcDisengages2 |
| `$C6C1` | `AMBAIS` | 93 | AmbientTempAISCompensation |
| `$C769` | `DCALRT` | 12 | DacalUpdateRate01 03 07 0f 1f 3f 7f ff |
| `$C779` | `AISINC` | 35 | AISPOSIncrementForSW2b7 |
| `$C7DB` | `DANOM2` | 2 | Base nominalCal2 |
| `$C7DD` | `DANOM` | 1 | Base nominalCal |
| `$C7ED` | `TEMPDC` | 6 | DecelAis FromTemp |
| `$C839` | `DCLMIN` | 2 | MinLimitOnDecelAisControlledMap |
| `$C83B` | `DLYTIM` | 16 | Decel AIS Delay after throttle closes when moving |
| `$C87E` | `RPMDLT` | 4 | RollingAisMinRpm |
| `$C882` | `ISPDCY` | 1 | RollingAisDecay |
| `$C883` | `DECAIS` | 2 | RollingAisUpdateRate 01 03 07 0f 1f 3f 7f ff |
| `$C893` | `FANTMP1` | 1 | Detailed Description3 |
| `$C894` | `FANTMP2` | 1 | Detailed Description3 |
| `$C895` | `FANTMP3` | 1 | Detailed Description3 |
| `$C896` | `FANTMP4` | 1 | Detailed Description3 |
| `$C897` | `FANTMP5` | 1 | Detailed Description3 |
| `$C898` | `FANTMP6` | 4 | Detailed Description3 |
| `$C998` | `CLTRMN` | 1 | MinimumCylinderTrim |
| `$CA70` | `SCNVLO` | 1 | CruiseControlForBrakeFlagManualTransmissionClutchDisableLo |
| `$CB26` | `MININC` | 1 | Amount MINTHR IsIncreasedAtKeyOnOnly |
| `$CB27` | `MAPTHR` | 1 | ThrottleSelfCalibrationMapDeltaThreshold |
| `$CB28` | `RPMTHR` | 1 | ThrottleSelfCalibrationRpmThreshold |
| `$CB31` | `EGR23` | 1 | ExhGasRecircConstFromMAP1 |
| `$CB32` | `EGR24` | 1 | ExhGasRecircConstFromMAP2 |
| `$CB35` | `EGR27` | 7 | ExhGasRecircConstFromCoolantTemp |
| `$CB46` | `EGR18` | 2 | ExhGasRecircConstLoLimit18 |
| `$CB48` | `EGR15` | 2 | ExhGasRecircConstFromRPMLoLimit15 |
| `$CB4A` | `EGR9` | 3 | ExhGasRecircConstFromTimeEngRunning9 |
| `$CB50` | `EGR16` | 1 | ExhGasRecircConstLoLimit16 |
| `$CB51` | `EGR16A` | 1 | ExhGasRecircConstHiLimit16a |
| `$CB52` | `EGR17A` | 1 | ExhGasRecircConstHiLimit17a |
| `$CB53` | `EGR19` | 1 | ExhGasRecircConstLoLimit19 |
| `$CB55` | `EGR6` | 1 | ExhGasRecircConst6 |
| `$CB57` | `SCRMP1` | 110 | SecondaryRampSubtractor1 |
| `$CDA8` | `COILHI` | 49 | HiLimitBatteryVoltsForCoilVerify |
| `$CF5D` | `RPMSCL` | 15 | Output is used as the input to the 3D tables |
| `$CFDF` | `RPMTHS` | 47 | AISPos from RPM |
| `$D423` | `FASTDA` | 6 | FastDataOutputAddressTable |
