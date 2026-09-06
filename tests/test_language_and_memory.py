"""Round-4 defences: language commands, in-session style, memory questions.

As with tests/test_honesty_and_retraction.py, every case here comes from a
transcript, and every defence is paired with a test proving it can still be
silent.
"""
import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.core.memory import MemoryStore
from vision.core.obsidian import VaultIndex, TfidfEmbedder
from vision.core.orchestrator import NO_MEMORY_REPLY, Orchestrator
from vision.core.router import Path, Router, language_command
from vision.core.signals import detect_language
from vision.core.trust import Trust


class Says:
    def __init__(self, text="ok"):
        self.text = text
        self.systems: list[str] = []
        self.contexts: list[str] = []
        self.max_tokens = 300

    def respond(self, system, history, user, context):
        self.systems.append(system)
        self.contexts.append(context)
        return self.text


def build(model=None):
    store = MemoryStore()
    vault = VaultIndex(TfidfEmbedder())
    vault.add_note("n.md", "# N\nnothing relevant here")
    vault.build_vectors()
    model = model or Says()
    return store, vault, model, Orchestrator(store, vault, model)


# ---------------------------------------------------------------------------
# F29 -- the marker list was missing very common words
# ---------------------------------------------------------------------------

class TestMarkerCoverage(unittest.TestCase):
    """MEASURED: recomputed across every user turn in rounds 1-3."""

    def test_bare_imperatives_are_hindi(self):
        for text in ["Simple bol.", "Chal Hinglish mein baat kar.",
                     "zara dekh le", "soch ke bata"]:
            self.assertIn(detect_language(text), ("hi", "hinglish"), text)

    def test_common_verb_forms_are_hindi(self):
        for text in ["Main usually kis language mein baat karta hoon?",
                     "main abhi ghar ja raha hoon",
                     "mujhe lagta hai ye galat hai"]:
            self.assertIn(detect_language(text), ("hi", "hinglish"), text)

    def test_english_is_still_english(self):
        """ANTI-FALSE-GREEN: a bigger Hindi list must not swallow English.

        The technical phrases here are not decoration. The first version of
        the expansion put "main" and "log" on the Hindi list -- both are
        real, common Hindi words -- and "push this to main" started
        scoring as HINGLISH in an English conversation about a git branch.
        This test is what that regression should have hit, and did not,
        until these cases were added.
        """
        for text in ["the deployment pipeline is broken",
                     "what is a database index",
                     "I meant the deployment pipeline.",
                     "explain docker networking",
                     "should i be worried",
                     "push this to main",
                     "merge it into main",
                     "check the log file",
                     "log in to the main branch",
                     "the main function returns early"]:
            self.assertEqual(detect_language(text), "en", text)


# ---------------------------------------------------------------------------
# F31 -- an explicit order to switch language
# ---------------------------------------------------------------------------

class TestLanguageCommand(unittest.TestCase):
    """MEASURED, M08: all four turns of the language-switching probe failed."""

    def test_the_order_beats_the_language_it_is_written_in(self):
        self.assertEqual(language_command("Now speak English."), "en")
        self.assertEqual(language_command("Acha ab Hindi mein bol."), "hi")
        self.assertEqual(language_command("Chal Hinglish mein baat kar."),
                         "hinglish")

    def test_the_router_reports_the_lock(self):
        route = Router().route("Now speak English.", [])
        self.assertEqual(route.lang, "en")
        self.assertTrue(route.lang_locked)

    def test_an_ordinary_turn_is_not_a_command(self):
        """ANTI-FALSE-GREEN: mentioning a language is not ordering one."""
        for text in ["my english is bad", "kya scene hai",
                     "explain what an API is", "hindi movies are great"]:
            route = Router().route(text, [])
            self.assertFalse(route.lang_locked, text)

    def test_the_lock_survives_later_turns(self):
        store, vault, model, orch = build()
        orch.handle("s", "yaar kya scene hai")
        res = orch.handle("s", "Now speak English.")
        self.assertEqual(res.route.lang, "en")
        res = orch.handle("s", "aur bata")          # Hindi-looking turn
        self.assertEqual(res.route.lang, "en",
                         "a locked language must not be silently overridden")

    def test_a_later_order_replaces_the_earlier_one(self):
        """ANTI-FALSE-GREEN: the lock must not be permanent."""
        store, vault, model, orch = build()
        orch.handle("s", "Now speak English.")
        res = orch.handle("s", "Acha ab Hindi mein bol.")
        self.assertEqual(res.route.lang, "hi")


