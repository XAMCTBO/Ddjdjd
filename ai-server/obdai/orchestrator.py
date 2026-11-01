"""Diagnostic orchestrator - the dispatcher in front of the specialist agents.

Every request enters here. The orchestrator:
  * routes it to the right agents (and only those),
  * enforces plan tiers and per-day rate limits,
  * owns the shared session memory (Store) that agents read and write.

Routing summary
  scan bundle        -> OBD Reader -> DTC Analyzer -> Recommendation (basic on free)
  "what is P0420"    -> DTC Analyzer knowledge lookup (no LLM tool loop needed)
  symptom / question -> Chat (which calls RAG / DTC lookups / vehicle context as tools)
  report request     -> Report Generator over all stored results for the session
  predictions        -> Prediction over the vehicle's session history
"""
from __future__ import annotations

import os
import re

from .agents.chat import ChatAgent
from .agents.dtc_analyzer import DTCAnalyzerAgent
from .agents.evidence import ambient_temp
from .agents.obd_reader import OBDReaderAgent
from .agents.prediction import PredictionAgent, summarize_samples
from .agents.rag import CODE, RAGAgent
from .agents.recommendation import RecommendationAgent
from .agents.report import ReportAgent
from .knowledge import dtc_catalog
from .llm import LLM
from .storage import Store

# per-day limits by tier; None = unlimited, 0 = not available on this tier
LIMITS = {
    "free": {"scan": 30, "chat": 10, "prediction": 0, "report": 0, "recommendation_full": 0},
    "pro": {"scan": None, "chat": 200, "prediction": None, "report": None, "recommendation_full": None},
}


class TierError(PermissionError):
    pass


class RateLimitError(RuntimeError):
    pass


