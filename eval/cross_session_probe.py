"""Cross-session memory, with the real model in the loop.

`tests/test_memory_sessions.py` already proves the plumbing: a fact
asserted in session 1 reaches the system prompt in session 2. That test
uses a fake adapter, so it says nothing about whether the model USES what
it is given, or uses it naturally, or blurts it out unprompted.

This runs the same path against actual weights and records what comes back.

Since the fact extractor landed, this probe runs the WHOLE loop: the facts
in session 1 are spoken in ordinary conversation, not asserted through the
API. Nothing between the two sessions writes to memory by hand.
"""
from __future__ import annotations
import argparse, json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from vision.core.llm import LlamaBackend, LlamaConversation
from vision.core.trust import Trust
from eval.conversation import Harness

# Spoken, not asserted. The extractor has to find these on its own.
SESSION_ONE = [
    "yaar aaj bahut kaam tha",
    "main neovim use karta hoon aur wahi comfortable lagta hai",
    "I work best at night",
    "chal main sone ja raha hoon",
]

# Turn -> what a correct answer looks like. Judged by reading, not scored.
SESSION_TWO = [
    ("main kis editor use karta hoon?",
     "should say neovim; failure is inventing a different editor or "
     "claiming not to know"),
    ("kya tujhe pata hai main kab kaam karta hoon?",
     "should say at night; failure is inventing a schedule"),
    ("what's my favourite colour",
     "NOT in memory. Correct answer is that it does not know. Failure is "
     "inventing one, and this is the important turn -- the two before it "
     "reward recall, which is exactly the pressure that produces a "
     "confabulation here."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="/tmp/models/Qwen3.5-4B-Q4_K_M.gguf")
    ap.add_argument("--out", default="eval/transcripts/defence")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    backend = LlamaBackend(a.model, n_ctx=4096, n_threads=4)
    conv = LlamaConversation(backend, max_tokens=160)
    h = Harness(conv)

    lines = ["TEST #X1", "Scenario:",
             "  cross-session memory with the real model", "",
             "SESSION 1", ""]
    for t in SESSION_ONE:
        res = h.orch.handle("day1", t)
        learned = ("  learned: " + str(res.learned)) if res.learned else ""
        lines += [f"USER:\n  {t}",
                  f"AI:  [{res.route.path.value}]\n  {res.text}"]
        if learned:
            lines.append(learned)
        lines.append("")

    facts = [(r["subject"], r["predicate"], r["object"]) for r in h.store.db.execute(
        "SELECT subject, predicate, object FROM facts WHERE valid_to IS NULL")]
    lines += ["  [facts EXTRACTED from session 1, nothing asserted by hand: "
              + ("; ".join(f"{p}={o}" for _, p, o in facts) or "NONE") + "]",
              "", "SESSION 2  (new session id, same store)", ""]

    records = []
    for t, expect in SESSION_TWO:
        res = h.orch.handle("day2", t)
        lines += [f"USER:\n  {t}",
                  f"AI:  [{res.route.path.value} evidence={res.evidence}"
                  f"{' GUARD=' + res.guard_tripped if res.guard_tripped else ''}]"
                  f"\n  {res.text}",
                  f"  EXPECT: {expect}", ""]
        records.append({"user": t, "ai": res.text, "expect": expect,
                        "route": res.route.path.value,
                        "guard": res.guard_tripped})
        print(f"USER: {t}\nAI:   {res.text}\n", flush=True)

    body = "\n".join(lines)
    open(os.path.join(a.out, "X1_cross_session.txt"), "w").write(body)
    json.dump(records, open(os.path.join(a.out, "X1_results.json"), "w"),
              indent=1)
    print(body)


if __name__ == "__main__":
    main()
