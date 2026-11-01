"""Prediction agent - spots slow trends across sessions before a code is set.

Every recorded session is reduced to a handful of health metrics
(`summarize_samples`). With >= 3 sessions the agent fits a robust trend per
metric and projects when it will cross a known fault threshold (e.g. total
fuel trim reaching the ±20-25 % that sets P0171). Risk scores are computed
deterministically; the LLM (if configured) only writes the plain-language
narrative on top, so numbers are never hallucinated.

Note: this compares the vehicle with *its own history* plus published
thresholds. It doesn't have a fleet-wide dataset of other cars.
"""
from __future__ import annotations

import json
import statistics
from typing import Iterable

from ..llm import LLM, LLMError
from . import evidence

MIN_SESSIONS = 3


# ---------------------------------------------------------------- per-session metrics
def _mean(xs: Iterable[float]) -> float | None:
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(statistics.fmean(xs), 2) if xs else None


def _switch_rate(series: list[tuple[float, float]]) -> float | None:
    """Crossings of 0.45 V per 10 s for a narrowband O2 signal."""
    if len(series) < 10:
        return None
    crossings = sum(1 for (_, a), (_, b) in zip(series, series[1:]) if (a - 0.45) * (b - 0.45) < 0)
    duration = (series[-1][0] - series[0][0]) / 1000
    return round(crossings * 10 / duration, 2) if duration > 5 else None


def summarize_samples(samples: list[dict]) -> dict:
    rows = [{evidence.ALIASES.get(k, k): v for k, v in r.items()} for r in samples or []]
    if not rows:
        return {}
    idle = [r for r in rows if (r.get("speed") or 0) == 0 and 450 < (r.get("rpm") or 0) < 1200]
    cruise = [r for r in rows if (r.get("speed") or 0) >= 50]
    warm = [r for r in rows if (r.get("coolant") or 0) >= 75]
    running = [r for r in rows if (r.get("rpm") or 0) > 450]

    def trim(rs, b="1"):
        return _mean((r.get(f"stft{b}") or 0) + r[f"ltft{b}"] for r in rs if isinstance(r.get(f"ltft{b}"), (int, float)))

    warmup_s = None
    first_cool = next((r for r in rows if isinstance(r.get("coolant"), (int, float))), None)
    if first_cool and first_cool["coolant"] < 40:
        reached = next((r for r in rows if (r.get("coolant") or 0) >= 80), None)
        if reached:
            warmup_s = round((reached.get("t", 0) - first_cool.get("t", 0)) / 1000)
    o2_up = [(r.get("t", 0), r["o2_b1s1"]) for r in warm if isinstance(r.get("o2_b1s1"), (int, float)) and (r.get("rpm") or 0) > 1500]
    o2_dn = [(r.get("t", 0), r["o2_b1s2"]) for r in warm if isinstance(r.get("o2_b1s2"), (int, float)) and (r.get("rpm") or 0) > 1500]
    up_rate, dn_rate = _switch_rate(o2_up), _switch_rate(o2_dn)
    s = {
        "duration_s": round((rows[-1].get("t", 0) - rows[0].get("t", 0)) / 1000),
        "samples": len(rows),
        "trim_idle_b1": trim([r for r in idle if (r.get("coolant") or 0) >= 75]),
        "trim_cruise_b1": trim([r for r in cruise if (r.get("coolant") or 0) >= 75]),
        "trim_warm_b1": trim(warm),
        "trim_warm_b2": trim(warm, "2"),
        "coolant_max": max((r["coolant"] for r in rows if isinstance(r.get("coolant"), (int, float))), default=None),
        "coolant_cruise": _mean(r.get("coolant") for r in cruise if (r.get("coolant") or 0) > 40),
        "warmup_s": warmup_s,
        "voltage_running": _mean(r.get("voltage") for r in running),
        "maf_idle": _mean(r.get("maf") for r in idle if (r.get("coolant") or 0) >= 75),
        "o2_up_switch_rate": up_rate,
        "cat_ratio": round(dn_rate / up_rate, 2) if up_rate and dn_rate is not None else None,
        "max_speed": max((r.get("speed") or 0 for r in rows), default=0),
    }
    return {k: v for k, v in s.items() if v is not None}


