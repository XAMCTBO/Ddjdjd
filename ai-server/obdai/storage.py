"""SQLite persistence: users, vehicles, sessions, agent results, chat, usage.

The orchestrator's "shared session memory" is just these tables: every agent
reads what earlier agents wrote for the same session/vehicle.
"""
from __future__ import annotations

import json
import secrets
import sqlite3
import threading
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  token TEXT PRIMARY KEY, name TEXT, tier TEXT NOT NULL DEFAULT 'free',
  profile TEXT NOT NULL DEFAULT '{}', created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS vehicles (
  id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT NOT NULL, vin TEXT,
  info TEXT NOT NULL DEFAULT '{}', created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle_id INTEGER NOT NULL, started REAL NOT NULL,
  scan TEXT NOT NULL DEFAULT '{}', samples TEXT NOT NULL DEFAULT '[]', summary TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS results (
  id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, vehicle_id INTEGER NOT NULL,
  agent TEXT NOT NULL, data TEXT NOT NULL, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS chat (
  id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle_id INTEGER NOT NULL, role TEXT NOT NULL,
  content TEXT NOT NULL, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS usage (
  token TEXT NOT NULL, day TEXT NOT NULL, agent TEXT NOT NULL, n INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (token, day, agent));
CREATE INDEX IF NOT EXISTS ix_sessions_vehicle ON sessions(vehicle_id);
CREATE INDEX IF NOT EXISTS ix_results_vehicle ON results(vehicle_id, agent);
"""


class Store:
    def __init__(self, path: str | Path = ":memory:"):
        self._lock = threading.Lock()
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def _q(self, sql: str, args=()):
        with self._lock:
            cur = self.db.execute(sql, args)
            self.db.commit()
            return cur

    # ---------------------------------------------------------------- users
    def create_user(self, name: str = "", tier: str = "free", profile: dict | None = None) -> str:
        token = secrets.token_urlsafe(24)
        self._q("INSERT INTO users(token,name,tier,profile,created) VALUES(?,?,?,?,?)",
                (token, name, tier, json.dumps(profile or {}), time.time()))
        return token

    def user(self, token: str) -> dict | None:
        r = self._q("SELECT * FROM users WHERE token=?", (token,)).fetchone()
        if not r:
            return None
        return {"token": r["token"], "name": r["name"], "tier": r["tier"], "profile": json.loads(r["profile"])}

    def update_profile(self, token: str, profile: dict):
        u = self.user(token)
        merged = {**(u["profile"] if u else {}), **profile}
        self._q("UPDATE users SET profile=? WHERE token=?", (json.dumps(merged), token))
        return merged

    def set_tier(self, token: str, tier: str):
        self._q("UPDATE users SET tier=? WHERE token=?", (tier, token))

    # ---------------------------------------------------------------- vehicles
    def upsert_vehicle(self, owner: str, info: dict, vehicle_id: int | None = None, vin: str | None = None) -> int:
        if vehicle_id:
            v = self.vehicle(vehicle_id, owner)
            if v:
                merged = {**v["info"], **{k: x for k, x in info.items() if x not in (None, "")}}
                self._q("UPDATE vehicles SET info=?, vin=COALESCE(?, vin) WHERE id=?",
                        (json.dumps(merged), vin, vehicle_id))
                return vehicle_id
        if vin:
            r = self._q("SELECT id FROM vehicles WHERE owner=? AND vin=?", (owner, vin)).fetchone()
            if r:
                return self.upsert_vehicle(owner, info, r["id"], vin)
        cur = self._q("INSERT INTO vehicles(owner,vin,info,created) VALUES(?,?,?,?)",
                      (owner, vin, json.dumps(info), time.time()))
        return cur.lastrowid

    def vehicle(self, vehicle_id: int, owner: str | None = None) -> dict | None:
        sql, args = "SELECT * FROM vehicles WHERE id=?", [vehicle_id]
        if owner is not None:
            sql += " AND owner=?"
            args.append(owner)
        r = self._q(sql, args).fetchone()
        return {"id": r["id"], "vin": r["vin"], "info": json.loads(r["info"])} if r else None

    def vehicles(self, owner: str) -> list[dict]:
        rows = self._q("SELECT * FROM vehicles WHERE owner=? ORDER BY id", (owner,)).fetchall()
        return [{"id": r["id"], "vin": r["vin"], "info": json.loads(r["info"])} for r in rows]

    # ---------------------------------------------------------------- sessions
    def add_session(self, vehicle_id: int, scan: dict, samples: list | None = None,
                    summary: dict | None = None, started: float | None = None) -> int:
        cur = self._q("INSERT INTO sessions(vehicle_id,started,scan,samples,summary) VALUES(?,?,?,?,?)",
                      (vehicle_id, started or time.time(), json.dumps(scan), json.dumps(samples or []),
                       json.dumps(summary or {})))
        return cur.lastrowid

    def session(self, session_id: int) -> dict | None:
        r = self._q("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
        return self._session_row(r) if r else None

    def sessions(self, vehicle_id: int, limit: int = 100, with_samples: bool = False) -> list[dict]:
        rows = self._q("SELECT * FROM sessions WHERE vehicle_id=? ORDER BY started DESC, id DESC LIMIT ?",
                       (vehicle_id, limit)).fetchall()
        out = [self._session_row(r, with_samples) for r in rows]
        return list(reversed(out))  # oldest first

    @staticmethod
    def _session_row(r, with_samples: bool = True) -> dict:
        d = {"id": r["id"], "vehicle_id": r["vehicle_id"], "started": r["started"],
             "scan": json.loads(r["scan"]), "summary": json.loads(r["summary"])}
        if with_samples:
            d["samples"] = json.loads(r["samples"])
        return d

    # ---------------------------------------------------------------- agent results
    def save_result(self, vehicle_id: int, agent: str, data: dict, session_id: int | None = None) -> int:
        cur = self._q("INSERT INTO results(session_id,vehicle_id,agent,data,created) VALUES(?,?,?,?,?)",
                      (session_id, vehicle_id, agent, json.dumps(data), time.time()))
        return cur.lastrowid

    def latest_result(self, vehicle_id: int, agent: str, session_id: int | None = None) -> dict | None:
        sql, args = "SELECT data FROM results WHERE vehicle_id=? AND agent=?", [vehicle_id, agent]
        if session_id is not None:
            sql += " AND session_id=?"
            args.append(session_id)
        r = self._q(sql + " ORDER BY id DESC LIMIT 1", args).fetchone()
        return json.loads(r["data"]) if r else None

    # ---------------------------------------------------------------- chat
    def add_chat(self, vehicle_id: int, role: str, content) -> None:
        self._q("INSERT INTO chat(vehicle_id,role,content,created) VALUES(?,?,?,?)",
                (vehicle_id, role, json.dumps(content), time.time()))

    def chat_history(self, vehicle_id: int, limit: int = 40) -> list[dict]:
        rows = self._q("SELECT role, content FROM chat WHERE vehicle_id=? ORDER BY id DESC LIMIT ?",
                       (vehicle_id, limit)).fetchall()
        msgs = [{"role": r["role"], "content": json.loads(r["content"])} for r in reversed(rows)]
        # history must start on a plain user turn (not a dangling tool_result)
        while msgs and not (msgs[0]["role"] == "user" and isinstance(msgs[0]["content"], str)):
            msgs.pop(0)
        return msgs

    # ---------------------------------------------------------------- usage / rate limiting
    def bump_usage(self, token: str, agent: str) -> int:
        day = time.strftime("%Y-%m-%d")
        self._q("INSERT INTO usage(token,day,agent,n) VALUES(?,?,?,1) "
                "ON CONFLICT(token,day,agent) DO UPDATE SET n=n+1", (token, day, agent))
        return self.usage(token, agent)

    def usage(self, token: str, agent: str) -> int:
        r = self._q("SELECT n FROM usage WHERE token=? AND day=? AND agent=?",
                    (token, time.strftime("%Y-%m-%d"), agent)).fetchone()
        return r["n"] if r else 0
