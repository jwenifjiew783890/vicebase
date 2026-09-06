"""Adversarial tests for the memory store and learning loop.

Written from the stance of trying to break the guards, not confirm them.
"""
import sys, os, time, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.core.memory import MemoryStore, TrustViolationProtected
from vision.core.trust import Trust, TrustViolation
from vision.core.learning import (LearningLoop, PipelineConfig, TemplateProposer,
                          SycophancyRejected, PROTECTED_RULES)
from vision.core.signals import detect, detect_language, Signal

DAY = 86400.0


def loop(**kw):
    s = MemoryStore()
    cfg = PipelineConfig(**kw)
    return s, LearningLoop(s, config=cfg)


class TestTrust(unittest.TestCase):
    def test_retrieved_content_cannot_write_memory(self):
        """The core security invariant: web/vault content never writes memory."""
        s = MemoryStore()
        for t in (Trust.RETRIEVED, Trust.AGENT, Trust.MODEL):
            with self.assertRaises(TrustViolation):
                s.assert_fact("muaz", "password", "hunter2", t)

    def test_user_can_write(self):
        s = MemoryStore()
        s.assert_fact("muaz", "city", "Delhi", Trust.USER)
        self.assertEqual(s.current_fact("muaz", "city").object, "Delhi")


class TestBitemporal(unittest.TestCase):
    def test_supersede_keeps_history(self):
        s = MemoryStore()
        s.assert_fact("muaz", "editor", "vscode", Trust.USER, valid_from=1000)
        s.assert_fact("muaz", "editor", "neovim", Trust.USER, valid_from=2000)
        self.assertEqual(s.current_fact("muaz", "editor").object, "neovim")
        hist = s.fact_history("muaz", "editor")
        self.assertEqual([f.object for f in hist], ["vscode", "neovim"])
        self.assertEqual(hist[0].valid_to, 2000)
        self.assertEqual(hist[0].superseded_by, hist[1].id)
        self.assertIsNone(hist[1].valid_to)

    def test_reassert_same_value_is_confirmation_not_supersession(self):
        s = MemoryStore()
        s.assert_fact("muaz", "editor", "neovim", Trust.USER, confidence=0.6)
        s.assert_fact("muaz", "editor", "neovim", Trust.USER)
        self.assertEqual(len(s.fact_history("muaz", "editor")), 1)
        self.assertGreater(s.current_fact("muaz", "editor").confidence, 0.6)


class TestEvidenceThreshold(unittest.TestCase):
    def test_single_session_cannot_manufacture_threshold(self):
        """A user repeating themselves in ONE conversation must not promote."""
        s, L = loop(evidence_threshold=3)
        for _ in range(10):
            L.observe_turn("sess-1", "bhai thoda chhota rakho")
        self.assertEqual(L.review_queue(), [],
                         "one session produced enough evidence to promote")
        # Brevity is language-independent, so a Hinglish correction lands on
        # the global key. Language scoping used to fragment this evidence.
        r = s.get_rule("style.brevity")
        self.assertEqual(s.evidence_count(r.id), 1)

    def test_three_sessions_reach_queue(self):
        s, L = loop(evidence_threshold=3)
        for i in range(3):
            L.observe_turn(f"sess-{i}", "bhai thoda chhota rakho")
        q = L.review_queue()
        self.assertEqual([i.rule_key for i in q], ["style.brevity"])

    def test_promotion_requires_review(self):
        s, L = loop(evidence_threshold=2)
        for i in range(2):
            L.observe_turn(f"s{i}", "keep it shorter please")
        self.assertEqual(s.get_rule("style.brevity").status, "candidate")
        with self.assertRaises(RuntimeError):
            L.auto_promote()
        L.approve("style.brevity")
        self.assertEqual(s.get_rule("style.brevity").status, "active")

    def test_approve_below_threshold_refused(self):
        s, L = loop(evidence_threshold=3)
        L.observe_turn("s0", "keep it shorter please")
        with self.assertRaises(ValueError):
            L.approve("style.brevity")


