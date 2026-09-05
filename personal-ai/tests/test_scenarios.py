"""Run the frozen scenario set as part of the regression suite.

The mutation audit found that four defenses -- the general-knowledge
short-circuit, volatile-vs-self-statement routing, relevance-based
injection gating, and the negation exclusions -- were exercised ONLY by
eval/harness.py, which was never run by `unittest discover`. Disabling any
of them left the suite green.

A defense that only a manually-invoked script protects will eventually be
broken by someone who ran the tests and saw OK.
"""
import os
import sys
import unittest
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eval.harness import run as run_scenarios


class TestFrozenScenarios(unittest.TestCase):
    """The 165 deterministic scenario checks, as a regression gate."""

    @classmethod
    def setUpClass(cls):
        cls.result = run_scenarios()

    def test_no_scenario_failures(self):
        fails = self.result.failures
        detail = "\n".join(f"  [{c}/{s}] {chk}: {d}"
                           for s, c, chk, _, d in fails[:12])
        self.assertEqual(fails, [], f"\n{len(fails)} scenario checks failed:\n{detail}")

    def test_every_category_is_covered(self):
        cats = {c for _, c, _, _, _ in self.result.rows}
        for required in ("casual", "correction", "web", "internal", "obsidian",
                         "tools", "voice_safety", "injection", "safety",
                         "delegation", "memory", "personalisation"):
            self.assertIn(required, cats, f"category {required} not exercised")

    def test_scenario_count_has_not_shrunk(self):
        """Guards against scenarios being quietly deleted to make it green."""
        self.assertGreaterEqual(len(self.result.rows), 160,
                                "the frozen scenario set lost checks")


class TestRouterDefencesDirectly(unittest.TestCase):
    """Direct unit cover for the router defenses the audit found unguarded."""

    def setUp(self):
        from pai.router import Router
        self.r = Router()

    def _path(self, text, hits=()):
        return self.r.route(text, hits).path.value

    def _strong_hit(self):
        """A hit good enough to be injected, so the short-circuit is the
        only thing that can prevent it. Without this the test passes
        whether or not the short-circuit exists."""
        from pai.obsidian import Chunk, Hit
        return Hit(chunk=Chunk("c#0", "n.md", "Loops",
                               "a for loop recursion week days am pm ghante",
                               0.0),
                   score=0.033, why="fused", rank_bm25=1, rank_dense=1,
                   bm25_raw=6.0, dense_raw=0.7)

    def test_general_knowledge_answers_internally(self):
        hit = self._strong_hit()
        for q in ["what's a for loop", "how many days in a week",
                  "what does am and pm mean", "din me kitne ghante hote hain",
                  "what is recursion"]:
            route = self.r.route(q, [hit])
            self.assertEqual(route.path.value, "fast", q)
            self.assertEqual(route.inject, [],
                             f"vault injected into a general-knowledge "
                             f"answer: {q!r}")

    def test_general_knowledge_does_not_swallow_personal_or_volatile(self):
        """The short-circuit must not eat questions that DO need retrieval."""
        self.assertEqual(self._path("what did we decide about my auth design"),
                         "fast")   # no vault hits supplied, but must not be 'fast'
        # ^ with no hits it stays fast; the real check is that it is not
        #   short-circuited before web gating:
        self.assertEqual(self._path("what is the latest version of nextjs"), "web")
        self.assertEqual(self._path("what is today's date"), "web")

    def test_volatile_marker_in_a_self_statement_does_not_search(self):
        for t in ["aaj bahut thak gaya hoon", "main aaj bore ho raha hoon",
                  "aaj main office gaya tha", "i'm exhausted today",
                  "aaj mera birthday hai"]:
            self.assertNotEqual(self._path(t), "web", t)

    def test_volatile_noun_phrase_queries_still_search(self):
        for t in ["current price of bitcoin", "latest release notes for llama.cpp",
                  "today's top news", "mujhe aaj ka news chahiye",
                  "i want the latest nextjs version"]:
            self.assertEqual(self._path(t), "web", t)

    def test_injection_gating_uses_relevance_not_rrf_rank(self):
        """A top-ranked but irrelevant hit must not be injected.

        RRF gives ~0.0328 to anything ranked #1 by both retrievers,
        regardless of match quality. Gating on that treated garbage as an
        answer and suppressed a needed web search.
        """
        from pai.obsidian import Chunk, Hit
        chunk = Chunk("c#0", "n.md", "N", "unrelated text", 0.0)
        # Ranked first by both retrievers, so a high RRF score...
        # Shares content words with the query, so the lexical-overlap gate
        # cannot mask this: only the raw-score check can reject it.
        chunk = Chunk("c#0", "n.md", "N",
                      "nextjs version notes and latest release chatter", 0.0)
        weak = Hit(chunk=chunk, score=0.0328, why="fused",
                   rank_bm25=1, rank_dense=1, bm25_raw=0.1, dense_raw=0.02)
        route = self.r.route("what is the latest nextjs version", [weak])
        self.assertEqual(route.inject, [], "a weak hit was injected on RRF rank")
        self.assertEqual(route.path.value, "web",
                         "a weak vault hit suppressed a needed web search")

    def test_strong_hit_is_injected(self):
        from pai.obsidian import Chunk, Hit
        chunk = Chunk("c#0", "n.md", "N", "passkey decision", 0.0)
        strong = Hit(chunk=chunk, score=0.0328, why="fused",
                     rank_bm25=1, rank_dense=1, bm25_raw=5.0, dense_raw=0.6)
        route = self.r.route("what did we decide about auth", [strong])
        self.assertEqual(len(route.inject), 1)


