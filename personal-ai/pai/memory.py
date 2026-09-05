"""Four-tier memory store.

    T0 Working    - the live conversation (RAM, not stored here)
    T1 Episodic   - what happened and when
    T2 Semantic   - stable facts about the user (BITEMPORAL)
    T3 Procedural - learned rules about HOW to talk to the user

Design decisions worth stating, because they are the ones that keep this
subsystem from destroying itself over months of use:

1.  T2 is bitemporal. Facts are never deleted or overwritten, they are
    *superseded*. When the user changes their mind the old fact gets a
    valid_to timestamp and points at its replacement. This is what lets the
    assistant say "you used to prefer X, you switched to Y in June" instead
    of silently contradicting itself, and it is the only defence against
    memory staleness that actually works.

2.  T3 is hard-capped. An uncapped behavioural rule list bloats the system
    prompt, develops internal contradictions, and eventually paralyses the
    model. When the cap is hit the lowest-value rule is evicted.

3.  Some T3 rules are PROTECTED. Preference learning can never weaken or
    remove them. This is the anti-sycophancy mechanism: without it, months
    of "user reacted well to agreement" evidence will quietly erode the
    assistant's willingness to disagree.

4.  Every write records its provenance and trust level. Retrieved content
    can never reach this store.
"""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from typing import Iterable, Optional, Sequence

from .trust import Trust, TrustViolation, require

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Raw conversation log. Source of truth for the learning loop.
CREATE TABLE IF NOT EXISTS turns (
    id           INTEGER PRIMARY KEY,
    session_id   TEXT    NOT NULL,
    ts           REAL    NOT NULL,
    role         TEXT    NOT NULL CHECK (role IN ('user','assistant','system','tool')),
    text         TEXT    NOT NULL,
    lang         TEXT,                    -- 'en' | 'hi' | 'hinglish' | NULL
    trust        INTEGER NOT NULL,
    meta         TEXT    NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id, ts);

