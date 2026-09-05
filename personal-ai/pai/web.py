"""Web search backend.

Everything this module returns is Tainted. Web content is the least
trustworthy input in the system: it is attacker-authorable by construction,
and the gateway must be able to see that a value came from here.

The provider is pluggable because search endpoints rot. Two are wired: the
DuckDuckGo instant-answer API (no key, structured) and an HTML result
scrape (broader, more fragile). Both are best-effort; a search that returns
nothing must surface as EMPTY so the model says it could not find anything
rather than answering from memory.
"""
from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

from .gateway import Tainted, scan_for_injection

UA = "Mozilla/5.0 (compatible; personal-ai/1.0)"
# Per-request timeout, and a HARD budget for the whole search.
#
# Measured: a query where both providers failed took 22.7 seconds. The
# acknowledgement masks a wait of a few seconds, not twenty -- past that the
# user has concluded the assistant is broken. A search that cannot answer
# within the budget must return EMPTY promptly so the model says it could
# not find anything.
TIMEOUT = 6
TOTAL_BUDGET_S = 9.0


@dataclass
class WebResult:
    title: str
    snippet: str
    url: str
    source: str = "web"

    def as_context(self) -> Tainted:
        return Tainted(f"[{self.title} — {self.url}]\n{self.snippet}",
                       source=f"web:{_host(self.url)}")


