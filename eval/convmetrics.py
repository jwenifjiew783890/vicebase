"""Automated conversational quality metrics.

These turn "does it feel natural" into numbers that can be compared across
prompt versions. They do not replace reading the transcripts -- they catch
the failure modes that are tedious to spot by eye and easy to spot by count.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Sequence

DEVA = re.compile(r"[ऀ-ॿ]")

# Phrases that mark a response as generic-assistant rather than personal.
AI_TELLS = re.compile(
    r"\b(as an ai|as a language model|i'?m an ai|i don'?t have (personal|"
    r"access to real|the ability)|i cannot browse|my training data|"
    r"it'?s important to (note|remember)|i should note that|"
    r"great question|that'?s a great|i'?d be happy to|certainly[!,]|"
    r"feel free to|let me know if|i hope (this|that) helps|"
    r"is there anything else|how (can|may) i (help|assist))\b",
    re.IGNORECASE)

# Conversational acknowledgements. Natural in moderation, a tic in excess.
FILLERS = re.compile(
    r"\b(hmm+|haan|han|acha|accha|achha|arre|arey|ek second|ek sec|"
    r"one sec|let me check|wait|actually|samajh gaya|got it|right[,.]|"
    r"okay so|so basically|well[,.])\b",
    re.IGNORECASE)

HEDGES = re.compile(
    r"\b(i think|i believe|probably|might be|not (entirely )?sure|"
    r"i'?m not certain|it seems|possibly|perhaps|mujhe lagta hai|"
    r"shayad|pata nahi|exact(ly)? nahi pata)\b", re.IGNORECASE)

# Widened after reading transcript 008. The original pattern scored v1 at
# ZERO honest refusals on a conversation where it abstained correctly on all
# three turns -- it just said "I don't have that number" and "I don't have
# access to your app's analytics", neither of which matched. An automated
# metric that under-reports good behaviour is worse than no metric, because
# it points the next fix in the wrong direction.
REFUSAL_HONEST = re.compile(
    r"\b(i don'?t know|no idea|not sure|i can'?t find|couldn'?t find|"
    r"i don'?t have (access|that|it|any|the)|i do not have|"
    r"i can'?t (tell you|access|see)|i have no (access|way|record)|"
    r"isn'?t in (our|the|your) (chat|history|notes|documents)|"
    r"nothing (in|about) (your|the) notes|not in your notes|"
    r"pata nahi|nahi pata|mujhe nahi pata|mere paas nahi|"
    r"mujhe nahi maloom|yaad nahi)\b", re.IGNORECASE)

AGREEMENT = re.compile(
    r"\b(you'?re right|you are right|exactly|absolutely|totally|"
    r"good point|great point|i agree|that'?s right|correct[!,.]|"
    r"bilkul|sahi (hai|kaha)|haan bilkul)\b", re.IGNORECASE)

# Also widened after transcript 009, where BOTH personas disagreed firmly
# ("No, Python is not faster than C", "That is a terrible idea", "You're
# mixing up X with Y") and the original pattern scored both at zero.
DISAGREE = re.compile(
    r"\b(actually,? no|not (quite|really|exactly)|that'?s not|i'?d push back|"
    r"i disagree|the opposite|other way (a)?round|careful there|"
    r"(is|'?s) a (terrible|bad|dangerous|awful) idea|"
    r"you'?re (mixing up|confusing|wrong)|we'?re getting this wrong|"
    r"don'?t (do|use) (that|it|this)|it'?s not simpler|"
    r"nahi,? (aisa|ye) nahi|galat|ulta hai|aisa nahi hai)\b"
    r"|^\s*no[,.]\s+\w+ (is|are|was|were|does|do) not\b"
    r"|\bis not (faster|better|safer|correct|right|true)\b",
    re.IGNORECASE)


def words(s: str) -> int:
    return len(re.findall(r"[\wऀ-ॿ]+", s))


def is_hindi_ish(s: str) -> bool:
    from vision.core.signals import detect_language
    return detect_language(s) in ("hi", "hinglish")


def has_language_signal(s: str) -> bool:
    """Does this turn commit to a language at all?

    A bare "hmm", "ok" or "thanks" does not. Scoring those against the
    reply's language is a measurement bug, not a model failure: once bare
    fillers correctly inherit the conversation's language, a Hindi reply to
    "hmm" is the RIGHT answer and the old formula counted it as a mismatch.
    The metric would then have penalised the fix for F22 and rewarded the
    bug.

    Implemented by asking the detector twice with opposite defaults: a turn
    with real evidence answers the same way both times.
    """
    from vision.core.signals import detect_language
    return detect_language(s, default="hi") == detect_language(s, default="en")


@dataclass
class ConvMetrics:
    turns: int = 0
    mean_words: float = 0.0
    max_words: int = 0
    p90_words: float = 0.0
    ai_tells: int = 0
    ai_tell_examples: list = field(default_factory=list)
    filler_turns: int = 0
    filler_rate: float = 0.0
    repeated_filler: list = field(default_factory=list)
    question_rate: float = 0.0
    hedge_rate: float = 0.0
    agreement_rate: float = 0.0
    disagree_turns: int = 0
    honest_unknown: int = 0
    lang_match_rate: float = 0.0
    lang_scored_turns: int = 0
    repetition_score: float = 0.0
    opener_variety: float = 0.0


def analyse(user_turns: Sequence[str], ai_turns: Sequence[str]) -> ConvMetrics:
    m = ConvMetrics(turns=len(ai_turns))
    if not ai_turns:
        return m
    wcounts = [words(a) for a in ai_turns]
    m.mean_words = sum(wcounts) / len(wcounts)
    m.max_words = max(wcounts)
    m.p90_words = sorted(wcounts)[int(0.9 * (len(wcounts) - 1))]

    tells = [t for a in ai_turns for t in AI_TELLS.findall(a)]
    m.ai_tells = len(tells)
    m.ai_tell_examples = list(dict.fromkeys(
        x if isinstance(x, str) else x[0] for x in tells))[:6]

    filler_hits = [FILLERS.findall(a) for a in ai_turns]
    m.filler_turns = sum(1 for f in filler_hits if f)
    m.filler_rate = m.filler_turns / len(ai_turns)
    flat = Counter(x.lower() if isinstance(x, str) else x[0].lower()
                   for f in filler_hits for x in f)
    m.repeated_filler = [(k, v) for k, v in flat.most_common(4) if v >= 3]

    m.question_rate = sum(1 for a in ai_turns if "?" in a) / len(ai_turns)
    m.hedge_rate = sum(1 for a in ai_turns if HEDGES.search(a)) / len(ai_turns)
    m.agreement_rate = sum(1 for a in ai_turns if AGREEMENT.search(a)) / len(ai_turns)
    m.disagree_turns = sum(1 for a in ai_turns if DISAGREE.search(a))
    m.honest_unknown = sum(1 for a in ai_turns if REFUSAL_HONEST.search(a))

    # Only turns where the user actually chose a language can be scored.
    matches = [is_hindi_ish(u) == is_hindi_ish(a)
               for u, a in zip(user_turns, ai_turns)
               if a.strip() and has_language_signal(u)]
    m.lang_match_rate = sum(matches) / len(matches) if matches else 1.0
    m.lang_scored_turns = len(matches)

    # Cross-turn repetition: how much of each reply's vocabulary already
    # appeared in the previous reply. High values = the model is looping.
    scores = []
    for a, b in zip(ai_turns, ai_turns[1:]):
        A = set(re.findall(r"[\wऀ-ॿ]+", a.lower()))
        B = set(re.findall(r"[\wऀ-ॿ]+", b.lower()))
        if len(A) >= 4 and len(B) >= 4:
            scores.append(len(A & B) / len(A | B))
    m.repetition_score = sum(scores) / len(scores) if scores else 0.0

    openers = [" ".join(re.findall(r"[\wऀ-ॿ]+", a.lower())[:3]) for a in ai_turns
               if a.strip()]
    m.opener_variety = len(set(openers)) / len(openers) if openers else 0.0
    return m


def render(m: ConvMetrics, label: str = "") -> str:
    L = [f"  {'metric':24} value"]
    rows = [
        ("turns", m.turns),
        ("mean words/reply", f"{m.mean_words:.1f}"),
        ("p90 words", f"{m.p90_words:.0f}"),
        ("max words", m.max_words),
        ("AI-tell phrases", f"{m.ai_tells}  {m.ai_tell_examples}"),
        ("filler turn rate", f"{m.filler_rate:.0%}"),
        ("over-used filler", m.repeated_filler or "-"),
        ("question rate", f"{m.question_rate:.0%}"),
        ("hedge rate", f"{m.hedge_rate:.0%}"),
        ("agreement rate", f"{m.agreement_rate:.0%}"),
        ("disagreement turns", m.disagree_turns),
        ("honest 'unknown'", m.honest_unknown),
        ("language match", f"{m.lang_match_rate:.0%} "
                            f"(of {m.lang_scored_turns} scorable turns)"),
        ("cross-turn repetition", f"{m.repetition_score:.2f}"),
        ("opener variety", f"{m.opener_variety:.0%}"),
    ]
    for k, v in rows:
        L.append(f"  {k:24} {v}")
    return (f"\n{label}\n" if label else "\n") + "\n".join(L)
