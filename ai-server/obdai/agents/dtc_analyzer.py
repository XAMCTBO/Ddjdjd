"""DTC Analyzer agent - interprets fault codes for a specific vehicle.

Inputs: decoded scan (codes + freeze frame + readiness + live), vehicle info,
earlier sessions for the same vehicle. Output: per-code explanation, ranked
likely causes, a diagnostic plan, code interactions and an overall verdict.
"""
from __future__ import annotations

import json

from ..knowledge import dtc_catalog
from ..llm import LLM, LLMError
from . import evidence
from .rag import RAGAgent

SEVERITY_ORDER = ["low", "medium", "high", "critical"]

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "overall_severity", "safe_to_drive", "codes", "interactions", "sources"],
    "properties": {
        "summary": {"type": "string"},
        "overall_severity": {"type": "string", "enum": SEVERITY_ORDER},
        "safe_to_drive": {"type": "string", "enum": ["yes", "with_caution", "no"]},
        "codes": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["code", "status", "description", "severity", "likely_causes", "diagnostic_plan",
                         "recurring", "manufacturer_specific"],
            "properties": {
                "code": {"type": "string"},
                "status": {"type": "string", "enum": ["stored", "pending", "permanent"]},
                "description": {"type": "string"},
                "severity": {"type": "string", "enum": SEVERITY_ORDER},
                "likely_causes": {"type": "array", "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["cause", "likelihood", "why"],
                    "properties": {"cause": {"type": "string"},
                                   "likelihood": {"type": "string", "enum": ["high", "medium", "low"]},
                                   "why": {"type": "string"}}}},
                "diagnostic_plan": {"type": "array", "items": {"type": "string"}},
                "recurring": {"type": "boolean"},
                "manufacturer_specific": {"type": "boolean"},
            }}},
        "interactions": {"type": "array", "items": {"type": "string"}},
        "sources": {"type": "array", "items": {"type": "string"}},
    },
}

SYSTEM = """You are the DTC Analyzer in a car-diagnostics system. You interpret OBD-II trouble codes for one specific vehicle.

Rules:
- Ground every claim in the <reference> documents, the decoded scan, and the vehicle history. List the doc ids you relied on in `sources`.
- Use freeze-frame and live values as evidence. For example, high positive fuel trims with P0300 point to an air leak, not coils. Say which values support each cause in `why`.
- Rank likely causes most probable first. At equal probability, put the cheaper or easier-to-check cause first.
- For manufacturer-specific codes (P1xxx, P3xxx, B/C/U 1xxx-2xxx) with no reference definition, say that the exact definition depends on the make. Don't invent one.
- Brake, ABS, steering and airbag codes are safety-critical: set safe_to_drive to "with_caution" or "no" and require a professional inspection.
- A code is `recurring` if it appears in the vehicle history from earlier sessions.
- Be concise and practical. The reader may be a car owner, not a mechanic."""


def _codes_with_status(scan: dict) -> list[tuple[str, str]]:
    out, seen = [], set()
    for status in ("stored", "permanent", "pending"):
        for c in (scan.get("dtcs") or {}).get(status, []):
            if c not in seen:
                seen.add(c)
                out.append((c, status))
    return out


