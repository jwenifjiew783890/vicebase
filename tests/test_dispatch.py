"""Which agent a turn goes to, and the two bugs that came from getting it wrong."""
import sys, os, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.dispatch import classify


class TestConversationIsTheDefault(unittest.TestCase):
    def test_small_talk_never_reaches_an_agent(self):
        for text in ["hey", "kya scene hai", "I am tired today",
                     "what is a for loop", "haha ok", "thanks"]:
            self.assertIsNone(classify(text).agent, text)


class TestShellDispatch(unittest.TestCase):
    """E2E failures K and L, both from the same mistake."""

    def test_the_whole_command_is_dispatched(self):
        """K: "run git status" dispatched the task "status", because the
        trigger phrase "run git" was cut out of the sentence."""
        d = classify("run git status")
        self.assertEqual(d.agent, "shell")
        self.assertEqual(d.task, "git status")

    def test_a_dangerous_command_still_reaches_the_gateway(self):
        """L: the pattern listed safe commands only, so "run rm -rf /"
        matched nothing, fell through to conversation, and was answered by
        the MODEL instead of being refused by the capability gateway.

        Routing decides where a request goes. The gateway decides whether
        it may happen. A dangerous command that never arrives at the thing
        which can say no is the worst possible outcome.
        """
        d = classify("run rm -rf /")
        self.assertEqual(d.agent, "shell")
        self.assertEqual(d.task, "rm -rf /")


class TestMemoryDispatch(unittest.TestCase):
    def test_a_write_keeps_the_verb(self):
        """The agent needs "remember"; stripping it turned a write into a
        read of the same words."""
        d = classify("remember I use neovim")
        self.assertEqual(d.agent, "memory")
        self.assertIn("remember", d.utterance)

    def test_hinglish_write(self):
        self.assertEqual(classify("yaad rakhna main raat ko kaam karta hoon").agent,
                         "memory")


class TestOtherRoutes(unittest.TestCase):
    def test_each_specialist_is_reachable(self):
        cases = {"research the python GIL": "research",
                 "write me a python script to reverse a string": "coding",
                 "plan my thesis chapter": "planner",
                 "check my notes about auth": "knowledge",
                 "find the file config.py": "files",
                 "search the web for nextjs 16": "web"}
        for text, agent in cases.items():
            self.assertEqual(classify(text).agent, agent, text)


if __name__ == "__main__":
    unittest.main()


class TestAgentsThatNeedTheWholeUtterance(unittest.TestCase):
    """Three agents have now been broken by the same mistake.

    The dispatcher strips the trigger phrase so that "research the GIL"
    searches for "the GIL" rather than for its own trigger. When the
    trigger OVERLAPS the payload, that strip destroys the request:

      "run git status"          -> "status"          (shell)
      "remember I use neovim"   -> "I use neovim"    (memory: write became read)
      "open http://x:8765/"     -> "x:8765/"         (browser: no scheme left)

    Each agent that needs the original text declares `wants_utterance`.
    This test pins the set, so the next one is caught here rather than by
    an agent silently running nothing.
    """

    def test_the_url_survives_dispatch(self):
        from vision.agents.registry import REGISTRY
        d = classify("open http://127.0.0.1:8765/")
        self.assertEqual(d.agent, "browser")
        agent = REGISTRY["browser"]
        payload = d.utterance if getattr(agent, "wants_utterance", False) else d.task
        self.assertIn("http://", payload)

    def test_every_overlapping_agent_declares_wants_utterance(self):
        from vision.agents.registry import REGISTRY
        import vision.agents.builtin  # noqa: F401
        for name in ("memory", "browser", "mcp", "desktop"):
            self.assertTrue(getattr(REGISTRY[name], "wants_utterance", False),
                            f"{name} needs the original utterance")


class TestUnavailableIsNotFailed(unittest.TestCase):
    """A capability that cannot run here is not a capability that broke.

    The desktop agent on a headless machine answered "I can't drive the
    desktop here. It didn't work: nothing ran" -- the second sentence
    reads as a malfunction and is wrong. Nothing was attempted.
    """

    def test_no_steps_reads_as_unavailable_not_broken(self):
        from vision.assistant import Vision
        from vision.agents.base import AgentResult
        v = Vision.__new__(Vision)          # no model, no store needed
        res = AgentResult(summary="I can't drive the desktop here.",
                          detail="no graphical session (no DISPLAY).")
        said = Vision._narrate(v, res, "take a screenshot")
        self.assertNotIn("didn't work", said)
        self.assertIn("DISPLAY", said)

    def test_a_real_failure_still_says_so(self):
        from vision.assistant import Vision
        from vision.agents.base import AgentResult, Step
        v = Vision.__new__(Vision)
        res = AgentResult(summary="Tried to read it.",
                          steps=[Step(action="file.read", ok=False,
                                      error="PermissionError: denied")])
        said = Vision._narrate(v, res, "read the file")
        self.assertIn("didn't work", said)
        self.assertIn("PermissionError", said)
