import copy
import json
import os
import threading
import time
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

os.environ["OBDAI_OFFLINE"] = "1"  # tests never call the real API

from obdai import mcp  # noqa: E402
from obdai.agents import obd_reader as r  # noqa: E402
from obdai.agents.prediction import PredictionAgent, summarize_samples  # noqa: E402
from obdai.llm import LLM  # noqa: E402
from obdai.orchestrator import LIMITS, Orchestrator, TierError  # noqa: E402
from obdai.server import make_handler  # noqa: E402
from obdai.storage import Store  # noqa: E402

VIN_RAW = "014\r0: 49 02 01 31 47 31\r1: 4A 43 35 34 34 34 52\r2: 37 32 35 32 33 36 37\r\r>"
BUNDLE = {
    "ati": "ELM327 v1.5\r\r>", "dpn": "A6\r\r>",
    "status": "41 01 82 07 65 04\r\r>",
    "vin": VIN_RAW,
    "stored": "43 02 03 00 01 71\r\r>",     # CAN: count 2 -> P0300, P0171
    "pending": "47 00\r\r>",
    "permanent": "NO DATA\r\r>",
    "supported": {"00": "41 00 BE 3F A8 13\r\r>"},
    "freeze": {"02": "42 02 00 03 00\r>", "07": "42 07 00 93\r>", "0C": "42 0C 00 0C 30\r>", "05": "42 05 00 7B\r>"},
    "live": {"0C": "410C0BB8\r\r>", "05": "41 05 7B\r>", "07": "41 07 92\r>", "42": "41 42 37 DC\r>"},
}


class ReaderTests(unittest.TestCase):
    def test_compact_and_spaced_mode01(self):
        self.assertEqual(r.parse_mode01("410C1AF8\r\r>", 0x0C)["value"], 1726)
        self.assertEqual(r.parse_mode01("SEARCHING...\r41 05 7B\r\r>", 0x05)["value"], 83)
        self.assertIsNone(r.parse_mode01("NO DATA\r>", 0x05))

    def test_fuel_trim_sign(self):
        self.assertEqual(r.parse_mode01("41 07 92", 0x07)["value"], 14.1)
        self.assertEqual(r.parse_mode01("41 07 70", 0x07)["value"], -12.5)

    def test_dtcs_can_and_legacy(self):
        self.assertEqual(r.parse_dtcs("43 02 01 33 04 20\r>", 0x03), ["P0133", "P0420"])
        self.assertEqual(r.parse_dtcs("43 01 33 04 20 00 00\r>", 0x03), ["P0133", "P0420"])
        self.assertEqual(r.parse_dtcs("43 00\r>", 0x03), [])
        self.assertEqual(r.decode_dtc(0x41, 0x23), "C0123")
        self.assertEqual(r.decode_dtc(0xC1, 0x00), "U0100")

    def test_vin_multiframe(self):
        self.assertEqual(r.parse_vin(VIN_RAW), "1G1JC5444R7252367")
        self.assertIn(1994, r.describe_vin("1G1JC5444R7252367")["model_year_candidates"])

    def test_readiness(self):
        st = r.parse_status("41 01 81 07 65 04")
        self.assertTrue(st["mil_on"])
        self.assertEqual(st["dtc_count"], 1)
        self.assertEqual(st["incomplete"], ["Evaporative system"])
        self.assertIn("Catalyst", [m["name"] for m in st["monitors"]])

    def test_freeze_frame_and_supported(self):
        self.assertEqual(r.parse_freeze_frame("42 02 00 01 71", 0x02)["value"], "P0171")
        self.assertEqual(r.parse_freeze_frame("42 05 00 7B", 0x05)["value"], 83)
        sup = r.parse_supported("41 00 BE 3F A8 13", 0x00)
        self.assertIn(0x0C, sup)
        self.assertIn(0x20, sup)

    def test_full_bundle(self):
        d = r.OBDReaderAgent().decode(BUNDLE)
        self.assertEqual(d["dtcs"]["stored"], ["P0300", "P0171"])
        self.assertEqual(d["vin"], "1G1JC5444R7252367")
        self.assertIn("CAN", d["protocol"])
        self.assertEqual(d["freeze_frame"]["trigger_dtc"]["value"], "P0300")
        self.assertEqual(d["live"]["voltage"]["value"], 14.3)


