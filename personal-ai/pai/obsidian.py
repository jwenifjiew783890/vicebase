"""Obsidian vault retrieval: heading-aware chunking + hybrid search.

Three things make this different from generic chunk-and-embed RAG, and all
three matter specifically for a *personal* vault:

1. HEADING BREADCRUMBS. Each chunk carries its heading path
   ("Projects > ViceBase > Auth decisions"). This improves embedding quality
   and lets the assistant cite precisely.

2. HYBRID RETRIEVAL, NOT DENSE-ONLY. A personal vault is full of project
   codenames, abbreviations and invented proper nouns. Embedding models
   handle rare tokens badly; exact match handles them perfectly. Dense-only
   retrieval on a personal vault is the single most common reason these
   systems feel useless. Results are fused with Reciprocal Rank Fusion.

3. WIKILINK EXPANSION. The vault is a graph. After retrieving a chunk we
   pull in its one-hop [[links]]. Generic RAG throws that structure away.

Everything returned is Tainted: vault notes are user-authored but can quote
web content, and a note written two years ago is not a live instruction.
"""
from __future__ import annotations

import math
import re
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional, Protocol, Sequence

from .gateway import Tainted

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


@dataclass
class Chunk:
    chunk_id: str
    path: str
    heading_path: str
    text: str
    mtime: float
    links: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    @property
    def embed_text(self) -> str:
        """What gets embedded / indexed: breadcrumb first, then body."""
        return f"{self.heading_path}\n{self.text}" if self.heading_path else self.text


@dataclass
class Hit:
    chunk: Chunk
    score: float           # RRF fusion score -- ORDERING ONLY, see below
    why: str = ""          # 'bm25' | 'dense' | 'fused' | 'link-expansion'
    rank_bm25: Optional[int] = None
    rank_dense: Optional[int] = None
    bm25_raw: float = 0.0  # relevance-bearing
    dense_raw: float = 0.0 # relevance-bearing (cosine, 0..1)

    @property
    def is_confident(self) -> bool:
        """Whether this hit is good enough to put in front of the model.

        IMPORTANT: `score` (RRF) must NOT be used for this. RRF is a rank
        fusion: any chunk ranked #1 by both retrievers scores 2/(60+1) =
        0.0328 whether it is a perfect match or the least-bad of three
        irrelevant notes. An earlier version gated injection on the RRF
        score and consequently treated a garbage top hit as a confident
        answer -- which then suppressed a web search the user needed.

        Relevance gating uses the RAW scores. RRF is only for ordering.
        """
        return self.dense_raw >= 0.25 or self.bm25_raw >= 1.5

    def as_context(self) -> Tainted:
        """Render for injection into the prompt. Always tainted."""
        age_days = (time.time() - self.chunk.mtime) / 86400.0
        return Tainted(
            f"[{self.chunk.path} :: {self.chunk.heading_path} "
            f"(modified {age_days:.0f}d ago)]\n{self.chunk.text}",
            source=f"vault:{self.chunk.path}",
        )


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER.match(text)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def chunk_note(path: str, text: str, mtime: float,
               target_chars: int = 1200) -> list[Chunk]:
    """Split a note by heading, then by paragraph if a section is too long.

    A chunk is a *section*, not a fixed window. Splitting mid-sentence to hit
    a token count destroys the thing that makes a note retrievable.
    """
    meta, body = parse_frontmatter(text)
    tags = tuple(t.strip() for t in meta.get("tags", "").strip("[]").split(",")
                 if t.strip())

    stack: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current: list[str] = []
    current_path = ""

    for line in body.splitlines():
        m = HEADING.match(line)
        if m:
            if current and any(l.strip() for l in current):
                sections.append((current_path, current))
            level = len(m.group(1))
            stack = stack[: level - 1]
            stack.append(m.group(2).strip())
            current_path = " > ".join(stack)
            current = []
        else:
            current.append(line)
    if current and any(l.strip() for l in current):
        sections.append((current_path, current))

    chunks: list[Chunk] = []
    for idx, (hpath, lines) in enumerate(sections):
        blob = "\n".join(lines).strip()
        if not blob:
            continue
        parts = _split_long(blob, target_chars)
        for j, part in enumerate(parts):
            chunks.append(Chunk(
                chunk_id=f"{path}#{idx}.{j}",
                path=path,
                heading_path=hpath,
                text=part,
                mtime=mtime,
                links=tuple(dict.fromkeys(WIKILINK.findall(part))),
                tags=tags,
            ))
    return chunks