def history_codes(history: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for s in history:
        for c in s.get("scan", {}).get("all_codes", []):
            counts[c] = counts.get(c, 0) + 1
    return counts


class DTCAnalyzerAgent:
    name = "dtc_analyzer"

    def __init__(self, llm: LLM, rag: RAGAgent):
        self.llm, self.rag = llm, rag

    def analyze(self, scan: dict, vehicle: dict | None = None, history: list[dict] | None = None) -> dict:
        codes = _codes_with_status(scan)
        hist = history_codes(history or [])
        if not codes:
            return self._no_codes(scan)
        kb = {c: dtc_catalog.lookup(c) for c, _ in codes}
        obs = evidence.observations(scan.get("live"), scan.get("freeze_frame"))
        patterns = dtc_catalog.related_patterns([c for c, _ in codes])

        if self.llm.available:
            query = " ".join(f"{c} {kb[c]['description']}" for c, _ in codes) + " " + \
                    " ".join(o["text"] for o in obs)
            user = (
                f"<vehicle>{json.dumps((vehicle or {}).get('info', {}))}</vehicle>\n"
                f"<scan>{json.dumps({k: scan.get(k) for k in ('dtcs', 'freeze_frame', 'status', 'live', 'protocol')})}</scan>\n"
                f"<observations>{json.dumps(obs)}</observations>\n"
                f"<history_code_counts>{json.dumps(hist)}</history_code_counts>\n"
                f"<catalog>{json.dumps(kb)}</catalog>\n"
                f"<known_interactions>{json.dumps(patterns)}</known_interactions>\n"
                f"<reference>\n{self.rag.context(query, k=8)}\n</reference>\n"
                "Analyze every code in the scan."
            )
            try:
                result = self.llm.json(SYSTEM, user, SCHEMA, effort="medium")
                result["engine"] = "llm"
                return self._enforce_safety(result, kb)
            except LLMError as e:
                fallback = self._offline(codes, kb, hist, patterns, obs)
                fallback["note"] = f"AI unavailable ({e}); showing knowledge-base analysis."
                return fallback
        return self._offline(codes, kb, hist, patterns, obs)

    # ---------------------------------------------------------------- offline
    def _offline(self, codes, kb, hist, patterns, obs) -> dict:
        items = []
        for code, status in codes:
            info = kb[code]
            causes = [{"cause": c, "likelihood": "high" if i == 0 else "medium" if i < 3 else "low",
                       "why": "Most common cause for this code" if i == 0 else "Common cause for this code"}
                      for i, c in enumerate(info["likely_causes"])]
            plan = list(info["first_checks"])
            sev = info["severity"]
            if status == "pending" and sev != "critical":
                sev = SEVERITY_ORDER[max(0, SEVERITY_ORDER.index(sev) - 1)]
            items.append({"code": code, "status": status, "description": info["description"], "severity": sev,
                          "likely_causes": causes, "diagnostic_plan": plan, "recurring": code in hist,
                          "manufacturer_specific": info["manufacturer_specific"]})
        overall = max((i["severity"] for i in items), key=SEVERITY_ORDER.index)
        safety = any(kb[c]["safety_critical"] for c, _ in codes)
        safe = "no" if overall == "critical" else "with_caution" if (overall == "high" or safety) else "yes"
        interactions = patterns + [o["text"] for o in obs if o["level"] != "info"]
        summary = (f"{len(items)} code(s) found. Most serious: {max(items, key=lambda i: SEVERITY_ORDER.index(i['severity']))['code']}"
                   f" ({overall}).")
        return {"summary": summary, "overall_severity": overall, "safe_to_drive": safe, "codes": items,
                "interactions": interactions, "sources": ["dtc-catalog"], "engine": "knowledge-base"}

    def _no_codes(self, scan: dict) -> dict:
        status = scan.get("status") or {}
        obs = evidence.observations(scan.get("live"), scan.get("freeze_frame"))
        msg = "No trouble codes stored or pending."
        if status.get("incomplete"):
            msg += " Incomplete readiness monitors: " + ", ".join(status["incomplete"]) + \
                   ". If codes were cleared recently, drive a full drive cycle before an inspection."
        return {"summary": msg, "overall_severity": "low", "safe_to_drive": "yes", "codes": [],
                "interactions": [o["text"] for o in obs], "sources": [], "engine": "rules"}

    @staticmethod
    def _enforce_safety(result: dict, kb: dict) -> dict:
        """Never let the model downgrade safety-critical systems."""
        if any(v["safety_critical"] for v in kb.values()) and result.get("safe_to_drive") == "yes":
            result["safe_to_drive"] = "with_caution"
            result.setdefault("interactions", []).append(
                "Brake/ABS/airbag code present - have the vehicle physically inspected by a professional.")
        return result
