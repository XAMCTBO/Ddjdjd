"""DTC knowledge base.

Two layers:
  1. CATALOG - hand-written entries for the most frequently seen generic codes,
     with ordered likely causes (most common / cheapest first), first checks,
     a severity and a rough repair cost range (USD, parts+labour, very
     approximate - shown to users as an estimate only).
  2. Range rules - every SAE J2012 code that isn't in CATALOG still gets the
     subsystem it belongs to and generic guidance, so nothing is "unknown".

Manufacturer-specific codes (P1xxx, P3xxx, B1xxx, C1xxx, U1xxx...) only get
subsystem-level info; the AI agents are told to say so rather than guess.
"""
from __future__ import annotations

# code: (description, system, severity, causes, first_checks, (cost_lo, cost_hi))
CATALOG: dict[str, tuple] = {
    # ---- fuel & air metering
    "P0100": ("Mass air flow (MAF) circuit malfunction", "fuel_air", "medium",
              ["Unplugged/corroded MAF connector", "Failed MAF sensor", "Wiring short/open"],
              ["Inspect connector", "Check MAF g/s at idle (≈ engine litres × 2-3)"], (20, 350)),
    "P0101": ("MAF sensor range/performance", "fuel_air", "medium",
              ["Dirty MAF element", "Air leak after the MAF", "Clogged air filter", "Failing MAF sensor"],
              ["Clean MAF with MAF-safe spray", "Inspect intake boot for cracks", "Replace air filter"], (10, 350)),
    "P0102": ("MAF sensor circuit low input", "fuel_air", "medium",
              ["MAF connector loose", "Open signal wire", "Failed MAF"], ["Check 5V/12V supply and ground"], (20, 350)),
    "P0103": ("MAF sensor circuit high input", "fuel_air", "medium",
              ["Signal wire shorted to voltage", "Failed MAF"], ["Back-probe signal voltage"], (20, 350)),
    "P0106": ("MAP sensor range/performance", "fuel_air", "medium",
              ["Cracked/disconnected MAP vacuum hose", "Vacuum leak", "Failed MAP sensor"],
              ["Compare MAP at KOEO with barometric pressure"], (20, 200)),
    "P0110": ("Intake air temperature sensor circuit", "fuel_air", "low",
              ["IAT connector", "Failed IAT (often inside MAF)"], ["Compare IAT with ambient on a cold engine"], (20, 150)),
    "P0113": ("Intake air temperature sensor circuit high", "fuel_air", "low",
              ["Unplugged IAT/MAF connector", "Open circuit", "Failed sensor"], ["Inspect connector"], (20, 150)),
    "P0115": ("Engine coolant temperature sensor circuit", "cooling", "medium",
              ["ECT connector", "Failed ECT sensor", "Wiring"], ["Compare ECT with IAT after overnight cold soak"], (20, 150)),
    "P0116": ("Coolant temperature sensor range/performance", "cooling", "medium",
              ["Thermostat stuck open", "Failing ECT sensor", "Low coolant"], ["Check warm-up curve on live data"], (30, 250)),
    "P0117": ("Coolant temperature sensor circuit low", "cooling", "medium",
              ["Shorted ECT sensor or wiring"], ["Check sensor resistance"], (20, 150)),
    "P0118": ("Coolant temperature sensor circuit high", "cooling", "medium",
              ["Unplugged ECT", "Open wire", "Failed sensor"], ["Inspect connector"], (20, 150)),
    "P0121": ("Throttle position sensor range/performance", "fuel_air", "medium",
              ["Dirty throttle body", "Worn TPS track", "Wiring"], ["Watch TPS for dropouts while sweeping pedal"], (0, 400)),
    "P0128": ("Coolant below thermostat regulating temperature", "cooling", "low",
              ["Thermostat stuck open", "Coolant temp sensor reading low", "Low coolant"],
              ["Log coolant temp: should reach 85-95 °C within ~10-15 min of driving"], (60, 300)),
    "P0130": ("O2 sensor circuit (bank 1 sensor 1)", "emissions", "medium",
              ["Failed upstream O2 sensor", "Wiring/connector", "Exhaust leak near sensor"],
              ["Check sensor switching 0.1-0.9 V at 2500 rpm"], (60, 300)),
    "P0133": ("O2 sensor slow response (bank 1 sensor 1)", "emissions", "medium",
              ["Aged upstream O2 sensor", "Exhaust leak", "Fuel contamination (silicone/oil)"],
              ["Count O2 switches: healthy narrowband ≥ 5-8 per 10 s at 2500 rpm"], (60, 300)),
    "P0135": ("O2 sensor heater circuit (bank 1 sensor 1)", "emissions", "low",
              ["Failed heater element in sensor", "Blown heater fuse", "Wiring"], ["Check heater fuse and resistance (≈ 2-15 Ω)"], (60, 300)),
    "P0136": ("O2 sensor circuit (bank 1 sensor 2)", "emissions", "low",
              ["Failed downstream O2 sensor", "Wiring"], ["Check downstream voltage is steady ~0.6-0.8 V warm"], (60, 250)),
    "P0141": ("O2 sensor heater circuit (bank 1 sensor 2)", "emissions", "low",
              ["Failed heater in downstream sensor", "Fuse", "Wiring"], ["Check heater resistance"], (60, 250)),
    "P0171": ("System too lean (bank 1)", "fuel_air", "medium",
              ["Vacuum leak (PCV hose, intake gasket, brake booster hose)", "Dirty/failing MAF sensor",
               "Weak fuel pump or clogged fuel filter", "Clogged injectors", "Exhaust leak before O2 sensor"],
              ["Check LTFT at idle vs 2500 rpm: high at idle only → vacuum leak; high everywhere → fuel/MAF",
               "Smoke test intake", "Clean MAF"], (10, 600)),
    "P0172": ("System too rich (bank 1)", "fuel_air", "medium",
              ["Leaking injector", "High fuel pressure / failed regulator", "Dirty MAF over-reading",
               "Coolant sensor reading cold", "Saturated EVAP canister purge"],
              ["Check fuel pressure", "Check ECT reads correctly", "Check oil for fuel smell"], (20, 600)),
    "P0174": ("System too lean (bank 2)", "fuel_air", "medium",
              ["Vacuum leak", "Dirty MAF", "Low fuel pressure", "Intake gasket on bank 2"],
              ["If P0171 too: common cause (MAF, fuel, central vacuum leak)"], (10, 600)),
    "P0175": ("System too rich (bank 2)", "fuel_air", "medium",
              ["Leaking injector bank 2", "High fuel pressure", "MAF over-reading"], ["Check fuel pressure"], (20, 600)),
    "P0190": ("Fuel rail pressure sensor circuit", "fuel_air", "high",
              ["Sensor connector", "Failed rail pressure sensor", "Wiring"], ["Compare rail pressure with spec"], (80, 400)),
    "P0200": ("Injector circuit malfunction", "fuel_air", "high",
              ["Injector connector", "Open injector coil", "Driver circuit"], ["Check injector resistance"], (50, 600)),
    "P0217": ("Engine overtemperature condition", "cooling", "critical",
              ["Low coolant / leak", "Failed thermostat (stuck closed)", "Cooling fan not working",
               "Water pump failure", "Head gasket"],
              ["STOP DRIVING - let engine cool before opening anything", "Check coolant level cold", "Check fans run"], (50, 2500)),
    "P0219": ("Engine overspeed condition", "engine", "high",
              ["Missed downshift", "Sensor fault"], ["Check for transmission fault codes"], (0, 300)),
    "P0234": ("Turbo/supercharger overboost", "fuel_air", "high",
              ["Stuck wastegate", "Boost control solenoid", "Wastegate actuator hose"], ["Check wastegate movement"], (80, 900)),
    "P0299": ("Turbo/supercharger underboost", "fuel_air", "high",
              ["Boost leak (split intercooler hose)", "Wastegate stuck open/actuator", "Failing turbo",
               "Boost control solenoid"], ["Pressure/smoke test charge pipes", "Check wastegate rod"], (20, 2500)),
    # ---- ignition / misfire
    "P0300": ("Random/multiple cylinder misfire detected", "ignition", "high",
              ["Worn spark plugs", "Vacuum leak / lean condition", "Low fuel pressure", "Failing coil(s)",
               "Low compression", "Bad fuel"],
              ["Check misfire counters per cylinder if available", "Check fuel trims - misfire + lean = air leak/fuel",
               "Inspect plugs"], (20, 1500)),
    **{f"P030{n}": (f"Cylinder {n} misfire detected", "ignition", "high",
                    ["Spark plug", "Ignition coil", "Injector", "Low compression / valve issue"],
                    [f"Swap cylinder {n} coil with a neighbour - if the misfire moves, replace the coil",
                     "Inspect plug", "Compression test if plug/coil OK"], (20, 1200)) for n in range(1, 9)},
    "P0316": ("Misfire detected on startup (first 1000 revolutions)", "ignition", "medium",
              ["Leaking injector", "Moisture in coil wells", "Low fuel pressure on start"], ["Check fuel pressure hold"], (20, 600)),
    "P0325": ("Knock sensor circuit (bank 1)", "ignition", "medium",
              ["Knock sensor connector/wiring", "Failed knock sensor"], ["Inspect harness under intake"], (60, 600)),
    "P0335": ("Crankshaft position sensor A circuit", "ignition", "critical",
              ["Failed crank sensor", "Damaged reluctor ring", "Wiring"], ["May stall/no start - check sensor & connector"], (50, 400)),
    "P0340": ("Camshaft position sensor A circuit (bank 1)", "ignition", "high",
              ["Failed cam sensor", "Wiring", "Timing chain stretch"], ["Check sensor; if new sensor fails check timing"], (40, 1500)),
    "P0341": ("Camshaft position sensor range/performance", "ignition", "high",
              ["Timing chain/belt stretched or jumped", "Cam sensor", "Reluctor"], ["Check cam/crank correlation"], (40, 1500)),
    "P0351": ("Ignition coil A primary/secondary circuit", "ignition", "high",
              ["Failed coil 1", "Connector", "Wiring"], ["Swap coil"], (40, 250)),
    # ---- emissions
    "P0401": ("EGR flow insufficient", "emissions", "medium",
              ["Carbon-clogged EGR passages", "Stuck EGR valve", "EGR vacuum solenoid / DPFE sensor"],
              ["Clean EGR valve and passages", "Command EGR open and watch MAP drop"], (50, 600)),
    "P0402": ("EGR flow excessive", "emissions", "medium",
              ["EGR valve stuck open", "Control solenoid"], ["Rough idle? check valve seats closed"], (80, 600)),
    "P0403": ("EGR circuit malfunction", "emissions", "medium", ["EGR solenoid/valve wiring", "Failed valve"], ["Check connector"], (80, 600)),
    "P0411": ("Secondary air injection incorrect flow", "emissions", "low",
              ["Failed air pump", "Stuck check valve", "Blocked passages"], ["Listen for pump at cold start"], (100, 900)),
    "P0420": ("Catalyst system efficiency below threshold (bank 1)", "emissions", "medium",
              ["Exhaust leak before/near the downstream O2 sensor", "Ageing or failing downstream O2 sensor",
               "Worn catalytic converter", "Engine running rich/misfiring and damaging the cat"],
              ["Compare upstream vs downstream O2: downstream should stay steady ~0.6-0.75 V; if it mirrors upstream the cat isn't storing oxygen",
               "Check for exhaust leaks", "Fix any misfire/fuel-trim codes FIRST - they kill new cats"], (100, 2500)),
    "P0430": ("Catalyst system efficiency below threshold (bank 2)", "emissions", "medium",
              ["Exhaust leak", "Downstream O2 sensor bank 2", "Worn catalyst bank 2"],
              ["Same procedure as P0420 for bank 2"], (100, 2500)),
    "P0440": ("Evaporative emission system malfunction", "evap", "low",
              ["Loose/worn fuel cap", "Cracked EVAP hose", "Purge or vent valve"], ["Check fuel cap seal"], (0, 400)),
    "P0441": ("EVAP incorrect purge flow", "evap", "low",
              ["Purge valve stuck", "Cracked purge hose"], ["Apply vacuum to purge valve - should hold when off"], (30, 250)),
    "P0442": ("EVAP small leak detected", "evap", "low",
              ["Fuel cap seal", "Small cracked hose", "Purge/vent valve not sealing", "Filler neck rust"],
              ["Replace fuel cap first (cheapest)", "Smoke test EVAP system"], (15, 500)),
    "P0446": ("EVAP vent control circuit", "evap", "low",
              ["Vent valve/solenoid stuck", "Spider webs/dirt in vent filter", "Wiring"], ["Inspect vent solenoid near canister"], (40, 300)),
    "P0455": ("EVAP large leak detected", "evap", "low",
              ["Fuel cap missing/loose", "Disconnected EVAP hose", "Purge valve stuck open", "Canister cracked"],
              ["Check fuel cap", "Visual inspection of EVAP hoses", "Smoke test"], (0, 500)),
    "P0456": ("EVAP very small leak detected", "evap", "low",
              ["Fuel cap seal", "Purge valve", "Tiny hose crack"], ["Replace cap, clear, re-run drive cycle"], (15, 400)),
    "P0457": ("EVAP leak detected (fuel cap loose/off)", "evap", "low", ["Fuel cap loose/off"], ["Tighten until it clicks"], (0, 30)),
    # ---- speed / idle
    "P0500": ("Vehicle speed sensor malfunction", "transmission", "medium",
              ["VSS / wheel speed sensor", "Wiring", "ABS module data"], ["Compare speed PID with GPS"], (40, 300)),
    "P0505": ("Idle air control system malfunction", "fuel_air", "medium",
              ["Dirty throttle body / IAC valve", "Vacuum leak"], ["Clean throttle body"], (10, 400)),
    "P0506": ("Idle control RPM lower than expected", "fuel_air", "low",
              ["Dirty throttle body", "Vacuum leak", "IAC"], ["Clean throttle body, run idle relearn"], (10, 400)),
    "P0507": ("Idle control RPM higher than expected", "fuel_air", "low",
              ["Vacuum leak", "Dirty/sticking throttle", "IAC"], ["Smoke test, clean throttle"], (10, 400)),
    "P0562": ("System voltage low", "electrical", "medium",
              ["Weak/failing alternator", "Loose or corroded battery terminals", "Worn battery"],
              ["Measure battery: ~12.6 V engine off, 13.8-14.7 V running"], (0, 600)),
    "P0563": ("System voltage high", "electrical", "high",
              ["Alternator voltage regulator failed"], ["Measure charging voltage; >15 V damages electronics"], (150, 600)),
    "P0571": ("Brake switch A circuit", "electrical", "medium", ["Brake light switch"], ["Check brake lights work"], (15, 120)),
    "P0600": ("Serial communication link malfunction (ECU)", "network", "high",
              ["Internal ECU fault", "Power/ground supply", "CAN wiring"], ["Check ECU grounds and supply"], (100, 1500)),
    "P0606": ("ECU processor fault", "network", "high",
              ["Internal control module fault", "Low voltage events", "Software"], ["Check for software update; check grounds"], (100, 1500)),
    # ---- transmission
    "P0700": ("Transmission control system malfunction", "transmission", "high",
              ["TCM has its own stored code - scan the transmission module"], ["Read TCM codes"], (0, 3000)),
    "P0715": ("Input/turbine speed sensor circuit", "transmission", "high",
              ["Speed sensor", "Wiring", "Valve body"], ["Check fluid level/condition"], (80, 600)),
    "P0730": ("Incorrect gear ratio", "transmission", "high",
              ["Low/worn ATF", "Slipping clutch packs", "Shift solenoid"], ["Check ATF level/smell"], (100, 4000)),
    "P0740": ("Torque converter clutch circuit", "transmission", "high",
              ["TCC solenoid", "Low ATF", "Wiring"], ["Check fluid"], (150, 1500)),
    "P0750": ("Shift solenoid A malfunction", "transmission", "high", ["Shift solenoid", "Wiring", "Dirty ATF"], ["Check fluid"], (150, 900)),
    # ---- diesel / aftertreatment
    "P0087": ("Fuel rail/system pressure too low", "fuel_air", "high",
              ["Clogged fuel filter", "Weak lift/high-pressure pump", "Rail pressure regulator", "Air in fuel"],
              ["Replace fuel filter first", "Check rail pressure under load"], (40, 2500)),
    "P0088": ("Fuel rail/system pressure too high", "fuel_air", "high",
              ["Pressure regulator / metering valve", "Rail pressure sensor"], ["Check regulator"], (100, 900)),
    "P0093": ("Fuel system large leak detected", "fuel_air", "critical",
              ["External fuel leak", "Injector leak-off excessive"], ["STOP - fire risk if leaking near hot parts"], (50, 2000)),
    "P0380": ("Glow plug/heater circuit A", "ignition", "medium", ["Glow plug(s)", "Glow plug relay/module"], ["Check plug resistance"], (60, 500)),
    "P2002": ("Diesel particulate filter efficiency below threshold (bank 1)", "emissions", "high",
              ["Cracked/damaged DPF", "Faulty differential pressure sensor"], ["Check DPF pressure readings"], (150, 3500)),
    "P2263": ("Turbo/supercharger boost system performance", "fuel_air", "high",
              ["Boost leak", "Variable vane sticking", "Boost sensor"], ["Smoke test charge air system"], (30, 2500)),
    "P242F": ("DPF restriction - ash accumulation", "emissions", "high",
              ["DPF full of ash (end of life)", "Repeated failed regenerations from short trips"],
              ["Forced regeneration or professional DPF cleaning"], (150, 3500)),
    "P2463": ("DPF restriction - soot accumulation", "emissions", "high",
              ["Short trips preventing regeneration", "EGR/injector faults causing soot", "Pressure sensor"],
              ["Drive 20+ min at steady motorway speed to allow regen", "Forced regeneration"], (0, 3500)),
    "P20EE": ("SCR NOx catalyst efficiency below threshold", "emissions", "high",
              ["Poor-quality or crystallised DEF/AdBlue", "DEF injector clogged", "NOx sensor", "SCR catalyst"],
              ["Check DEF quality with refractometer"], (100, 3500)),
    # ---- misc powertrain
    "P0011": ("Camshaft timing over-advanced (bank 1, intake)", "engine", "high",
              ["Low/dirty oil", "VVT solenoid/oil control valve", "Stretched timing chain"],
              ["Check oil level and condition FIRST", "Inspect VVT solenoid screen"], (0, 1800)),
    "P0012": ("Camshaft timing over-retarded (bank 1, intake)", "engine", "high",
              ["Low/dirty oil", "VVT solenoid", "Timing chain"], ["Check oil"], (0, 1800)),
    "P0014": ("Camshaft timing over-advanced (bank 1, exhaust)", "engine", "high",
              ["Oil level/condition", "Exhaust VVT solenoid", "Timing chain"], ["Check oil"], (0, 1800)),
    "P0016": ("Crank/cam position correlation (bank 1 sensor A)", "engine", "high",
              ["Stretched timing chain / jumped belt", "VVT solenoid", "Cam/crank sensor"],
              ["Don't ignore - a jumped chain can destroy the engine"], (100, 2000)),
    "P0030": ("HO2S heater control circuit (bank 1 sensor 1)", "emissions", "low",
              ["O2 sensor heater", "Fuse", "Wiring"], ["Check heater resistance"], (60, 300)),
    "P0050": ("HO2S heater control circuit (bank 2 sensor 1)", "emissions", "low", ["O2 heater", "Wiring"], ["Check fuse"], (60, 300)),
    "P0068": ("MAP/MAF - throttle position correlation", "fuel_air", "medium",
              ["Vacuum leak", "Dirty MAF", "Throttle body"], ["Smoke test"], (10, 500)),
    "P0122": ("Throttle position sensor A circuit low", "fuel_air", "high",
              ["TPS / throttle body", "Wiring"], ["May cause limp mode"], (60, 500)),
    "P0123": ("Throttle position sensor A circuit high", "fuel_air", "high", ["TPS / throttle body", "Wiring"], ["Check connector"], (60, 500)),
    "P0191": ("Fuel rail pressure sensor range/performance", "fuel_air", "high",
              ["Fuel filter", "Pump", "Sensor"], ["Compare rail pressure with spec"], (40, 900)),
    "P0221": ("Throttle/pedal position sensor B range/performance", "fuel_air", "high", ["Throttle body", "Wiring"], ["Clean throttle body"], (60, 500)),
    "P2101": ("Throttle actuator control motor circuit range/performance", "fuel_air", "high",
              ["Electronic throttle body", "Wiring", "Carbon buildup"], ["Clean throttle, check connector"], (60, 500)),
    "P2135": ("Throttle/pedal position sensor A/B voltage correlation", "fuel_air", "high",
              ["Throttle body", "Connector", "Pedal sensor"], ["Limp mode likely - inspect connector"], (60, 500)),
    "P2195": ("O2 sensor signal biased/stuck lean (bank 1 sensor 1)", "emissions", "medium",
              ["Vacuum/exhaust leak", "Upstream O2/AF sensor", "Low fuel pressure"], ["Check fuel trims"], (60, 400)),
    "P2196": ("O2 sensor signal biased/stuck rich (bank 1 sensor 1)", "emissions", "medium",
              ["Leaking injector", "O2/AF sensor", "High fuel pressure"], ["Check fuel trims"], (60, 400)),
    "P2270": ("O2 sensor signal stuck lean (bank 1 sensor 2)", "emissions", "low",
              ["Exhaust leak", "Downstream O2 sensor"], ["Check for leaks near sensor"], (60, 300)),
    # ---- chassis (generic)
    "C0035": ("Left front wheel speed sensor circuit", "brakes", "high",
              ["Damaged sensor/cable", "Debris on tone ring", "Wheel bearing play"],
              ["ABS/traction disabled - brakes still work but without ABS; have it inspected"], (40, 350)),
    "C0040": ("Right front wheel speed sensor circuit", "brakes", "high",
              ["Damaged sensor/cable", "Debris on tone ring", "Wheel bearing"], ["Inspect sensor and wiring"], (40, 350)),
    "C0045": ("Left rear wheel speed sensor circuit", "brakes", "high", ["Sensor/cable", "Tone ring"], ["Inspect"], (40, 350)),
    "C0050": ("Right rear wheel speed sensor circuit", "brakes", "high", ["Sensor/cable", "Tone ring"], ["Inspect"], (40, 350)),
    "C0265": ("ABS motor relay circuit", "brakes", "high", ["ABS module / relay", "Power supply"], ["Professional inspection"], (150, 1500)),
    # ---- body (generic)
    "B0001": ("Driver frontal stage 1 deployment control", "airbag", "critical",
              ["Clock spring", "Airbag module connector", "Wiring"], ["Airbag may not deploy - professional inspection only"], (100, 800)),
    "B0100": ("Electronic frontal sensor 1", "airbag", "critical", ["Crash sensor", "Wiring"], ["Professional inspection only"], (100, 600)),
    # ---- network
    "U0100": ("Lost communication with ECM/PCM A", "network", "critical",
              ["Low battery voltage", "CAN bus wiring / connector", "ECM power or ground", "Failed ECM"],
              ["Check battery & ECM fuses/grounds first"], (0, 1500)),
    "U0101": ("Lost communication with TCM", "network", "high", ["TCM power/ground", "CAN wiring"], ["Check TCM fuses"], (0, 1500)),
    "U0121": ("Lost communication with ABS module", "network", "high",
              ["ABS module power/ground", "CAN wiring", "Failed ABS module"], ["Check ABS fuses"], (0, 1500)),
    "U0140": ("Lost communication with body control module", "network", "medium", ["BCM power", "CAN wiring"], ["Check fuses"], (0, 1000)),
    "U0155": ("Lost communication with instrument cluster", "network", "medium", ["Cluster power", "CAN wiring"], ["Check fuses"], (0, 1000)),
}

