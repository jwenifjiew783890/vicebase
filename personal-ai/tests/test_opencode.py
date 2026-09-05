"""OpenCode integration, tested against a REAL local HTTP server.

The point is not to mock the client's own methods -- that would prove
nothing. A throwaway http.server implements OpenCode's documented shape
(POST /session, POST /session/{id}/message, GET /health) and the client
talks to it over a real socket. That exercises the URL construction, JSON
encoding, response parsing, timeouts and error paths.
"""
import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pai.opencode import (OpenCodeClient, TaskBrief, build_brief, SessionResult)
from pai.gateway import is_tainted


class FakeOpenCode(BaseHTTPRequestHandler):
    """Implements the documented endpoints. Records what it received."""
    received: list = []
    mode = "ok"

    def log_message(self, *a):  # silence
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"status": "ok"})
        self._send(404, {})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(n) or b"{}")
        FakeOpenCode.received.append((self.path, payload))
        if FakeOpenCode.mode == "boom":
            return self._send(500, {"error": "internal"})
        if self.path == "/session":
            return self._send(200, {"id": "sess-42"})
        if self.path.startswith("/session/") and self.path.endswith("/message"):
            return self._send(200, {
                "summary": "Fixed the failing login test by awaiting the "
                           "session lookup.",
                "files_changed": ["src/auth/login.ts", "src/auth/login.test.ts"]})
        self._send(404, {})


class ServerFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = HTTPServer(("127.0.0.1", 0), FakeOpenCode)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def setUp(self):
        FakeOpenCode.received.clear()
        FakeOpenCode.mode = "ok"


class TestBriefBuilder(unittest.TestCase):
    """The brief is the delegation quality bottleneck."""

    def test_a_specific_request_becomes_actionable(self):
        b = build_brief("fix the failing login test in src/auth/login.ts",
                        repo="vicebase")
        self.assertTrue(b.is_actionable, b.missing)
        self.assertIn("login.ts", " ".join(b.files_hint))
        self.assertIn("test passes", " ".join(b.acceptance).lower())

    def test_vague_requests_are_flagged_not_guessed(self):
        """A specialist agent sent off on a guess wastes its capability."""
        for vague in ["kar do", "wo wala", "fix it", "mera assignment",
                      "kal wala kaam", "do it"]:
            b = build_brief(vague, repo="vicebase")
            self.assertFalse(b.is_actionable, f"{vague!r} was treated as actionable")
            self.assertTrue(b.missing)

    def test_missing_repo_is_flagged(self):
        b = build_brief("fix the login bug")
        self.assertFalse(b.is_actionable)
        self.assertIn("which repository", " ".join(b.missing))

    def test_hinglish_request_is_stripped_to_the_instruction(self):
        b = build_brief("yaar opencode mein login page ka bug fix kar do",
                        repo="vicebase", lang="hinglish")
        self.assertTrue(b.is_actionable, b.missing)
        self.assertNotIn("yaar", b.goal.lower())
        self.assertNotIn("opencode", b.goal.lower())
        self.assertIn("bug", b.goal.lower())

    def test_rendered_brief_has_the_sections_an_agent_needs(self):
        b = build_brief("implement the export endpoint in api/export.py",
                        repo="vicebase")
        text = b.render()
        for section in ("# Task", "## Repository", "## Acceptance criteria",
                        "## Constraints"):
            self.assertIn(section, text)


class TestClientAgainstRealServer(ServerFixture):
    def setUp(self):
        super().setUp()
        self.c = OpenCodeClient(self.base, timeout=5)

    def test_health_check(self):
        self.assertTrue(self.c.available())

    def test_delegate_creates_a_session_and_sends_the_brief(self):
        b = build_brief("fix the failing login test in src/auth/login.ts",
                        repo="vicebase")
        r = self.c.delegate(b)
        self.assertTrue(r.ok, r.error)
        self.assertEqual(r.session_id, "sess-42")
        self.assertIn("login", r.summary.lower())
        self.assertEqual(r.files_changed,
                         ["src/auth/login.ts", "src/auth/login.test.ts"])
        paths = [p for p, _ in FakeOpenCode.received]
        self.assertEqual(paths, ["/session", "/session/sess-42/message"])
        sent = FakeOpenCode.received[1][1]["parts"][0]["text"]
        self.assertIn("# Task", sent)
        self.assertIn("vicebase", sent)

    def test_incomplete_brief_is_never_sent(self):
        r = self.c.delegate(build_brief("kar do", repo="vicebase"))
        self.assertFalse(r.ok)
        self.assertIn("incomplete", r.error)
        self.assertEqual(FakeOpenCode.received, [],
                         "a vague brief reached the agent")

    def test_server_error_is_returned_not_raised(self):
        FakeOpenCode.mode = "boom"
        r = self.c.delegate(build_brief("fix the login test in a.ts",
                                        repo="vicebase"))
        self.assertFalse(r.ok)
        self.assertTrue(r.error)

    def test_unreachable_server_is_handled(self):
        dead = OpenCodeClient("http://127.0.0.1:1", timeout=2)
        self.assertFalse(dead.available())
        r = dead.delegate(build_brief("fix the login test in a.ts", repo="r"))
        self.assertFalse(r.ok)
        self.assertIn("unreachable", r.error.lower())

    def test_agent_output_is_tainted(self):
        """A compromised or confused agent must not be able to drive tools."""
        r = self.c.delegate(build_brief("fix the login test in a.ts",
                                        repo="vicebase"))
        self.assertTrue(is_tainted(r.as_context()))
        self.assertEqual(r.as_context().source, "agent:opencode")

    def test_agent_output_cannot_execute_an_action(self):
        from pai.gateway import Action, Gateway, Verdict
        from pai.trust import Trust
        r = self.c.delegate(build_brief("fix the login test in a.ts",
                                        repo="vicebase"))
        d = Gateway().submit(Action("shell.run", {"cmd": r.as_context()}),
                             Trust.USER)
        self.assertIs(d.verdict, Verdict.DENY)


if __name__ == "__main__":
    unittest.main(verbosity=2)