-- T1: episodic. What happened, when.
CREATE TABLE IF NOT EXISTS episodes (
    id           INTEGER PRIMARY KEY,
    session_id   TEXT    NOT NULL,
    ts_start     REAL    NOT NULL,
    ts_end       REAL    NOT NULL,
    summary      TEXT    NOT NULL,
    salience     REAL    NOT NULL DEFAULT 0.5,
    meta         TEXT    NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_episodes_ts ON episodes(ts_end DESC);

-- T2: semantic, bitemporal. Facts are superseded, never overwritten.
CREATE TABLE IF NOT EXISTS facts (
    id            INTEGER PRIMARY KEY,
    subject       TEXT    NOT NULL,
    predicate     TEXT    NOT NULL,
    object        TEXT    NOT NULL,
    confidence    REAL    NOT NULL DEFAULT 0.7,
    valid_from    REAL    NOT NULL,       -- when this became true
    valid_to      REAL,                   -- NULL = still current
    recorded_at   REAL    NOT NULL,       -- when the system learned it
    superseded_by INTEGER REFERENCES facts(id),
    source_turn   INTEGER REFERENCES turns(id),
    trust         INTEGER NOT NULL,
    meta          TEXT    NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_facts_sp ON facts(subject, predicate);
CREATE INDEX IF NOT EXISTS idx_facts_current ON facts(subject, predicate, valid_to);

-- T3: procedural. HOW to talk to this user.
CREATE TABLE IF NOT EXISTS rules (
    id            INTEGER PRIMARY KEY,
    rule_key      TEXT    NOT NULL UNIQUE, -- stable slug for dedup/versioning
    text          TEXT    NOT NULL,
    scope         TEXT    NOT NULL DEFAULT 'global',
    confidence    REAL    NOT NULL DEFAULT 0.5,
    status        TEXT    NOT NULL DEFAULT 'candidate'
                  CHECK (status IN ('candidate','active','archived','rejected')),
    protected     INTEGER NOT NULL DEFAULT 0,  -- 1 = learning may never weaken it
    version       INTEGER NOT NULL DEFAULT 1,
    created_at    REAL    NOT NULL,
    last_confirmed REAL   NOT NULL,
    superseded_by INTEGER REFERENCES rules(id),
    meta          TEXT    NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_rules_status ON rules(status, confidence DESC);

-- Evidence backing each rule. A rule is only promoted past a threshold.
CREATE TABLE IF NOT EXISTS rule_evidence (
    id          INTEGER PRIMARY KEY,
    rule_id     INTEGER NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
    turn_id     INTEGER REFERENCES turns(id),
    session_id  TEXT    NOT NULL,
    signal      TEXT    NOT NULL,
    ts          REAL    NOT NULL,
    note        TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_ev_rule ON rule_evidence(rule_id);
-- One observation per (rule, session): stops a single conversation from
-- manufacturing an evidence threshold by repeating itself.
CREATE UNIQUE INDEX IF NOT EXISTS idx_ev_unique ON rule_evidence(rule_id, session_id);

-- Full history for rollback/inspection.
CREATE TABLE IF NOT EXISTS rule_versions (
    id         INTEGER PRIMARY KEY,
    rule_id    INTEGER NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
    version    INTEGER NOT NULL,
    text       TEXT    NOT NULL,
    status     TEXT    NOT NULL,
    confidence REAL    NOT NULL,
    ts         REAL    NOT NULL,
    reason     TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_rv_rule ON rule_versions(rule_id, version DESC);
"""


@dataclass
class Rule:
    id: int
    rule_key: str
    text: str
    scope: str
    confidence: float
    status: str
    protected: bool
    version: int
    created_at: float
    last_confirmed: float
    evidence_count: int = 0

    def to_prompt_line(self) -> str:
        return f"- {self.text}"


@dataclass
class Fact:
    id: int
    subject: str
    predicate: str
    object: str
    confidence: float
    valid_from: float
    valid_to: Optional[float]
    recorded_at: float
    superseded_by: Optional[int]

    @property
    def is_current(self) -> bool:
        return self.valid_to is None


class MemoryStore:
    """SQLite-backed four-tier memory."""

    # Hard cap on active T3 rules. Above ~50 the system prompt bloats and
    # rules start contradicting each other; below ~20 there is not enough
    # personalisation to notice. 40 is the operating point.
    MAX_ACTIVE_RULES = 40

    def __init__(self, path: str = ":memory:", max_active_rules: int | None = None):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        if max_active_rules is not None:
            self.MAX_ACTIVE_RULES = max_active_rules

    def close(self) -> None:
        self.db.close()

    # ---------------------------------------------------------------- turns

    def add_turn(
        self,
        session_id: str,
        role: str,
        text: str,
        trust: Trust,
        lang: str | None = None,
        ts: float | None = None,
        meta: dict | None = None,
    ) -> int:
        cur = self.db.execute(
            "INSERT INTO turns(session_id, ts, role, text, lang, trust, meta) "
            "VALUES (?,?,?,?,?,?,?)",
            (session_id, ts or time.time(), role, text, lang, int(trust),
             json.dumps(meta or {})),
        )
        self.db.commit()
        return cur.lastrowid

    def turns(self, session_id: str) -> list[sqlite3.Row]:
        return list(self.db.execute(
            "SELECT * FROM turns WHERE session_id=? ORDER BY ts, id", (session_id,)
        ))

    # ------------------------------------------------------------- episodic

    def add_episode(
        self, session_id: str, summary: str, ts_start: float, ts_end: float,
        salience: float = 0.5,
    ) -> int:
        cur = self.db.execute(
            "INSERT INTO episodes(session_id, ts_start, ts_end, summary, salience) "
            "VALUES (?,?,?,?,?)",
            (session_id, ts_start, ts_end, summary, salience),
        )
        self.db.commit()
        return cur.lastrowid

    def recent_episodes(self, limit: int = 5) -> list[sqlite3.Row]:
        return list(self.db.execute(
            "SELECT * FROM episodes ORDER BY ts_end DESC LIMIT ?", (limit,)
        ))

    # ------------------------------------------------------------- semantic

    def assert_fact(
        self,
        subject: str,
        predicate: str,
        obj: str,
        trust: Trust,
        confidence: float = 0.7,
        valid_from: float | None = None,
        source_turn: int | None = None,
    ) -> int:
        """Record a fact, superseding any current fact with the same (s,p).

        This is the bitemporal write. The previous value is not destroyed:
        it gets a valid_to and a pointer to its replacement, so the history
        stays queryable.
        """
        # Use the property, not a bare comparison. The mutation audit found
        # that Trust.may_write_memory was dead code: flipping it to always
        # return True changed nothing, because this guard duplicated the
        # comparison instead of consulting it. Two sources of truth for one
        # invariant is exactly how a security property rots.
        if not trust.may_write_memory:
            raise TrustViolation("memory.assert_fact", trust, Trust.USER)
        now = valid_from or time.time()

        prev = self.db.execute(
            "SELECT id, object FROM facts "
            "WHERE subject=? AND predicate=? AND valid_to IS NULL",
            (subject, predicate),
        ).fetchone()

        # Re-asserting the same value is a confirmation, not a supersession.
        if prev is not None and prev["object"] == obj:
            self.db.execute(
                "UPDATE facts SET confidence=MIN(1.0, confidence+0.1), recorded_at=? "
                "WHERE id=?", (now, prev["id"]),
            )
            self.db.commit()
            return prev["id"]

        cur = self.db.execute(
            "INSERT INTO facts(subject,predicate,object,confidence,valid_from,"
            "valid_to,recorded_at,source_turn,trust) VALUES (?,?,?,?,?,NULL,?,?,?)",
            (subject, predicate, obj, confidence, now, now, source_turn, int(trust)),
        )
        new_id = cur.lastrowid
        if prev is not None:
            self.db.execute(
                "UPDATE facts SET valid_to=?, superseded_by=? WHERE id=?",
                (now, new_id, prev["id"]),
            )
        self.db.commit()
        return new_id

    def current_fact(self, subject: str, predicate: str) -> Optional[Fact]:
        row = self.db.execute(
            "SELECT * FROM facts WHERE subject=? AND predicate=? AND valid_to IS NULL",
            (subject, predicate),
        ).fetchone()
        return _fact(row) if row else None

    def fact_history(self, subject: str, predicate: str) -> list[Fact]:
        rows = self.db.execute(
            "SELECT * FROM facts WHERE subject=? AND predicate=? ORDER BY valid_from",
            (subject, predicate),
        )
        return [_fact(r) for r in rows]

    # ----------------------------------------------------------- procedural

    def upsert_rule(
        self,
        rule_key: str,
        text: str,
        *,
        scope: str = "global",
        confidence: float = 0.4,
        status: str = "candidate",
        protected: bool = False,
        reason: str = "created",
    ) -> int:
        now = time.time()
        row = self.db.execute(
            "SELECT id, version, protected FROM rules WHERE rule_key=?", (rule_key,)
        ).fetchone()
        if row is None:
            cur = self.db.execute(
                "INSERT INTO rules(rule_key,text,scope,confidence,status,protected,"
                "version,created_at,last_confirmed) VALUES (?,?,?,?,?,?,1,?,?)",
                (rule_key, text, scope, confidence, status, int(protected), now, now),
            )
            rid = cur.lastrowid
            self._snapshot(rid, 1, text, status, confidence, now, reason)
            self.db.commit()
            return rid

        rid, version = row["id"], row["version"] + 1
        self.db.execute(
            "UPDATE rules SET text=?, confidence=?, status=?, version=?, "
            "last_confirmed=? WHERE id=?",
            (text, confidence, status, version, now, rid),
        )
        self._snapshot(rid, version, text, status, confidence, now, reason)
        self.db.commit()
        return rid

    def _snapshot(self, rid, version, text, status, confidence, ts, reason) -> None:
        self.db.execute(
            "INSERT INTO rule_versions(rule_id,version,text,status,confidence,ts,reason)"
            " VALUES (?,?,?,?,?,?,?)",
            (rid, version, text, status, confidence, ts, reason),
        )

    def add_evidence(
        self, rule_id: int, session_id: str, signal: str,
        turn_id: int | None = None, note: str = "", ts: float | None = None,
    ) -> bool:
        """Record one observation supporting a rule.

        Returns False if this session already contributed evidence for this
        rule. That constraint matters: without it a single frustrated
        conversation could fabricate an entire evidence threshold on its own.
        """
        try:
            self.db.execute(
                "INSERT INTO rule_evidence(rule_id,turn_id,session_id,signal,ts,note) "
                "VALUES (?,?,?,?,?,?)",
                (rule_id, turn_id, session_id, signal, ts or time.time(), note),
            )
            self.db.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def evidence_count(self, rule_id: int) -> int:
        return self.db.execute(
            "SELECT COUNT(*) c FROM rule_evidence WHERE rule_id=?", (rule_id,)
        ).fetchone()["c"]

    def get_rule(self, rule_key: str) -> Optional[Rule]:
        row = self.db.execute(
            "SELECT * FROM rules WHERE rule_key=?", (rule_key,)
        ).fetchone()
        if row is None:
            return None
        return _rule(row, self.evidence_count(row["id"]))

    def active_rules(self) -> list[Rule]:
        rows = self.db.execute(
            "SELECT * FROM rules WHERE status='active' "
            "ORDER BY protected DESC, confidence DESC, last_confirmed DESC"
        )
        return [_rule(r, self.evidence_count(r["id"])) for r in rows]

    def set_status(self, rule_id: int, status: str, reason: str = "") -> None:
        row = self.db.execute("SELECT * FROM rules WHERE id=?", (rule_id,)).fetchone()
        if row is None:
            raise KeyError(rule_id)
        if row["protected"] and status in ("archived", "rejected"):
            raise TrustViolationProtected(row["rule_key"], status)
        version = row["version"] + 1
        now = time.time()
        self.db.execute(
            "UPDATE rules SET status=?, version=?, last_confirmed=? WHERE id=?",
            (status, version, now, rule_id),
        )
        self._snapshot(rule_id, version, row["text"], status, row["confidence"],
                       now, reason or f"status->{status}")
        self.db.commit()

    def rollback_rule(self, rule_id: int, to_version: int) -> None:
        row = self.db.execute(
            "SELECT * FROM rule_versions WHERE rule_id=? AND version=?",
            (rule_id, to_version),
        ).fetchone()
        if row is None:
            raise KeyError((rule_id, to_version))
        cur_version = self.db.execute(
            "SELECT version FROM rules WHERE id=?", (rule_id,)
        ).fetchone()["version"]
        new_version = cur_version + 1
        now = time.time()
        self.db.execute(
            "UPDATE rules SET text=?, status=?, confidence=?, version=?, "
            "last_confirmed=? WHERE id=?",
            (row["text"], row["status"], row["confidence"], new_version, now, rule_id),
        )
        self._snapshot(rule_id, new_version, row["text"], row["status"],
                       row["confidence"], now, f"rollback->v{to_version}")
        self.db.commit()

    def rule_versions(self, rule_id: int) -> list[sqlite3.Row]:
        return list(self.db.execute(
            "SELECT * FROM rule_versions WHERE rule_id=? ORDER BY version", (rule_id,)
        ))

    # ------------------------------------------------------- capacity/decay

    def enforce_cap(self) -> list[str]:
        """Evict the weakest active rules until the cap is satisfied.

        Protected rules are never evicted, and they do not count toward the
        cap being *exceeded* by eviction: if protected rules alone exceed the
        cap we keep them all and evict nothing, because losing an honesty
        guarantee to save prompt tokens is the wrong trade.
        """
        evicted: list[str] = []
        active = self.active_rules()
        if len(active) <= self.MAX_ACTIVE_RULES:
            return evicted
        # active_rules() is already ordered protected-first then by confidence,
        # so the tail is the weakest unprotected set.
        for rule in reversed(active):
            if len(self.active_rules()) <= self.MAX_ACTIVE_RULES:
                break
            if rule.protected:
                continue
            self.set_status(rule.id, "archived", reason="evicted: rule cap")
            evicted.append(rule.rule_key)
        return evicted

    def decay(self, now: float | None = None, half_life_days: float = 60.0,
              floor: float = 0.30) -> list[str]:
        """Age out rules that stopped being confirmed.

        A preference the user held in April and has not exercised since is
        weaker evidence than one confirmed last week. Protected rules do not
        decay -- they are policy, not observation.
        """
        now = now or time.time()
        archived: list[str] = []
        for rule in self.active_rules():
            if rule.protected:
                continue
            age_days = (now - rule.last_confirmed) / 86400.0
            if age_days <= 0:
                continue
            decayed = rule.confidence * (0.5 ** (age_days / half_life_days))
            self.db.execute(
                "UPDATE rules SET confidence=? WHERE id=?", (decayed, rule.id)
            )
            if decayed < floor:
                self.db.commit()
                self.set_status(rule.id, "archived", reason="decayed below floor")
                archived.append(rule.rule_key)
        self.db.commit()
        return archived


class TrustViolationProtected(Exception):
    """Raised when learning tries to remove a protected behavioural rule."""

    def __init__(self, rule_key: str, attempted: str):
        super().__init__(
            f"rule {rule_key!r} is protected; cannot set status={attempted!r}"
        )


def _rule(row: sqlite3.Row, evidence: int) -> Rule:
    return Rule(
        id=row["id"], rule_key=row["rule_key"], text=row["text"],
        scope=row["scope"], confidence=row["confidence"], status=row["status"],
        protected=bool(row["protected"]), version=row["version"],
        created_at=row["created_at"], last_confirmed=row["last_confirmed"],
        evidence_count=evidence,
    )


def _fact(row: sqlite3.Row) -> Fact:
    return Fact(
        id=row["id"], subject=row["subject"], predicate=row["predicate"],
        object=row["object"], confidence=row["confidence"],
        valid_from=row["valid_from"], valid_to=row["valid_to"],
        recorded_at=row["recorded_at"], superseded_by=row["superseded_by"],
    )