def drive(ltft: float, warmup_slow: int = 0, volts: float = 14.2):
    """Synthetic 10-minute drive: cold start, idle, then cruise."""
    rows = []
    for i in range(600):
        coolant = min(90, 20 + i * (0.25 - warmup_slow * 0.0004))
        speed = 0 if i < 120 else 70
        rows.append({"t": i * 1000, "rpm": 800 if speed == 0 else 2200, "speed": speed, "coolant": round(coolant),
                     "stft": 1.0, "ltft": ltft, "voltage": volts})
    return rows


class PredictionTests(unittest.TestCase):
    def test_summary(self):
        s = summarize_samples(drive(4.0))
        self.assertAlmostEqual(s["trim_warm_b1"], 5.0)
        self.assertIn("warmup_s", s)

    def test_detects_drift(self):
        sessions = [{"started": time.time() - (5 - i) * 7 * 86400, "summary": summarize_samples(drive(4 + i * 3))}
                    for i in range(5)]
        res = PredictionAgent(LLM()).predict(sessions, {"info": {"km_per_day": 40}})
        self.assertTrue(res["ready"])
        top = res["components"][0]
        self.assertIn("Fuel mixture bank 1", top["component"])
        self.assertTrue(top["worsening"])
        self.assertIsNotNone(top["days_to_threshold"])

    def test_needs_three_sessions(self):
        res = PredictionAgent(LLM()).predict([{"started": 0, "summary": {"trim_warm_b1": 3}}])
        self.assertFalse(res["ready"])


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.orch = Orchestrator(self.store)
        self.token = self.store.create_user("t", "pro")
        self.user = self.store.user(self.token)

    def test_scan_flow_offline(self):
        out = self.orch.ingest_scan(self.user, {"raw": BUNDLE, "vehicle": {"make": "Chevrolet", "year": 1994},
                                                "samples": drive(14)})
        diag = out["diagnosis"]
        self.assertEqual([c["code"] for c in diag["codes"]], ["P0300", "P0171"])
        self.assertTrue(any("air leak" in x for x in diag["interactions"]))
        self.assertTrue(out["recommendations"]["steps"])
        html = self.orch.report(self.user, out["vehicle_id"], mode="sale", lang="uk")
        self.assertIn("P0300", html)
        self.assertIn("<svg", html)
        self.assertIn("Перевірка", html)

    def test_chat_routes_definition_without_model(self):
        vid = self.store.upsert_vehicle(self.token, {"make": "VW"})
        out = self.orch.chat(self.user, vid, "What does P0420 mean?")
        self.assertEqual(out["routed"], ["dtc_analyzer"])
        self.assertIn("Catalyst", out["text"])
        out = self.orch.chat(self.user, vid, "my car dies at the stop light")
        self.assertIn("chat", out["routed"])
        self.assertTrue(out["actions"])  # points the user to live fuel trims

    def test_free_tier_gating(self):
        tok = self.store.create_user("f", "free")
        u = self.store.user(tok)
        vid = self.store.upsert_vehicle(tok, {})
        with self.assertRaises(TierError):
            self.orch.predict(u, vid)
        for _ in range(LIMITS["free"]["chat"]):
            self.orch.chat(u, vid, "it shakes at idle")
        with self.assertRaises(Exception):
            self.orch.chat(u, vid, "it shakes at idle")

    def test_safety_codes_never_safe(self):
        scan = {"dtcs": {"stored": ["C0035"], "pending": [], "permanent": []}, "live": {}, "freeze_frame": {}}
        self.assertNotEqual(self.orch.analyzer.analyze(scan)["safe_to_drive"], "yes")

    def test_mcp(self):
        lst = mcp.handle(self.orch, self.user, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        self.assertTrue(lst["result"]["tools"])
        res = mcp.handle(self.orch, self.user, {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                                                 "params": {"name": "decode_obd_response",
                                                            "arguments": {"raw": "43 01 33 04 20 00 00", "mode": "03"}}})
        self.assertEqual(json.loads(res["result"]["content"][0]["text"]), ["P0133", "P0420"])
        self.assertIsNone(mcp.handle(self.orch, self.user, {"jsonrpc": "2.0", "method": "notifications/initialized"}))


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(Orchestrator(Store())))
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def call(self, path, body=None, token=None):
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {token}"} if token else {})})
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def test_end_to_end(self):
        st, body = self.call("/api/register", {"name": "me"})
        self.assertEqual(st, 200)
        token = json.loads(body)["token"]
        self.assertEqual(self.call("/api/me")[0], 401)
        st, body = self.call("/api/scan", {"raw": BUNDLE, "vehicle": {"make": "Chevrolet"}}, token)
        self.assertEqual(st, 200, body)
        vid = json.loads(body)["vehicle_id"]
        st, body = self.call(f"/api/vehicles/{vid}/report?mode=mechanic", token=token)
        self.assertEqual(st, 200)
        self.assertIn(b"ISO 15765-4", body)
        st, body = self.call(f"/api/vehicles/{vid}/chat", {"message": "what is P0171?"}, token)
        self.assertIn("lean", json.loads(body)["text"])
        self.assertEqual(self.call("/api/dtc/P0420")[0], 200)
        self.assertEqual(self.call("/")[0], 200)
        self.assertEqual(self.call("/api/vehicles/999/predictions", token=token)[0], 404)


