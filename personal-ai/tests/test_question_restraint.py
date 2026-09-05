"""Consecutive-question restraint.

The most persistent conversational tic measured in this project: 100% of
turns ended with a question under personas v1, v2 AND v3, on casual
conversations, despite v2 stating "Do not end every message with a
question" in plain English. The A/B showed prompting moves it
inconsistently (better on two cases, worse on one, unchanged on one).

So it is enforced. These tests check the enforcement is real, is mild
enough not to mangle replies, and does not fire when asking is correct.
"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pai.memory import MemoryStore
from pai.obsidian import VaultIndex, TfidfEmbedder
from pai.orchestrator import Orchestrator, strip_trailing_question


def orch(replies):
    s = MemoryStore()
    v = VaultIndex(TfidfEmbedder()); v.add_note("a.md", "# A\nx"); v.build_vectors()
    seq = list(replies)
    class C:
        max_tokens = 300
        def respond(self, *a): return seq.pop(0) if seq else "ok."
    return Orchestrator(s, v, C())


class TestStripper(unittest.TestCase):
    def test_strips_a_trailing_question_when_content_remains(self):
        self.assertEqual(
            strip_trailing_question("Bas chill raha hu, koi news nahi. Tu bata kya haal hai?"),
            "Bas chill raha hu, koi news nahi.")

    def test_keeps_a_reply_that_is_only_a_question(self):
        """Stripping would leave nothing, which is worse than the tic."""
        for t in ["Kya idea hai?", "What do you mean?", "Kaunsa wala?"]:
            self.assertEqual(strip_trailing_question(t), t)

    def test_leaves_non_questions_alone(self):
        for t in ["hey", "Bhai, sab badhiya.", "That is a terrible idea."]:
            self.assertEqual(strip_trailing_question(t), t)

    def test_handles_devanagari_sentence_ends(self):
        self.assertEqual(
            strip_trailing_question("मैं ठीक हूँ। तुम कैसे हो?"), "मैं ठीक हूँ।")

    def test_a_one_word_remainder_is_kept_if_it_is_a_complete_sentence(self):
        """"Nice." is a real reply. Requiring 3 words reverted the strip."""
        self.assertEqual(strip_trailing_question("Nice. What are you building?"),
                         "Nice.")
        self.assertEqual(strip_trailing_question("Ok. Why?"), "Ok.")

    def test_a_dangling_remainder_is_not_produced(self):
        # No terminator before the question -> stripping would leave a
        # fragment, so the original is kept.
        self.assertEqual(strip_trailing_question("so then what?"),
                         "so then what?")


class TestOrchestratorRestraint(unittest.TestCase):
    QUESTIONING = ["I'm good thanks. How are you?",
                   "Just working. What about you?",
                   "Nice. What are you building?",
                   "Cool. Want to talk through it?"]

    def test_first_two_questions_are_allowed(self):
        o = orch(self.QUESTIONING)
        self.assertTrue(o.handle("s", "hi").text.endswith("?"))
        self.assertTrue(o.handle("s", "hi").text.endswith("?"))

    def test_third_consecutive_question_is_stripped(self):
        o = orch(self.QUESTIONING)
        for _ in range(2):
            o.handle("s", "hi")
        third = o.handle("s", "hi").text
        self.assertFalse(third.endswith("?"), f"tic not restrained: {third!r}")
        self.assertIn("Nice", third)

    def test_counter_resets_after_a_non_question(self):
        o = orch(["A? ", "B?", "Plain statement.", "C?", "D?"])
        o.handle("s", "x"); o.handle("s", "x")
        self.assertFalse(o.handle("s", "x").text.endswith("?"))  # statement
        # counter reset: two questions allowed again
        self.assertTrue(o.handle("s", "x").text.endswith("?"))
        self.assertTrue(o.handle("s", "x").text.endswith("?"))

    def test_pure_question_replies_survive_the_restraint(self):
        """Clarifying questions must not be destroyed by the tic guard."""
        o = orch(["Sure?", "Ok?", "Which one?"])
        o.handle("s", "x"); o.handle("s", "x")
        self.assertEqual(o.handle("s", "x").text, "Which one?")


if __name__ == "__main__":
    unittest.main(verbosity=2)