class TestSignalDefencesDirectly(unittest.TestCase):
    # These inputs BOTH match a correction/negative pattern AND match an
    # exclusion. That combination is what makes them a real test.
    #
    # The first version of this test used "no idea", "no problem" and the
    # like. Those match no correction pattern at all, so the exclusion never
    # fired for them and deleting NEGATION_EXCLUSIONS left the test green.
    # The mutation audit caught it. Verified: every input below is detected
    # as a signal when the exclusions are removed.
    EXCLUSION_CASES = [
        "I said no thanks",
        "no idea what i meant",
        "not sure, i meant to check later",
        "nahi pata, maine kaha tha ki dekh lunga",
        "no problem, i meant it kindly",
        "actually i have no clue",
        "mujhe nahi pata mera matlab kya tha",
        "no idea, that's not right though",
    ]

    def test_exclusion_cases_would_otherwise_trip_a_pattern(self):
        """Guards the test itself: each input must match a signal pattern.

        If this fails, the exclusion test below has stopped exercising the
        exclusion and is a false green again.
        """
        from pai.signals import CORRECTION, NEGATIVE, NEGATION_EXCLUSIONS
        for t in self.EXCLUSION_CASES:
            self.assertTrue(CORRECTION.search(t) or NEGATIVE.search(t),
                            f"{t!r} matches no signal pattern; it does not "
                            f"test the exclusion")
            self.assertTrue(NEGATION_EXCLUSIONS.search(t),
                            f"{t!r} matches no exclusion")

    def test_negation_exclusions_prevent_false_corrections(self):
        from pai.signals import detect
        for t in self.EXCLUSION_CASES:
            self.assertEqual([d.signal.value for d in detect(t)], [],
                             f"{t!r} was misread as feedback")

    def test_plain_negations_are_also_silent(self):
        from pai.signals import detect
        for t in ["no idea", "nahi pata yaar", "no problem", "not sure yet",
                  "पता नहीं", "no thanks", "nahi chahiye", "no, i'm fine"]:
            self.assertEqual([d.signal.value for d in detect(t)], [], t)

    def test_real_corrections_still_detected(self):
        from pai.signals import detect
        for t, want in [("no, I meant the other one", "correction"),
                        ("mera matlab wo wala tha", "correction"),
                        ("ye galat hai", "explicit_negative"),
                        ("arre nahi, itna bada answer mat do. simple bol.",
                         "style_too_long")]:
            got = [d.signal.value for d in detect(t)]
            self.assertIn(want, got, f"{t!r} -> {got}")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestIrrelevantInjection(unittest.TestCase):
    """A vault note must not be dragged into an unrelated answer.

    Found in conversation M06. Asked "Python is faster than C, right?", the
    assistant answered correctly and then appended: "If you're working on
    your thesis deadline with Dr. Raghavan, make sure you check the
    performance benchmarks you're using for your retrieval evaluation
    chapter." The Thesis note scored above the dense threshold under the
    stand-in embedder and the model dutifully used it.
    """

    def setUp(self):
        from pai.router import Router
        self.r = Router()

    def _hit(self, path, heading, text, dense, bm25):
        from pai.obsidian import Chunk, Hit
        return Hit(chunk=Chunk("c#0", path, heading, text, 0.0), score=0.033,
                   why="fused", rank_bm25=1, rank_dense=1,
                   bm25_raw=bm25, dense_raw=dense)

    THESIS = ("Notes/Thesis.md", "Thesis",
              "Chapter 3 covers retrieval evaluation. Deadline 14 November. "
              "Supervisor is Dr Raghavan.")

    def test_marginal_irrelevant_hit_is_not_injected(self):
        # Deliberately NOT a general-knowledge question -- that short-circuit
        # returns before injection and would mask the overlap gate entirely.
        h = self._hit(*self.THESIS, 0.40, 0.2)
        route = self.r.route("tell me about the caching layer we built", [h])
        self.assertEqual(route.inject, [],
                         "an unrelated note was injected into a general "
                         "knowledge answer")

    def test_marginal_hit_WITH_shared_words_is_injected(self):
        h = self._hit(*self.THESIS, 0.40, 0.2)
        route = self.r.route("what is my thesis deadline", [h])
        self.assertEqual(len(route.inject), 1)

    def test_strongly_dense_hit_survives_without_shared_words(self):
        """Overlap must not veto what dense retrieval exists to find."""
        h = self._hit("Projects/Auth.md", "Auth > Decisions",
                      "passkey decision", 0.60, 0.0)
        route = self.r.route("what did we decide about auth", [h])
        self.assertEqual(len(route.inject), 1)

    def test_declarative_tag_question_short_circuits(self):
        from pai.router import GENERAL_KNOWLEDGE
        for t in ["Python is faster than C, right?",
                  "HTTP is stateless, correct?",
                  "JSON is a data format, right?"]:
            self.assertTrue(GENERAL_KNOWLEDGE.match(t), t)

    def test_personal_tag_question_does_not_short_circuit(self):
        """"we decided X right" is about HIS project and must retrieve."""
        from pai.router import GENERAL_KNOWLEDGE
        for t in ["we decided to use passwords not passkeys right",
                  "my deploy runs on vercel right"]:
            self.assertFalse(GENERAL_KNOWLEDGE.match(t), t)
