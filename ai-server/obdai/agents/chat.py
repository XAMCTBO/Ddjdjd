"""Chat agent - conversational co-pilot ("my car dies at the stop light").

Uses Claude tool use so the model pulls exactly what it needs: DTC lookups,
knowledge-base search, the latest scan/diagnosis/predictions for this car,
and a pointer to the app screen where the user can see a value live.

Stored chat history is plain text only (user text + final assistant text).
Each turn's tool loop runs append-only within that turn, so no thinking blocks
are ever replayed into an edited or truncated history.
"""
from __future__ import annotations

import json
import re

from ..knowledge import dtc_catalog
from ..llm import LLM, LLMError
from .rag import CODE, RAGAgent

# informal symptom words -> technical search terms
SYMPTOMS = [
    (r"dies|stall|cuts? out|shuts? off", "stall idle vacuum leak throttle body idle control fuel pressure crank sensor"),
    (r"jerk|hesitat|stumbl|bucking|shak|vibrat|rough", "misfire spark plug coil rough idle"),
    (r"smell.*(fuel|petrol|gas)|fuel smell", "EVAP fuel leak rich injector purge"),
    (r"sweet smell|smell.*sweet|coolant|steam", "coolant leak overheating head gasket thermostat"),
    (r"rattl|knock|ping", "knock sensor timing chain heat shield exhaust"),
    (r"overheat|temperature (high|gauge)|hot engine", "overheating cooling fan thermostat coolant"),
    (r"won'?t start|no start|hard start|cranks", "crank sensor fuel pressure battery starting"),
    (r"battery|alternator|charging|lights dim", "battery charging voltage alternator"),
    (r"check engine|engine light|mil", "check engine light trouble codes readiness"),
    (r"abs|traction|brake light|airbag|srs", "ABS wheel speed sensor airbag safety brakes"),
    (r"poor (fuel )?economy|mileage|consum", "fuel trim O2 sensor thermostat MAF"),
    (r"no power|limp|sluggish|slow accel", "underboost turbo limp mode throttle DPF"),
    (r"smoke|black smoke|white smoke|blue smoke", "rich injector head gasket oil burning DPF"),
    (r"inspection|emissions test|smog|mot|readiness", "readiness monitors drive cycle inspection"),
]
SCREENS = {"live": "Live data (gauges)", "scan": "Diagnostics → Scan codes", "record": "Recording",
           "ai": "AI diagnostics", "report": "AI diagnostics → Generate report"}

SYSTEM = """You are the chat co-pilot of a car-diagnostics app. The user is usually a car owner, not a mechanic, and talks informally ("it jerks", "smells like fuel").

How to work:
- Use your tools to ground answers. Look up codes with lookup_dtc, search the knowledge base with search_knowledge, and check this car's latest scan, diagnosis, and predictions before saying anything specific about it.
- If the description is vague, ask one or two short clarifying questions: when it happens (cold or warm, at idle or under load), any warning lights, recent work.
- When a live value would help (for example fuel trims for a suspected vacuum leak), call suggest_screen to point the user to the right app screen and say what value to watch.
- Keep answers short and practical: likely causes ranked, the cheapest check first, and when to see a mechanic.
- Brakes, steering and airbags: advise a professional inspection. Overheating, a flashing check-engine light, or a fuel smell inside the car: advise stopping driving.
- You're an assistant, not a certified diagnosis. Don't invent code definitions or specifications that aren't in the tool results."""

TOOLS = [
    {"name": "lookup_dtc", "description": "Definition, severity, likely causes and first checks for one OBD-II trouble code.",
     "input_schema": {"type": "object", "properties": {"code": {"type": "string", "description": "e.g. P0420"}},
                      "required": ["code"], "additionalProperties": False}, "strict": True},
    {"name": "search_knowledge", "description": "Search the repair knowledge base (guides, procedures, code combinations). Use technical terms.",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}},
                      "required": ["query"], "additionalProperties": False}, "strict": True},
    {"name": "get_vehicle_context", "description": "This car's info, latest decoded scan (codes, freeze frame, readiness, live values), latest diagnosis and predictions.",
     "input_schema": {"type": "object", "properties": {}, "required": [], "additionalProperties": False}, "strict": True},
    {"name": "suggest_screen", "description": "Point the user to an app screen. screen: live | scan | record | ai | report.",
     "input_schema": {"type": "object", "properties": {"screen": {"type": "string", "enum": list(SCREENS)},
                                                         "watch": {"type": "string", "description": "What to look at there"}},
                      "required": ["screen", "watch"], "additionalProperties": False}, "strict": True},
]


def expand_symptoms(text: str) -> str:
    extra = [terms for pat, terms in SYMPTOMS if re.search(pat, text, re.I)]
    return text + " " + " ".join(extra)


class ChatAgent:
    name = "chat"

    def __init__(self, llm: LLM, rag: RAGAgent):
        self.llm, self.rag = llm, rag

    def reply(self, message: str, history: list[dict], context_fn) -> dict:
        """context_fn() -> dict with vehicle/scan/diagnosis/prediction (lazy, only if the model asks)."""
        actions: list[dict] = []
        if self.llm.available:
            def run_tool(name, args):
                if name == "lookup_dtc":
                    return json.dumps(dtc_catalog.lookup(args["code"]))
                if name == "search_knowledge":
                    return self.rag.context(expand_symptoms(args["query"]), k=5)
                if name == "get_vehicle_context":
                    return json.dumps(context_fn())[:12000]
                if name == "suggest_screen":
                    actions.append({"type": "open_screen", "screen": args["screen"],
                                    "label": SCREENS[args["screen"]], "watch": args.get("watch", "")})
                    return "shown to user"
                raise ValueError(f"unknown tool {name}")

            msgs = history + [{"role": "user", "content": message}]
            try:
                text, _ = self.llm.tool_loop(SYSTEM, msgs, TOOLS, run_tool, effort="low")
                return {"text": text, "actions": actions, "engine": "llm"}
            except LLMError as e:
                out = self._offline(message, context_fn)
                out["text"] = f"(AI unavailable: {e})\n\n" + out["text"]
                return out
        return self._offline(message, context_fn)

    def _offline(self, message: str, context_fn) -> dict:
        codes = sorted({c.upper() for c in CODE.findall(message)})
        parts, actions = [], []
        for c in codes[:3]:
            info = dtc_catalog.lookup(c)
            causes = ", ".join(info["likely_causes"][:3]) or "make-specific: check service information"
            parts.append(f"**{c}** - {info['description']} (severity: {info['severity']}). Common causes: {causes}.")
        if not codes:
            ctx = context_fn() or {}
            diag = ctx.get("diagnosis") or {}
            hits = self.rag.search(expand_symptoms(message), k=2, sources=("article",))
            if hits:
                parts.append(f"From the guide *{hits[0]['title']}*:\n{hits[0]['text']}")
            if diag.get("summary"):
                parts.append(f"Your latest scan: {diag['summary']}")
            if re.search(r"lean|vacuum|dies|stall|trim|economy", expand_symptoms(message), re.I):
                actions.append({"type": "open_screen", "screen": "live", "label": SCREENS["live"],
                                "watch": "Short and long fuel trim at idle vs 2500 rpm"})
            if not parts:
                parts.append("Can you tell me more? When does it happen (cold/warm, idle/driving), and is any warning light on? "
                             "Running a code scan from the Diagnostics screen also helps.")
        return {"text": "\n\n".join(parts), "actions": actions, "engine": "knowledge-base"}