# ---------------------------------------------------------------- trend maths
def theil_sen(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Robust slope/intercept: one odd session doesn't create a fake trend."""
    slopes = [(ys[j] - ys[i]) / (xs[j] - xs[i]) for i in range(len(xs)) for j in range(i + 1, len(xs)) if xs[j] != xs[i]]
    if not slopes:
        return 0.0, statistics.median(ys)
    m = statistics.median(slopes)
    b = statistics.median(y - m * x for x, y in zip(xs, ys))
    return m, b


# metric, component, threshold, direction (+1 = bad when rising), healthy level, advice
RULES = [
    ("trim_warm_b1", "Fuel mixture bank 1 (vacuum leak / MAF / fuel delivery)", 20.0, +1, 5.0,
     "Inspect intake hoses for leaks and clean the MAF sensor before the lean code (P0171) sets."),
    ("trim_warm_b1", "Fuel mixture bank 1 (rich - injector / pressure)", -20.0, -1, -5.0,
     "Check for a leaking injector or high fuel pressure before P0172 sets."),
    ("trim_warm_b2", "Fuel mixture bank 2", 20.0, +1, 5.0, "Look for a bank-2 intake leak, or a shared cause if bank 1 also drifts."),
    ("warmup_s", "Thermostat (sticking open)", 900.0, +1, 600.0, "Warm-up is getting slower: replace the thermostat before P0128."),
    ("coolant_cruise", "Thermostat (sticking open)", 78.0, -1, 88.0, "Coolant temperature at cruise is falling: the thermostat may be opening early."),
    ("coolant_max", "Cooling system (overheating risk)", 108.0, +1, 100.0, "Peak coolant temperature is rising: check coolant level, the fan, and the radiator."),
    ("voltage_running", "Charging system / alternator", 13.2, -1, 14.0, "Charging voltage is drifting down: test the alternator and battery terminals."),
    ("o2_up_switch_rate", "Upstream O2 sensor ageing", 3.0, -1, 6.0, "The O2 sensor is getting slower: plan a replacement before P0133 and fuel economy loss."),
    ("cat_ratio", "Catalytic converter efficiency", 0.7, +1, 0.2, "The downstream O2 sensor is starting to mirror the upstream one: the catalyst's oxygen storage is falling (P0420 risk)."),
]


class PredictionAgent:
    name = "prediction"

    def __init__(self, llm: LLM):
        self.llm = llm

    def predict(self, sessions: list[dict], vehicle: dict | None = None) -> dict:
        usable = [s for s in sessions if s.get("summary")]
        if len(usable) < MIN_SESSIONS:
            return {"ready": False, "sessions_used": len(usable), "components": [],
                    "summary": f"Need at least {MIN_SESSIONS} recorded sessions for predictions (have {len(usable)})."}
        t0 = usable[0]["started"]
        days_span = max((usable[-1]["started"] - t0) / 86400, 1e-6)
        km_per_day = (vehicle or {}).get("info", {}).get("km_per_day")
        comps: dict[str, dict] = {}
        for metric, comp, thr, direction, healthy, advice in RULES:
            pts = [((s["started"] - t0) / 86400, s["summary"][metric]) for s in usable if metric in s["summary"]]
            if len(pts) < MIN_SESSIONS:
                continue
            xs, ys = zip(*pts)
            slope, icpt = theil_sen(list(xs), list(ys))
            now = slope * xs[-1] + icpt
            # how far along the healthy->threshold path is the current level (0..1)
            span = (thr - healthy) * direction
            progress = max(0.0, min(1.0, ((now - healthy) * direction) / span)) if span else 0
            worsening = slope * direction > 0
            days_to = None
            if worsening and abs(slope) > 1e-9 and (thr - now) * direction > 0:
                days_to = (thr - now) / slope
            # risk: current level + how soon it reaches the threshold (90-day horizon)
            soon = 0.0 if days_to is None else max(0.0, 1 - days_to / 90)
            risk = round(min(1.0, 0.6 * progress + 0.4 * soon + (0.3 if (now - thr) * direction >= 0 else 0)), 2)
            if not worsening and risk < 0.33:
                continue  # stable and not near the limit: nothing to report
            entry = {
                "component": comp, "metric": metric, "risk": risk,
                "level": "high" if risk >= 0.66 else "medium" if risk >= 0.33 else "low",
                "current": round(now, 2), "threshold": thr,
                "trend_per_30_days": round(slope * 30, 2), "worsening": worsening,
                "days_to_threshold": round(days_to) if days_to is not None else None,
                "km_to_threshold": round(days_to * km_per_day) if days_to is not None and km_per_day else None,
                "evidence": [round(y, 2) for y in ys[-6:]], "advice": advice,
            }
            if comp not in comps or comps[comp]["risk"] < risk:
                comps[comp] = entry
        components = sorted(comps.values(), key=lambda c: -c["risk"])
        result = {"ready": True, "sessions_used": len(usable), "span_days": round(days_span, 1),
                  "components": components, "engine": "trend-model"}
        result["summary"] = self._narrative(components, vehicle)
        return result

    def _narrative(self, components: list[dict], vehicle: dict | None) -> str:
        risky = [c for c in components if c["level"] != "low"]
        if not risky:
            base = "No worrying trends: all tracked metrics are stable or inside healthy ranges."
        else:
            base = "; ".join(
                f"{c['component']}: {c['level']} risk" + (f", threshold in ~{c['days_to_threshold']} days" if c["days_to_threshold"] else "")
                for c in risky)
        if not self.llm.available or not risky:
            return base
        try:
            return self.llm.text(
                "You explain predictive-maintenance results to a car owner in 3-5 short sentences. Use only the numbers given. Don't invent any. Mention the most urgent item first, and what to do about it.",
                [{"role": "user", "content": f"Vehicle: {json.dumps((vehicle or {}).get('info', {}))}\nTrends: {json.dumps(risky)}"}],
                effort="low", max_tokens=2000)
        except LLMError:
            return base
