"""Mutation audit: prove the tests actually exercise their failure modes.

A passing test is not evidence. A test that still passes when you delete
the thing it claims to protect is a FALSE GREEN, and it is worse than no
test because it buys unearned confidence.

For each defense, this applies a mutation that disables it, runs the suite,
and requires that at least one test FAILS. A mutation that everything
survives names an untested defense.

Run:  python3 eval/mutation_audit.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


# The suite MUST run in a fresh interpreter for each mutation.
#
# The first version of this audit ran it in-process, popping pai.* out of
# sys.modules between runs. That produced a spectacular false green: the
# audit reported 25/25 mutations killed, and every single one was "killed"
# by the same four failures. Those failures had nothing to do with the
# mutations -- popping the modules left the already-imported test modules
# holding references to the OLD enum classes, so assertIs(status,
# ExecStatus.OK) compared two distinct ExecStatus types and failed on every
# run after the first.
#
# An audit tool that cannot tell a real kill from its own reload bug is
# worse than no audit. Subprocesses are slower and correct.
def run_suite() -> tuple[int, list[str]]:
    """Run the full suite in a clean subprocess. Returns (failures, names)."""
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
        cwd=ROOT, capture_output=True, text=True, timeout=300)
    out = proc.stdout + proc.stderr
    names = re.findall(r"^(?:FAIL|ERROR): (\w+)", out, re.MULTILINE)
    m = re.search(r"failures=(\d+)", out)
    e = re.search(r"errors=(\d+)", out)
    total = (int(m.group(1)) if m else 0) + (int(e.group(1)) if e else 0)
    if "OK" in out.splitlines()[-1:] and total == 0:
        return 0, []
    return total or (0 if proc.returncode == 0 else 1), names


# (label, file, find, replace) -- each disables one defense.
MUTATIONS = [
    ("trust: retrieved content may write memory", "pai/trust.py",
     "        return self >= Trust.USER\n\n    @property\n    def may_emit_action",
     "        return True\n\n    @property\n    def may_emit_action"),

    ("trust: retrieved content may emit actions", "pai/trust.py",
     '        """Only a user request can cause an action to be considered.',
     '        return True  # MUTANT\n        """Only a user request can cause an action to be considered.'),

    ("gateway: taint check removed", "pai/gateway.py",
     "        tainted_args = [k for k, v in action.args.items() if is_tainted(v)]",
     "        tainted_args = []  # MUTANT"),

    ("gateway: voice rule removed", "pai/gateway.py",
     "        if channel is Channel.VOICE and cap.tier >= Tier.IRREVERSIBLE:",
     "        if False and channel is Channel.VOICE:  # MUTANT"),

    ("gateway: schema validation removed", "pai/gateway.py",
     "        missing = [k for k in cap.required if k not in action.args]",
     "        missing = []  # MUTANT"),

    ("gateway: app allowlist removed", "pai/gateway.py",
     "            if app not in self.app_allowlist:",
     "            if False:  # MUTANT"),

    ("gateway: shell allowlist removed", "pai/gateway.py",
     "            if cmd not in self.shell_allowlist:",
     "            if False:  # MUTANT"),

    ("gateway: typed confirmation accepts anything", "pai/gateway.py",
     "            if reply != TYPED_CONFIRM_PHRASE:",
     "            if False:  # MUTANT"),

    ("gateway: unimplemented tools return empty not error",
     "pai/orchestrator.py",
     '            raise NotImplementedError(\n                f"no handler registered for {action.name!r}")',
     "            return None  # MUTANT"),

    ("learning: evidence threshold ignored", "pai/learning.py",
     "            if n < self.cfg.evidence_threshold:\n                continue",
     "            pass  # MUTANT"),

    ("learning: one session can supply all evidence", "pai/memory.py",
     "CREATE UNIQUE INDEX IF NOT EXISTS idx_ev_unique ON rule_evidence(rule_id, session_id);",
     "-- MUTANT"),

    ("learning: sycophancy tripwire removed", "pai/learning.py",
     "        if SYCOPHANCY_PATTERNS.search(cand.text):",
     "        if False:  # MUTANT"),

    ("memory: protected rules can be archived", "pai/memory.py",
     '        if row["protected"] and status in ("archived", "rejected"):',
     "        if False:  # MUTANT"),

    ("memory: protected rules decay", "pai/memory.py",
     "            if rule.protected:\n                continue\n            age_days",
     "            age_days"),

    ("memory: rule cap not enforced", "pai/memory.py",
     "        if len(active) <= self.MAX_ACTIVE_RULES:\n            return evicted",
     "        return evicted  # MUTANT"),

    ("memory: facts overwritten instead of superseded", "pai/memory.py",
     '            self.db.execute(\n                "UPDATE facts SET valid_to=?, superseded_by=? WHERE id=?",',
     '            self.db.execute(\n                "UPDATE facts SET superseded_by=? WHERE id=? AND ?=?",'),

    ("router: general-knowledge short-circuit removed", "pai/router.py",
     "        if (GENERAL_KNOWLEDGE.match(user_text.strip())",
     "        if False and (GENERAL_KNOWLEDGE.match(user_text.strip())"),

    ("router: volatile fires on self-statements", "pai/router.py",
     "        volatile = (volatile_now and _is_information_request(user_text)\n"
     "                    and _has_searchable_subject(user_text))",
     "        volatile = volatile_now and _has_searchable_subject(user_text)"),

    ("router: injection gated on RRF score again", "pai/router.py",
     "        confident = [h for h in vault_hits\n                     if h.dense_raw >= self.cfg.min_dense\n                     or h.bm25_raw >= self.cfg.min_bm25]",
     "        confident = [h for h in vault_hits if h.score >= 0.02]  # MUTANT"),

    ("llm: reasoning trace no longer stripped", "pai/llm.py",
     '    out = _THINK.sub("", text)',
     "    out = text  # MUTANT"),

    ("llm: empty response fallback removed", "pai/llm.py",
     "        if not out:\n            from .signals import detect_language",
     "        if False:\n            from .signals import detect_language"),

    ("orchestrator: learned brevity no longer enforced", "pai/orchestrator.py",
     '        if params.get("max_sentences"):',
     "        if False:  # MUTANT"),

    ("orchestrator: annotations reach the model", "pai/orchestrator.py",
     "        rules = _second_person(self.learning.system_rules_block(lang=lang))",
     '        rules = _second_person(self.learning.system_rules_block(lang=lang)) + "\\n[test 999: leak]"'),

    ("signals: negation exclusions removed", "pai/signals.py",
     "    excluded = bool(NEGATION_EXCLUSIONS.search(text))",
     "    excluded = False  # MUTANT"),

    ("web: results no longer tainted", "pai/web.py",
     'source=f"web:{_host(self.url)}")',
     'source="trusted")  # MUTANT'),

    ("web: search time budget removed", "pai/web.py",
     "        if time.perf_counter() - t0 > TOTAL_BUDGET_S:",
     "        if False:  # MUTANT"),

    ("opencode: vague briefs are sent anyway", "pai/opencode.py",
     "        return bool(self.goal.strip()) and not self.missing",
     "        return True  # MUTANT"),

    ("opencode: dangling-reference check removed", "pai/opencode.py",
     "    if len(re.findall(r\"[\\w]+\", content)) < 1 and not brief.files_hint:",
     "    if False:  # MUTANT"),

    ("opencode: agent output no longer tainted", "pai/opencode.py",
     'return Tainted(self.summary, source="agent:opencode")',
     "return self.summary  # MUTANT"),

    ("orchestrator: post-hoc question strip removed", "pai/orchestrator.py",
     "                and res.text.rstrip().endswith(\"?\"):\n"
     "            res.text = strip_trailing_question(res.text)",
     "                and False:\n"
     "            res.text = strip_trailing_question(res.text)"),

    ("orchestrator: restraint mangles pure questions", "pai/orchestrator.py",
     "    if not words:\n        return text",
     "    if False:\n        return text"),

    ("router: lexical overlap gate removed", "pai/router.py",
     "        if self.cfg.require_lexical_overlap:",
     "        if False:  # MUTANT"),

    ("router: overlap gate applied to strong hits too", "pai/router.py",
     "                         if h.dense_raw >= self.cfg.strong_dense\n                         or h.bm25_raw >= self.cfg.strong_bm25\n                         or _shares_content_word(user_text, h)]",
     "                         if _shares_content_word(user_text, h)]"),

    ("voice: endpointing ignores incomplete tails", "pai/voice.py",
     "        if _INCOMPLETE_TAIL.search(text.strip()):",
     "        if False:  # MUTANT"),

    ("voice: clause chunking disabled", "pai/voice.py",
     "        if len(buf) >= min_chars:",
     "        if False:  # MUTANT"),

    ("voice: barge-in does not clear pending speech", "pai/voice.py",
     "        self.pending_chunks = []\n        self.state = TurnState.INTERRUPTED",
     "        self.state = TurnState.INTERRUPTED"),

    ("voice: voice identity varies by language", "pai/voice.py",
     'VOICE_BY_LANG = {"en": "primary_female", "hi": "primary_female",\n                 "hinglish": "primary_female"}',
     'VOICE_BY_LANG = {"en": "en_female", "hi": "hi_female",\n                 "hinglish": "mixed_female"}'),

    # ---- round 2: defences added after the mandatory conversation set ----

    ("router: retraction no longer detected", "pai/router.py",
     "        if RETRACTION.search(user_text):",
     "        if False and RETRACTION.search(user_text):"),

    ("orchestrator: retraction cancels nothing", "pai/orchestrator.py",
     "        pending = self._pending.pop(session_id, [])",
     "        pending = []  # MUTANT"),

    ("orchestrator: bare retraction goes back to the model",
     "pai/orchestrator.py",
     "            if route.path is Path.FAST and _is_bare_retraction(user_text):",
     "            if False and _is_bare_retraction(user_text):"),

    ("router: explicit vault command ignored", "pai/router.py",
     "        if forced_vault:\n            r.vault_forced = True",
     "        if False:\n            r.vault_forced = True"),

    ("router: back-references may become web queries", "pai/router.py",
     "        volatile = (volatile_now and _is_information_request(user_text)\n"
     "                    and _has_searchable_subject(user_text))",
     "        volatile = volatile_now and _is_information_request(user_text)"),

    ("router: ack promised for an unstartable delegation", "pai/router.py",
     "            r.delegate_ready = build_brief(user_text).is_actionable",
     "            r.delegate_ready = True  # MUTANT"),

    ("signals: bare fillers count as English again", "pai/signals.py",
     "    if not has_deva and hi_hits == 0 and en_hits == 0:",
     "    if False:"),

    ("orchestrator: web route dispatches nothing (F24 regression)",
     "pai/orchestrator.py",
     "        if route.needs_web:\n            t_w = time.perf_counter()",
     "        if False:\n            t_w = time.perf_counter()"),

    ("orchestrator: empty-retrieval directive removed", "pai/orchestrator.py",
     "        if res.evidence == 0:\n            if route.needs_web:",
     "        if False:\n            if route.needs_web:"),

    ("orchestrator: fabricated source claims allowed through",
     "pai/orchestrator.py",
     "        if res.evidence == 0 and SOURCE_CLAIM.search(res.text):",
     "        if False:"),

    ("orchestrator: claimed-but-unrun actions allowed through",
     "pai/orchestrator.py",
     "                and ACTION_CLAIM.search(res.text) \\",
     "                and False \\"),

    # NOTE, and it is the point of the whole tool: the first version of
    # this mutation was `res.text = res.text` -- a no-op. It "survived",
    # and the audit correctly reported a survivor, because nothing can
    # detect a change that was never made. An ineffective mutation is
    # indistinguishable from an untested defence, so the audit's report was
    # right and my mutation was wrong. This one actually writes the
    # unguarded reply to the store first.
    ("orchestrator: the fabricated reply is what reaches memory",
     "pai/orchestrator.py",
     "        # NOTE: the assistant turn is NOT written here.",
     "        self.store.add_turn(session_id, \"assistant\", res.text,\n"
     "                            Trust.MODEL, lang=route.lang)  # MUTANT\n"
     "        # NOTE: the assistant turn is NOT written here."),

    ("llm: planner accepts only arrays again (F26 regression)", "pai/llm.py",
     "        if not items:\n            items = _json_objects(text)",
     "        if False:\n            items = _json_objects(text)"),

    ("llm: flattened planner args no longer lifted", "pai/llm.py",
     "                if k not in (\"action\", \"args\") and k not in args:",
     "                if False:"),

    ("opencode: only the first repo candidate is considered",
     "pai/opencode.py",
     "        for pattern in (_REPO_NAMED, _REPO_HINT):",
     "        for pattern in (_REPO_HINT,):  # MUTANT"),

    ("orchestrator: pre-generation question restraint removed",
     "pai/orchestrator.py",
     "            system += \"\\n\\n\" + QUESTION_RESTRAINT",
     "            pass  # MUTANT"),

    ("orchestrator: question runs counted globally, not per session",
     "pai/orchestrator.py",
     "        self._recent_questions[session_id] = (\n"
     "            self._recent_questions.get(session_id, 0) + 1",
     "        self._recent_questions[\"GLOBAL\"] = (\n"
     "            self._recent_questions.get(session_id, 0) + 1"),

    ("orchestrator: source claims allowed on the fast path",
     "pai/orchestrator.py",
     "        if res.evidence == 0 and SOURCE_CLAIM.search(res.text):",
     "        if route.needs_web and SOURCE_CLAIM.search(res.text):"),

    ("obsidian: user text passed raw to FTS MATCH", "pai/obsidian.py",
     '    toks = [t for t in _tok(query) if len(t) > 1]\n    return " OR ".join(f\'"{t}"\' for t in toks)',
     "    return query  # MUTANT"),
]