class Orchestrator:
    def __init__(self, store: Store, llm: LLM | None = None, rag: RAGAgent | None = None):
        self.store = store
        self.llm = llm or LLM()
        self.rag = rag or RAGAgent()
        self.reader = OBDReaderAgent()
        self.analyzer = DTCAnalyzerAgent(self.llm, self.rag)
        self.recommender = RecommendationAgent(self.llm, self.rag)
        self.predictor = PredictionAgent(self.llm)
        self.reporter = ReportAgent()
        self.chat_agent = ChatAgent(self.llm, self.rag)

    # ---------------------------------------------------------------- gating
    def _gate(self, user: dict, feature: str, count: bool = True) -> bool:
        limit = LIMITS.get(user["tier"], LIMITS["free"]).get(feature)
        if limit == 0:
            return False
        if limit is not None and self.store.usage(user["token"], feature) >= limit:
            raise RateLimitError(f"Daily limit reached for {feature} on the {user['tier']} plan ({limit}/day).")
        if count:
            self.store.bump_usage(user["token"], feature)
        return True

    def _require(self, user: dict, feature: str):
        if not self._gate(user, feature):
            raise TierError(f"{feature} is available on the pro plan.")

    def _vehicle(self, user: dict, vehicle_id) -> dict:
        v = self.store.vehicle(int(vehicle_id), user["token"]) if vehicle_id else None
        if not v:
            raise KeyError("vehicle not found")
        return v

    # ---------------------------------------------------------------- flows
    def ingest_scan(self, user: dict, payload: dict) -> dict:
        """Phone uploads a raw scan bundle (and optionally recorded samples)."""
        self._gate(user, "scan")
        decoded = self.reader.decode(payload.get("raw") or {})
        info = payload.get("vehicle") or {}
        vin = decoded.get("vin") or info.get("vin")
        vid = self.store.upsert_vehicle(user["token"], {k: v for k, v in info.items() if k != "vin"},
                                        payload.get("vehicle_id"), vin)
        vehicle = self.store.vehicle(vid)
        history = self.store.sessions(vid)
        samples = payload.get("samples") or []
        summary = summarize_samples(samples)
        sid = self.store.add_session(vid, decoded, samples, summary, payload.get("started"))
        diagnosis = self.analyzer.analyze(decoded, vehicle, history)
        self.store.save_result(vid, "dtc_analyzer", diagnosis, sid)
        full = self._gate(user, "recommendation_full")
        recs = self.recommender.recommend(diagnosis, decoded, user["profile"], ambient_temp(decoded), basic=not full)
        self.store.save_result(vid, "recommendation", recs, sid)
        return {"vehicle_id": vid, "session_id": sid, "decoded": decoded, "diagnosis": diagnosis,
                "recommendations": recs, "routed": ["obd_reader", "dtc_analyzer", "recommendation"]}

    def ingest_recording(self, user: dict, payload: dict) -> dict:
        """A drive recording with no fresh code scan - feeds the Prediction agent."""
        vid = self.store.upsert_vehicle(user["token"], payload.get("vehicle") or {}, payload.get("vehicle_id"))
        samples = payload.get("samples") or []
        summary = summarize_samples(samples)
        sid = self.store.add_session(vid, {"live": {}}, samples, summary, payload.get("started"))
        return {"vehicle_id": vid, "session_id": sid, "summary": summary, "routed": ["obd_reader"]}

    def predict(self, user: dict, vehicle_id) -> dict:
        self._require(user, "prediction")
        v = self._vehicle(user, vehicle_id)
        res = self.predictor.predict(self.store.sessions(v["id"]), v)
        self.store.save_result(v["id"], "prediction", res)
        return res

    def report(self, user: dict, vehicle_id, session_id=None, mode="owner", lang="en") -> str:
        self._require(user, "report")
        v = self._vehicle(user, vehicle_id)
        sessions = self.store.sessions(v["id"], with_samples=False)
        if not sessions:
            raise KeyError("no sessions for this vehicle")
        sid = int(session_id) if session_id else sessions[-1]["id"]
        session = self.store.session(sid)
        if not session or session["vehicle_id"] != v["id"]:
            raise KeyError("session not found")
        return self.reporter.render(
            v, session,
            self.store.latest_result(v["id"], "dtc_analyzer", sid),
            self.store.latest_result(v["id"], "recommendation", sid),
            self.store.latest_result(v["id"], "prediction"),
            sessions, mode=mode, lang=lang)

    def lookup(self, code: str) -> dict:
        return dtc_catalog.lookup(code)

    # ---------------------------------------------------------------- chat routing
    REPORT_INTENT = re.compile(r"\b(report|pdf|print|звіт)\b", re.I)
    DEFINITION_INTENT = re.compile(r"^\s*(what('?s| is| does)|meaning of|define|що (означає|таке))\b.{0,20}\b[PCBU][0-9][0-9A-F]{3}\b\s*(mean)?\??\s*$", re.I)
    PREDICT_INTENT = re.compile(r"\b(predict|forecast|how long|will .* fail|прогноз)\b", re.I)

    def chat(self, user: dict, vehicle_id, message: str) -> dict:
        v = self._vehicle(user, vehicle_id)
        message = (message or "").strip()[:2000]
        if not message:
            raise ValueError("empty message")
        # cheap paths that don't need the chat model
        if self.DEFINITION_INTENT.match(message):
            code = CODE.search(message).group(0).upper()
            info = dtc_catalog.lookup(code)
            text = (f"**{code}**: {info['description']}. Severity: {info['severity']}.\n"
                    + ("Common causes: " + "; ".join(info["likely_causes"]) + ".\n" if info["likely_causes"] else "")
                    + ("First checks: " + "; ".join(info["first_checks"]) if info["first_checks"] else ""))
            self.store.add_chat(v["id"], "user", message)
            self.store.add_chat(v["id"], "assistant", text)
            return {"text": text, "actions": [], "routed": ["dtc_analyzer"]}
        if self.REPORT_INTENT.search(message):
            allowed = LIMITS.get(user["tier"], LIMITS["free"]).get("report") != 0
            return {"text": "You can generate a printable report for your latest session." if allowed
                    else "PDF reports are available on the pro plan.",
                    "actions": [{"type": "open_report", "vehicle_id": v["id"]}] if allowed else [],
                    "routed": ["report"]}
        self._gate(user, "chat")

        def context():
            sessions = self.store.sessions(v["id"], limit=5, with_samples=False)
            latest = sessions[-1] if sessions else None
            ctx = {"vehicle": v, "latest_scan": latest["scan"] if latest else None,
                   "diagnosis": self.store.latest_result(v["id"], "dtc_analyzer"),
                   "recommendations": self.store.latest_result(v["id"], "recommendation"),
                   "predictions": self.store.latest_result(v["id"], "prediction"),
                   "recent_session_summaries": [s["summary"] for s in sessions]}
            if self.PREDICT_INTENT.search(message) and ctx["predictions"] is None \
                    and LIMITS.get(user["tier"], LIMITS["free"]).get("prediction") != 0:
                ctx["predictions"] = self.predictor.predict(self.store.sessions(v["id"]), v)
            return ctx

        history = self.store.chat_history(v["id"], limit=20)
        out = self.chat_agent.reply(message, history, context)
        self.store.add_chat(v["id"], "user", message)
        self.store.add_chat(v["id"], "assistant", out["text"])
        out["routed"] = ["chat", "rag", "dtc_analyzer"]
        return out


def default_tier() -> str:
    # Self-hosted: give yourself everything by default. Set OBDAI_DEFAULT_TIER=free to mimic a freemium setup.
    return os.environ.get("OBDAI_DEFAULT_TIER", "pro")
