# Reading fuel trims (STFT / LTFT)
tags: fuel trim, lean, rich, P0171, P0172, P0174, P0175, vacuum leak, MAF

Short-term fuel trim (STFT) is the ECU's instant correction; long-term fuel trim (LTFT) is the learned correction. Positive values mean the ECU is adding fuel (it sees a lean mixture); negative means it is removing fuel (rich).

- Total trim (STFT + LTFT) within ±5 % is healthy, ±5-10 % worth watching, beyond ±10 % is a fault, and beyond about ±20-25 % the ECU sets P0171/P0174 (lean) or P0172/P0175 (rich).
- Compare at idle and at a steady 2500 rpm. Lean at idle that improves at 2500 rpm points to a vacuum leak, because a fixed leak is a bigger share of the small idle airflow. Lean everywhere, worse under load, points to fuel delivery (weak pump, clogged filter, low pressure) or a MAF under-reading.
- Both banks lean together means a shared cause (MAF, fuel pressure, PCV/brake booster leak). One bank only means a cause on that bank (intake gasket, injectors, exhaust leak before that O2 sensor).
- A slow upward drift of LTFT across several weeks of sessions is an early warning of a developing leak or a dirty MAF, often before any code is stored.

Cheap first steps: inspect the intake boot between MAF and throttle for cracks, check the PCV hose, clean the MAF with dedicated MAF cleaner, replace an old air filter. A smoke test finds the remaining vacuum leaks.
