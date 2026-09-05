"""The learning loop: how the assistant gets better at talking to this user.

    conversation -> signal detection -> candidate rule -> dedup
      -> contradiction check -> evidence accumulation -> threshold
      -> review queue -> promotion -> decay

Two guards in this pipeline are the difference between a system that learns
the user and one that learns noise about the user:

  EVIDENCE THRESHOLD. A rule needs N independent observations, from N
  distinct sessions, before it can be promoted. Without this, one bad day
  becomes permanent behaviour.

  HUMAN REVIEW. Promotion is proposed, never automatic. Roughly five
  minutes a week. Without it the rule set drifts somewhere the user did
  not choose and there is no point at which they find out.

And one guard that protects the system from the user's own approval:

  ANTI-SYCOPHANCY. Candidates that would reduce honesty, increase
  agreement, or weaken a protected rule are rejected outright, no matter
  how much evidence supports them. Agreement feels good in the moment and
  scores well on every implicit signal, which is exactly why optimising
  for it is dangerous over months.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional, Protocol

from .memory import MemoryStore, Rule
from .signals import Detection, Signal, detect, detect_language

# ---------------------------------------------------------------------------
# Protected rules: policy, not observation. Learning may never weaken these.
# ---------------------------------------------------------------------------

PROTECTED_RULES: list[tuple[str, str]] = [
    ("honesty.unknown",
     "Say plainly when you don't know something. Never invent a fact to seem useful."),
    ("honesty.disagree",
     "Disagree when the user is wrong, and say why. Do not soften a real problem."),
    ("honesty.no_flattery",
     "Do not open with praise or agreement to make the user feel good."),
    ("honesty.grounded",
     "When answering from retrieved material, state where it came from. "
     "Do not present retrieved claims as your own knowledge."),
    ("safety.no_manipulation",
     "Never use emotional pressure to steer the user toward a decision."),
]

# Candidate rules whose text matches these are rejected regardless of evidence.
# This is the sycophancy tripwire.
SYCOPHANCY_PATTERNS = re.compile(
    r"\b(always agree|agree with (the )?user|avoid disagree|don'?t (dis)?agree|"
    r"never (dis)?agree|never contradict|don'?t (correct|challenge|push back)|"
    r"be more (agreeable|positive|encouraging|supportive)|"
    r"avoid (criticism|negative|saying no)|validate (the )?user|"
    r"tell (the )?user what they want|praise|compliment|flatter|"
    r"soften|never say no|avoid conflict)\b",
    re.IGNORECASE,
)


class SycophancyRejected(Exception):
    """A candidate rule would have made the assistant more agreeable."""


# ---------------------------------------------------------------------------
# Candidate proposal
# ---------------------------------------------------------------------------

@dataclass
class Candidate:
    rule_key: str
    text: str
    signal: Signal
    session_id: str
    turn_id: Optional[int] = None
    scope: str = "global"
    note: str = ""


class RuleProposer(Protocol):
    """Turns detected signals into candidate behavioural rules.

    In production this is an LLM call, run offline overnight where latency
    does not matter and a strong model is affordable. The deterministic
    implementation below exists so the whole pipeline is testable without a
    model, and so there is a fallback when no model is available.
    """

    def propose(self, det: Detection, session_id: str,
                turn_id: int | None, context: dict) -> Optional[Candidate]: ...


# Signal -> (rule_key, rule_text). Scoped by language where the lesson is
# language-specific, because "keep it short" and "Hindi me chhota rakho" are
# genuinely different preferences that can be held independently.
_TEMPLATES: dict[Signal, tuple[str, str]] = {
    Signal.STYLE_TOO_LONG: (
        "style.brevity",
        "Default to short answers for conversational questions. "
        "Expand only when the user asks for detail or the task needs it."),
    Signal.STYLE_TOO_SHORT: (
        "style.detail",
        "When the user asks about something technical or asks 'why', "
        "give the full explanation rather than a summary."),
    Signal.STYLE_TOO_FORMAL: (
        "style.register",
        "Match the user's casual register. Skip formal openers and closings."),
}


# Signals whose lesson is language-INDEPENDENT. Preferring short answers is
# a preference about this person, not about Hindi.
#
# An earlier version scoped every rule by the language the correction
# arrived in. The end-to-end learning test exposed the cost: correcting
# once in Hinglish and twice in English produced three pieces of evidence
# split across style.brevity.hinglish and style.brevity, so NEITHER reached
# the threshold of 3 and nothing was ever learned. Language scoping was
# fragmenting exactly the evidence it needed to accumulate.
#
# Only register/formality is genuinely language-specific -- how casual to be
# in Hindi really can differ from English.
_GLOBAL_SIGNALS = {Signal.STYLE_TOO_LONG, Signal.STYLE_TOO_SHORT}


class TemplateProposer:
    """Deterministic proposer. High precision, narrow coverage."""

    def propose(self, det: Detection, session_id: str,
                turn_id: int | None, context: dict) -> Optional[Candidate]:
        tpl = _TEMPLATES.get(det.signal)
        if tpl is None:
            return None
        key, text = tpl
        lang = det.lang
        if det.signal not in _GLOBAL_SIGNALS and lang in ("hi", "hinglish"):
            key = f"{key}.{lang}"
            text = f"When the conversation is in {lang}, {text[0].lower()}{text[1:]}"
            return Candidate(rule_key=key, text=text, signal=det.signal,
                             session_id=session_id, turn_id=turn_id,
                             scope=lang, note=det.matched)
        return Candidate(rule_key=key, text=text, signal=det.signal,
                         session_id=session_id, turn_id=turn_id,
                         scope="global", note=det.matched)


# ---------------------------------------------------------------------------
# The pipeline
# ---------------------------------------------------------------------------

@dataclass
class PipelineConfig:
    evidence_threshold: int = 3       # distinct sessions before promotion
    promote_confidence: float = 0.60
    decay_half_life_days: float = 60.0
    decay_floor: float = 0.30
    require_review: bool = True       # promotion needs a human OK


@dataclass
class ReviewItem:
    rule_key: str
    rule_id: int
    text: str
    evidence: int
    signals: list[str]
    proposed_at: float


class LearningLoop:
    def __init__(self, store: MemoryStore,
                 proposer: RuleProposer | None = None,
                 config: PipelineConfig | None = None):
        self.store = store
        self.proposer = proposer or TemplateProposer()
        self.cfg = config or PipelineConfig()
        self._install_protected()

    def _install_protected(self) -> None:
        for key, text in PROTECTED_RULES:
            if self.store.get_rule(key) is None:
                self.store.upsert_rule(key, text, confidence=1.0, status="active",
                                       protected=True, reason="protected baseline")

    # -------------------------------------------------------------- ingest

    def observe_turn(self, session_id: str, user_text: str,
                     turn_id: int | None = None, context: dict | None = None
                     ) -> list[Candidate]:
        """Process one user turn. Returns candidates that gained evidence."""
        accepted: list[Candidate] = []
        for det in detect(user_text):
            cand = self.proposer.propose(det, session_id, turn_id, context or {})
            if cand is None:
                continue
            try:
                if self._ingest(cand, det):
                    accepted.append(cand)
            except SycophancyRejected:
                # Deliberately swallowed here and recorded as a rejected rule
                # so it shows up in metrics rather than silently vanishing.
                continue
        return accepted

    def _ingest(self, cand: Candidate, det: Detection) -> bool:
        self._check_sycophancy(cand)

        existing = self.store.get_rule(cand.rule_key)
        if existing is not None and existing.protected:
            # A learned candidate can never modify a protected rule.
            raise SycophancyRejected(
                f"candidate targets protected rule {cand.rule_key}")

        contradicted = self._find_contradiction(cand)
        if contradicted is not None:
            # Do NOT silently overwrite. Weaken the old rule and queue both
            # for review -- the user decides which one reflects reality.
            self.store.db.execute(
                "UPDATE rules SET confidence=MAX(0.0, confidence-0.2) WHERE id=?",
                (contradicted.id,))
            self.store.db.commit()
            self.store.upsert_rule(
                cand.rule_key, cand.text, scope=cand.scope,
                confidence=0.35, status="candidate",
                reason=f"contradicts {contradicted.rule_key}")
        elif existing is None:
            self.store.upsert_rule(cand.rule_key, cand.text, scope=cand.scope,
                                   confidence=0.35, status="candidate",
                                   reason=f"proposed from {det.signal.value}")

        rule = self.store.get_rule(cand.rule_key)
        assert rule is not None
        return self.store.add_evidence(
            rule.id, cand.session_id, det.signal.value,
            turn_id=cand.turn_id, note=cand.note)

    def _check_sycophancy(self, cand: Candidate) -> None:
        if SYCOPHANCY_PATTERNS.search(cand.text):
            self.store.upsert_rule(
                f"rejected.{cand.rule_key}", cand.text, confidence=0.0,
                status="rejected", reason="sycophancy tripwire")
            raise SycophancyRejected(cand.text)

    # Rules that cannot both be active. Learned pairs only -- protected
    # rules are handled separately and are never on either side.
    _OPPOSED = [
        ({"style.brevity"}, {"style.detail"}),
        ({"style.brevity.hi"}, {"style.detail.hi"}),
        ({"style.brevity.hinglish"}, {"style.detail.hinglish"}),
    ]

    def _find_contradiction(self, cand: Candidate) -> Optional[Rule]:
        for a, b in self._OPPOSED:
            other = None
            if cand.rule_key in a:
                other = next(iter(b))
            elif cand.rule_key in b:
                other = next(iter(a))
            if other:
                r = self.store.get_rule(other)
                if r and r.status == "active":
                    return r
        return None

    # ------------------------------------------------------------- promote

    def review_queue(self) -> list[ReviewItem]:
        """Candidates that have met the evidence threshold and await approval."""
        items: list[ReviewItem] = []
        rows = self.store.db.execute(
            "SELECT * FROM rules WHERE status='candidate'")
        for row in rows:
            n = self.store.evidence_count(row["id"])
            if n < self.cfg.evidence_threshold:
                continue
            sigs = [r["signal"] for r in self.store.db.execute(
                "SELECT DISTINCT signal FROM rule_evidence WHERE rule_id=?",
                (row["id"],))]
            items.append(ReviewItem(row["rule_key"], row["id"], row["text"],
                                    n, sigs, row["created_at"]))
        return items

    def approve(self, rule_key: str) -> Rule:
        rule = self.store.get_rule(rule_key)
        if rule is None:
            raise KeyError(rule_key)
        n = self.store.evidence_count(rule.id)
        if n < self.cfg.evidence_threshold:
            raise ValueError(
                f"{rule_key}: {n} observations, need {self.cfg.evidence_threshold}")
        conf = min(1.0, self.cfg.promote_confidence + 0.05 * (n - self.cfg.evidence_threshold))
        self.store.upsert_rule(rule_key, rule.text, scope=rule.scope,
                               confidence=conf, status="active",
                               reason=f"approved with {n} observations")
        # Deactivate anything it contradicts, now that the user has chosen.
        for a, b in self._OPPOSED:
            other_key = None
            if rule_key in a:
                other_key = next(iter(b))
            elif rule_key in b:
                other_key = next(iter(a))
            if other_key:
                other = self.store.get_rule(other_key)
                if other and other.status == "active" and not other.protected:
                    self.store.set_status(other.id, "archived",
                                          reason=f"superseded by {rule_key}")
        self.store.enforce_cap()
        return self.store.get_rule(rule_key)

    def reject(self, rule_key: str, reason: str = "user rejected") -> None:
        rule = self.store.get_rule(rule_key)
        if rule is None:
            raise KeyError(rule_key)
        self.store.set_status(rule.id, "rejected", reason=reason)

    def auto_promote(self) -> list[str]:
        """Promote without review. Only for testing or an explicit opt-in."""
        if self.cfg.require_review:
            raise RuntimeError(
                "auto_promote called while require_review=True. Human review "
                "is the guard that keeps the rule set from drifting; disable "
                "it deliberately, not by accident.")
        promoted = []
        for item in self.review_queue():
            self.approve(item.rule_key)
            promoted.append(item.rule_key)
        return promoted

    # -------------------------------------------------------------- decay

    def run_decay(self, now: float | None = None) -> list[str]:
        return self.store.decay(now=now,
                                half_life_days=self.cfg.decay_half_life_days,
                                floor=self.cfg.decay_floor)

    # ------------------------------------------------------------ metrics

    def sycophancy_report(self) -> dict:
        rejected = self.store.db.execute(
            "SELECT COUNT(*) c FROM rules WHERE status='rejected'").fetchone()["c"]
        protected = self.store.db.execute(
            "SELECT COUNT(*) c FROM rules WHERE protected=1 AND status='active'"
        ).fetchone()["c"]
        return {
            "rejected_candidates": rejected,
            "protected_active": protected,
            "protected_expected": len(PROTECTED_RULES),
            "protected_intact": protected == len(PROTECTED_RULES),
        }

    # ------------------------------------------------------- prompt export

    def system_rules_block(self, lang: str = "en", max_chars: int = 1400) -> str:
        """Render active rules for the system prompt.

        Protected rules always come first and are never truncated away.
        Language-scoped rules are only included when they match the current
        conversation language, which keeps the block small and stops a Hindi
        brevity preference from silently governing English turns.
        """
        rules = self.store.active_rules()
        keep = [r for r in rules
                if r.scope == "global" or r.scope == lang]
        keep.sort(key=lambda r: (not r.protected, -r.confidence))
        lines, total = [], 0
        for r in keep:
            line = r.to_prompt_line()
            if not r.protected and total + len(line) > max_chars:
                continue
            lines.append(line)
            total += len(line)
        return "\n".join(lines)