def _split_long(blob: str, target: int) -> list[str]:
    if len(blob) <= target:
        return [blob]
    paras = [p for p in re.split(r"\n\s*\n", blob) if p.strip()]
    out, buf = [], ""
    for p in paras:
        if buf and len(buf) + len(p) + 2 > target:
            out.append(buf.strip())
            buf = p
        else:
            buf = f"{buf}\n\n{p}" if buf else p
    if buf.strip():
        out.append(buf.strip())
    return out or [blob[:target]]


# ---------------------------------------------------------------------------
# Embedding interface
# ---------------------------------------------------------------------------

class Embedder(Protocol):
    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class TfidfEmbedder:
    """Dependency-free stand-in for a real embedding model.

    Production uses a real model (see docs: EmbeddingGemma-300M or
    Qwen3-Embedding-0.6B on CPU, ~10-30ms/query). This exists so the fusion,
    ranking and expansion logic is testable without torch, and so the system
    degrades to *something* rather than nothing if the model fails to load.

    It deliberately reproduces the weakness of real dense retrieval that
    matters here: rare proper nouns get little weight relative to common
    words, which is exactly why hybrid retrieval is not optional.
    """

    def __init__(self):
        self.idf: dict[str, float] = {}
        self.vocab: list[str] = []

    def fit(self, docs: Sequence[str]) -> "TfidfEmbedder":
        df: dict[str, int] = defaultdict(int)
        for d in docs:
            for t in set(_tok(d)):
                df[t] += 1
        n = max(1, len(docs))
        self.idf = {t: math.log(1 + n / (1 + c)) for t, c in df.items()}
        self.vocab = sorted(self.idf)
        return self

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        out = []
        for t in texts:
            counts: dict[str, int] = defaultdict(int)
            for tok in _tok(t):
                counts[tok] += 1
            vec = [counts.get(v, 0) * self.idf.get(v, 0.0) for v in self.vocab]
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            out.append([x / norm for x in vec])
        return out


def _tok(s: str) -> list[str]:
    return re.findall(r"[a-z0-9ऀ-ॿ]+", s.lower())


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


# ---------------------------------------------------------------------------
# The index
# ---------------------------------------------------------------------------

