"""HTTP API + web panel + MCP endpoint (stdlib only, besides the optional SDK).

Run:  python -m obdai.server --port 8787 --db obdai.sqlite
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import mcp
from .orchestrator import Orchestrator, RateLimitError, TierError, default_tier
from .storage import Store

log = logging.getLogger("obdai.server")
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
MAX_BODY = 8 * 1024 * 1024  # recordings can be large


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def make_handler(orch: Orchestrator):
    store = orch.store
    admin_key = os.environ.get("OBDAI_ADMIN_KEY")  # if set, registering needs it
    routes: list[tuple[str, re.Pattern, str]] = []

    def route(method, pattern):
        def deco(fn):
            routes.append((method, re.compile("^" + pattern + "$"), fn.__name__))
            return fn
        return deco

    class Handler(BaseHTTPRequestHandler):
        server_version = "obdai/1.0"

        # ------------------------------------------------------------ plumbing
        def log_message(self, fmt, *args):
            log.info("%s - %s", self.address_string(), fmt % args)

        def _cors(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Obd-Token, Mcp-Session-Id, Mcp-Protocol-Version")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

        def _send(self, status: int, body: bytes, ctype: str):
            self.send_response(status)
            self._cors()
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def json_out(self, data, status=200):
            self._send(status, json.dumps(data).encode(), "application/json; charset=utf-8")

        def body(self) -> dict:
            n = int(self.headers.get("Content-Length") or 0)
            if n > MAX_BODY:
                raise ApiError(413, "request too large")
            if not n:
                return {}
            try:
                data = json.loads(self.rfile.read(n))
            except json.JSONDecodeError:
                raise ApiError(400, "invalid JSON")
            if not isinstance(data, dict):
                raise ApiError(400, "JSON object expected")
            return data

        def token(self) -> str | None:
            auth = self.headers.get("Authorization", "")
            if auth.lower().startswith("bearer "):
                return auth[7:].strip()
            return self.headers.get("X-Obd-Token") or (self.query.get("token") or [None])[0]

        def user(self) -> dict:
            u = store.user(self.token() or "")
            if not u:
                raise ApiError(401, "missing or invalid token")
            return u

        def do_OPTIONS(self):
            self._send(204, b"", "text/plain")

        def do_GET(self):
            self._dispatch("GET")

        def do_HEAD(self):
            self._dispatch("GET")

        def do_POST(self):
            self._dispatch("POST")

        def _dispatch(self, method):
            url = urlparse(self.path)
            self.query = parse_qs(url.query)
            for m, rx, name in routes:
                mt = rx.match(url.path)
                if m == method and mt:
                    try:
                        return getattr(self, name)(*mt.groups())
                    except ApiError as e:
                        return self.json_out({"error": str(e)}, e.status)
                    except TierError as e:
                        return self.json_out({"error": str(e), "upgrade": True}, 402)
                    except RateLimitError as e:
                        return self.json_out({"error": str(e)}, 429)
                    except KeyError as e:
                        return self.json_out({"error": str(e).strip("'")}, 404)
                    except ValueError as e:
                        return self.json_out({"error": str(e)}, 400)
                    except Exception:
                        log.error("unhandled error\n%s", traceback.format_exc())
                        return self.json_out({"error": "internal error"}, 500)
            self.json_out({"error": "not found"}, 404)

        # ------------------------------------------------------------ web panel
        @route("GET", r"/")
        def index(self):
            self._send(200, (WEB_DIR / "index.html").read_bytes(), "text/html; charset=utf-8")

        @route("GET", r"/health")
        def health(self):
            self.json_out({"ok": True, "llm": orch.llm.available, "model": orch.llm.model if orch.llm.available else None,
                           "kb_chunks": len(orch.rag.chunks)})

        # ------------------------------------------------------------ account
        @route("POST", r"/api/register")
        def register(self):
            b = self.body()
            if admin_key and b.get("admin_key") != admin_key:
                raise ApiError(403, "registration requires the admin key")
            token = store.create_user(str(b.get("name", ""))[:80], b.get("tier") if admin_key and b.get("tier") else default_tier(),
                                      {"diy_level": "beginner", "tools": [], "lang": "en"})
            self.json_out({"token": token, "user": store.user(token)})

        @route("GET", r"/api/me")
        def me(self):
            u = self.user()
            self.json_out({**u, "vehicles": store.vehicles(u["token"])})

        @route("POST", r"/api/profile")
        def profile(self):
            u = self.user()
            b = self.body()
            allowed = {k: b[k] for k in ("diy_level", "tools", "lang", "units") if k in b}
            if "diy_level" in allowed and allowed["diy_level"] not in ("none", "beginner", "intermediate", "advanced"):
                raise ApiError(400, "diy_level must be none|beginner|intermediate|advanced")
            self.json_out({"profile": store.update_profile(u["token"], allowed)})

        # ------------------------------------------------------------ vehicles & sessions
        @route("POST", r"/api/vehicles")
        def add_vehicle(self):
            u = self.user()
            b = self.body()
            info = {k: b[k] for k in ("make", "model", "year", "engine", "fuel", "odometer_km", "km_per_day", "name") if k in b}
            vid = store.upsert_vehicle(u["token"], info, b.get("id"), b.get("vin"))
            self.json_out(store.vehicle(vid))

        @route("GET", r"/api/vehicles/(\d+)/sessions")
        def sessions(self, vid):
            u = self.user()
            v = orch._vehicle(u, vid)
            self.json_out({"vehicle": v, "sessions": store.sessions(v["id"], with_samples=False),
                           "diagnosis": store.latest_result(v["id"], "dtc_analyzer"),
                           "recommendations": store.latest_result(v["id"], "recommendation")})

        @route("POST", r"/api/scan")
        def scan(self):
            self.json_out(orch.ingest_scan(self.user(), self.body()))

        @route("POST", r"/api/recording")
        def recording(self):
            self.json_out(orch.ingest_recording(self.user(), self.body()))

        @route("GET", r"/api/vehicles/(\d+)/predictions")
        def predictions(self, vid):
            self.json_out(orch.predict(self.user(), vid))

        @route("GET", r"/api/vehicles/(\d+)/report")
        def report(self, vid):
            q = {k: v[0] for k, v in self.query.items()}
            mode = q.get("mode", "owner") if q.get("mode") in ("owner", "mechanic", "sale") else "owner"
            html = orch.report(self.user(), vid, q.get("session"), mode, q.get("lang", "en"))
            self._send(200, html.encode(), "text/html; charset=utf-8")

        @route("POST", r"/api/vehicles/(\d+)/chat")
        def chat(self, vid):
            self.json_out(orch.chat(self.user(), vid, str(self.body().get("message", ""))))

        # ------------------------------------------------------------ knowledge
        @route("GET", r"/api/dtc/([A-Za-z0-9]{5})")
        def dtc(self, code):
            self.json_out(orch.lookup(code))

        @route("GET", r"/api/search")
        def search(self):
            q = (self.query.get("q") or [""])[0]
            self.json_out({"results": orch.rag.search(q, k=8)})

        # ------------------------------------------------------------ MCP
        @route("POST", r"/mcp")
        def mcp_endpoint(self):
            user = self.user()
            resp = mcp.handle(orch, user, self.body())
            if resp is None:  # notification
                return self._send(202, b"", "text/plain")
            self.json_out(resp)

    return Handler


def main(argv=None):
    ap = argparse.ArgumentParser(description="OBD AI diagnostics server")
    ap.add_argument("--host", default=os.environ.get("OBDAI_HOST", "0.0.0.0"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("OBDAI_PORT", "8787")))
    ap.add_argument("--db", default=os.environ.get("OBDAI_DB", "obdai.sqlite"))
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    orch = Orchestrator(Store(args.db))
    log.info("LLM: %s", f"enabled ({orch.llm.model})" if orch.llm.available else "offline - knowledge-base mode")
    srv = ThreadingHTTPServer((args.host, args.port), make_handler(orch))
    log.info("listening on http://%s:%d", args.host, args.port)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