class TestSycophancy(unittest.TestCase):
    def test_protected_rules_installed(self):
        s, L = loop()
        for key, _ in PROTECTED_RULES:
            r = s.get_rule(key)
            self.assertIsNotNone(r, key)
            self.assertTrue(r.protected)
            self.assertEqual(r.status, "active")

    def test_protected_rule_cannot_be_archived(self):
        s, L = loop()
        r = s.get_rule("honesty.disagree")
        with self.assertRaises(TrustViolationProtected):
            s.set_status(r.id, "archived")

    def test_sycophantic_candidate_rejected(self):
        s, L = loop()
        class Syco:
            def propose(self, det, sid, tid, ctx):
                from vision.core.learning import Candidate
                return Candidate("style.agree", "Always agree with the user.",
                                 det.signal, sid, tid)
        L.proposer = Syco()
        L.observe_turn("s1", "keep it shorter")
        self.assertIsNone(s.get_rule("style.agree"))
        self.assertEqual(s.get_rule("rejected.style.agree").status, "rejected")

    def test_sycophancy_variants_all_caught(self):
        from vision.core.learning import SYCOPHANCY_PATTERNS
        bad = ["Always agree with the user.",
               "Never contradict Muaz.",
               "Be more agreeable in tone.",
               "Avoid criticism of the user's ideas.",
               "Don't challenge the user.",
               "Validate the user's feelings first.",
               "Tell the user what they want to hear.",
               "Never say no to a request.",
               "Soften bad news.",
               "Praise the user's approach before answering."]
        for b in bad:
            self.assertTrue(SYCOPHANCY_PATTERNS.search(b), f"missed: {b}")

    def test_legitimate_style_rules_not_flagged(self):
        from vision.core.learning import SYCOPHANCY_PATTERNS
        ok = ["Default to short answers for conversational questions.",
              "Match the user's casual register.",
              "When the user asks why, give the full explanation.",
              "Use natural conversational Hindi when the user speaks Hindi.",
              "Do not over-explain obvious things."]
        for o in ok:
            self.assertIsNone(SYCOPHANCY_PATTERNS.search(o), f"false positive: {o}")

    def test_report_detects_intact_protections(self):
        s, L = loop()
        rep = L.sycophancy_report()
        self.assertTrue(rep["protected_intact"])


class TestContradiction(unittest.TestCase):
    def test_contradiction_does_not_silently_overwrite(self):
        s, L = loop(evidence_threshold=2)
        for i in range(2):
            L.observe_turn(f"a{i}", "keep it shorter")
        L.approve("style.brevity")
        self.assertEqual(s.get_rule("style.brevity").status, "active")
        before = s.get_rule("style.brevity").confidence

        # Now the user starts asking for more detail.
        for i in range(2):
            L.observe_turn(f"b{i}", "can you explain more")
        # Old rule weakened but NOT removed; new one is a candidate awaiting review.
        self.assertEqual(s.get_rule("style.brevity").status, "active")
        self.assertLess(s.get_rule("style.brevity").confidence, before)
        self.assertEqual(s.get_rule("style.detail").status, "candidate")

    def test_approving_opposite_archives_old(self):
        s, L = loop(evidence_threshold=2)
        for i in range(2):
            L.observe_turn(f"a{i}", "keep it shorter")
        L.approve("style.brevity")
        for i in range(2):
            L.observe_turn(f"b{i}", "can you explain more")
        L.approve("style.detail")
        self.assertEqual(s.get_rule("style.brevity").status, "archived")
        self.assertEqual(s.get_rule("style.detail").status, "active")


class TestCapAndDecay(unittest.TestCase):
    def test_cap_never_evicts_protected(self):
        s = MemoryStore(max_active_rules=6)
        L = LearningLoop(s)   # installs 5 protected
        for i in range(20):
            s.upsert_rule(f"junk.{i}", f"junk rule {i}",
                          confidence=0.5, status="active")
        s.enforce_cap()
        active = s.active_rules()
        self.assertLessEqual(len(active), 6)
        prot = {r.rule_key for r in active if r.protected}
        self.assertEqual(prot, {k for k, _ in PROTECTED_RULES})

    def test_cap_keeps_protected_even_when_they_exceed_it(self):
        s = MemoryStore(max_active_rules=2)
        LearningLoop(s)  # 5 protected > cap of 2
        s.enforce_cap()
        self.assertEqual(len([r for r in s.active_rules() if r.protected]), 5)

    def test_decay_archives_stale_unprotected(self):
        s, L = loop()
        now = time.time()
        s.upsert_rule("style.old", "stale preference",
                      confidence=0.65, status="active")
        s.db.execute("UPDATE rules SET last_confirmed=? WHERE rule_key='style.old'",
                     (now - 200 * DAY,))
        s.db.commit()
        archived = L.run_decay(now=now)
        self.assertIn("style.old", archived)

    def test_decay_never_touches_protected(self):
        s, L = loop()
        now = time.time()
        s.db.execute("UPDATE rules SET last_confirmed=? WHERE protected=1",
                     (now - 5000 * DAY,))
        s.db.commit()
        L.run_decay(now=now)
        for key, _ in PROTECTED_RULES:
            self.assertEqual(s.get_rule(key).status, "active", key)
            self.assertEqual(s.get_rule(key).confidence, 1.0, key)


