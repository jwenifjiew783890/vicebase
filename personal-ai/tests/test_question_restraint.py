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

    def test_punctuation_only_remainder_is_rejected(self):
        """Stripping can leave "..." -- terminator present, no words.

        The mutation audit showed the empty-words guard was otherwise
        unreachable by any test, because every case it caught was also
        caught by the terminator check.
        """
        self.assertEqual(strip_trailing_question("... what?"), "... what?")
        self.assertEqual(strip_trailing_question("?! why?"), "?! why?")

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

    def test_a_third_consecutive_question_never_reaches_the_user(self):
        """The invariant. HOW it is prevented changed in round 4.

        It used to be the strip alone. The strip is now the backstop behind
        one retry with a harder directive, so the reply the user sees on
        this turn is the RETRY's, not a trimmed version of the first
        attempt. What must not change is that the third question does not
        arrive.
        """
        o = orch(self.QUESTIONING)
        for _ in range(2):
            o.handle("s", "hi")
        res = o.handle("s", "hi")
        self.assertFalse(res.text.endswith("?"),
                         f"tic not restrained: {res.text!r}")
        self.assertTrue(res.question_retry)

    def test_the_strip_still_catches_a_retry_that_asks_again(self):
        """ANTI-FALSE-GREEN: the backstop must still be wired.

        Every scripted reply here is a question, so the retry cannot help
        and the strip is the only thing left.
        """
        o = orch(["A? Really?", "B? Sure?", "Nice. What are you building?",
                  "Cool. Want to talk it through?"])
        for _ in range(2):
            o.handle("s", "hi")
        res = o.handle("s", "hi")
        self.assertFalse(res.text.endswith("?"), res.text)
        self.assertIn("Cool", res.text)

    def test_counter_resets_after_a_non_question(self):
        o = orch(["A? ", "B?", "Plain statement.", "C?", "D?"])
        o.handle("s", "x"); o.handle("s", "x")
        self.assertFalse(o.handle("s", "x").text.endswith("?"))  # statement
        # counter reset: two questions allowed again
        self.assertTrue(o.handle("s", "x").text.endswith("?"))
        self.assertTrue(o.handle("s", "x").text.endswith("?"))

    def test_pure_question_replies_survive_the_restraint(self):
        """Clarifying questions must not be destroyed by the tic guard.

        Every reply here is a bare question with nothing else in it, so
        neither the retry nor the strip can produce anything better. A
        clarifying question the assistant genuinely needs to ask must reach
        the user intact rather than being mangled into a fragment.
        """
        o = orch(["Sure?", "Ok?", "Which one?", "Which one?"])
        o.handle("s", "x"); o.handle("s", "x")
        self.assertEqual(o.handle("s", "x").text, "Which one?")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestLanguageDirective(unittest.TestCase):
    """The router knows the language; the model must be told, not asked.

    Measured failure (M03, persona v3): plainly English turns, correctly
    detected as lang=en, answered in Hinglish -- twice. A standing "match
    his language" instruction did not survive two Hinglish turns of history.
    """

    def _prompt(self, lang):
        s = MemoryStore()
        v = VaultIndex(TfidfEmbedder()); v.add_note("a.md", "# A\nx")
        v.build_vectors()
        class C:
            def respond(self, *a): return "ok."
        return Orchestrator(s, v, C()).build_system_prompt(lang)

    def test_english_turn_gets_an_english_directive(self):
        p = self._prompt("en")
        self.assertIn("Reply in English only", p)
        self.assertNotIn("Reply in natural spoken Hindi", p)

    def test_hindi_turn_gets_a_hindi_directive(self):
        p = self._prompt("hi")
        self.assertIn("natural spoken Hindi", p)
        self.assertIn("Do not answer in English", p)

    def test_hinglish_turn_asks_for_the_same_mix(self):
        self.assertIn("same\nmix", self._prompt("hinglish").replace(" mix", "\nmix"))

    def test_directive_is_present_for_every_supported_language(self):
        for lang in ("en", "hi", "hinglish"):
            self.assertIn("This message", self._prompt(lang), lang)

    def test_directive_follows_the_router_not_the_history(self):
        """An English turn after Hindi ones must still get English."""
        s = MemoryStore()
        v = VaultIndex(TfidfEmbedder()); v.add_note("a.md", "# A\nx")
        v.build_vectors()
        seen = []
        class C:
            def respond(self, system, history, user, context):
                seen.append(system); return "theek hai."
        o = Orchestrator(s, v, C())
        o.handle("s", "kya haal hai")
        o.handle("s", "tu kya kar raha hai")
        o.handle("s", "I meant the deployment pipeline.")
        self.assertIn("Reply in English only", seen[-1],
                      "history language leaked past the router's decision")


