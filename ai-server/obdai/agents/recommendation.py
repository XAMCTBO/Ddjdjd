"""Recommendation agent - turns a diagnosis into an ordered action plan.

Personalised by the user's DIY level and tools, aware of weather (ambient
temperature) constraints, ordered cheapest/least-invasive first.
"""
from __future__ import annotations

import json

from ..knowledge import dtc_catalog
from ..llm import LLM, LLMError
from . import evidence
from .rag import RAGAgent

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["steps", "when_to_see_mechanic", "notes"],
    "properties": {
        "steps": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["title", "detail", "for_codes", "diy", "difficulty", "est_cost_usd", "tools", "confirms"],
            "properties": {
                "title": {"type": "string"},
                "detail": {"type": "string"},
                "for_codes": {"type": "array", "items": {"type": "string"}},
                "diy": {"type": "boolean"},
                "difficulty": {"type": "string", "enum": ["easy", "moderate", "hard", "professional"]},
                "est_cost_usd": {"type": "string"},
                "tools": {"type": "array", "items": {"type": "string"}},
                "confirms": {"type": "string"},
            }}},
        "when_to_see_mechanic": {"type": "string"},
        "notes": {"type": "array", "items": {"type": "string"}},
    },
}

SYSTEM = """You are the Recommendation agent in a car-diagnostics system. You get a finished diagnosis and write a step-by-step action plan.

Rules:
- Order the steps from the cheapest and least invasive to the most expensive. For example, check the fuel cap before smoke-testing EVAP, and clean the MAF before replacing it.
- Mark steps beyond the user's DIY level or tools as diy=false or difficulty "professional".
- Each step says what result confirms or rules out a cause (`confirms`).
- If one fault can cause another, fix the root cause first. For example, fix a misfire before the catalyst.
- Respect weather: if the ambient temperature is below about 4 °C, warn that EVAP tests and drive-cycle monitors may not run.
- For brake, ABS, steering or airbag issues, the first step is a professional inspection.
- Cost estimates are rough ranges in USD, for example "$0-15". Base them on the reference material, not guesses.
- Don't suggest clearing codes as a fix. Suggest it only to confirm a repair, after saving a report."""


class RecommendationAgent:
    name = "recommendation"

    def __init__(self, llm: LLM, rag: RAGAgent):
        self.llm, self.rag = llm, rag

    def recommend(self, diagnosis: dict, scan: dict, profile: dict | None = None,
                  ambient_c: float | None = None, basic: bool = False) -> dict:
        profile = profile or {}
        if ambient_c is None:
            ambient_c = evidence.ambient_temp(scan)
        if not diagnosis.get("codes") and not diagnosis.get("interactions"):
            return {"steps": [], "when_to_see_mechanic": "No action needed right now.", "notes": [], "engine": "rules"}
        if self.llm.available and not basic:
            codes = [c["code"] for c in diagnosis.get("codes", [])]
            user = (
                f"<user_profile>{json.dumps({'diy_level': profile.get('diy_level', 'beginner'), 'tools': profile.get('tools', []), 'currency_note': 'USD'})}</user_profile>\n"
                f"<ambient_c>{ambient_c}</ambient_c>\n"
                f"<diagnosis>{json.dumps(diagnosis)}</diagnosis>\n"
                f"<reference>\n{self.rag.context(' '.join(codes) + ' repair procedure ' + diagnosis.get('summary', ''), k=6)}\n</reference>"
            )
            try:
                out = self.llm.json(SYSTEM, user, SCHEMA, effort="medium")
                out["engine"] = "llm"
                return out
            except LLMError as e:
                res = self._offline(diagnosis, profile, ambient_c)
                res["notes"].append(f"AI unavailable ({e}); basic plan shown.")
                return res
        return self._offline(diagnosis, profile, ambient_c)

    def _offline(self, diagnosis: dict, profile: dict, ambient_c) -> dict:
        diy = profile.get("diy_level", "beginner")
        steps, notes = [], []
        codes = diagnosis.get("codes", [])
        ordered = sorted(codes, key=lambda c: (c["code"][:4] != "P030", c["code"] not in ("P0171", "P0174", "P0172", "P0175")))
        safety = False
        for c in ordered:
            info = dtc_catalog.lookup(c["code"])
            if info["safety_critical"]:
                safety = True
            for n, check in enumerate(info["first_checks"]):
                steps.append({"title": check, "detail": f"For {c['code']}: {info['description']}.",
                              "for_codes": [c["code"]], "diy": not info["safety_critical"] and diy != "none",
                              "difficulty": "professional" if info["safety_critical"] else "easy",
                              "est_cost_usd": (f"${info['cost_usd']['low']}-{info['cost_usd']['high']} if a repair is needed"
                                               if info["cost_usd"] and n == 0 else "$0 (check only)" if n else "unknown"),
                              "tools": [], "confirms": "Narrows down the cause before buying parts."})
        if ambient_c is not None and ambient_c < 4:
            notes.append("It is cold: EVAP and some readiness monitors may not run until temperatures rise above ~4 °C.")
        notes.append("After a repair, save a report, then clear codes and drive a full drive cycle to confirm.")
        mech = ("Brake/ABS/airbag issue: book a professional inspection now." if safety else
                "See a mechanic if the cheap checks don't resolve it, or sooner if the check-engine light flashes.")
        return {"steps": steps, "when_to_see_mechanic": mech, "notes": notes, "engine": "knowledge-base"}
