"""Rule-based observations from live data / freeze frames.

Used two ways: as the offline answer when no LLM is configured, and as
pre-digested facts handed to the LLM agents (so the model reasons over
"LTFT +14 % at idle" instead of raw numbers alone).
"""
from __future__ import annotations

ALIASES = {"stft": "stft1", "ltft": "ltft1", "intake": "iat"}


def values(block: dict | None) -> dict:
    """{'ltft1': {'value': 12.5, ...}} or {'ltft': 12.5} -> {'ltft1': 12.5}"""
    out = {}
    for k, v in (block or {}).items():
        val = v.get("value") if isinstance(v, dict) else v
        out[ALIASES.get(k, k)] = val
    return out


def observations(live: dict | None, freeze: dict | None = None, ambient_c: float | None = None) -> list[dict]:
    obs: list[dict] = []
    for label, block in (("freeze frame", freeze), ("live data", live)):
        v = values(block)
        if not v:
            continue

        def add(level, text, key):
            obs.append({"level": level, "text": f"{text} ({label})", "key": key})

        for bank in ("1", "2"):
            st, lt = v.get(f"stft{bank}"), v.get(f"ltft{bank}")
            if isinstance(lt, (int, float)):
                total = lt + (st if isinstance(st, (int, float)) else 0)
                if total >= 10:
                    add("warn" if total < 20 else "bad", f"Bank {bank} running lean: total fuel trim {total:+.1f} %", f"lean{bank}")
                elif total <= -10:
                    add("warn" if total > -20 else "bad", f"Bank {bank} running rich: total fuel trim {total:+.1f} %", f"rich{bank}")
        c = v.get("coolant")
        if isinstance(c, (int, float)):
            if c >= 110:
                add("bad", f"Coolant temperature high: {c} °C", "overheat")
            elif c < 70 and isinstance(v.get("run_time"), (int, float)) and v["run_time"] > 900:
                add("warn", f"Coolant only {c} °C after {v['run_time'] // 60} min running - thermostat may be stuck open", "cold_engine")
        volt = v.get("voltage")
        if isinstance(volt, (int, float)):
            rpm = v.get("rpm") or 0
            if rpm > 400 and volt < 13.2:
                add("warn", f"Charging voltage low while running: {volt} V", "low_charge")
            elif volt > 15.0:
                add("bad", f"Charging voltage high: {volt} V", "high_charge")
            elif rpm < 100 and volt < 12.2:
                add("warn", f"Battery voltage low with engine off: {volt} V", "low_battery")
        maf, rpm = v.get("maf"), v.get("rpm")
        if isinstance(maf, (int, float)) and isinstance(rpm, (int, float)) and 500 < rpm < 1000 and maf < 1.5:
            add("warn", f"MAF very low at idle ({maf} g/s) - possible dirty or failing MAF", "maf_low")
        if v.get("fuel_system") and "open loop (fault)" in str(v["fuel_system"]):
            add("bad", "Fuel system in open loop due to a fault", "open_loop_fault")
        load = v.get("load")
        if isinstance(load, (int, float)) and isinstance(rpm, (int, float)) and 500 < rpm < 1000 and load > 45:
            add("info", f"High load at idle ({load} %) - accessory load or restriction", "idle_load")
    if ambient_c is not None and ambient_c < 4:
        obs.append({"level": "info", "text": f"Ambient {ambient_c} °C: the EVAP monitor usually won't run below ~4 °C",
                    "key": "cold_ambient"})
    return obs


def ambient_temp(scan: dict) -> float | None:
    for block in (scan.get("live"), scan.get("freeze_frame")):
        v = values(block)
        if isinstance(v.get("ambient"), (int, float)):
            return v["ambient"]
    v = values(scan.get("live"))
    # a cold-soaked engine's intake air temperature approximates ambient
    if isinstance(v.get("iat"), (int, float)) and isinstance(v.get("coolant"), (int, float)) \
            and abs(v["iat"] - v["coolant"]) < 5:
        return v["iat"]
    return None
