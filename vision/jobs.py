"""Long-running work that survives you closing the tab.

A job is an agent run that outlives the request that started it. It has an
id, a status, a live log, a result and a cancel switch, and all of that is
written to the database as it happens -- so "what happened while I was
away" has an answer after a restart, which is the whole point.

Cancellation is cooperative and honest about being cooperative: a job is
asked to stop between steps and reports CANCELLED when it does. Nothing
here claims the ability to kill a step already inside a network call.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  id          TEXT PRIMARY KEY,
  created_at  REAL NOT NULL,
  updated_at  REAL NOT NULL,
  session_id  TEXT,
  agent       TEXT,
  request     TEXT,
  status      TEXT NOT NULL,     -- queued|running|done|failed|cancelled
  progress    TEXT,              -- last human-readable line
  log_json    TEXT,
  result_json TEXT
);
CREATE INDEX IF NOT EXISTS jobs_created ON jobs(created_at DESC);
"""

RUNNING, DONE, FAILED, CANCELLED, QUEUED = (
    "running", "done", "failed", "cancelled", "queued")


@dataclass
class Job:
    id: str
    agent: str
    request: str
    session_id: str = "default"
    status: str = QUEUED
    progress: str = ""
    log: list = field(default_factory=list)
    result: dict | None = None
    created_at: float = field(default_factory=time.time)

    def as_dict(self) -> dict:
        return {"id": self.id, "agent": self.agent, "request": self.request,
                "session_id": self.session_id, "status": self.status,
                "progress": self.progress, "log": self.log[-40:],
                "result": self.result, "created_at": self.created_at,
                "age_s": round(time.time() - self.created_at, 1)}


class JobStore:
    """Runs jobs on background threads and keeps the database current."""

    def __init__(self, db_path: str, runner):
        self.db = sqlite3.connect(str(db_path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.commit()
        self._runner = runner              # callable(agent, task, job) -> result
        self._lock = threading.RLock()
        self._cancel: dict[str, threading.Event] = {}
        self._live: dict[str, Job] = {}
        # Anything left "running" belongs to a process that is gone.
        with self._lock:
            self.db.execute(
                "UPDATE jobs SET status=?, progress=? WHERE status IN (?,?)",
                (FAILED, "interrupted by a restart", RUNNING, QUEUED))
            self.db.commit()

    # ------------------------------------------------------------- write
    def _save(self, job: Job) -> None:
        with self._lock:
            self.db.execute(
                "INSERT INTO jobs(id,created_at,updated_at,session_id,agent,"
                "request,status,progress,log_json,result_json) "
                "VALUES (?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET updated_at=excluded.updated_at,"
                "status=excluded.status,progress=excluded.progress,"
                "log_json=excluded.log_json,result_json=excluded.result_json",
                (job.id, job.created_at, time.time(), job.session_id, job.agent,
                 job.request, job.status, job.progress, json.dumps(job.log[-200:]),
                 json.dumps(job.result) if job.result else None))
            self.db.commit()

    # ------------------------------------------------------------- run
    def start(self, agent: str, task: str, session_id: str = "default") -> Job:
        job = Job(id=uuid.uuid4().hex[:12], agent=agent, request=task,
                  session_id=session_id, status=QUEUED)
        self._cancel[job.id] = threading.Event()
        self._live[job.id] = job
        self._save(job)

        def _work():
            job.status = RUNNING
            job.progress = "started"
            self._save(job)
            try:
                res = self._runner(agent, task, job)
                if self._cancel[job.id].is_set():
                    job.status = CANCELLED
                    job.progress = "cancelled"
                else:
                    job.result = res
                    job.status = DONE if res.get("ok") else FAILED
                    job.progress = res.get("summary", "")[:200]
            except Exception as exc:
                job.status = FAILED
                job.progress = f"{type(exc).__name__}: {exc}"
                job.log.append({"t": time.time(), "line": traceback.format_exc(limit=3)})
            finally:
                self._save(job)

        threading.Thread(target=_work, daemon=True, name=f"job-{job.id}").start()
        return job

    def note(self, job: Job, line: str) -> None:
        job.log.append({"t": time.time(), "line": line[:400]})
        job.progress = line[:200]
        self._save(job)

    def cancelled(self, job_id: str) -> bool:
        ev = self._cancel.get(job_id)
        return bool(ev and ev.is_set())

    def cancel(self, job_id: str) -> dict:
        ev = self._cancel.get(job_id)
        if not ev:
            return {"ok": False, "error": "no such live job"}
        ev.set()
        job = self._live.get(job_id)
        if job and job.status in (QUEUED, RUNNING):
            job.progress = "cancelling -- will stop after the current step"
            self._save(job)
        return {"ok": True, "id": job_id,
                "note": "cooperative: stops between steps"}

    # ------------------------------------------------------------- read
    def get(self, job_id: str) -> dict | None:
        live = self._live.get(job_id)
        if live:
            return live.as_dict()
        row = self.db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return self._row(row) if row else None

    def recent(self, limit: int = 30) -> list[dict]:
        rows = self.db.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,))
        return [self._row(r) for r in rows]

    @staticmethod
    def _row(r) -> dict:
        d = dict(r)
        for k, into in (("log_json", "log"), ("result_json", "result")):
            raw = d.pop(k, None)
            try:
                d[into] = json.loads(raw) if raw else ([] if into == "log" else None)
            except Exception:
                d[into] = [] if into == "log" else None
        d["age_s"] = round(time.time() - d["created_at"], 1)
        return d
