"""Cross-session memory: does what I said last time reach the prompt this time?

Tests the plumbing without a model, so the model-time test only has to
judge whether the assistant USES the memory naturally, not whether it
arrived at all.
"""
import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.core.memory import MemoryStore
from vision.core.obsidian import VaultIndex, TfidfEmbedder
from vision.core.orchestrator import Orchestrator
from vision.core.trust import Trust


class Recorder:
    """Captures exactly what the model would have received."""
    def __init__(self): self.prompts = []; self.contexts = []; self.last = None
    def respond(self, system, history, user, context):
        self.prompts.append(system); self.contexts.append(context)
        return "ok"


def build():
    store = MemoryStore()
    vault = VaultIndex(TfidfEmbedder())
    vault.add_note("n.md", "# N\nnothing relevant here")
    vault.build_vectors()
    rec = Recorder()
    return store, Orchestrator(store, vault, rec), rec


class TestCrossSession(unittest.TestCase):
    def test_fact_from_session_one_reaches_session_two_prompt(self):
        store, orch, rec = build()
        orch.handle("s1", "hello")
        self.assertNotIn("neovim", rec.prompts[-1])
        store.assert_fact("muaz", "editor", "neovim", Trust.USER)
        orch.handle("s2", "what editor do i use")
        self.assertIn("neovim", rec.prompts[-1])

    def test_superseded_fact_shows_only_the_current_value(self):
        store, orch, rec = build()
        store.assert_fact("muaz", "editor", "neovim", Trust.USER)
        store.assert_fact("muaz", "editor", "zed", Trust.USER)
        orch.handle("s3", "what editor do i use")
        p = rec.prompts[-1]
        self.assertIn("zed", p)
        self.assertNotIn("neovim", p,
                         "superseded value leaked into the prompt; the model "
                         "would see two conflicting editors")

    def test_history_is_queryable_even_though_it_is_not_in_the_prompt(self):
        store, orch, rec = build()
        store.assert_fact("muaz", "editor", "neovim", Trust.USER, valid_from=1)
        store.assert_fact("muaz", "editor", "zed", Trust.USER, valid_from=2)
        hist = store.fact_history("muaz", "editor")
        self.assertEqual([f.object for f in hist], ["neovim", "zed"])
        self.assertFalse(hist[0].is_current)
        self.assertTrue(hist[1].is_current)

    def test_memory_block_is_capped(self):
        store, orch, rec = build()
        for i in range(40):
            store.assert_fact("muaz", f"pred{i}", f"val{i}", Trust.USER)
        orch.handle("s4", "hi")
        block = rec.prompts[-1]
        self.assertLessEqual(block.count("- muaz "), 12,
                             "memory header is unbounded; it will crowd out "
                             "the persona and blow the prompt cache")

    def test_retrieved_context_is_separate_from_the_memory_header(self):
        """Vault content must arrive fenced, not merged into 'what you know'."""
        store = MemoryStore()
        vault = VaultIndex(TfidfEmbedder())
        vault.add_note("Projects/Auth.md",
                       "# Auth\n## Decisions\nWe chose passkeys, codename Thornbury.")
        vault.build_vectors()
        rec = Recorder()
        orch = Orchestrator(store, vault, rec)
        orch.handle("s5", "what did we decide about auth Thornbury")
        self.assertIn("untrusted_content", rec.contexts[-1])
        self.assertNotIn("Thornbury", rec.prompts[-1],
                         "vault text leaked into the trusted system header")

    def test_new_session_does_not_inherit_conversation_history(self):
        store, orch, rec = build()
        orch.handle("s1", "my secret project is called Falcon")
        orch.handle("s2", "what am i working on")
        turns = [t["text"] for t in
                 [dict(r) for r in store.turns("s2")]]
        self.assertNotIn("my secret project is called Falcon", turns)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestTheStoreSurvivesAThreadpool(unittest.TestCase):
    """The application server answers requests on a threadpool.

    Found by launching the app: /api/status raised
    "SQLite objects created in a thread can only be used in that same
    thread". Every unit test ran on one thread, so nothing caught it --
    the bug was only reachable through the running server.
    """

    def test_a_store_is_readable_from_another_thread(self):
        import threading, tempfile, os
        from vision.core.memory import MemoryStore
        from vision.core.trust import Trust
        path = os.path.join(tempfile.mkdtemp(), "t.db")
        store = MemoryStore(path)
        store.assert_fact("muaz", "editor", "neovim", Trust.USER)

        seen, errors = [], []

        def read():
            try:
                seen.append(store.current_fact("muaz", "editor").object)
            except Exception as exc:            # pragma: no cover
                errors.append(exc)

        t = threading.Thread(target=read)
        t.start(); t.join()
        self.assertEqual(errors, [])
        self.assertEqual(seen, ["neovim"])

    def test_concurrent_writes_do_not_raise(self):
        import threading, tempfile, os
        from vision.core.memory import MemoryStore
        from vision.core.trust import Trust
        path = os.path.join(tempfile.mkdtemp(), "t2.db")
        store = MemoryStore(path)
        errors = []

        def write(i):
            try:
                store.add_turn(f"s{i}", "user", f"turn {i}", Trust.USER)
            except Exception as exc:            # pragma: no cover
                errors.append(exc)

        threads = [threading.Thread(target=write, args=(i,)) for i in range(8)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(errors, [])
        self.assertEqual(
            list(store.db.execute("SELECT COUNT(*) c FROM turns"))[0]["c"], 8)
