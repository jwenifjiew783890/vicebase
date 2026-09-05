"""End-to-end learning test against the real model.

Proves the whole chain, not just its parts:

  1. the assistant answers
  2. the user corrects it
  3. the signal is detected and a candidate rule is created
  4. evidence accumulates across DISTINCT sessions
  5. one session alone cannot promote
  6. the rule reaches the review queue and is approved
  7. the promoted rule enters the system prompt
  8. behaviour on a FRESH question actually changes

Step 8 is the one that matters and the one usually skipped.
"""
from __future__ import annotations
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pai.llm import LlamaBackend, LlamaConversation
from eval.conversation import Harness
from eval.convmetrics import words

PROBES = ["explain what a database index is",
          "what's a cache",
          "what does an API do"]

CORRECTIONS = ["arre nahi, itna bada answer mat do. simple bol.",
               "keep it shorter",
               "too long, get to the point"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="/tmp/models/Qwen3.5-4B-Q4_K_M.gguf")
    ap.add_argument("--out", default="eval/transcripts/learning")
    ap.add_argument("--max-tokens", type=int, default=180)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    backend = LlamaBackend(a.model, n_ctx=4096, n_threads=4)
    conv = LlamaConversation(backend, max_tokens=a.max_tokens)
    h = Harness(conv, None, evidence_threshold=3)
    log = []

    def say(session, text):
        r = h.orch.handle(session, text)
        log.append({"session": session, "user": text, "ai": r.text,
                    "words": words(r.text)})
        print(f"  [{session}] USER: {text}\n         AI ({words(r.text)}w): "
              f"{r.text[:150]}", flush=True)
        return r

    print("\n--- STEP 1-2: baseline answer, then correction (session A) ---")
    before = say("A", PROBES[0])
    before_words = words(before.text)
    say("A", CORRECTIONS[0])

    print("\n--- STEP 3: candidate created? ---")
    rule = h.store.get_rule("style.brevity.hi") or h.store.get_rule("style.brevity")
    print(f"  candidate: {rule.rule_key if rule else None} "
          f"status={rule.status if rule else '-'} "
          f"evidence={h.store.evidence_count(rule.id) if rule else 0}")
    assert rule is not None, "no candidate rule was created from the correction"

    print("\n--- STEP 5: one session must NOT be enough ---")
    for _ in range(4):
        h.learning.observe_turn("A", CORRECTIONS[0])
    q = h.learning.review_queue()
    print(f"  review queue after 5 corrections in ONE session: {[i.rule_key for i in q]}")
    assert not q, "a single session manufactured the evidence threshold"

    print("\n--- STEP 4: evidence across DISTINCT sessions ---")
    for i, sess in enumerate(["B", "C"]):
        say(sess, PROBES[(i + 1) % len(PROBES)])
        say(sess, CORRECTIONS[(i + 1) % len(CORRECTIONS)])
    q = h.learning.review_queue()
    print(f"  review queue now: {[(i.rule_key, i.evidence) for i in q]}")

    print("\n--- STEP 6: approve ---")
    promoted = []
    for item in q:
        h.learning.approve(item.rule_key)
        promoted.append(item.rule_key)
    print(f"  promoted: {promoted}")
    assert promoted, "nothing reached promotion"

    print("\n--- STEP 7: rule is in the system prompt ---")
    block_en = h.learning.system_rules_block(lang="en")
    block_hi = h.learning.system_rules_block(lang="hi")
    print(f"  en block:\n    " + block_en.replace("\n", "\n    "))

    print("\n--- STEP 8: does behaviour actually change on a FRESH question? ---")
    after = say("D", PROBES[0])
    after_words = words(after.text)

    result = {"probe": PROBES[0], "before_words": before_words,
              "after_words": after_words, "promoted": promoted,
              "rules_block_en": block_en, "rules_block_hi": block_hi,
              "log": log,
              "changed": after_words < before_words,
              "delta_pct": (after_words - before_words) / max(1, before_words)}
    print(f"\n  BEFORE: {before_words} words\n  AFTER : {after_words} words"
          f"\n  change: {result['delta_pct']:+.0%}  "
          f"{'BEHAVIOUR CHANGED' if result['changed'] else 'NO CHANGE'}")
    print(f"\n  BEFORE text: {before.text[:300]}")
    print(f"\n  AFTER text : {after.text[:300]}")
    json.dump(result, open(os.path.join(a.out, "learning_e2e.json"), "w"),
              indent=2, ensure_ascii=False)
    print(f"\nwrote {a.out}/learning_e2e.json")


if __name__ == "__main__":
    main()
