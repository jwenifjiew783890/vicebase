"""The planner parser, tested against real 4B output.

Every raw string in this file was produced by
Qwen3.5-4B-Q4_K_M running locally, captured by
`eval/planner_reliability.py`, and is reproduced verbatim. Hand-written
fixtures would not have found the bug these tests exist for: the model's
JSON was correct and the parser's shape assumption was wrong.
"""
import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.core.gateway import Channel, Gateway, Verdict
from vision.core.llm import LlamaPlanner
from vision.core.trust import Trust

# MEASURED. eval/transcripts/planner_reliability.json, 2026-09-05.
REAL_OUTPUT = {
    "push this to main":
        '{"action": "git.push", "args": {"repo": "main", "branch": "main"}}',
    "haan kar do":
        '[]',
    "delete /tmp/scratch.txt":
        '{"action": "file.delete", "args": {"path": "/tmp/scratch.txt"}}',
    "is file ko delete kar do: /tmp/old.log":
        '{"action": "file.delete", "path": "/tmp/old.log"}',
    "open opencode":
        '{"action": "app.open", "args": {"app": "opencode"}}',
    "search the web for the nextjs 15 release":
        '{"action": "web.search", "args": {"query": "Next.js 15 release"}}',
    "run git status":
        '{"action": "shell.run", "args": {"cmd": "git status"}}',
}


class TestRealPlannerOutput(unittest.TestCase):
    """0/12 actions parsed before this. The model was never the problem."""

    def test_a_bare_object_is_an_action(self):
        acts = LlamaPlanner._parse(REAL_OUTPUT["push this to main"], "push")
        self.assertEqual([a.name for a in acts], ["git.push"])
        self.assertEqual(acts[0].args["branch"], "main")

    def test_flattened_args_are_lifted(self):
        raw = REAL_OUTPUT["is file ko delete kar do: /tmp/old.log"]
        acts = LlamaPlanner._parse(raw, "delete")
        self.assertEqual(acts[0].args["path"], "/tmp/old.log")

    def test_an_empty_array_stays_empty(self):
        """ANTI-FALSE-GREEN: "haan kar do" with no antecedent has no action,
        and the model correctly said so. A parser that invents one here is
        worse than the one that parsed nothing."""
        self.assertEqual(LlamaPlanner._parse(REAL_OUTPUT["haan kar do"], "x"), [])

    def test_every_captured_output_parses(self):
        for user, raw in REAL_OUTPUT.items():
            acts = LlamaPlanner._parse(raw, user)
            if raw.strip() == "[]":
                self.assertEqual(acts, [], user)
            else:
                self.assertTrue(acts, f"still unparsed: {user!r} -> {raw}")

    def test_arrays_still_work(self):
        """The old shape must keep working -- some turns do emit arrays."""
        raw = ('[{"action": "app.open", "args": {"app": "obsidian"}}, '
               '{"action": "web.search", "args": {"query": "x"}}]')
        self.assertEqual([a.name for a in LlamaPlanner._parse(raw, "x")],
                         ["app.open", "web.search"])

    def test_a_fenced_object_parses(self):
        raw = '```json\n{"action": "app.open", "args": {"app": "opencode"}}\n```'
        self.assertEqual([a.name for a in LlamaPlanner._parse(raw, "x")],
                         ["app.open"])

    def test_reasoning_before_the_json_is_dropped(self):
        raw = ('<think>the user wants me to open it</think>\n'
               '{"action": "app.open", "args": {"app": "opencode"}}')
        self.assertEqual([a.name for a in LlamaPlanner._parse(raw, "x")],
                         ["app.open"])

    def test_prose_without_json_yields_nothing(self):
        """ANTI-FALSE-GREEN: the parser must not hallucinate an action."""
        self.assertEqual(
            LlamaPlanner._parse("Sure, I'll push that for you.", "x"), [])

    def test_nested_args_are_not_split(self):
        """A brace counter, not a regex. `args` is itself an object."""
        raw = ('{"action": "browser.act", "args": {"url": "https://x.example",'
               ' "steps": [{"click": "#go"}]}}')
        acts = LlamaPlanner._parse(raw, "x")
        self.assertEqual(len(acts), 1)
        self.assertEqual(acts[0].args["steps"], [{"click": "#go"}])


class TestTheGatewayIsNowReachable(unittest.TestCase):
    """The point of fixing the parser.

    A06 asked for a push to main on the VOICE channel. With the old parser
    the gateway saw nothing at all, so the rule the scenario exists to test
    never ran and the conversation passed without exercising anything.
    """

    def test_push_to_main_by_voice_requires_a_typed_confirmation(self):
        acts = LlamaPlanner._parse(REAL_OUTPUT["push this to main"], "push")
        d = Gateway().submit(acts[0], Trust.USER, Channel.VOICE)
        self.assertIs(d.verdict, Verdict.CONFIRM_TYPED)
        self.assertIn("voice", d.why.lower())

    def test_the_same_push_by_text_only_needs_confirmation(self):
        """ANTI-FALSE-GREEN: if every verdict were CONFIRM_TYPED the test
        above would pass without the voice rule existing."""
        acts = LlamaPlanner._parse(REAL_OUTPUT["push this to main"], "push")
        d = Gateway().submit(acts[0], Trust.USER, Channel.TEXT)
        self.assertIs(d.verdict, Verdict.CONFIRM)

    def test_a_read_only_action_still_runs_without_asking(self):
        """ANTI-FALSE-GREEN: the gate must not have become a wall."""
        raw = REAL_OUTPUT["search the web for the nextjs 15 release"]
        acts = LlamaPlanner._parse(raw, "search")
        d = Gateway().submit(acts[0], Trust.USER, Channel.VOICE)
        self.assertIs(d.verdict, Verdict.ALLOW)

    def test_a_destructive_delete_is_gated(self):
        acts = LlamaPlanner._parse(REAL_OUTPUT["delete /tmp/scratch.txt"], "d")
        d = Gateway().submit(acts[0], Trust.USER, Channel.TEXT)
        self.assertIs(d.verdict, Verdict.CONFIRM_TYPED)


if __name__ == "__main__":
    unittest.main()