# ---------------------------------------------------------------------------
# F30 -- an explicit style correction applies immediately
# ---------------------------------------------------------------------------

class TestInSessionStyle(unittest.TestCase):
    """MEASURED, M04: 33 -> 22 -> 27 -> 40 words after asking twice for
    shorter answers."""

    def test_a_brevity_correction_caps_the_next_reply(self):
        model = Says("one two three four five")
        store, vault, _, orch = build(model)
        first = orch.handle("s", "Explain what an API is.")
        self.assertEqual(first.gen_params["max_tokens"], 300)
        res = orch.handle("s", "Arre itna bada answer kyun de raha hai?")
        self.assertEqual(res.gen_params["max_tokens"], 35)
        self.assertEqual(res.gen_params["max_sentences"], 2)

    def test_it_holds_for_the_rest_of_the_session(self):
        model = Says("short")
        store, vault, _, orch = build(model)
        orch.handle("s", "Simple bol.")
        res = orch.handle("s", "Ab batao, cache kya hota hai?")
        self.assertEqual(res.gen_params["max_tokens"], 35)

    def test_asking_for_detail_reverses_it(self):
        """ANTI-FALSE-GREEN: not a one-way ratchet."""
        model = Says("x")
        store, vault, _, orch = build(model)
        orch.handle("s", "chhota rakho")
        res = orch.handle("s", "isko detail mein explain kar")
        self.assertEqual(res.gen_params["max_tokens"], 420)

    def test_it_is_scoped_to_the_session(self):
        """ANTI-FALSE-GREEN: one conversation must not shrink another."""
        model = Says("x")
        store, vault, _, orch = build(model)
        orch.handle("a", "Simple bol.")
        res = orch.handle("b", "what's a database index")
        self.assertEqual(res.gen_params["max_tokens"], 300)

    def test_an_ordinary_turn_changes_nothing(self):
        """ANTI-FALSE-GREEN."""
        model = Says("x")
        store, vault, _, orch = build(model)
        res = orch.handle("s", "what's a database index")
        self.assertEqual(res.gen_params["max_tokens"], 300)


# ---------------------------------------------------------------------------
# F32 / F33 -- memory questions
# ---------------------------------------------------------------------------

class TestMemoryQuestions(unittest.TestCase):
    """MEASURED, M07 t2.

    USER: Kal maine jo bola tha yaad hai?
    ROUTE: web   ran=web.search[EMPTY]
    AI:   "Haan yaad hai, kal tumne kaha tha ki tu project launch kar raha
           hai aur team ko ek meeting call karwana hai."

    He had said no such thing.
    """

    def test_a_memory_question_does_not_route_to_the_web(self):
        for text in ["Kal maine jo bola tha yaad hai?",
                     "do you remember what I said last week",
                     "Maine tujhe ye pehle kab bataya tha?",
                     "what did we decide last time"]:
            route = Router().route(text, [])
            self.assertTrue(route.memory_query, text)
            self.assertIsNot(route.path, Path.WEB, text)
            self.assertEqual(route.ack_text, "", text)

    def test_a_real_web_question_is_unaffected(self):
        """ANTI-FALSE-GREEN."""
        for text in ["what's the latest nextjs version",
                     "current price of bitcoin"]:
            self.assertIs(Router().route(text, []).path, Path.WEB, text)

    def test_an_invented_memory_is_replaced(self):
        model = Says("Haan yaad hai, kal tumne kaha tha ki tu project "
                     "launch kar raha hai.")
        store, vault, _, orch = build(model)
        res = orch.handle("s", "Kal maine jo bola tha yaad hai?")
        self.assertEqual(res.evidence, 0)
        self.assertEqual(res.guard_tripped, "fabricated_memory")
        self.assertIn(res.text, NO_MEMORY_REPLY.values())

    def test_the_english_form_is_caught_too(self):
        model = Says("Yes, I remember — you said the deploy was blocked.")
        store, vault, _, orch = build(model)
        res = orch.handle("s", "do you remember what I said last week")
        self.assertEqual(res.guard_tripped, "fabricated_memory")

    def test_a_real_record_is_retrieved_and_the_claim_stands(self):
        """ANTI-FALSE-GREEN: when the store HAS it, remembering is true."""
        model = Says("Yeah — you said the passkey rollout was blocked on "
                     "Safari.")
        store, vault, _, orch = build(model)
        store.add_turn("yesterday", "user",
                       "the passkey rollout is blocked on Safari 16",
                       Trust.USER)
        res = orch.handle("today", "do you remember what I said about "
                                   "the passkey rollout")
        self.assertGreater(res.evidence, 0)
        self.assertEqual(res.guard_tripped, "")
        self.assertIn("Safari", model.contexts[-1])

    def test_the_model_is_told_when_there_is_no_record(self):
        store, vault, model, orch = build()
        orch.handle("s", "Kal maine jo bola tha yaad hai?")
        self.assertIn("NO record", model.systems[-1])

    def test_an_honest_denial_is_never_rewritten(self):
        """ANTI-FALSE-GREEN."""
        model = Says("Nope, I don't have anything about that.")
        store, vault, _, orch = build(model)
        res = orch.handle("s", "Kal maine jo bola tha yaad hai?")
        self.assertEqual(res.guard_tripped, "")
        self.assertIn("Nope", res.text)

    def test_the_search_does_not_return_the_current_session(self):
        """The turn just logged must not become its own evidence."""
        store, vault, model, orch = build()
        orch.handle("s", "the passkey rollout is blocked on Safari 16")
        res = orch.handle("s", "do you remember the passkey rollout")
        self.assertEqual(res.evidence, 0,
                         "a question answered itself from its own session")


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# F34 -- an empty query is not a query
# ---------------------------------------------------------------------------