# ---------------------------------------------------------------- relationships
# (set of codes, explanation) - when ALL codes of a pattern are present together
PATTERNS: list[tuple[set[str], str]] = [
    ({"P0300", "P0171"}, "Misfire together with a lean condition usually points to an air leak (vacuum hose, intake gasket) or low fuel delivery rather than plugs/coils."),
    ({"P0171", "P0174"}, "Both banks lean at once means a shared cause: MAF sensor, fuel pressure, or a central vacuum leak (PCV, brake booster) - not a single-bank issue."),
    ({"P0172", "P0175"}, "Both banks rich: shared cause such as high fuel pressure, MAF over-reading, coolant sensor reading cold, or EVAP purge stuck open."),
    ({"P0420", "P0300"}, "Fix the misfire first. Unburnt fuel from misfires overheats and destroys catalytic converters - replacing the cat before fixing the misfire wastes money."),
    ({"P0420", "P0171"}, "A long-running lean condition can skew O2 readings; fix fuel trims first, then clear and re-test the catalyst monitor."),
    ({"P0128", "P0420"}, "An engine that never warms up (thermostat) can fail the catalyst monitor - fix P0128 first."),
    ({"P0011", "P0016"}, "Cam timing + correlation codes together strongly suggest oil-supply or timing-chain problems. Check oil level now."),
    ({"P0562", "U0100"}, "Low system voltage commonly causes lost-communication codes. Fix charging/battery first, then clear and re-scan."),
    ({"P0299", "P0234"}, "Both under- and over-boost suggests erratic wastegate/vane control rather than a leak."),
    ({"P0455", "P0442"}, "Both EVAP leak sizes: start with the fuel cap and the purge valve."),
    ({"P0101", "P0171"}, "MAF performance plus lean: a dirty or failing MAF under-reports airflow - clean it before chasing vacuum leaks."),
]