def _host(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc or "unknown"
    except Exception:
        return "unknown"


def _get(url: str, timeout: int = TIMEOUT) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    for enc in ("utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def strip_html(s: str) -> str:
    return _WS.sub(" ", html.unescape(_TAG.sub(" ", s))).strip()


# ---------------------------------------------------------------- providers

def ddg_instant(query: str, k: int = 5) -> list[WebResult]:
    """DuckDuckGo instant-answer API. Structured, no key, often sparse."""
    url = ("https://api.duckduckgo.com/?q=" + urllib.parse.quote(query)
           + "&format=json&no_html=1&skip_disambig=1")
    try:
        data = json.loads(_get(url))
    except Exception:
        return []
    out: list[WebResult] = []
    if data.get("AbstractText"):
        out.append(WebResult(data.get("Heading") or query,
                             data["AbstractText"],
                             data.get("AbstractURL", ""), "ddg-abstract"))
    for topic in data.get("RelatedTopics", []):
        if len(out) >= k:
            break
        if isinstance(topic, dict) and topic.get("Text"):
            out.append(WebResult(topic.get("Text", "")[:70],
                                 topic["Text"],
                                 topic.get("FirstURL", ""), "ddg-related"))
    return out[:k]


_RESULT_BLOCK = re.compile(
    r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?'
    r'class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)


def ddg_html(query: str, k: int = 5) -> list[WebResult]:
    """HTML result scrape. Broader coverage, more fragile."""
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    try:
        page = _get(url)
    except Exception:
        return []
    out = []
    for href, title, snippet in _RESULT_BLOCK.findall(page)[:k]:
        target = href
        m = re.search(r"uddg=([^&]+)", href)
        if m:
            target = urllib.parse.unquote(m.group(1))
        out.append(WebResult(strip_html(title), strip_html(snippet),
                             target, "ddg-html"))
    return out


PROVIDERS: list[Callable[[str, int], list[WebResult]]] = [ddg_instant, ddg_html]


# ------------------------------------------------------------------ search

@dataclass
class SearchOutcome:
    query: str
    results: list[WebResult] = field(default_factory=list)
    provider: str = ""
    elapsed_ms: float = 0.0
    injection_findings: int = 0

    @property
    def found(self) -> bool:
        return bool(self.results)

    def as_context(self, limit: int = 3) -> Tainted:
        blocks = [str(r.as_context()) for r in self.results[:limit]]
        return Tainted("\n\n".join(blocks), source="web")


_CACHE: dict[str, tuple[float, SearchOutcome]] = {}
CACHE_TTL = 900.0


def search(query: str, k: int = 5, use_cache: bool = True) -> SearchOutcome:
    """Search the web. Returns an outcome whose content is always tainted."""
    key = " ".join(query.lower().split())
    now = time.time()
    if use_cache and key in _CACHE:
        ts, cached = _CACHE[key]
        if now - ts < CACHE_TTL:
            return cached

    t0 = time.perf_counter()
    outcome = SearchOutcome(query=query)
    for provider in PROVIDERS:
        if time.perf_counter() - t0 > TOTAL_BUDGET_S:
            outcome.provider = "budget-exhausted"
            break
        try:
            results = provider(query, k)
        except Exception:
            continue
        if results:
            outcome.results = results
            outcome.provider = provider.__name__
            break
    outcome.elapsed_ms = (time.perf_counter() - t0) * 1000

    # Scan for injection so it lands in the audit trail. The scan is a
    # detection aid, not the defence -- the defence is that this content
    # is tainted and the adapter that reads it cannot emit actions.
    for r in outcome.results:
        outcome.injection_findings += len(
            scan_for_injection(f"{r.title} {r.snippet}", f"web:{_host(r.url)}"))

    if use_cache:
        _CACHE[key] = (now, outcome)
    return outcome


# Words that cannot carry a query on their own. If nothing but these
# survives the rewrite, there is nothing to search for.
_HOLLOW = {"latest", "current", "now", "today", "recent", "this", "that",
           "it", "one", "thing", "answer", "aaj", "abhi", "kal", "taza",
           "wala", "wali", "ye", "yeh", "wo", "woh", "iska", "uska"}


def rewrite_query(user_text: str, context: str = "") -> str:
    """Turn a conversational utterance into a search query.

    A 4B model's raw phrasing makes poor queries, and this runs before any
    model call anyway. Deterministic: strip conversational scaffolding and
    the Hindi/Hinglish request verbs, keep the content words.

    Returns "" when nothing contentful survives, and an empty query is NOT
    searched.

    MEASURED, M10 t4: "Iska latest answer web se check kar" is almost
    entirely scaffolding -- its subject is "iska", *this*, and what "this"
    refers to is in the previous turn. The rewrite reduced it to "latest .",
    which DuckDuckGo answered with an album by Cheap Trick, and two
    irrelevant results were injected as evidence. `context` is the previous
    user turn, used to resolve exactly that case.
    """
    q = _rewrite(user_text)
    if _is_hollow(q) and context:
        q = _rewrite(context)
    return "" if _is_hollow(q) else q


def _is_hollow(q: str) -> bool:
    words = [w for w in re.findall(r"[\w\u0900-\u097f]+", q.lower())]
    return not [w for w in words if w not in _HOLLOW and len(w) > 1]


def _rewrite(user_text: str) -> str:
    t = user_text.strip()
    t = re.sub(r"^(hey|yaar|arre|acha|ok|so|umm|bhai)[,\s]+", "", t, flags=re.I)
    t = re.sub(r"\b(can you|could you|please|search (the )?web for|"
               r"look up|google|tell me|find out|check)\b", " ", t, flags=re.I)
    # Hinglish request scaffolding. Measured residue from an earlier
    # version: "Iska latest answer web se check kar" left "latest answer
    # kar - nextjs version", which searches for the word "kar".
    t = re.sub(r"\b(web (pe|par|se)|internet (pe|par)|"
               r"(search|check|pata|dhund|dekh)\s*(kar(o|na|de)?|lo|le)?|"
               r"kar\s*(do|de|na)?|batao?|bata|de\s*do|"
               r"iska|iski|uska|ka latest|answer)\b", " ", t, flags=re.I)
    t = re.sub(r"\s+[-—:,]+\s+", " ", t)          # orphaned punctuation
    t = re.sub(r"^[\s\-—:,]+|[\s\-—:,]+$", "", t)
    t = re.sub(r"^\b(ke|ka|ki|se|me|mein|ko|aur|to|toh)\b\s*", "", t, flags=re.I)
    t = re.sub(r"[?।]+", " ", t)
    t = _WS.sub(" ", t).strip()
    # Deliberately NOT `or user_text.strip()`. Falling back to the original
    # text when the rewrite stripped everything is what sent "check kar" and
    # "Iska latest answer web se check kar" to a search engine. An
    # utterance that is entirely scaffolding has no query in it, and the
    # caller needs to be able to tell.
    return t
