# Catalytic converter efficiency (P0420 / P0430)
tags: P0420, P0430, catalyst, catalytic converter, O2 sensor, downstream, exhaust leak

The ECU judges the catalyst by comparing the upstream (sensor 1) and downstream (sensor 2) oxygen sensors. A working catalyst stores oxygen, so the downstream sensor stays fairly steady (about 0.6-0.75 V on a narrowband sensor) while the upstream one switches rapidly between 0.1 and 0.9 V. When the downstream signal starts to mirror the upstream one, oxygen storage is gone and P0420 (bank 1) or P0430 (bank 2) is stored.

Check before buying a converter:
1. Fix misfire and fuel-trim codes first. Misfires send raw fuel into the cat and overheat it, and a lean or rich engine skews the test.
2. Look for exhaust leaks ahead of or around the downstream sensor - outside air fools the sensor.
3. Watch both O2 sensors on live data at a steady 2500 rpm with a fully warm engine. If the downstream sensor is lazy, flat at 0.45 V, or reads oddly, test or replace it (cheap) before the converter.
4. A thermostat stuck open (P0128) can stop the monitor running correctly.

Converters typically wear out after 150 000-250 000 km. Aftermarket units are cheaper but some regions require OEM-grade or CARB-approved parts. After a repair, clear codes and drive a complete drive cycle so the catalyst readiness monitor completes.
