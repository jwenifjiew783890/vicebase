"""Voice policy tests.

These cover the parts that cause most of the perceived badness in a voice
assistant and that need no audio hardware: endpointing, clause chunking,
barge-in, voice selection and latency accounting.

What is NOT covered here, and is NOT claimed to work: actual STT accuracy,
actual TTS naturalness, and real end-to-end audio latency. Those need a
microphone, a speaker and the models, none of which exist in this
environment.
"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.core.voice import (EndpointPolicy, TurnState, VoiceSession, VoiceTimings,
                       clause_chunks, pick_voice, stream_for_tts)


class TestEndpointing(unittest.TestCase):
    """Cutting the user off mid-thought ruins voice faster than bad ASR."""

    def setUp(self):
        self.p = EndpointPolicy()

    def test_long_silence_always_ends_the_turn(self):
        self.assertTrue(self.p.is_endpoint("so I was thinking and", 1200))

    def test_short_silence_after_a_complete_sentence_ends_the_turn(self):
        self.assertTrue(self.p.is_endpoint("open opencode.", 400))
        self.assertTrue(self.p.is_endpoint("kya haal hai", 500))

    def test_short_silence_mid_thought_does_NOT_end_the_turn(self):
        """People pause to think. Silence alone is not a finished sentence."""
        for t in ["so I was thinking about the auth thing and",
                  "I want to but", "the problem is that",
                  "mujhe lagta hai ki", "ye kaam karega agar",
                  "we should probably, um"]:
            self.assertFalse(self.p.is_endpoint(t, 400), t)

    def test_code_switch_boundary_is_not_an_endpoint(self):
        """Hinglish speakers pause where they switch language."""
        for t in ["mujhe ye feature implement karna hai aur",
                  "the deployment fail ho raha hai kyunki"]:
            self.assertFalse(self.p.is_endpoint(t, 400), t)

    def test_very_short_silence_never_ends_the_turn(self):
        self.assertFalse(self.p.is_endpoint("open opencode.", 100))

    def test_empty_input_is_never_an_endpoint(self):
        self.assertFalse(self.p.is_endpoint("", 5000))
        self.assertFalse(self.p.is_endpoint("   ", 5000))

    def test_trailing_comma_keeps_listening(self):
        self.assertFalse(self.p.is_endpoint("first the auth part,", 400))


class TestClauseChunking(unittest.TestCase):
    """Waiting for a full sentence costs first-audio; every comma is choppy."""

    def test_splits_on_clause_boundaries(self):
        chunks = clause_chunks(
            "Bas chill raha hu, koi news nahi. Tu bata kya haal hai?")
        self.assertGreaterEqual(len(chunks), 2)
        # Each chunk must end at a real boundary. The first one absorbs the
        # too-short comma clause, which is correct -- speaking "Bas chill
        # raha hu," alone would be choppy.
        for c in chunks:
            self.assertRegex(c, r"[.!?।,;]$", f"chunk cut mid-clause: {c!r}")

    def test_short_fragments_are_merged_not_spoken_alone(self):
        chunks = clause_chunks("Yes, no, maybe, fine.")
        for c in chunks:
            self.assertGreaterEqual(len(c), 12, f"choppy chunk: {c!r}")

    def test_a_short_reply_is_one_chunk(self):
        self.assertEqual(clause_chunks("hey"), ["hey"])

    def test_devanagari_danda_is_a_boundary(self):
        chunks = clause_chunks("मैं ठीक हूँ। तुम कैसे हो, बताओ।")
        self.assertGreaterEqual(len(chunks), 1)
        self.assertIn("।", chunks[0])

    def test_nothing_is_lost(self):
        text = "First part here, second part here. Third part follows."
        joined = " ".join(clause_chunks(text))
        for word in ("First", "second", "Third", "follows"):
            self.assertIn(word, joined)

    def test_empty_input(self):
        self.assertEqual(clause_chunks(""), [])
        self.assertEqual(clause_chunks("   "), [])

    def test_streaming_emits_before_the_reply_is_complete(self):
        tokens = ["Bas ", "chill ", "raha ", "hu, ", "koi ", "news ",
                  "nahi. ", "Tu ", "bata."]
        out = list(stream_for_tts(iter(tokens)))
        self.assertGreaterEqual(len(out), 2,
                                "streaming produced only one chunk")
        self.assertIn("chill", out[0])


class TestBargeIn(unittest.TestCase):
    """A user who cannot interrupt will not talk to it twice."""

    def test_interruption_stops_the_remaining_chunks(self):
        s = VoiceSession()
        s.begin_speaking(["one,", "two,", "three."])
        s.speak_next()
        said = s.barge_in()
        self.assertEqual(s.state, TurnState.INTERRUPTED)
        self.assertEqual(s.pending_chunks, [])
        self.assertEqual(said, "one,")

    def test_what_was_already_said_is_preserved(self):
        """The model must know what the user actually heard."""
        s = VoiceSession()
        s.begin_speaking(["Storing passwords in plaintext is a bad idea,",
                          "you should use a KDF,", "and rotate the salt."])
        s.speak_next(); s.speak_next()
        heard = s.barge_in()
        self.assertIn("plaintext", heard)
        self.assertIn("KDF", heard)
        self.assertNotIn("salt", heard)

    def test_session_returns_to_listening_after_the_last_chunk(self):
        s = VoiceSession()
        s.begin_speaking(["only chunk."])
        s.speak_next()
        self.assertEqual(s.state, TurnState.LISTENING)

    def test_speak_next_is_inert_when_not_speaking(self):
        s = VoiceSession()
        self.assertIsNone(s.speak_next())

    def test_interruptions_are_counted(self):
        s = VoiceSession()
        for _ in range(3):
            s.begin_speaking(["a.", "b."]); s.speak_next(); s.barge_in()
        self.assertEqual(s.interruptions, 3)


class TestVoiceSelection(unittest.TestCase):
    def test_one_voice_across_languages(self):
        """Switching voice mid-conversation reads as a different person."""
        voices = {pick_voice(l) for l in ("en", "hi", "hinglish", "unknown")}
        self.assertEqual(len(voices), 1, f"voice identity is unstable: {voices}")


class TestLatencyAccounting(unittest.TestCase):
    def test_retrieval_is_not_on_the_critical_path(self):
        a = VoiceTimings(endpoint_ms=150, stt_ms=150, prefill_ms=130,
                         first_token_ms=35, first_chunk_ms=180,
                         tts_first_audio_ms=120)
        b = VoiceTimings(**{**a.__dict__, "retrieval_ms": 500})
        self.assertEqual(a.time_to_first_audio_ms, b.time_to_first_audio_ms)

    def test_verdict_bands(self):
        self.assertEqual(VoiceTimings(endpoint_ms=500).verdict(), "responsive")
        self.assertEqual(VoiceTimings(endpoint_ms=1500).verdict(), "acceptable")
        self.assertEqual(VoiceTimings(endpoint_ms=2000).verdict(), "sluggish")
        self.assertEqual(VoiceTimings(endpoint_ms=3000).verdict(), "broken")


if __name__ == "__main__":
    unittest.main(verbosity=2)
