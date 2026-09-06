"""Voice pipeline: the parts that can be built and tested without audio.

What needs hardware (a microphone, a speaker, a GPU to run the models) is
behind interfaces and is explicitly NOT tested here. What does not need
hardware -- endpointing policy, clause chunking for streaming TTS, the
barge-in state machine, the language routing for voice selection, and the
latency accounting -- is real code with real tests.

That split matters: in a voice assistant these policy layers cause more
perceived badness than the models do. Cutting the user off mid-sentence,
or speaking a paragraph they cannot interrupt, ruins the experience no
matter how good the ASR is.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterator, Optional, Protocol, Sequence


# ---------------------------------------------------------------- interfaces

class STT(Protocol):
    """Speech to text. Needs audio hardware and a model: NOT tested here."""
    def transcribe(self, pcm: bytes, sample_rate: int) -> "Transcript": ...


class TTS(Protocol):
    """Text to speech. Needs a model: NOT tested here."""
    def synthesize(self, text: str, voice: str) -> bytes: ...


@dataclass
class Transcript:
    text: str
    is_final: bool = False
    confidence: float = 1.0
    lang: str = "en"


# ------------------------------------------------------------- endpointing

class TurnState(Enum):
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"


# A trailing conjunction or filler means the speaker has not finished, even
# if they have gone quiet. Waiting on silence alone is what makes assistants
# cut people off mid-thought.
_INCOMPLETE_TAIL = re.compile(
    r"\b(and|but|so|because|or|if|then|that|which|the|a|an|to|for|with|"
    r"um+|uh+|like|i mean)\s*$"
    r"|\b(aur|par|lekin|kyunki|ya|agar|toh|ki|jo|ka|ke|ki|se|matlab|"
    r"yaani|wo|ye)\s*$"
    r"|[,;:\-–—]\s*$",
    re.IGNORECASE)

_COMPLETE_TAIL = re.compile(r"[.!?।]\s*$")


@dataclass
class EndpointPolicy:
    """When has the user actually finished speaking?

    Silence alone is a bad signal: people pause mid-sentence to think, and
    Hindi/Hinglish speakers pause around code-switch boundaries. So a short
    silence ends the turn only when the text also looks complete.
    """
    short_silence_ms: int = 350     # enough when the utterance looks finished
    long_silence_ms: int = 900      # enough regardless
    min_words: int = 1

    def is_endpoint(self, text: str, silence_ms: int) -> bool:
        words = len(re.findall(r"[\wऀ-ॿ]+", text))
        if words < self.min_words:
            return False
        if silence_ms >= self.long_silence_ms:
            return True
        if silence_ms < self.short_silence_ms:
            return False
        if _INCOMPLETE_TAIL.search(text.strip()):
            return False        # they are mid-thought; keep listening
        return True


# --------------------------------------------------- clause chunking (TTS)

# Split for streaming synthesis. Waiting for a full sentence adds hundreds of
# milliseconds to first audio; splitting on every comma produces choppy,
# unnatural prosody. Clause boundaries with a minimum length is the
# compromise.
_CLAUSE_END = re.compile(r"(?<=[.!?।])\s+|(?<=[,;])\s+")


def clause_chunks(text: str, min_chars: int = 24) -> list[str]:
    """Split a reply into chunks suitable for streaming TTS."""
    if not text.strip():
        return []
    pieces = [p for p in _CLAUSE_END.split(text.strip()) if p.strip()]
    out: list[str] = []
    buf = ""
    for piece in pieces:
        buf = f"{buf} {piece}".strip() if buf else piece
        if len(buf) >= min_chars:
            out.append(buf)
            buf = ""
    if buf:
        # Merge the tail only if it is too short to speak on its own.
        # An earlier version merged ANY leftover, which collapsed
        # "Bas chill raha hu, koi news nahi. Tu bata kya haal hai?" into a
        # single chunk -- a 21-character tail is perfectly speakable, and
        # merging it defeats the streaming this function exists for.
        if out and len(buf) < min_chars // 2:
            out[-1] = f"{out[-1]} {buf}".strip()
        else:
            out.append(buf)
    return out


def stream_for_tts(tokens: Iterator[str], min_chars: int = 24) -> Iterator[str]:
    """Yield speakable chunks as generation tokens arrive."""
    buf = ""
    for tok in tokens:
        buf += tok
        if re.search(r"[.!?।,;]\s*$", buf) and len(buf.strip()) >= min_chars:
            yield buf.strip()
            buf = ""
    if buf.strip():
        yield buf.strip()


# ------------------------------------------------------------- voice choice

# One engine for both languages. Routing between a Hindi and an English
# voice changes the voice audibly mid-conversation, and a companion
# assistant with an unstable voice reads as broken.
VOICE_BY_LANG = {"en": "primary_female", "hi": "primary_female",
                 "hinglish": "primary_female"}


def pick_voice(lang: str) -> str:
    return VOICE_BY_LANG.get(lang, "primary_female")


# --------------------------------------------------------------- barge-in

@dataclass
class VoiceSession:
    """Turn-taking state machine, including interruption.

    Barge-in is the single most important voice affordance: a user who
    cannot interrupt will not talk to the thing twice.
    """
    state: TurnState = TurnState.LISTENING
    spoken_chunks: list[str] = field(default_factory=list)
    pending_chunks: list[str] = field(default_factory=list)
    interruptions: int = 0

    def begin_speaking(self, chunks: Sequence[str]) -> None:
        self.state = TurnState.SPEAKING
        self.pending_chunks = list(chunks)
        self.spoken_chunks = []

    def speak_next(self) -> Optional[str]:
        if self.state is not TurnState.SPEAKING or not self.pending_chunks:
            return None
        chunk = self.pending_chunks.pop(0)
        self.spoken_chunks.append(chunk)
        if not self.pending_chunks:
            self.state = TurnState.LISTENING
        return chunk

    def barge_in(self) -> str:
        """User started talking. Stop immediately; keep what was said."""
        self.interruptions += 1
        self.pending_chunks = []
        self.state = TurnState.INTERRUPTED
        return " ".join(self.spoken_chunks)

    def resume_listening(self) -> None:
        self.state = TurnState.LISTENING


# --------------------------------------------------------------- latency

@dataclass
class VoiceTimings:
    """Time-to-first-audio accounting. Filled by whatever runs the pipeline."""
    endpoint_ms: float = 0.0
    stt_ms: float = 0.0
    retrieval_ms: float = 0.0
    prefill_ms: float = 0.0
    first_token_ms: float = 0.0
    first_chunk_ms: float = 0.0
    tts_first_audio_ms: float = 0.0

    @property
    def time_to_first_audio_ms(self) -> float:
        # Retrieval runs in parallel with the model call and is not on the
        # critical path.
        return (self.endpoint_ms + self.stt_ms + self.prefill_ms
                + self.first_token_ms + self.first_chunk_ms
                + self.tts_first_audio_ms)

    def verdict(self) -> str:
        t = self.time_to_first_audio_ms
        return ("responsive" if t < 1000 else "acceptable" if t < 1800
                else "sluggish" if t < 2500 else "broken")