if __name__ == "__main__":
    unittest.main()


class FakeBlock:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def to_dict(self):
        return dict(self.__dict__)


class FakeResp:
    def __init__(self, content, stop_reason="end_turn"):
        self.content, self.stop_reason = content, stop_reason


class FakeMessages:
    def __init__(self, script):
        self.script, self.calls = list(script), []

    def create(self, **kw):
        self.calls.append(copy.deepcopy(kw))  # snapshot: the caller keeps appending to its list
        return self.script.pop(0)


class FakeClient:
    def __init__(self, script):
        self.beta = FakeBlock(messages=FakeMessages(script))


class LLMPathTests(unittest.TestCase):
    """Exercises the Claude code path with a fake client (no network)."""

    def make(self, script):
        llm = LLM()
        llm.client = FakeClient(script)
        return llm, llm.client.beta.messages

    def test_structured_analysis_and_safety_override(self):
        answer = {"summary": "ABS sensor", "overall_severity": "medium", "safe_to_drive": "yes", "codes": [],
                  "interactions": [], "sources": ["dtc:C0035"]}
        llm, msgs = self.make([FakeResp([FakeBlock(type="text", text=json.dumps(answer))])])
        orch = Orchestrator(Store(), llm=llm)
        scan = {"dtcs": {"stored": ["C0035"], "pending": [], "permanent": []}, "live": {}, "freeze_frame": {}}
        res = orch.analyzer.analyze(scan)
        self.assertEqual(res["engine"], "llm")
        self.assertEqual(res["safe_to_drive"], "with_caution")  # model said "yes" for a brake code
        kw = msgs.calls[0]
        self.assertEqual(kw["model"], "claude-opus-5-5")
        self.assertEqual(kw["output_config"]["format"]["type"], "json_schema")
        self.assertEqual(kw["fallbacks"], "default")
        self.assertIn("<reference>", kw["messages"][0]["content"])

    def test_chat_tool_loop(self):
        script = [
            FakeResp([FakeBlock(type="tool_use", id="t1", name="lookup_dtc", input={"code": "P0171"}),
                      FakeBlock(type="tool_use", id="t2", name="suggest_screen", input={"screen": "live", "watch": "LTFT"})],
                     stop_reason="tool_use"),
            FakeResp([FakeBlock(type="text", text="Likely a vacuum leak.")]),
        ]
        llm, msgs = self.make(script)
        store = Store()
        orch = Orchestrator(store, llm=llm)
        tok = store.create_user("u", "pro")
        vid = store.upsert_vehicle(tok, {})
        out = orch.chat(store.user(tok), vid, "it idles rough and the light is on")
        self.assertEqual(out["text"], "Likely a vacuum leak.")
        self.assertEqual(out["actions"][0]["screen"], "live")
        second = msgs.calls[1]["messages"]
        results = second[-1]["content"]
        self.assertEqual([r["tool_use_id"] for r in results], ["t1", "t2"])  # both results in one message
        self.assertIn("lean", results[0]["content"])
        # stored history is plain text only
        self.assertEqual([m["role"] for m in store.chat_history(vid)], ["user", "assistant"])

    def test_refusal_falls_back_to_knowledge_base(self):
        llm, _ = self.make([FakeResp([], stop_reason="refusal")])
        orch = Orchestrator(Store(), llm=llm)
        scan = {"dtcs": {"stored": ["P0420"], "pending": [], "permanent": []}, "live": {}, "freeze_frame": {}}
        res = orch.analyzer.analyze(scan)
        self.assertEqual(res["engine"], "knowledge-base")
        self.assertIn("AI unavailable", res["note"])