class VaultIndex:
    RRF_K = 60          # standard RRF damping constant

    def __init__(self, embedder: Embedder | None = None):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE VIRTUAL TABLE chunks USING fts5(
                chunk_id UNINDEXED, path, heading_path, text, tokenize='unicode61'
            );
        """)
        self.chunks: dict[str, Chunk] = {}
        self.by_note: dict[str, list[str]] = defaultdict(list)
        self.embedder = embedder
        self._vectors: dict[str, list[float]] = {}

    def add_note(self, path: str, text: str, mtime: float | None = None) -> int:
        mtime = mtime if mtime is not None else time.time()
        added = chunk_note(path, text, mtime)
        for c in added:
            self.chunks[c.chunk_id] = c
            self.by_note[_note_name(c.path)].append(c.chunk_id)
            self.db.execute(
                "INSERT INTO chunks(chunk_id, path, heading_path, text) "
                "VALUES (?,?,?,?)",
                (c.chunk_id, c.path, c.heading_path, c.text))
        self.db.commit()
        return len(added)

    def build_vectors(self) -> None:
        if self.embedder is None:
            return
        ids = list(self.chunks)
        texts = [self.chunks[i].embed_text for i in ids]
        if hasattr(self.embedder, "fit"):
            self.embedder.fit(texts)
        vecs = self.embedder.embed(texts)
        self._vectors = dict(zip(ids, vecs))

    # ------------------------------------------------------------ searches

    def bm25(self, query: str, k: int = 20) -> list[tuple[str, float]]:
        q = _fts_query(query)
        if not q:
            return []
        try:
            rows = self.db.execute(
                "SELECT chunk_id, bm25(chunks) AS score FROM chunks "
                "WHERE chunks MATCH ? ORDER BY score LIMIT ?", (q, k)).fetchall()
        except sqlite3.OperationalError:
            return []
        # sqlite bm25() returns lower-is-better; negate for consistency.
        return [(r["chunk_id"], -r["score"]) for r in rows]

    def dense(self, query: str, k: int = 20) -> list[tuple[str, float]]:
        if self.embedder is None or not self._vectors:
            return []
        qv = self.embedder.embed([query])[0]
        scored = [(cid, cosine(qv, v)) for cid, v in self._vectors.items()]
        scored = [s for s in scored if s[1] > 0]
        scored.sort(key=lambda x: -x[1])
        return scored[:k]

    def search(self, query: str, k: int = 5, *, expand_links: bool = True,
               recency_boost: bool = True, now: float | None = None
               ) -> list[Hit]:
        """Hybrid search: BM25 + dense, fused with RRF, then link-expanded."""
        now = now or time.time()
        bm = self.bm25(query, k * 4)
        dn = self.dense(query, k * 4)

        rank_bm = {cid: i + 1 for i, (cid, _) in enumerate(bm)}
        rank_dn = {cid: i + 1 for i, (cid, _) in enumerate(dn)}

        fused: dict[str, float] = defaultdict(float)
        for cid, r in rank_bm.items():
            fused[cid] += 1.0 / (self.RRF_K + r)
        for cid, r in rank_dn.items():
            fused[cid] += 1.0 / (self.RRF_K + r)

        if recency_boost:
            for cid in list(fused):
                age_days = max(0.0, (now - self.chunks[cid].mtime) / 86400.0)
                # Gentle: a note from today is worth ~10% more than one from
                # a year ago. Strong recency weighting buries good old notes.
                fused[cid] *= 1.0 + 0.10 * math.exp(-age_days / 180.0)

        ordered = sorted(fused.items(), key=lambda x: -x[1])[:k]
        raw_bm = dict(bm)
        raw_dn = dict(dn)
        hits = [Hit(chunk=self.chunks[cid], score=score,
                    why="fused" if cid in rank_bm and cid in rank_dn
                        else ("bm25" if cid in rank_bm else "dense"),
                    rank_bm25=rank_bm.get(cid), rank_dense=rank_dn.get(cid),
                    bm25_raw=raw_bm.get(cid, 0.0), dense_raw=raw_dn.get(cid, 0.0))
                for cid, score in ordered]

        if expand_links:
            hits += self._expand(hits, limit=max(1, k // 2))
        return hits

    def _expand(self, hits: Sequence[Hit], limit: int) -> list[Hit]:
        """Pull in one-hop [[wikilinks]] from the retrieved chunks."""
        have = {h.chunk.chunk_id for h in hits}
        out: list[Hit] = []
        for h in hits:
            for link in h.chunk.links:
                for cid in self.by_note.get(_note_name(link), []):
                    if cid in have or len(out) >= limit:
                        continue
                    have.add(cid)
                    out.append(Hit(self.chunks[cid], h.score * 0.5,
                                   why="link-expansion"))
        return out


def _note_name(path_or_link: str) -> str:
    base = path_or_link.rsplit("/", 1)[-1]
    return base[:-3].lower() if base.endswith(".md") else base.lower()


def _fts_query(query: str) -> str:
    """Build a safe FTS5 OR-query. User text is never passed raw to MATCH."""
    toks = [t for t in _tok(query) if len(t) > 1]
    return " OR ".join(f'"{t}"' for t in toks)
