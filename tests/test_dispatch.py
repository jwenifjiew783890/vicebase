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