def _tree_is_clean() -> bool:
    """Refuse to start on a tree that already carries a mutation.

    A `finally` does not run when the process is killed. An audit
    terminated mid-mutation once left `pai/llm.py` on disk with the empty
    response fallback replaced by `if False:` -- a silently disabled
    defence in a tree that otherwise looked fine. The next run would then
    have audited the wrong code and reported a survivor as a kill.
    """
    proc = subprocess.run(["git", "diff", "--name-only", "--", "pai"],
                          cwd=ROOT, capture_output=True, text=True)
    dirty = [f for f in proc.stdout.split() if f.endswith(".py")]
    if dirty:
        print("working tree has uncommitted changes under pai/:")
        for f in dirty:
            print("   ", f)
        print("That is fine for ordinary work, but this audit rewrites those\n"
              "same files, so a crash would leave you unable to tell your\n"
              "edits from a mutation. Commit or stash first.")
        return False
    return True


def main():
    if "--force" not in sys.argv and not _tree_is_clean():
        return 2
    base_fails, base_names = run_suite()
    print(f"baseline: {base_fails} failures\n")
    if base_fails:
        print("  suite is not green; fix before auditing:", base_names[:5])
        return 1

    survived, killed = [], []
    for label, relpath, find, repl in MUTATIONS:
        path = os.path.join(ROOT, relpath)
        original = open(path).read()
        if find not in original:
            print(f"  SKIP  {label}\n        (anchor not found in {relpath})")
            survived.append((label, "anchor missing"))
            continue
        # Breadcrumb: if the process dies between these two writes, this
        # file is what tells the next run (and the next reader) which
        # source file is currently mutated and how to put it back.
        crumb = os.path.join(ROOT, ".mutation-in-flight")
        try:
            with open(crumb, "w") as fh:
                fh.write(f"{relpath}\n{label}\n"
                         "restore with: git checkout -- " + relpath + "\n")
            open(path, "w").write(original.replace(find, repl, 1))
            n, names = run_suite()
        finally:
            open(path, "w").write(original)
            if os.path.exists(crumb):
                os.remove(crumb)
        if n > 0:
            killed.append((label, n, names[:2]))
            print(f"  KILLED  {label}\n          ({n} tests fail, e.g. {names[0]})")
        else:
            survived.append((label, "no test failed"))
            print(f"  SURVIVED  {label}   <-- FALSE GREEN: nothing tests this")

    print(f"\n{'='*70}")
    print(f"mutations killed by the suite : {len(killed)}/{len(MUTATIONS)}")
    print(f"mutations that SURVIVED       : {len(survived)}")
    for label, why in survived:
        print(f"   - {label}  ({why})")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