# ---------------------------------------------------------------- range rules
SYSTEM_LABEL = {
    "fuel_air": "Fuel and air metering", "ignition": "Ignition / misfire", "emissions": "Auxiliary emission controls",
    "evap": "Evaporative emissions (EVAP)", "cooling": "Engine cooling", "engine": "Engine mechanical / valve timing",
    "transmission": "Transmission", "electrical": "Charging / computer output circuits", "network": "Network / module communication",
    "brakes": "Brakes / ABS / traction", "airbag": "Airbag / SRS", "body": "Body electrical", "chassis": "Chassis",
}
P_RANGES = [
    (0x000, 0x0FF, "fuel_air"), (0x100, 0x1FF, "fuel_air"), (0x200, 0x2FF, "fuel_air"),
    (0x300, 0x3FF, "ignition"), (0x400, 0x4FF, "emissions"), (0x500, 0x5FF, "fuel_air"),
    (0x600, 0x6FF, "electrical"), (0x700, 0x9FF, "transmission"), (0xA00, 0xAFF, "electrical"),
]
SAFETY_SYSTEMS = {"brakes", "airbag"}


def _code_system(code: str) -> str:
    letter = code[0]
    if letter == "C":
        return "brakes" if code[1] in "0" else "chassis"
    if letter == "B":
        return "airbag" if code[1:3] in ("00",) else "body"
    if letter == "U":
        return "network"
    try:
        n = int(code[2:], 16)
    except ValueError:
        return "fuel_air"
    if code[1] in ("2", "3") and code[2] == "0":
        return "fuel_air"
    for lo, hi, sysname in P_RANGES:
        if lo <= n <= hi:
            return sysname
    return "fuel_air"