class TestQueryRewrite(unittest.TestCase):
    """MEASURED, M10 t4: rewrite_query("Iska latest answer web se check
    kar.") returned "latest .", DuckDuckGo answered with a Cheap Trick
    album, and two irrelevant results were injected as evidence."""

    def test_a_hollow_utterance_yields_no_query(self):
        from vision.core.web import rewrite_query
        for text in ["Iska latest answer web se check kar.",
                     "check this",
                     "iska latest bata"]:
            self.assertEqual(rewrite_query(text), "", text)

    def test_the_previous_turn_resolves_the_reference(self):
        from vision.core.web import rewrite_query
        q = rewrite_query("Iska latest answer web se check kar.",
                          context="what is the latest nextjs version")
        self.assertIn("nextjs", q.lower())

    def test_a_real_query_is_left_alone(self):
        """ANTI-FALSE-GREEN: the rewrite must not eat good queries."""
        from vision.core.web import rewrite_query
        for text in ["what is the latest nextjs version",
                     "current price of bitcoin",
                     "aaj ka weather kya hai"]:
            self.assertTrue(rewrite_query(text), text)

    def test_no_search_runs_when_there_is_nothing_to_search_for(self):
        calls = []
        model = Says("no idea")
        store, vault, _, orch = build(model)
        orch.register("web.search", lambda a: calls.append(a) or [])
        orch.handle("s", "search the web for iska latest answer")
        self.assertEqual(calls, [], "searched for nothing")

    def test_a_real_query_still_searches(self):
        """ANTI-FALSE-GREEN."""
        calls = []
        model = Says("ok")
        store, vault, _, orch = build(model)
        orch.register("web.search", lambda a: calls.append(a) or [])
        orch.handle("s", "what's the latest nextjs version")
        self.assertEqual(len(calls), 1)


