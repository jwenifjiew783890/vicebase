"""OpenCode integration: turn a spoken request into a precise agent brief.

OpenCode exposes a headless HTTP API (`opencode serve --port 4096`). This
module is the client plus, more importantly, the BRIEF BUILDER.

The brief is the quality bottleneck for delegation. The 4B conversational
model should not attempt the coding; its job is to convert a casual,
often-Hinglish utterance into a specification a specialist agent can act
on. A vague brief wastes the specialist's capability entirely, so the
conversion is deterministic where it can be and model-assisted only where
it must be.

Everything the agent returns is Tainted: an agent's output is a program's
output, and a compromised or confused agent must not be able to drive the
gateway.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Optional

from .gateway import Tainted

DEFAULT_BASE = "http://127.0.0.1:4096"


# ---------------------------------------------------------------- the brief

@dataclass
class TaskBrief:
    """A specification precise enough for a coding agent to act on."""
    goal: str
    repo: str = ""
    files_hint: list[str] = field(default_factory=list)
    acceptance: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    language: str = "en"
    missing: list[str] = field(default_factory=list)

    @property
    def is_actionable(self) -> bool:
        """A brief without a goal or a repo is not worth sending."""
        return bool(self.goal.strip()) and not self.missing

    def render(self) -> str:
        lines = [f"# Task\n{self.goal}"]
        if self.repo:
            lines.append(f"\n## Repository\n{self.repo}")
        if self.files_hint:
            lines.append("\n## Likely files\n" +
                         "\n".join(f"- {f}" for f in self.files_hint))
        lines.append("\n## Acceptance criteria\n" +
                     "\n".join(f"- {c}" for c in
                               self.acceptance or ["The change builds and tests pass."]))
        if self.constraints:
            lines.append("\n## Constraints\n" +
                         "\n".join(f"- {c}" for c in self.constraints))
        return "\n".join(lines)


# Casual phrasings that carry no actionable content on their own.
_VAGUE = re.compile(
    r"^\s*(kar\s*do|kar\s*de|do it|fix it|fix karo|banao|bana do|"
    r"wo wala|us wala|kal wala|ye wala|that one|the thing|"
    r"mera assignment|assignment kar\s*(do|de)?)\s*[.!?]?\s*$",
    re.IGNORECASE)

_ACTION_VERB = re.compile(
    r"\b(fix|add|implement|refactor|remove|delete|rename|migrate|update|"
    r"write|create|build|test|debug|optimi[sz]e|handle|support)\b"
    r"|\b(theek kar|thik kar|banao|likh|jod|hata|badal)\b", re.IGNORECASE)

_FILEISH = re.compile(r"\b([\w./-]+\.(py|ts|tsx|js|jsx|go|rs|java|rb|md|json|"
                      r"yaml|yml|toml|sql|css|html))\b")

# Words that follow "in"/"for" but are not a repository name. Without this
# the pattern happily captured the literal word "repo" out of "for repo
# vicebase" and reported a complete brief pointing at a repository called
# "repo" -- an incomplete brief that looked complete, which is the exact
# failure mode the brief builder exists to prevent. Found by
# test_the_ack_gate_is_not_a_blanket_suppression once an acknowledgement
# started depending on brief completeness.
_NOT_A_REPO = {"repo", "repository", "project", "the", "a", "an", "this",
               "that", "my", "our", "it", "them", "there", "now", "me"}

# Two passes, in order. An explicit "repo X" is unambiguous and is checked
# first; a bare "in X" / "for X" is a weaker guess and is only consulted
# when the strong form is absent. One combined alternation does NOT work:
# scanning "in api.py for repo vicebase" left to right, the weak branch
# consumes "for repo" and the strong branch never sees "repo vicebase".
_REPO_NAMED = re.compile(
    r"\b(?:repo|repository|project)\s+([\w.-]{2,})\b", re.IGNORECASE)
_REPO_HINT = re.compile(
    r"\b(?:in|for)\s+(?:the\s+)?([\w.-]{2,})\b", re.IGNORECASE)


def build_brief(utterance: str, *, repo: str = "", lang: str = "en",
                recent_context: str = "") -> TaskBrief:
    """Deterministically extract what can be extracted; flag what is missing.

    This runs BEFORE any model call. A vague request should produce a brief
    marked as missing information so the orchestrator asks one clarifying
    question, rather than sending a specialist agent off on a guess.
    """
    text = utterance.strip()
    brief = TaskBrief(goal="", repo=repo, language=lang)

    if _VAGUE.match(text):
        brief.missing.append("what specifically needs to change")
        brief.goal = text
        return brief

    if not _ACTION_VERB.search(text):
        brief.missing.append("what action to take (fix, add, implement, ...)")

    brief.files_hint = list(dict.fromkeys(_FILEISH.findall(text)))
    brief.files_hint = [f[0] if isinstance(f, tuple) else f
                        for f in brief.files_hint]

    if not brief.repo:
        # Every candidate, not just the first. "implement retry logic in
        # api.py for repo vicebase" put a filename in the first slot; the
        # single-shot version rejected it and then gave up, reporting the
        # repository as missing when the sentence names it.
        for pattern in (_REPO_NAMED, _REPO_HINT):
            for m in pattern.finditer(text):
                cand = m.group(1)
                if not cand or _FILEISH.match(cand):
                    continue
                if cand.lower() in _NOT_A_REPO:
                    continue
                brief.repo = cand
                break
            if brief.repo:
                break
    if not brief.repo:
        brief.missing.append("which repository")

    # Strip the conversational wrapper; keep the instruction.
    # Repeating group: a single-shot strip left "opencode mein login page..."
    # after removing only the leading "yaar".
    goal = re.sub(r"^(?:\s*(?:yaar|arre|arey|acha|accha|bhai|hey|ok|okay|"
                  r"please|zara|thoda|opencode(?:\s+(?:mein|me|se|par|pe))?)"
                  r"[,\s]+)+", "", text, flags=re.IGNORECASE)
    goal = re.sub(r"\b(kar\s*do|kar\s*de|kardo)\b\s*$", "", goal,
                  flags=re.IGNORECASE).strip()
    brief.goal = goal or text

    # A goal that is only a verb and a pronoun has no object. "ye theek kar
    # do" ("fix this") passes the action-verb check and is still unusable --
    # the specialist has nothing to act on. Found by inspecting brief output
    # for "arre bhai opencode se ye theek kar do", which built the goal
    # "ye theek" and was marked actionable.
    content = re.sub(r"\b(ye|yeh|wo|woh|is|us|this|that|it|isko|usko|"
                     r"theek|thik|fix|kar|do|de|na|please|"
                     # Placeholder nouns carry no more information than the
                     # pronouns do. "that one fix" left the word "one" and
                     # was treated as actionable.
                     r"one|thing|stuff|ek|cheez|wala|wali|kaam|task|"
                     r"the|a|an|my|mera|meri|please|jaldi)\b", " ",
                     brief.goal, flags=re.IGNORECASE)
    if len(re.findall(r"[\w]+", content)) < 1 and not brief.files_hint:
        brief.missing.append("what specifically needs to change")

    if re.search(r"\btest", text, re.I):
        brief.acceptance.append("The named test passes.")
    brief.constraints.append("Do not change unrelated files.")
    return brief


# --------------------------------------------------------------- the client

@dataclass
class SessionResult:
    ok: bool
    session_id: str = ""
    summary: str = ""
    files_changed: list[str] = field(default_factory=list)
    error: str = ""
    elapsed_ms: float = 0.0

    def as_context(self) -> Tainted:
        return Tainted(self.summary, source="agent:opencode")


class OpenCodeClient:
    """Client for OpenCode's headless HTTP API."""

    def __init__(self, base_url: str = DEFAULT_BASE, timeout: float = 20.0,
                 opener=None):
        self.base = base_url.rstrip("/")
        self.timeout = timeout
        self._opener = opener or self._http

    def _http(self, method: str, path: str, payload: dict | None = None) -> dict:
        url = f"{self.base}{path}"
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            url, data=data, method=method,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            body = r.read().decode("utf-8", "replace")
        return json.loads(body) if body.strip() else {}

    def available(self) -> bool:
        try:
            self._opener("GET", "/health")
            return True
        except Exception:
            return False

    def delegate(self, brief: TaskBrief) -> SessionResult:
        """Send a brief and wait for the agent's result."""
        t0 = time.perf_counter()
        if not brief.is_actionable:
            return SessionResult(False, error=f"brief incomplete: {brief.missing}",
                                 elapsed_ms=0.0)
        try:
            created = self._opener("POST", "/session",
                                   {"cwd": brief.repo or "."})
            sid = str(created.get("id") or created.get("session_id") or "")
            if not sid:
                return SessionResult(False, error="no session id returned")
            resp = self._opener("POST", f"/session/{sid}/message",
                                {"parts": [{"type": "text",
                                            "text": brief.render()}]})
            summary = (resp.get("summary") or resp.get("text")
                       or resp.get("content") or "")
            files = resp.get("files_changed") or resp.get("files") or []
            return SessionResult(True, sid, str(summary), list(files),
                                 elapsed_ms=(time.perf_counter() - t0) * 1000)
        except urllib.error.URLError as exc:
            return SessionResult(False, error=f"opencode unreachable: {exc.reason}",
                                 elapsed_ms=(time.perf_counter() - t0) * 1000)
        except Exception as exc:
            return SessionResult(False, error=f"{type(exc).__name__}: {exc}",
                                 elapsed_ms=(time.perf_counter() - t0) * 1000)