class TestPreGenerationRestraint(unittest.TestCase):
    """The post-hoc strip does not hold the cap on its own.

    MEASURED, round 2 of the mandatory set: three conversations of twenty
    (M03, M09, A04) ran to THREE consecutive question-ending replies
    against a cap of two.  The strip removes the final question clause, and
    when what remains is itself a question --

        "Kya kar raha hai tu abhi? Koi game khelna ya kuch naya karna?"
          -> "Kya kar raha hai tu abhi?"

    -- the reply still ends in "?" and the run continues.  So the model is
    now also TOLD, before generating, on exactly the turn where it matters.
    """

    def _orch(self, replies):
        from pai.memory import MemoryStore
        from pai.obsidian import VaultIndex, TfidfEmbedder
        from pai.orchestrator import Orchestrator
        s = MemoryStore(); v = VaultIndex(TfidfEmbedder())
        v.add_note("n.md", "# N\nnothing"); v.build_vectors()
        seen = []
        class C:
            def __init__(self): self.i = 0
            def respond(self, system, history, user, context):
                seen.append(system)
                r = replies[min(self.i, len(replies) - 1)]; self.i += 1
                return r
        return Orchestrator(s, v, C()), seen

    def test_the_directive_appears_only_after_two_question_turns(self):
        from pai.orchestrator import QUESTION_RESTRAINT
        orch, seen = self._orch(["What's up?", "And then?", "Anything else?"])
        orch.handle("s", "hi")
        self.assertNotIn(QUESTION_RESTRAINT, seen[0])
        orch.handle("s", "hi")
        self.assertNotIn(QUESTION_RESTRAINT, seen[1],
                         "fired one turn early")
        orch.handle("s", "hi")
        self.assertIn(QUESTION_RESTRAINT, seen[2])

    def test_a_statement_resets_the_run(self):
        """ANTI-FALSE-GREEN: the directive must not become permanent."""
        from pai.orchestrator import QUESTION_RESTRAINT
        orch, seen = self._orch(["What's up?", "And then?", "Fair enough.",
                                 "Right."])
        for _ in range(4):
            orch.handle("s", "hi")
        self.assertIn(QUESTION_RESTRAINT, seen[2])
        self.assertNotIn(QUESTION_RESTRAINT, seen[3],
                         "a non-question reply must clear the run")

    def test_the_run_is_counted_per_session(self):
        """ANTI-FALSE-GREEN: one conversation must not silence another."""
        from pai.orchestrator import QUESTION_RESTRAINT
        orch, seen = self._orch(["What's up?"])
        orch.handle("a", "hi"); orch.handle("a", "hi")
        orch.handle("b", "hi")
        self.assertNotIn(QUESTION_RESTRAINT, seen[-1])


