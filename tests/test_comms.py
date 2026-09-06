"""Communication agents: the safety properties, not the plumbing.

An assistant that can message real people is the place where "it did
something it shouldn't" stops being an inconvenience. These tests pin the
two properties that matter: it never sends without confirmation, and it
never pretends to have sent.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.agents.base import AgentContext
from vision.agents.comms import WhatsAppAgent, EmailAgent


class TestWhatsAppNeverSendsUnasked(unittest.TestCase):
    def setUp(self):
        self._saved = {k: os.environ.get(k) for k in
                       ("VISION_WHATSAPP_TOKEN", "VISION_WHATSAPP_PHONE_ID")}

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_without_credentials_it_says_so_and_does_nothing(self):
        os.environ.pop("VISION_WHATSAPP_TOKEN", None)
        os.environ.pop("VISION_WHATSAPP_PHONE_ID", None)
        r = WhatsAppAgent().run("whatsapp 919876543210 saying hi", AgentContext())
        self.assertEqual(r.steps, [], "no call may be attempted")
        self.assertIn("credential", r.detail.lower())
        self.assertFalse(r.ok)

    def test_with_credentials_it_still_asks_first(self):
        """The important one. Credentials present is not permission."""
        os.environ["VISION_WHATSAPP_TOKEN"] = "test"
        os.environ["VISION_WHATSAPP_PHONE_ID"] = "1"
        r = WhatsAppAgent().run(
            "send a whatsapp to 919876543210 saying I am running late",
            AgentContext())
        self.assertEqual(r.steps, [], "nothing may go over the wire yet")
        self.assertIsNotNone(r.needs_confirmation)
        self.assertEqual(r.needs_confirmation["to"], "919876543210")
        self.assertEqual(r.needs_confirmation["body"], "I am running late")

    def test_it_never_claims_delivery_it_did_not_observe(self):
        """A substring check is not good enough here, and getting that
        wrong is instructive: "nothing has been sent" contains "sent".
        What must be absent is an AFFIRMATIVE claim of delivery."""
        import re
        os.environ["VISION_WHATSAPP_TOKEN"] = "test"
        os.environ["VISION_WHATSAPP_PHONE_ID"] = "1"
        r = WhatsAppAgent().run("whatsapp 919876543210 saying hi", AgentContext())
        said = (r.summary + " " + r.detail).lower()
        claim = re.compile(
            r"(?<!nothing has been )(?<!not )(?<!never )"
            r"\b(i (sent|messaged)|message (sent|delivered)|has been delivered)\b")
        self.assertIsNone(claim.search(said), f"claimed delivery: {said!r}")
        # and it must positively say that nothing went out
        self.assertRegex(said, r"nothing has been sent|not been sent")


class TestEmailDraftsWithoutSending(unittest.TestCase):
    def test_drafting_needs_no_account_and_sends_nothing(self):
        r = EmailAgent().run("draft an email to bob@example.com about the release",
                             AgentContext())
        self.assertIn("nothing sent", (r.summary + r.detail).lower())
        self.assertFalse(any(s.action == "email.send" for s in r.steps))


if __name__ == "__main__":
    unittest.main()
