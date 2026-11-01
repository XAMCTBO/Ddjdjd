"""Minimal MCP (Model Context Protocol) endpoint over HTTP JSON-RPC.

Lets any MCP-capable AI client (e.g. Claude Desktop, Claude Code) use the
diagnostics tools directly: decode raw OBD responses, look up codes, search
the knowledge base, analyze a set of codes, and read a vehicle's history and
predictions. Same auth token as the REST API (Authorization: Bearer ...).
"""
from __future__ import annotations

import json

from .agents import obd_reader

PROTOCOL_VERSION = "2025-06-18"

TOOLS = [
    {"name": "decode_obd_response",
     "description": "Decode a raw ELM327 response. mode: 01 (live PID), 02 (freeze frame), 03/07/0A (DTCs), 09 (VIN), 0101 (readiness).",
     "inputSchema": {"type": "object", "properties": {"raw": {"type": "string"}, "mode": {"type": "string"},
                                                      "pid": {"type": "string", "description": "hex PID for mode 01/02"}},
                     "required": ["raw", "mode"]}},
    {"name": "lookup_dtc", "description": "Definition, severity, likely causes and first checks for a trouble code.",
     "inputSchema": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}},
    {"name": "search_knowledge", "description": "Search the repair knowledge base.",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "analyze_codes", "description": "Run the DTC Analyzer on a list of codes with optional freeze-frame values.",
     "inputSchema": {"type": "object", "properties": {
         "codes": {"type": "array", "items": {"type": "string"}},
         "freeze_frame": {"type": "object", "description": "e.g. {\"ltft1\": 14.8, \"rpm\": 780}"},
         "vehicle": {"type": "object", "description": "make/model/year/engine"}}, "required": ["codes"]}},
    {"name": "list_vehicles", "description": "Vehicles of the authenticated user.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "vehicle_history", "description": "Session summaries and the latest diagnosis for a vehicle.",
     "inputSchema": {"type": "object", "properties": {"vehicle_id": {"type": "integer"}}, "required": ["vehicle_id"]}},
    {"name": "predict_failures", "description": "Trend-based failure predictions for a vehicle (needs >= 3 sessions).",
     "inputSchema": {"type": "object", "properties": {"vehicle_id": {"type": "integer"}}, "required": ["vehicle_id"]}},
]


def _decode(args: dict):
    raw, mode = args["raw"], args["mode"].upper().replace("0X", "")
    pid = int(args["pid"], 16) if args.get("pid") else None
    if mode == "0101":
        return obd_reader.parse_status(raw)
    if mode in ("03", "07", "0A"):
        return obd_reader.parse_dtcs(raw, int(mode, 16))
    if mode == "09":
        vin = obd_reader.parse_vin(raw)
        return {"vin": vin, **obd_reader.describe_vin(vin)}
    if mode == "01" and pid is not None:
        return obd_reader.parse_mode01(raw, pid)
    if mode == "02" and pid is not None:
        return obd_reader.parse_freeze_frame(raw, pid)
    raise ValueError("unsupported mode/pid combination")


def call_tool(orch, user: dict, name: str, args: dict):
    if name == "decode_obd_response":
        return _decode(args)
    if name == "lookup_dtc":
        return orch.lookup(args["code"])
    if name == "search_knowledge":
        return orch.rag.search(args["query"], k=6)
    if name == "analyze_codes":
        ff = {k: {"key": k, "name": k, "unit": "", "value": v} for k, v in (args.get("freeze_frame") or {}).items()}
        scan = {"dtcs": {"stored": [c.upper() for c in args["codes"]], "pending": [], "permanent": []},
                "freeze_frame": ff, "live": {}}
        return orch.analyzer.analyze(scan, {"info": args.get("vehicle") or {}}, [])
    if name == "list_vehicles":
        return orch.store.vehicles(user["token"])
    if name == "vehicle_history":
        v = orch._vehicle(user, args["vehicle_id"])
        return {"vehicle": v, "sessions": [{"id": s["id"], "started": s["started"], "codes": s["scan"].get("all_codes", []),
                                            "summary": s["summary"]} for s in orch.store.sessions(v["id"])],
                "latest_diagnosis": orch.store.latest_result(v["id"], "dtc_analyzer")}
    if name == "predict_failures":
        return orch.predict(user, args["vehicle_id"])
    raise KeyError(f"unknown tool {name}")


def handle(orch, user: dict, req: dict):
    rid, method, params = req.get("id"), req.get("method"), req.get("params") or {}
    if rid is None:  # notification (e.g. notifications/initialized)
        return None

    def ok(result):
        return {"jsonrpc": "2.0", "id": rid, "result": result}

    if method == "initialize":
        return ok({"protocolVersion": params.get("protocolVersion", PROTOCOL_VERSION),
                   "capabilities": {"tools": {"listChanged": False}},
                   "serverInfo": {"name": "obd-ai-diagnostics", "version": "1.0.0"}})
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": TOOLS})
    if method == "tools/call":
        try:
            data = call_tool(orch, user, params.get("name"), params.get("arguments") or {})
            return ok({"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}], "isError": False})
        except Exception as e:  # tool errors are results, not protocol errors
            return ok({"content": [{"type": "text", "text": f"error: {e}"}], "isError": True})
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"method not found: {method}"}}