class TestVersioning(unittest.TestCase):
    def test_rollback_restores_previous_text(self):
        s, L = loop()
        rid = s.upsert_rule("style.x", "version one", status="active")
        s.upsert_rule("style.x", "version two", status="active")
        self.assertEqual(s.get_rule("style.x").text, "version two")
        s.rollback_rule(rid, 1)
        self.assertEqual(s.get_rule("style.x").text, "version one")
        # Rollback is itself a new version -- history is append-only.
        self.assertGreaterEqual(len(s.rule_versions(rid)), 3)


class TestLanguageScoping(unittest.TestCase):
    def test_language_specific_rule_does_not_govern_other_languages(self):
        """Register IS language-specific; brevity is not. Only register scopes."""
        s, L = loop(evidence_threshold=2)
        for i in range(2):
            L.observe_turn(f"s{i}", "normal baat karo yaar")
        key = "style.register.hinglish"
        self.assertIsNotNone(s.get_rule(key), "register rule was not scoped")
        L.approve(key)
        marker = "When the conversation is in hinglish"
        self.assertNotIn(marker, L.system_rules_block(lang="en"))
        self.assertIn(marker, L.system_rules_block(lang="hinglish"))

    def test_brevity_evidence_is_not_fragmented_by_language(self):
        """Correcting in Hinglish then English must accumulate on ONE rule.

        Regression for the defect the end-to-end learning test exposed:
        language-scoped brevity split three corrections across two keys, so
        neither reached the threshold and nothing was ever learned.
        """
        s, L = loop(evidence_threshold=3)
        for i, t in enumerate(["arre nahi, itna bada answer mat do. simple bol.",
                               "keep it shorter",
                               "too long, get to the point"]):
            L.observe_turn(f"s{i}", t)
        keys = [r["rule_key"] for r in s.db.execute(
            "SELECT rule_key FROM rules WHERE rule_key LIKE 'style.brevity%'")]
        self.assertEqual(keys, ["style.brevity"], f"evidence fragmented: {keys}")
        self.assertEqual([(i.rule_key, i.evidence) for i in L.review_queue()],
                         [("style.brevity", 3)])

    def test_protected_always_present_in_every_language(self):
        s, L = loop()
        for lang in ("en", "hi", "hinglish"):
            block = L.system_rules_block(lang=lang)
            for key, text in PROTECTED_RULES:
                self.assertIn(text.split(".")[0][:30], block, f"{key} missing in {lang}")



class TestEnforceableRules(unittest.TestCase):
    """A learned rule that can be enforced must be enforced, not requested.

    The end-to-end learning test ran the whole pipeline correctly --
    correction detected, evidence across three sessions, review, promotion,
    rule present in the system prompt -- and the model then answered a fresh
    question in 55 words where its pre-correction baseline was 45. Asking a
    4B model to be brief is a request; capping its token budget is a fact.
    """

    def test_no_effect_before_promotion(self):
        s, L = loop(evidence_threshold=3)
        p = L.generation_params()
        self.assertEqual(p["applied"], [])
        self.assertEqual(p["max_tokens"], 300)

    def test_candidate_alone_does_not_apply(self):
        s, L = loop(evidence_threshold=3)
        L.observe_turn("s0", "keep it shorter")
        self.assertEqual(L.generation_params()["applied"], [])

    def test_promoted_brevity_caps_tokens(self):
        s, L = loop(evidence_threshold=3)
        for i, t in enumerate(["arre nahi, itna bada answer mat do. simple bol.",
                               "keep it shorter", "too long, get to the point"]):
            L.observe_turn(f"s{i}", t)
        L.approve("style.brevity")
        p = L.generation_params()
        self.assertEqual(p["max_tokens"], 35)
        self.assertEqual(p["max_sentences"], 2)
        self.assertEqual([k for k, _ in p["applied"]], ["style.brevity"])

    def test_promoted_detail_raises_the_cap(self):
        s, L = loop(evidence_threshold=2)
        for i in range(2):
            L.observe_turn(f"d{i}", "can you explain more")
        L.approve("style.detail")
        self.assertEqual(L.generation_params()["max_tokens"], 420)

    def test_archiving_the_rule_removes_the_effect(self):
        s, L = loop(evidence_threshold=2)
        for i in range(2):
            L.observe_turn(f"s{i}", "keep it shorter")
        L.approve("style.brevity")
        self.assertEqual(L.generation_params()["max_tokens"], 35)
        s.set_status(s.get_rule("style.brevity").id, "archived")
        self.assertEqual(L.generation_params()["max_tokens"], 300)

    def test_trim_keeps_only_complete_sentences(self):
        from vision.core.orchestrator import trim_to_sentences as T
        self.assertEqual(T("A. B. C. D.", 2), "A. B.")
        self.assertEqual(T("First. Second. Third but cut off mid", 2),
                         "First. Second.")
        self.assertEqual(T("हाँ। ठीक। और।", 2), "हाँ। ठीक।")
        self.assertEqual(T("Only one.", 2), "Only one.")
        # A single unterminated sentence is kept -- dropping it would leave
        # nothing, and silence is worse than a slightly clipped reply.
        self.assertEqual(T("no terminator here", 2), "no terminator here")

    def test_orchestrator_trims_when_brevity_is_active(self):
        from vision.core.obsidian import VaultIndex, TfidfEmbedder
        from vision.core.orchestrator import Orchestrator
        s, L = loop(evidence_threshold=2)
        v = VaultIndex(TfidfEmbedder()); v.add_note("a.md", "# A\nx"); v.build_vectors()
        class C:
            max_tokens = 300
            def respond(self, *a): return "One. Two. Three. Four."
        o = Orchestrator(s, v, C(), learning=L)
        self.assertEqual(o.handle("t", "hi").text, "One. Two. Three. Four.")
        for i in range(2):
            L.observe_turn(f"s{i}", "keep it shorter")
        L.approve("style.brevity")
        self.assertEqual(o.handle("t", "hi again").text, "One. Two.")

    def test_orchestrator_applies_and_restores_the_cap(self):
        from vision.core.obsidian import VaultIndex, TfidfEmbedder
        from vision.core.orchestrator import Orchestrator
        s, L = loop(evidence_threshold=2)
        v = VaultIndex(TfidfEmbedder()); v.add_note("a.md", "# A\nx"); v.build_vectors()
        seen = []
        class C:
            max_tokens = 300
            def respond(self, *a):
                seen.append(C.max_tokens if False else conv.max_tokens)
                return "ok"
        conv = C()
        o = Orchestrator(s, v, conv, learning=L)
        o.handle("t", "hello")
        self.assertEqual(seen[-1], 300)
        for i in range(2):
            L.observe_turn(f"s{i}", "keep it shorter")
        L.approve("style.brevity")
        o.handle("t", "hello again")
        self.assertEqual(seen[-1], 35, "cap was not applied during the call")
        self.assertEqual(conv.max_tokens, 300, "cap was not restored after")

