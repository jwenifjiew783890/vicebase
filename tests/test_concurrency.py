"""Things that only break when two threads do them at once.

Every one of these was found by running the application, and none of them
is reachable from a single-threaded unit test. The application server
answers on a threadpool and runs background jobs, so "works when called
once" is not the property that matters.
"""
import os
import sys
import threading
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTheModelBackendIsSerialised(unittest.TestCase):
    """The crash that took the whole process down.

    Background jobs call the model on worker threads while the conversation
    handler calls it on another. llama.cpp keeps mutable decode state on the
    context and is not re-entrant. Two threads inside one context did not
    raise -- the process died:

        traps: python3[13757] trap divide error ... in libc.so.6

    A SIGFPE from native code, no Python traceback, the server simply gone.
    A lock at LlamaBackend.chat covers every caller.
    """

    def test_chat_holds_a_lock_for_the_whole_generation(self):
        from vision.core.llm import LlamaBackend

        overlaps = []
        inside = threading.Event()

        class Fake(LlamaBackend):
            def __init__(self):                     # no weights needed
                self._lock = threading.RLock()
                self.model_path = "fake"
                self.busy = False

            def _chat(self, messages, **kw):
                # If the lock works, no second thread is ever in here.
                overlaps.append(self.busy)
                self.busy = True
                inside.set()
                import time as _t
                _t.sleep(0.05)
                self.busy = False
                from vision.core.llm import GenStats
                return "ok", GenStats()

        b = Fake()
        threads = [threading.Thread(target=lambda: b.chat([{"role": "user",
                                                            "content": "hi"}]))
                   for _ in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(overlaps, [False] * 6,
                         "two threads were inside the model at once")

    def test_every_model_path_goes_through_chat(self):
        """ANTI-FALSE-GREEN: the lock is worthless if a caller bypasses it.

        Both adapters and the raw completion helper must call
        backend.chat() rather than backend.llm directly.
        """
        import inspect
        from vision.core import llm as mod
        src = inspect.getsource(mod)
        # The only place the raw llama object may be touched is inside
        # _chat and the constructor.
        for cls in ("LlamaConversation", "LlamaPlanner"):
            body = inspect.getsource(getattr(mod, cls))
            self.assertNotIn(".llm.create_chat_completion", body,
                             f"{cls} bypasses the lock")
        import vision.assistant as va
        self.assertIn("self.backend.chat(", inspect.getsource(va.Vision._raw_llm))


class TestTheStoreIsSerialised(unittest.TestCase):
    def test_many_threads_can_write_turns(self):
        from vision.core.memory import MemoryStore
        from vision.core.trust import Trust
        path = os.path.join(tempfile.mkdtemp(), "c.db")
        store = MemoryStore(path)
        errors = []

        def w(i):
            try:
                for k in range(5):
                    store.add_turn(f"s{i}", "user", f"{i}-{k}", Trust.USER)
            except Exception as exc:                # pragma: no cover
                errors.append(exc)

        ts = [threading.Thread(target=w, args=(i,)) for i in range(6)]
        for t in ts: t.start()
        for t in ts: t.join()
        self.assertEqual(errors, [])
        self.assertEqual(
            list(store.db.execute("SELECT COUNT(*) c FROM turns"))[0]["c"], 30)


class TestJobsSurviveARestart(unittest.TestCase):
    def test_running_jobs_are_marked_interrupted_not_left_running(self):
        """A job row still saying "running" after a restart is a lie: the
        thread that owned it died with the process."""
        from vision.jobs import JobStore
        path = os.path.join(tempfile.mkdtemp(), "j.db")
        s1 = JobStore(path, lambda a, t, j: {"ok": True, "summary": "x"})
        s1.db.execute(
            "INSERT INTO jobs(id,created_at,updated_at,session_id,agent,"
            "request,status,progress,log_json,result_json) "
            "VALUES ('zz',1,1,'s','research','x','running','',NULL,NULL)")
        s1.db.commit()
        s2 = JobStore(path, lambda a, t, j: {"ok": True, "summary": "x"})
        row = s2.get("zz")
        self.assertEqual(row["status"], "failed")
        self.assertIn("restart", row["progress"])


if __name__ == "__main__":
    unittest.main()
