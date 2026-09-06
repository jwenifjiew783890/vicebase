"""Tests for the model adapter layer that do not need a model.

Parsing and sanitisation are where a local model's rough edges become the
system's bugs, so they get tested independently of inference.
"""
import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.core.llm import _strip_thinking, LlamaPlanner
from vision.core.gateway import Action, Gateway, Verdict
from vision.core.trust import Trust


class TestThinkingStripping(unittest.TestCase):
    """Reasoning traces must never reach TTS or the user."""

    def test_well_formed_block_removed(self):
        self.assertEqual(
            _strip_thinking("<think>let me consider</think>Hey, all good."),
            "Hey, all good.")

    def test_multiline_block_removed(self):
        self.assertEqual(
            _strip_thinking("<think>\na\nb\n</think>\n\nHaan bhai."), "Haan bhai.")

    def test_unterminated_block_truncated_not_leaked(self):
        """Running out of token budget mid-thought must not emit the thought."""
        out = _strip_thinking("<think>I should say hi but first")
        self.assertNotIn("<think>", out)
        self.assertNotIn("I should say hi", out)

    def test_content_before_unclosed_block_is_kept(self):
        self.assertEqual(_strip_thinking("Hey. <think>now let me"), "Hey.")

    def test_closed_block_then_reply(self):
        self.assertEqual(_strip_thinking("<think>reasoning</think>Real reply"),
                         "Real reply")

    def test_stray_closing_tag_keeps_what_follows(self):
        self.assertEqual(_strip_thinking("leaked notes</think>Actual reply"),
                         "Actual reply")

    def test_plain_text_untouched(self):
        self.assertEqual(_strip_thinking("  just a reply  "), "just a reply")

    def test_case_insensitive(self):
        self.assertEqual(_strip_thinking("<THINK>x</THINK>ok"), "ok")


class TestPlannerParsing(unittest.TestCase):
    """A 4B model emits malformed plans. That must be a PARSE_ERR, not a hazard."""

    P = staticmethod(LlamaPlanner._parse)

    def test_clean_array(self):
        acts = self.P('[{"action":"app.open","args":{"app":"opencode"}}]', "u")
        self.assertEqual(len(acts), 1)
        self.assertEqual(acts[0].name, "app.open")

    def test_array_wrapped_in_prose(self):
        raw = 'Sure! Here you go:\n```json\n[{"action":"web.search","args":{"query":"x"}}]\n```\nHope that helps'
        acts = self.P(raw, "u")
        self.assertEqual([a.name for a in acts], ["web.search"])

    def test_empty_array_means_no_tool(self):
        self.assertEqual(self.P("[]", "u"), [])

    def test_pure_prose_yields_nothing(self):
        self.assertEqual(self.P("I think you want me to open something.", "u"), [])

    def test_malformed_json_yields_nothing_not_an_exception(self):
        for bad in ['[{"action": }]', '[{action:app.open}]', '[', '[}',
                    '[{"action":"a","args":{,}}]']:
            self.assertEqual(self.P(bad, "u"), [], bad)

    def test_missing_action_key_skipped(self):
        self.assertEqual(self.P('[{"args":{"app":"x"}}]', "u"), [])

    def test_non_dict_elements_skipped(self):
        acts = self.P('["app.open", {"action":"web.search","args":{"query":"q"}}]', "u")
        self.assertEqual([a.name for a in acts], ["web.search"])

    def test_hallucinated_tool_is_parsed_then_denied_by_the_gateway(self):
        """Parsing is permissive; the gateway is where invention dies."""
        acts = self.P('[{"action":"system.root_shell","args":{"cmd":"rm -rf /"}}]', "u")
        self.assertEqual(len(acts), 1)
        d = Gateway().submit(acts[0], Trust.USER)
        self.assertIs(d.verdict, Verdict.DENY)
        self.assertIn("unknown capability", d.why)

    def test_missing_required_args_denied_downstream(self):
        acts = self.P('[{"action":"git.push","args":{}}]', "u")
        d = Gateway().submit(acts[0], Trust.USER)
        self.assertIs(d.verdict, Verdict.DENY)
        self.assertIn("missing", d.why)

    def test_reason_records_the_user_turn_not_model_prose(self):
        acts = self.P('[{"action":"app.open","args":{"app":"opencode"}}]',
                      "open opencode please")
        self.assertIn("open opencode please", acts[0].reason)



class TestEmptyResponseFallback(unittest.TestCase):
    """Stripping a reasoning block can leave nothing. Never emit an empty turn."""

    class FakeBackend:
        def __init__(self, outputs): self.outputs = list(outputs); self.calls = 0
        def chat(self, msgs, **kw):
            from vision.core.llm import GenStats
            self.calls += 1
            out = self.outputs.pop(0) if self.outputs else ""
            return out, GenStats(completion_tokens=len(out.split()))

    def _conv(self, outputs):
        from vision.core.llm import LlamaConversation
        c = LlamaConversation.__new__(LlamaConversation)
        c.backend = self.FakeBackend(outputs)
        c.max_tokens = 100; c.temperature = 0.7; c.last = None
        return c

    def test_retries_once_when_stripping_leaves_nothing(self):
        c = self._conv(["<think>hmm let me work this out",
                        "Haan bhai, sab theek."])
        out = c.respond("sys", [], "kya haal hai", "")
        self.assertEqual(out, "Haan bhai, sab theek.")
        self.assertEqual(c.backend.calls, 2)

    def test_falls_back_in_the_users_language_when_retry_also_fails(self):
        from vision.core.llm import LlamaConversation
        c = self._conv(["<think>a", "<think>b"])
        out = c.respond("sys", [], "kya haal hai", "")
        self.assertEqual(out, LlamaConversation.FALLBACKS["hi"])

    def test_english_fallback_for_english_turn(self):
        from vision.core.llm import LlamaConversation
        c = self._conv(["<think>a", "<think>b"])
        out = c.respond("sys", [], "what's going on", "")
        self.assertEqual(out, LlamaConversation.FALLBACKS["en"])

    def test_never_returns_empty(self):
        c = self._conv(["", ""])
        self.assertTrue(c.respond("sys", [], "hey", "").strip())

    def test_no_retry_when_first_response_is_fine(self):
        c = self._conv(["All good."])
        self.assertEqual(c.respond("sys", [], "hey", ""), "All good.")
        self.assertEqual(c.backend.calls, 1)

    def test_fallback_is_not_an_error_string(self):
        """This text reaches TTS; it must sound like a person."""
        from vision.core.llm import LlamaConversation
        for v in LlamaConversation.FALLBACKS.values():
            for bad in ("error", "exception", "none", "null", "failed", "sorry, i"):
                self.assertNotIn(bad, v.lower().replace("sorry, lost", "x"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