if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestSeveredReplies(unittest.TestCase):
    """A brevity cap that truncates mid-sentence trades one flaw for another.

    MEASURED, M04 round 4. The in-session brevity fix worked -- the reply
    after "Arre itna bada answer kyun de raha hai?" went from 40 words to
    13 -- and then the 35-token cap cut the NEXT one mid-word:

        "API bas ek interface hai jo ek software ko dusre se connect karta
         hai, jaise tum fridge ka door khola kar bhi andar ka food nahi
         dekh"

    trim_to_sentences could not help: there was no complete sentence in
    there to keep.
    """

    def test_a_severed_clause_is_closed_at_the_last_boundary(self):
        from vision.core.orchestrator import trim_to_sentences
        out = trim_to_sentences(
            "API bas ek interface hai jo ek software ko dusre se connect "
            "karta hai, jaise tum fridge ka door khola kar bhi andar ka "
            "food nahi dekh", 2)
        self.assertEqual(
            out, "API bas ek interface hai jo ek software ko dusre se "
                 "connect karta hai.")

    def test_a_trailing_connective_is_dropped(self):
        from vision.core.orchestrator import trim_to_sentences
        self.assertEqual(
            trim_to_sentences("Yeh kaam thoda mushkil hai lekin", 2),
            "Yeh kaam thoda mushkil hai.")
        self.assertEqual(
            trim_to_sentences("I think the answer is probably yes because", 2),
            "I think the answer is probably yes.")

    def test_a_finished_reply_is_untouched(self):
        """ANTI-FALSE-GREEN: this must not rewrite normal output."""
        from vision.core.orchestrator import trim_to_sentences
        for text in ["Good, just chilling. What's up with you?",
                     "Bas chill raha hu, koi news nahi.",
                     "No, you didn't. The data shows passkeys."]:
            self.assertEqual(trim_to_sentences(text, 2), text, text)

    def test_a_fragment_too_short_to_save_is_left_alone(self):
        """ANTI-FALSE-GREEN: "API bas ek" -> "API." helps nobody."""
        from vision.core.orchestrator import trim_to_sentences
        self.assertEqual(trim_to_sentences("API bas ek", 2), "API bas ek")

    def test_the_sentence_limit_still_applies(self):
        """ANTI-FALSE-GREEN: closing a severed clause must not disable the
        limit it exists to make safe."""
        from vision.core.orchestrator import trim_to_sentences
        self.assertEqual(trim_to_sentences("One. Two. Three. Four.", 2),
                         "One. Two.")
