"""Durable record of what Vision did.

Every turn and every agent run is written here, so "what happened while I
was away" has an answer after a restart. This is the persistence behind the
activity feed and the task list.
"""
from __future__ import annotations

import json
import sqlite3
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS activity (
  id          INTEGER PRIMARY KEY,
  ts          REAL NOT NULL,
  session_id  TEXT NOT NULL,
  request     TEXT NOT NULL,
  agent       TEXT,
  ok          INTEGER,
  summary     TEXT,
  steps_json  TEXT,
  ms          REAL
);
CREATE INDEX IF NOT EXISTS activity_ts ON activity(ts DESC);
"""


class TaskStore:
    def __init__(self, path: str):
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.commit()

    def record(self, session_id: str, request: str, reply) -> int:
        ar = getattr(reply, "agent_result", None)
        cur = self.db.execute(
            "INSERT INTO activity(ts,session_id,request,agent,ok,summary,steps_json,ms)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (time.time(), session_id, request, reply.agent,
             1 if (ar or {}).get("ok") else 0,
             (ar or {}).get("summary") or reply.text[:300],
             json.dumps((ar or {}).get("steps", [])), reply.ms))
        self.db.commit()
        return cur.lastrowid

    def recent(self, limit: int = 40) -> list[dict]:
        rows = self.db.execute(
            "SELECT * FROM activity ORDER BY ts DESC LIMIT ?", (limit,))
        out = []
        for r in rows:
            d = dict(r)
            try:
                d["steps"] = json.loads(d.pop("steps_json") or "[]")
            except Exception:
                d["steps"] = []
            out.append(d)
        return out
