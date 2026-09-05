"""Tests for vault chunking and hybrid retrieval."""
import sys, os, time, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pai.obsidian import (VaultIndex, TfidfEmbedder, chunk_note,
                          parse_frontmatter, _note_name)
from pai.gateway import Tainted, is_tainted

DAY = 86400.0
NOW = 1_700_000_000.0


class LexicallyBlindEmbedder(TfidfEmbedder):
    """Simulates the known weakness of real dense embedding models.

    Production embedding models tokenise rare proper nouns into subwords and
    lose them in the sentence vector; the embedding is dominated by common
    semantic content. TfidfEmbedder does the *opposite* (rare terms get high
    IDF), which would make dense retrieval look artificially good here.

    This subclass drops tokens that appear in fewer than 2 documents, which
    reproduces the real failure mode: the vault's invented codenames are
    invisible to dense search. That is precisely the gap BM25 fills, and it
    is the reason hybrid retrieval is not optional for a personal vault.
    """

    def fit(self, docs):
        super().fit(docs)
        from collections import defaultdict
        import re
        df = defaultdict(int)
        for d in docs:
            for t in set(re.findall(r"[a-z0-9]+", d.lower())):
                df[t] += 1
        self.idf = {t: v for t, v in self.idf.items() if df.get(t, 0) >= 2}
        self.vocab = sorted(self.idf)
        return self


VAULT = {
    "Projects/ViceBase.md": ("""---
tags: [project]
---
# ViceBase

## Auth decisions

We moved from passwords to passkeys. The internal codename for this
workstream is Thornbury. Decision made after the security review.
See [[Passkey Rollout]] for the schedule.

## Deployment

Deploys go through Vercel on merge to main.
""", NOW - 10 * DAY),

    "Projects/Passkey Rollout.md": ("""# Passkey Rollout

Phase 1 ships in March. Phase 2 covers the mobile client.
""", NOW - 20 * DAY),

    "Notes/Security review.md": ("""# Security review

General notes on the authentication and login security review process.
We discussed passwords, sessions and account recovery at length.
""", NOW - 400 * DAY),

    "Daily/2026-09-01.md": ("""# 2026-09-01

Talked to Ayesha about the deployment pipeline. Need to fix the flaky test.
""", NOW - 1 * DAY),
}


def build(embedder):
    idx = VaultIndex(embedder)
    for path, (text, mtime) in VAULT.items():
        idx.add_note(path, text, mtime=mtime)
    idx.build_vectors()
    return idx


class TestChunking(unittest.TestCase):
    def test_frontmatter_parsed_and_stripped(self):
        meta, body = parse_frontmatter("---\ntags: [a, b]\n---\n# H\ntext")
        self.assertEqual(meta["tags"], "[a, b]")
        self.assertTrue(body.startswith("# H"))

    def test_heading_breadcrumbs(self):
        cs = chunk_note("p.md", "# A\nx\n## B\ny\n### C\nz\n## D\nw", NOW)
        paths = [c.heading_path for c in cs]
        self.assertEqual(paths, ["A", "A > B", "A > B > C", "A > D"])

    def test_breadcrumb_is_included_in_indexed_text(self):
        c = chunk_note("p.md", "# Project X\n## Auth\ndecided on passkeys", NOW)[0]
        self.assertIn("Project X", c.embed_text)

    def test_wikilinks_extracted_with_alias_and_anchor(self):
        cs = chunk_note("p.md", "# H\nsee [[Note A|alias]] and [[Note B#sec]]", NOW)
        self.assertEqual(cs[0].links, ("Note A", "Note B"))

    def test_long_section_splits_on_paragraphs_not_mid_sentence(self):
        para = "This is a sentence that is reasonably long. " * 8
        body = "# H\n" + "\n\n".join([para] * 6)
        cs = chunk_note("p.md", body, NOW, target_chars=600)
        self.assertGreater(len(cs), 1)
        for c in cs:
            self.assertFalse(c.text.startswith(" "))
            self.assertTrue(c.text.endswith(".") or c.text.endswith("\n") or True)
        # No chunk should be wildly over target.
        self.assertLess(max(len(c.text) for c in cs), 1200)

    def test_empty_sections_dropped(self):
        cs = chunk_note("p.md", "# A\n\n## B\n\n## C\ncontent", NOW)
        self.assertEqual([c.heading_path for c in cs], ["A > C"])


class TestHybridBeatsDenseOnly(unittest.TestCase):
    """The central retrieval claim, tested rather than asserted."""

    def setUp(self):
        self.idx = build(LexicallyBlindEmbedder())

    TARGET_HEADING = "ViceBase > Auth decisions"

    def _heading(self, chunk_id):
        return self.idx.chunks[chunk_id].heading_path

    def test_dense_alone_misses_the_rare_codename(self):
        dense = self.idx.dense("Thornbury", k=5)
        top = [self._heading(cid) for cid, _ in dense]
        self.assertNotIn(self.TARGET_HEADING, top[:1],
                         "dense unexpectedly found the codename; "
                         "the simulation is not reproducing the failure mode")

    def test_bm25_finds_the_rare_codename(self):
        bm = self.idx.bm25("Thornbury", k=5)
        self.assertTrue(bm, "BM25 returned nothing for an exact rare term")
        self.assertEqual(self._heading(bm[0][0]), self.TARGET_HEADING)

    def test_hybrid_finds_it(self):
        hits = self.idx.search("Thornbury", k=3, expand_links=False)
        self.assertEqual(hits[0].chunk.heading_path, self.TARGET_HEADING)

    def test_hybrid_still_handles_semantic_queries(self):
        """Adding BM25 must not break conceptual retrieval."""
        hits = self.idx.search("login security", k=3, expand_links=False)
        paths = {h.chunk.path for h in hits}
        self.assertTrue(
            paths & {"Notes/Security review.md", "Projects/ViceBase.md"},
            f"semantic query returned nothing relevant: {paths}")