class TestLockedLanguageEnforcement(unittest.TestCase):
    """One retry, only on an explicit order, only when it was disobeyed."""

    class Twice:
        """Answers in Hindi first, English on the retry."""
        max_tokens = 300
        def __init__(self):
            self.calls = 0
            self.systems = []
        def respond(self, system, history, user, context):
            self.systems.append(system)
            self.calls += 1
            return ("Kya scene hai bhai, thoda busy hoon" if self.calls == 1
                    else "Not much, just working through some things.")

    def test_a_disobeyed_order_is_retried_once(self):
        store, vault, _, orch = build(self.Twice())
        res = orch.handle("s", "Now speak English.")
        self.assertTrue(res.language_retry)
        self.assertTrue(res.language_obeyed)
        self.assertIn("Not much", res.text)
        self.assertIn("CRITICAL", orch.conversation.systems[-1])
        self.assertEqual(orch.conversation.calls, 2, "retried more than once")

    def test_an_obeyed_order_is_not_retried(self):
        """ANTI-FALSE-GREEN: the retry must be conditional."""
        model = Says("Sure, English it is. What's up?")
        store, vault, _, orch = build(model)
        res = orch.handle("s", "Now speak English.")
        self.assertFalse(res.language_retry)
        self.assertEqual(len(model.systems), 1)

    def test_an_unlocked_turn_is_never_retried(self):
        """ANTI-FALSE-GREEN: only an explicit order earns a second call."""
        model = Says("Kya scene hai bhai")
        store, vault, _, orch = build(model)
        res = orch.handle("s", "what are you up to")
        self.assertFalse(res.language_retry)
        self.assertEqual(len(model.systems), 1)

    def test_hinglish_satisfies_a_hindi_order(self):
        """ANTI-FALSE-GREEN: a technical English word in spoken Hindi is
        how he talks, not a violation."""
        model = Says("Haan bhai, main deployment pipeline dekh raha hoon")
        store, vault, _, orch = build(model)
        res = orch.handle("s", "Acha ab Hindi mein bol.")
        self.assertFalse(res.language_retry)


class TestDenyingMemory(unittest.TestCase):
    """MEASURED, defence probe B1 t3 in round 4.

        USER: arre wahi jo maine kal bola tha
        AI:   "...Maine record nahi rakh sakta tumhare baaton ka."
              ("I can't keep a record of what you say.")

    It can. The turn routed as a memory question and the store was
    searched; there was simply nothing in it. Saying "there is no record of
    that" is honest and saying "I cannot keep records" is not.
    """

    def test_denying_the_memory_after_searching_it_is_replaced(self):
        model = Says("Maine record nahi rakh sakta tumhare baaton ka.")
        store, vault, _, orch = build(model)
        res = orch.handle("s", "arre wahi jo maine kal bola tha")
        self.assertTrue(res.route.memory_query)
        self.assertEqual(res.guard_tripped, "denied_a_capability_it_has")

    def test_the_honest_no_record_reply_survives(self):
        """ANTI-FALSE-GREEN, and a sharp one: the guard's OWN replacement
        text says "Mere paas iska koi record nahi hai". A pattern that
        caught that would replace an honest answer with itself and would
        have caught the correct reply in every future run."""
        from vision.core.orchestrator import NO_MEMORY_REPLY, NO_EVIDENCE_REPLY
        from vision.core.orchestrator import CAPABILITY_DENIAL
        for text in (list(NO_MEMORY_REPLY.values())
                     + list(NO_EVIDENCE_REPLY.values())
                     + ["Nahi yaad hai, maine yeh baat chat history mein "
                        "nahi dekhi.",
                        "Nothing in your notes about that."]):
            self.assertIsNone(CAPABILITY_DENIAL.search(text), text)


class TestAQuestionAboutThisConversation(unittest.TestCase):
    """E2E failure F, found by running the application.

    "I am working on my thesis chapter three" then "what did I just say I
    was working on" was answered "I couldn't actually find anything on
    that". search_turns deliberately excludes the current session, so
    evidence was 0 and the model was told "You have NO record of this
    conversation" -- while the conversation sat three lines above it in its
    own prompt. A confident false denial is the same class of failure as a
    confident false claim.
    """

    def test_the_no_record_directive_is_withheld_when_history_can_answer(self):
        store, vault, model, orch = build()
        orch.handle("s", "I am working on my thesis chapter three")
        orch.handle("s", "what did I just say I was working on")
        self.assertNotIn("NO record", model.systems[-1])

    def test_a_question_about_an_earlier_session_still_gets_the_directive(self):
        """ANTI-FALSE-GREEN: the fix must not disable the guard wholesale.

        A long conversation does not make "what did I say yesterday"
        answerable from it.
        """
        store, vault, model, orch = build()
        orch.handle("s", "hello there")
        orch.handle("s", "how are you")
        orch.handle("s", "Kal maine jo bola tha yaad hai?")
        self.assertIn("NO record", model.systems[-1])

    def test_a_fabricated_memory_about_yesterday_is_still_caught(self):
        model = Says("Haan yaad hai, kal tumne kaha tha ki tu launch kar raha hai.")
        store, vault, _, orch = build(model)
        orch.handle("s", "hi")
        orch.handle("s", "how are you")
        res = orch.handle("s", "Kal maine jo bola tha yaad hai?")
        self.assertEqual(res.guard_tripped, "fabricated_memory")