class TestQuestionRetry(unittest.TestCase):
    """One louder attempt when the soft directive is ignored.

    MEASURED negative result, round 3: QUESTION_RESTRAINT alone did
    nothing. It fired twice and was disobeyed both times, question density
    did not move (0.78 -> 0.80 marks per reply) and replies carrying more
    than one question went up. The retry exists because the directive did
    not earn its place on its own.
    """

    class Twice:
        max_tokens = 300
        def __init__(self, first, second):
            self.first, self.second = first, second
            self.systems = []
        def respond(self, system, history, user, context):
            self.systems.append(system)
            return self.first if len(self.systems) <= 3 else self.second

    def _orch(self, model):
        from pai.memory import MemoryStore
        from pai.obsidian import VaultIndex, TfidfEmbedder
        from pai.orchestrator import Orchestrator
        s = MemoryStore(); v = VaultIndex(TfidfEmbedder())
        v.add_note("n.md", "# N\nnothing"); v.build_vectors()
        return Orchestrator(s, v, model)

    def test_a_third_question_triggers_one_retry(self):
        from pai.orchestrator import QUESTION_RESTRAINT_HARD
        model = self.Twice("So what happened?", "Fair enough.")
        orch = self._orch(model)
        orch.handle("s", "hi"); orch.handle("s", "hi")
        res = orch.handle("s", "hi")
        self.assertTrue(res.question_retry)
        self.assertTrue(res.question_complied, "the model ignored the retry")
        self.assertTrue(res.question_obeyed, "a third question reached the user")
        self.assertEqual(res.text, "Fair enough.")
        self.assertIn(QUESTION_RESTRAINT_HARD, model.systems[-1])

    def test_only_one_retry_happens(self):
        """ANTI-FALSE-GREEN: a retry loop would be worse than the tic."""
        model = self.Twice("So what happened?", "And then what?")
        orch = self._orch(model)
        orch.handle("s", "hi"); orch.handle("s", "hi")
        before = len(model.systems)
        res = orch.handle("s", "hi")
        self.assertEqual(len(model.systems) - before, 2)
        self.assertFalse(res.question_complied, "the model complied after all")
        # And here the backstop cannot help either: "And then what?" is a
        # bare question with nothing else in it, so stripping it would
        # leave an empty reply. Both fields are False, which is the honest
        # reading -- the user does see a third question. That is the
        # documented ceiling on this defence (§15 of the report), not a bug
        # hidden by an optimistic assertion.
        self.assertFalse(res.question_obeyed)
        self.assertTrue(res.text.rstrip().endswith("?"))

    def test_no_retry_below_the_cap(self):
        """ANTI-FALSE-GREEN: two questions in a row is fine."""
        model = self.Twice("So what happened?", "x")
        orch = self._orch(model)
        orch.handle("s", "hi")
        res = orch.handle("s", "hi")
        self.assertFalse(res.question_retry)
        self.assertEqual(len(model.systems), 2)

    def test_no_retry_when_the_reply_is_not_a_question(self):
        """ANTI-FALSE-GREEN."""
        model = self.Twice("Fair enough.", "x")
        orch = self._orch(model)
        for _ in range(3):
            res = orch.handle("s", "hi")
        self.assertFalse(res.question_retry)


class TestDetailRequests(unittest.TestCase):
    """L3, local conversation E04.

    "explain recursion in one line" -> 15 words, correct. "ok now explain
    it properly, with an example" -> 25 words and NO EXAMPLE. The persona
    caps replies at one or two sentences "unless he asks for more", and
    nothing decided that he had asked.
    """

    def test_an_explicit_request_for_more_is_detected(self):
        from pai.router import Router
        rt = Router()
        for text in ["ok now explain it properly, with an example",
                     "tell me more", "explain it step by step",
                     "give me an example", "in more detail",
                     "thoda detail mein bata", "aur batao"]:
            self.assertTrue(rt.route(text).detail, text)

    def test_ordinary_turns_do_not_lift_the_brevity_cap(self):
        """ANTI-FALSE-GREEN: over-triggering makes every reply an essay."""
        from pai.router import Router
        rt = Router()
        for text in ["hey", "what is docker", "and kubernetes?",
                     "explain recursion in one line", "kya scene hai",
                     "thanks"]:
            self.assertFalse(rt.route(text).detail, text)

    def test_the_directive_reaches_the_prompt_only_when_asked(self):
        from pai.orchestrator import DETAIL_DIRECTIVE
        from eval.conversation import Harness

        class Spy:
            max_tokens = 300
            def __init__(self): self.systems = []; self.last = None
            def respond(self, system, history, user, context):
                self.systems.append(system); return "ok"

        spy = Spy()
        h = Harness(spy)
        h.orch.handle("s", "what is docker")
        self.assertNotIn(DETAIL_DIRECTIVE, spy.systems[-1])
        h.orch.handle("s", "explain it properly, with an example")
        self.assertIn(DETAIL_DIRECTIVE, spy.systems[-1])
