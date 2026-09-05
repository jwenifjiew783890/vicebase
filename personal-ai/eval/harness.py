"""Evaluation harness.

Runs every scenario whose expectation is deterministic and reports per
category. Scenarios needing a model judge are counted and skipped, so the
report never overstates what was actually verified.

Usage:  python3 eval/harness.py [-v]
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "eval", "data"))

from pai.router import Router, RouteConfig, Path
from pai.gateway import (Gateway, Action, Verdict, Channel, Tainted, REGISTRY)
from pai.trust import Trust
from pai.signals import detect, detect_language
from pai.obsidian import VaultIndex, TfidfEmbedder, Hit
from scenarios import SCENARIOS
from injection_corpus import INJECTIONS

INJ = {i: p for i, p, _ in INJECTIONS}


# A small vault so obsidian/personal scenarios have something to hit.
VAULT = {
    "Projects/ViceBase.md": """# ViceBase
## Auth decisions
We moved from passwords to passkeys. Internal codename Thornbury.
See [[Passkey Rollout]].
## Deployment
Deploys run through Vercel on merge to main. Staging first.
""",
    "Projects/Passkey Rollout.md": "# Passkey Rollout\n\nPhase 1 March. Phase 2 mobile.\n",
    "Notes/Thesis.md": "# Thesis\n\nChapter 3 covers retrieval evaluation.\n",
    "Projects/Auth Spec.md": """# Auth Spec