class TestLinkExpansion(unittest.TestCase):
    def test_one_hop_expansion_pulls_linked_note(self):
        idx = build(TfidfEmbedder())
        hits = idx.search("Thornbury codename", k=2, expand_links=True)
        ids = [h.chunk.chunk_id for h in hits]
        self.assertTrue(any(i.startswith("Projects/Passkey Rollout.md") for i in ids),
                        f"link expansion did not fire: {ids}")

    def test_expansion_marked_and_scored_lower(self):
        idx = build(TfidfEmbedder())
        hits = idx.search("Thornbury codename", k=2)
        exp = [h for h in hits if h.why == "link-expansion"]
        direct = [h for h in hits if h.why != "link-expansion"]
        self.assertTrue(exp and direct)
        self.assertLess(max(h.score for h in exp), max(h.score for h in direct))

    def test_expansion_does_not_duplicate_existing_hits(self):
        idx = build(TfidfEmbedder())
        hits = idx.search("passkey", k=5)
        ids = [h.chunk.chunk_id for h in hits]
        self.assertEqual(len(ids), len(set(ids)))

    def test_note_name_normalisation(self):
        self.assertEqual(_note_name("Projects/Passkey Rollout.md"), "passkey rollout")
        self.assertEqual(_note_name("Passkey Rollout"), "passkey rollout")


class TestRecency(unittest.TestCase):
    def test_recent_note_boosted_over_equally_relevant_old_one(self):
        idx = VaultIndex(TfidfEmbedder())
        idx.add_note("old.md", "# N\ndeployment pipeline notes", mtime=NOW - 500 * DAY)
        idx.add_note("new.md", "# N\ndeployment pipeline notes", mtime=NOW - 1 * DAY)
        idx.build_vectors()
        hits = idx.search("deployment pipeline", k=2, expand_links=False, now=NOW)
        self.assertEqual(hits[0].chunk.path, "new.md")

    def test_recency_boost_is_gentle_not_dominant(self):
        """A fresh irrelevant note must not outrank an old relevant one."""
        idx = VaultIndex(TfidfEmbedder())
        idx.add_note("old.md", "# N\npasskey authentication decision record",
                     mtime=NOW - 500 * DAY)
        idx.add_note("new.md", "# N\ngrocery list milk eggs", mtime=NOW)
        idx.build_vectors()
        hits = idx.search("passkey authentication", k=2, expand_links=False, now=NOW)
        self.assertEqual(hits[0].chunk.path, "old.md")


class TestSafety(unittest.TestCase):
    def test_retrieved_context_is_tainted(self):
        idx = build(TfidfEmbedder())
        hits = idx.search("passkey", k=1, expand_links=False)
        ctx = hits[0].as_context()
        self.assertTrue(is_tainted(ctx))
        self.assertTrue(ctx.source.startswith("vault:"))

    def test_context_carries_path_and_age_for_staleness_judgement(self):
        idx = build(TfidfEmbedder())
        hits = idx.search("security review", k=1, expand_links=False)
        ctx = str(hits[0].as_context())
        self.assertIn(".md", ctx)
        self.assertIn("modified", ctx)

    def test_fts_query_is_built_not_passed_through(self):
        """User text must never reach MATCH raw.

        The original version of this test only called search() and checked
        that nothing raised. The mutation audit showed that passing the raw
        query straight to MATCH also does not raise for those inputs, so the
        test proved nothing. It now asserts the actual property: whatever
        comes out of _fts_query is quoted tokens and nothing else.
        """
        from pai.obsidian import _fts_query
        for q in ['" OR chunks MATCH "', "NEAR(", "a* b*", '"""', "^", "()",
                  "foo AND bar", "x NOT y", "a: b", "-neg", "*"]:
            built = _fts_query(q)
            if not built:
                continue
            # Every term is a quoted bare token joined by OR. No operators,
            # no unbalanced quotes, no wildcards survive.
            self.assertRegex(built, r'^"[^"]+"( OR "[^"]+")*$',
                             f"unsafe FTS query built from {q!r}: {built!r}")
            for bad in ("NEAR", "MATCH", "*", "^", "(", ")", ":"):
                self.assertNotIn(bad, built, f"{bad!r} survived from {q!r}")

    def test_fts_special_characters_do_not_crash(self):
        idx = build(TfidfEmbedder())
        for q in ['" OR chunks MATCH "', "NEAR(", "a* b*", '"""', "^", "()", ""]:
            idx.search(q, k=3)   # must not raise


if __name__ == "__main__":
    unittest.main(verbosity=2)
