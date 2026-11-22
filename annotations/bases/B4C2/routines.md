# B4C2-specific routine notes

Same format as annotations/routines.md, keyed by B4C2 addresses.

## 22E9 ObdPid14_O2Sensor1
Service 1 PID $14: upstream O2 voltage. [reviewed]

B4C2 sends the raw A/D byte of O2SensorVolts. The other code bases (B559, B4F3, B4CC) first scale it
by $03ED/256 to the J1979 unit of 5 mV per bit and send $FF from $41 up, so a scan tool reads B4C2's
O2 voltage about four times too low.

## 2301 ObdPid15_O2Sensor2
Service 1 PID $15: downstream O2 voltage. [reviewed]

Same as PID $14 for the downstream sensor ($016F): raw A/D byte, without the scaling of the other
code bases.