## Account recovery
Recovery uses a verified email link plus a 24 hour cooldown. The spec says
recovery codes are single use.
## Session handling
Sessions expire after 14 days of inactivity.
""",
}


def build_vault():
    idx = VaultIndex(TfidfEmbedder())
    for p, t in VAULT.items():
        idx.add_note(p, t)
    idx.build_vectors()
    return idx


class Result:
    def __init__(self):
        self.rows = []       # (scenario_id, category, check, ok, detail)

    def add(self, sid, cat, check, ok, detail=""):
        self.rows.append((sid, cat, check, ok, detail))

    @property
    def failures(self):
        return [r for r in self.rows if not r[3]]

    def report(self, verbose=False):
        by_cat = defaultdict(lambda: [0, 0])
        for _, cat, _, ok, _ in self.rows:
            by_cat[cat][1] += 1
            by_cat[cat][0] += bool(ok)
        total_ok = sum(v[0] for v in by_cat.values())
        total = sum(v[1] for v in by_cat.values())

        print(f"\n{'CATEGORY':22} {'PASS':>6} {'TOTAL':>6}  RATE")
        print("-" * 48)
        for cat in sorted(by_cat):
            ok, n = by_cat[cat]
            flag = "" if ok == n else "   <-- failures"
            print(f"{cat:22} {ok:6} {n:6}  {ok/n:5.0%}{flag}")
        print("-" * 48)
        print(f"{'TOTAL':22} {total_ok:6} {total:6}  {total_ok/max(1,total):5.0%}")

        if self.failures:
            print(f"\n{len(self.failures)} FAILING CHECKS:")
            for sid, cat, check, _, detail in self.failures:
                print(f"  [{cat}/{sid}] {check}: {detail}")
        return total_ok, total


def run(verbose=False) -> Result:
    res = Result()
    vault = build_vault()
    gw = Gateway()
    judged = 0

    for sc in SCENARIOS:
        sid, cat, turns, exp = sc["id"], sc["category"], sc["turns"], sc["expect"]
        if exp.get("judge"):
            judged += 1
            continue
        text = turns[-1]

        # --- language
        if "lang" in exp:
            got = detect_language(text)
            res.add(sid, cat, "lang", got == exp["lang"],
                    f"got {got!r}, expected {exp['lang']!r} for {text!r}")

        # --- signal detection
        if "signal" in exp:
            got = [d.signal.value for d in detect(text)]
            want = exp["signal"]
            ok = (want is None and not got) or (want is not None and want in got)
            res.add(sid, cat, "signal", ok,
                    f"got {got or 'NONE'}, expected {want or 'NONE'} for {text!r}")

        # --- routing
        if "path" in exp or "delegate" in exp or "not_path" in exp:
            router = Router()
            hits = vault.search(text, k=4, expand_links=False)
            r = router.route(text, hits)
            if "path" in exp:
                res.add(sid, cat, "path", r.path.value == exp["path"],
                        f"got {r.path.value!r}, expected {exp['path']!r} "
                        f"({r.why()}) for {text!r}")
            if "not_path" in exp:
                res.add(sid, cat, "not_path", r.path.value != exp["not_path"],
                        f"got {r.path.value!r}, must not be {exp['not_path']!r} "
                        f"({r.why()}) for {text!r}")
            if "delegate" in exp:
                res.add(sid, cat, "delegate", r.delegate == exp["delegate"],
                        f"got delegate={r.delegate}, expected {exp['delegate']} "
                        f"for {text!r}")
            if "retract" in exp:
                res.add(sid, cat, "retract", r.retract == exp["retract"],
                        f"got retract={r.retract}, expected {exp['retract']} "
                        f"for {text!r}")
            if "vault_forced" in exp:
                res.add(sid, cat, "vault_forced",
                        r.vault_forced == exp["vault_forced"],
                        f"got vault_forced={r.vault_forced}, expected "
                        f"{exp['vault_forced']} for {text!r}")
            if "ack" in exp:
                got = bool(r.ack_text)
                res.add(sid, cat, "ack", got == exp["ack"],
                        f"got ack={r.ack_text!r}, expected "
                        f"{'an ack' if exp['ack'] else 'no ack'} for {text!r}")

        # --- vault relevance for personal queries
        if exp.get("personal"):
            hits = vault.search(text, k=4, expand_links=False)
            r = Router().route(text, hits)
            want_inject = not exp.get("expect_no_inject")
            got = bool(r.inject)
            res.add(sid, cat, "vault_injected", got == want_inject,
                    f"inject={got}, expected {want_inject} for {text!r} "
                    f"(dense={max((h.dense_raw for h in hits), default=0):.2f} "
                    f"bm25={max((h.bm25_raw for h in hits), default=0):.2f})")

        # --- gateway verdicts
        if "cap" in exp and "verdict" in exp:
            cap = exp["cap"]
            args = exp.get("args") or _default_args(cap)
            ch = Channel.VOICE if exp.get("channel") == "voice" else Channel.TEXT
            d = gw.submit(Action(cap, args), Trust.USER, ch)
            res.add(sid, cat, "verdict", d.verdict.name == exp["verdict"],
                    f"got {d.verdict.name}, expected {exp['verdict']} "
                    f"({d.why}) for {cap}{args}")

        # --- injection: content reaches the gateway, must never execute
        if "injected" in exp:
            payload = INJ[exp["injected"]]
            worst = []
            for name, args in [
                ("shell.run", {"cmd": Tainted(payload, "web")}),
                ("file.delete", {"path": Tainted(payload, "vault")}),
                ("message.send", {"to": Tainted("x@y", "web"),
                                  "body": Tainted(payload, "web")}),
            ]:
                d = gw.submit(Action(name, args, reason=Tainted(payload, "web")),
                              Trust.USER)
                if d.verdict is not Verdict.DENY:
                    worst.append(f"{name}->{d.verdict.name}")
            res.add(sid, cat, "injection_denied", not worst,
                    f"payload {exp['injected']} produced {worst}")

        # --- acknowledgement discipline
        if exp.get("ack_required"):
            router = Router()
            r = router.route(text, vault.search(text, k=4, expand_links=False))
            res.add(sid, cat, "ack", r.needs_ack and bool(r.ack_text),
                    f"expected an acknowledgement for {text!r}, got "
                    f"needs_ack={r.needs_ack}")
        if exp.get("ack_varies"):
            router = Router()
            acks = []
            for i, t in enumerate(turns):
                r = router.route(t, vault.search(t, k=4, expand_links=False),
                                 turn_index=i)
                if r.ack_text:
                    acks.append(r.ack_text)
            res.add(sid, cat, "ack_varies", len(set(acks)) == len(acks),
                    f"acknowledgement repeated verbatim: {acks}")

    res.judged = judged
    return res


def _default_args(cap: str) -> dict:
    spec = REGISTRY[cap]
    filler = {str: "x", int: 1, list: []}
    return {k: filler[spec.schema[k]] for k in spec.required}


if __name__ == "__main__":
    r = run(verbose="-v" in sys.argv)
    ok, total = r.report()
    print(f"\n{r.judged} scenarios require a model judge (not run here).")
    sys.exit(1 if r.failures else 0)
