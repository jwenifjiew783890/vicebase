"""Which agent, if any, should handle this turn?

Deterministic, like every other routing decision in this system. The model
is not asked "which agent should I use", because that is a control-flow
decision and control flow is not the model's job -- the same principle that
keeps the router, the gateway and the memory writes in ordinary code.

Returning None means "this is conversation", which is the common case and
the default. An assistant that routes small talk to a research agent is
worse than one with no agents at all.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Dispatch:
    agent: str | None = None
    task: str = ""          # the request with the trigger phrase removed
    utterance: str = ""     # exactly what the user said
    reason: str = ""


# Ordered. The first match wins, so the more specific patterns come first.
_RULES: list[tuple[str, re.Pattern, str]] = [
    ("memory", re.compile(
        r"^\s*(vision[,\s]+)?(remember|note that|yaad rakh(?:na|o)?)\b",
        re.I), "explicit instruction to remember"),
    ("memory", re.compile(
        r"\bwhat do you (remember|know) about\b|\bwhat did i tell you\b",
        re.I), "asking what is remembered"),
    # A goal that needs several different specialists, not one. Checked
    # before "research" so "research X and write it to a file" goes to the
    # crew rather than to a single searcher that cannot write files.
    ("crew", re.compile(
        r"\b(and then|, then |after that)\b.*\b(write|save|summar|report|code|open)\b"
        r"|^\s*(vision[,\s]+)?(do this|handle this|work on this|take care of)\b"
        r"|\bmulti[- ]step\b|\bstep by step and\b", re.I),
     "a goal needing several specialists"),
    ("browser", re.compile(
        r"^\s*(vision[,\s]+)?(open|visit|browse|go to|load)\s+\S*https?://"
        r"|\bopen (the )?(page|site|url|link)\b"
        r"|\bwhat(?:'s| is) on (this|that) page\b", re.I),
     "explicit page to open"),
    ("research", re.compile(
        r"^\s*(vision[,\s]+)?(research|investigate|look into|compare)\b"
        r"|\bdo (some )?research\b|\bresearch kar\b", re.I),
     "explicit research request"),
    ("coding", re.compile(
        r"^\s*(vision[,\s]+)?(write|build|create|make) (me )?(a |an )?"
        r"(python |small |simple )?(script|program|function|code)\b"
        r"|\bcode (this|it|kar)\b|\bwrite the code\b", re.I),
     "explicit coding request"),
    ("planner", re.compile(
        r"^\s*(vision[,\s]+)?(plan|outline|break down|help me plan)\b"
        r"|\bmake a plan\b|\bplan bana\b", re.I), "explicit planning request"),
    ("knowledge", re.compile(
        r"\b(my|the) (notes?|vault|obsidian)\b|\bcheck my notes\b"
        r"|\bmere notes?\b", re.I), "explicit personal-knowledge request"),
    ("files", re.compile(
        r"\b(find|search for|locate|open|list) (the |a |my )?"
        r"(file|files|folder|directory)\b|\bfile (dhoond|khol)\b", re.I),
     "explicit file request"),
    # Any "run X", not a safe subset. MEASURED: the pattern used to list
    # git|ls|pwd|cat|python|pytest|npm|make, which meant "run rm -rf /"
    # matched nothing, fell through to conversation, and was answered by
    # the MODEL instead of being refused by the gateway. The dispatcher was
    # doing safety filtering, which is the wrong layer -- routing decides
    # WHERE a request goes and the capability gateway decides whether it
    # may happen. A dangerous command must reach the thing that can say no.
    ("mcp", re.compile(
        r"\bmcp\b|\b(what|which) tools\b|\bconnected tools\b", re.I),
     "MCP tools"),
    ("desktop", re.compile(
        r"\b(screenshot|screen shot|what'?s on (my |the )?screen)\b"
        r"|^\s*(vision[,\s]+)?(open|launch|start) (the )?(app|application|chrome|firefox|"
        r"notepad|terminal|vscode|code|explorer|finder)\b", re.I),
     "desktop automation"),
    ("shell", re.compile(r"^\s*(?:vision[,\s]+)?run\s+`?(?P<cmd>.+?)`?\s*$",
                         re.I), "explicit command to run"),
    ("web", re.compile(
        r"^\s*(vision[,\s]+)?(search the web|google|look up online)\b"
        r"|\bweb pe search\b", re.I), "explicit web request"),
]

# A single word is conversation whatever it says: "plan" on its own is not
# a planning request and "remember" on its own is not a write. Two words
# can be a real command ("open chrome", "take screenshot"), so the floor
# stops at one.
_MIN_WORDS = 2


_HAS_URL = re.compile(r"https?://\S+", re.I)


def classify(text: str) -> Dispatch:
    words = text.split()
    # The length floor stops "plan" on its own becoming a planning request.
    # A URL is never ambiguous, so it is exempt: "open https://x.com" is two
    # words and unmistakably a browser request.
    if len(words) < _MIN_WORDS and not _HAS_URL.search(text):
        return Dispatch(utterance=text, reason="too short to be a task")
    for agent, pattern, reason in _RULES:
        m = pattern.search(text)
        if m:
            # The task is the utterance minus the trigger phrase, so
            # "research the GIL" researches "the GIL", not "research the GIL".
            # Two forms, because agents need different things. "research
            # the GIL" should SEARCH for "the GIL", so the trigger is
            # stripped -- but "remember I use neovim" is a write and the
            # verb is the whole intent, so the original is kept alongside.
            # Stripping only one of them broke the memory agent: it got
            # "I use neovim", matched no write pattern, and did a read.
            # A rule may name the exact payload with a `cmd` group --
            # "run git status" must dispatch the whole command, not the
            # sentence with "run git" cut out of it, which is how it
            # became "status".
            captured = m.groupdict().get("cmd") if m.groupdict() else None
            if captured:
                task = captured.strip()
            else:
                task = (text[:m.start()] + text[m.end():]).strip(" ,.:;-")
            return Dispatch(agent=agent, task=task or text, utterance=text,
                            reason=reason)
    return Dispatch(utterance=text, reason="conversation")
