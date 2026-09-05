"""Fact extraction from ordinary conversation.

The gap this closes, stated plainly in every previous version of the
report: the system learned *how* he liked to be spoken to and did not learn
*what he told it*. Facts arrived only through `store.assert_fact`, which is
an API call, not a conversation. "The AI should get better at talking to me
the more we talk" was two-thirds true.

DESIGN STANCE, inherited from signals.py and for the same reason: high
precision, low recall.

A missed fact costs nothing -- he will mention it again, or you can ask. A
WRONG fact is durable, reaches every later prompt, and is exactly the
material a confabulation is made of. This project spent three rounds
building guards against the assistant inventing things about him; an
extractor that guesses would be feeding the thing those guards exist to
stop.

So every pattern here fires only on an unambiguous first-person statement
of fact about himself, and everything else is left alone. Negations,
questions, hypotheticals and second-hand reports are excluded explicitly
rather than by hoping the patterns miss them.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Candidate:
    """One extracted fact, with the sentence it came from."""
    subject: str
    predicate: str
    object: str
    source: str          # the clause it was read out of
    pattern: str         # which rule fired, for debugging a bad extraction

    def as_tuple(self) -> tuple[str, str, str]:
        return (self.subject, self.predicate, self.object)


# --------------------------------------------------------------------- veto

# Nothing is extracted from a turn that is asking, negating, supposing, or
# reporting someone else. Checked BEFORE the patterns, because a pattern
# that matches inside "I don't use neovim" is worse than no pattern at all.
_VETO = re.compile(
    r"\?\s*$"                                   # a question
    r"|\b(don'?t|do not|never|no longer|used to|stopped|quit)\b"
    r"|\b(if|would|should|maybe|might|perhaps|suppose|imagine)\b"
    r"|\b(he|she|they|his|her|their) (uses?|works?|lives?|prefers?)\b"
    r"|\b(nahi|nahin|mat|kabhi nahi|pehle|shayad|agar)\b"
    r"|\bकभी नहीं|\bनहीं|\bअगर|\bशायद",
    re.IGNORECASE | re.UNICODE)

# A value that is a pronoun, a filler or a placeholder is not a fact.
_EMPTY_VALUE = {
    "it", "that", "this", "those", "these", "one", "thing", "stuff",
    "something", "anything", "nothing", "some", "a", "an", "the",
    "ye", "yeh", "wo", "woh", "kuch", "koi", "cheez", "wala", "wali",
    "aisa", "waisa", "sab", "kya",
}

# Values that are clearly not nouns the way these patterns want them.
_MAX_VALUE_WORDS = 6


# ----------------------------------------------------------------- patterns

# (predicate, regex). Group "v" is the value. Every regex is anchored on a
# first-person subject, so "he uses neovim" cannot match.
_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("editor", re.compile(
        r"\bi (?:use|code in|write in|work in)\s+(?P<v>[\w.+#-]+)"
        r"(?:\s+(?:as my|for my)\s+(?:editor|ide))?\b"
        r"|\bmy (?:editor|ide) is\s+(?P<v2>[\w.+#-]+)"
        r"|\bmain\s+(?P<v3>[\w.+#-]+)\s+use karta ho(?:on|un|n)?\b"
        r"|\bmera (?:editor|ide) (?P<v4>[\w.+#-]+) hai\b",
        re.IGNORECASE)),

    ("works_at", re.compile(
        r"\bi work (?:at|for)\s+(?P<v>[\w &.-]{2,40}?)(?:\s*[,.]|$)"
        r"|\bmain\s+(?P<v2>[\w &.-]{2,40}?)\s+me[in]?\s+kaam karta ho(?:on|un|n)?\b",
        re.IGNORECASE)),

    ("lives_in", re.compile(
        r"\bi live in\s+(?P<v>[\w &.-]{2,40}?)(?:\s*[,.]|$)"
        r"|\bmain\s+(?P<v2>[\w &.-]{2,40}?)\s+me[in]?\s+rehta ho(?:on|un|n)?\b",
        re.IGNORECASE)),

    ("studies", re.compile(
        r"\bi(?:'?m| am) studying\s+(?P<v>[\w &.-]{2,40}?)(?:\s*[,.]|$)"
        r"|\bmy (?:thesis|dissertation) is (?:on|about)\s+(?P<v2>[\w &.-]{2,60}?)(?:\s*[,.]|$)",
        re.IGNORECASE)),

    ("name", re.compile(
        r"\bmy name is\s+(?P<v>[\w.-]{2,30})\b"
        r"|\bmera na(?:a)?m\s+(?P<v2>[\w.-]{2,30})\s+hai\b",
        re.IGNORECASE)),

    ("works_when", re.compile(
        r"\bi (?:work|code) (?:best )?(?P<v>at night|late at night|in the "
        r"mornings?|early|late)\b"
        r"|\bmain\s+(?P<v2>raat ko|subah|din me[in]?|late night)\s+kaam karta",
        re.IGNORECASE)),

    ("prefers", re.compile(
        r"\bi prefer\s+(?P<v>[\w &.+#-]{2,40}?)(?:\s*[,.]|$)"
        r"|\bmujhe\s+(?P<v2>[\w &.+#-]{2,40}?)\s+pasand hai\b",
        re.IGNORECASE)),
]


def extract_facts(text: str, subject: str = "muaz") -> list[Candidate]:
    """Every unambiguous first-person fact in this turn. Usually none.

    `subject` is the user; these patterns only ever describe him, which is
    why there is no subject detection here and why the veto above rejects
    third-person statements outright.
    """
    out: list[Candidate] = []
    for clause in re.split(r"(?<=[.!?।])\s+|\s+(?:aur|and|but|lekin)\s+", text):
        clause = clause.strip()
        if not clause or _VETO.search(clause):
            continue
        for predicate, pattern in _PATTERNS:
            m = pattern.search(clause)
            if not m:
                continue
            value = next((g for g in m.groupdict().values() if g), "")
            value = value.strip(" .,;:-")
            if not _usable(value):
                continue
            out.append(Candidate(subject, predicate, value, clause,
                                 pattern=predicate))
            break          # one fact per clause; the first match wins
    return out


def _usable(value: str) -> bool:
    if not value:
        return False
    words = value.split()
    if len(words) > _MAX_VALUE_WORDS:
        return False
    return not all(w.lower().strip(".,") in _EMPTY_VALUE for w in words)