def is_manufacturer_specific(code: str) -> bool:
    """SAE J2012: P1xxx/P3xxx and B/C/U 1xxx/2xxx are defined by each manufacturer."""
    d = code[1]
    if code[0] == "P":
        return d in ("1", "3")
    return d in ("1", "2")


def lookup(code: str) -> dict:
    code = code.strip().upper()
    if code in CATALOG:
        desc, system, sev, causes, checks, cost = CATALOG[code]
        return {"code": code, "description": desc, "system": system, "system_label": SYSTEM_LABEL[system],
                "severity": sev, "likely_causes": causes, "first_checks": checks,
                "cost_usd": {"low": cost[0], "high": cost[1]}, "source": "catalog",
                "manufacturer_specific": False, "safety_critical": system in SAFETY_SYSTEMS}
    system = _code_system(code)
    ms = is_manufacturer_specific(code)
    return {"code": code,
            "description": (f"Manufacturer-specific {SYSTEM_LABEL[system].lower()} code" if ms
                            else f"Generic {SYSTEM_LABEL[system].lower()} code"),
            "system": system, "system_label": SYSTEM_LABEL[system],
            "severity": "high" if system in SAFETY_SYSTEMS else "medium",
            "likely_causes": [], "first_checks": ["Look up the exact definition for this make in service information"],
            "cost_usd": None, "source": "range-rule", "manufacturer_specific": ms,
            "safety_critical": system in SAFETY_SYSTEMS}


def related_patterns(codes: list[str]) -> list[str]:
    s = {c.upper() for c in codes}
    return [text for pattern, text in PATTERNS if pattern <= s]
