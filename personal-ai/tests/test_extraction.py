"""Fact extraction from ordinary conversation.

This closes the gap every earlier version of the report stated plainly: the
system learned HOW he liked to be spoken to and never learned WHAT he told
it. Facts arrived only through an API call.

The stance is signals.py's, for the same reason: a missed fact costs
nothing, and a wrong one is durable, reaches every later prompt, and is
exactly the material a confabulation is made of. Three rounds of this
project went into guards against the assistant inventing things about him;
an extractor that guesses would feed the thing those guards exist to stop.

So the negative tests here matter more than the positive ones.
"""
import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pai.extract import extract_facts
from pai.memory import MemoryStore
from pai.obsidian import VaultIndex, TfidfEmbedder
from pai.orchestrator import Orchestrator
from pai.trust import Trust


class Says:
    max_tokens = 300
    def __init__(self, text="ok."):
        self.text = text
        self.systems: list[str] = []
    def respond(self, system, history, user, context):
        self.systems.append(system)
        return self.text


def build():
    store = MemoryStore()
    vault = VaultIndex(TfidfEmbedder())
    vault.add_note("n.md", "# N\nnothing")
    vault.build_vectors()
    model = Says()
    return store, model, Orchestrator(store, vault, model)


class TestWhatIsExtracted(unittest.TestCase):
    CASES = [
        ("I use neovim",                        ("editor", "neovim")),
        ("main neovim use karta hoon",          ("editor", "neovim")),
        ("my editor is helix",                  ("editor", "helix")),
        ("I work at Anthropic",                 ("works_at", "Anthropic")),
        ("main Google me kaam karta hoon",      ("works_at", "Google")),
        ("I live in Bangalore",                 ("lives_in", "Bangalore")),
        ("my name is Muaz",                     ("name", "Muaz")),
        ("mera naam Muaz hai",                  ("name", "Muaz")),
        ("I work best at night",                ("works_when", "at night")),
        ("I prefer dark mode",                  ("prefers", "dark mode")),
        ("mujhe short answers pasand hai",      ("prefers", "short answers")),
        ("my thesis is about retrieval evaluation",
                                                ("studies", "retrieval evaluation")),
    ]

    def test_first_person_statements_are_extracted(self):
        for text, (predicate, value) in self.CASES:
            got = extract_facts(text)
            self.assertTrue(got, f"missed: {text!r}")
            self.assertEqual((got[0].predicate, got[0].object),
                             (predicate, value), text)

    def test_the_source_clause_is_kept(self):
        """A bad extraction has to be traceable to the sentence it came
        from, or it cannot be argued with."""
        got = extract_facts("yaar main neovim use karta hoon aaj kal")
        self.assertTrue(got)
        self.assertIn("neovim", got[0].source)


class TestWhatIsNotExtracted(unittest.TestCase):
    """The half that matters. Every one of these would be a durable lie."""

    NOT_FACTS = [
        "I don't use neovim",
        "I do not work at Google",
        "do you use neovim?",
        "what editor do I use?",
        "he works at Google",
        "she lives in Delhi",
        "I used to live in Delhi",
        "if I worked at Google I'd be richer",
        "I might use neovim",
        "maybe I prefer dark mode",
        "I use it",
        "I use that thing",
        "main nahi karta",
        "agar main Google me kaam karta",
        "shayad main neovim use karta hoon",
        "kya main neovim use karta hoon?",
    ]

    def test_nothing_is_extracted_from_any_of_these(self):
        for text in self.NOT_FACTS:
            self.assertEqual(extract_facts(text), [],
                             f"invented a fact from: {text!r}")

    def test_ordinary_conversation_yields_nothing(self):
        for text in ["yaar kya scene hai", "I'm bored", "explain docker",
                     "push this to main", "hmm", "thanks",
                     "Python is faster than C, right?"]:
            self.assertEqual(extract_facts(text), [], text)


class TestTheLoopEndToEnd(unittest.TestCase):
    def test_a_fact_mentioned_in_one_session_reaches_a_later_prompt(self):
        store, model, orch = build()
        res = orch.handle("monday", "yaar main neovim use karta hoon")
        self.assertEqual(res.learned, [("muaz", "editor", "neovim")])

        orch.handle("friday", "kuch bhi")
        facts = [l for l in model.systems[-1].splitlines()
                 if l.startswith("- muaz")]
        self.assertIn("- muaz editor: neovim", facts)

    def test_a_changed_fact_supersedes_rather_than_duplicating(self):
        store, model, orch = build()
        orch.handle("s", "I use neovim")
        orch.handle("s", "my editor is helix")
        self.assertEqual(store.current_fact("muaz", "editor").object, "helix")
        history = store.fact_history("muaz", "editor")
        self.assertEqual(len(history), 2, "the old value was destroyed")

    def test_repeating_a_fact_does_not_write_it_again(self):
        """ANTI-FALSE-GREEN: saying the same thing twice must not fill the
        supersession chain with noise."""
        store, model, orch = build()
        orch.handle("s", "I use neovim")
        second = orch.handle("s", "I use neovim")
        self.assertEqual(second.learned, [])
        self.assertEqual(len(store.fact_history("muaz", "editor")), 1)

    def test_an_ordinary_turn_writes_nothing(self):
        """ANTI-FALSE-GREEN."""
        store, model, orch = build()
        res = orch.handle("s", "what is a for loop")
        self.assertEqual(res.learned, [])
        self.assertEqual(store.current_fact("muaz", "editor"), None)

    def test_a_negated_statement_writes_nothing(self):
        """ANTI-FALSE-GREEN, and the one that would hurt most."""
        store, model, orch = build()
        res = orch.handle("s", "I don't use neovim")
        self.assertEqual(res.learned, [])
        self.assertIsNone(store.current_fact("muaz", "editor"))

    def test_extracted_facts_carry_user_trust(self):
        """He said it, so it is USER trust -- retrieved content could never
        reach this path, because only the user turn is passed to it."""
        store, model, orch = build()
        orch.handle("s", "I use neovim")
        row = store.db.execute(
            "SELECT trust FROM facts WHERE predicate='editor'").fetchone()
        self.assertEqual(row["trust"], int(Trust.USER))


if __name__ == "__main__":
    unittest.main()
