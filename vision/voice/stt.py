"""Speech to text, via faster-whisper.

Chosen over the alternatives for one reason that matters here: Whisper is
multilingual in a way that survives code-switching. Vision's user speaks
English, Hindi and Hinglish in the same sentence, and a monolingual
recogniser forces a choice the user did not make.

Loaded lazily and reports its own absence, so the application starts and
stays usable when the model has not been downloaded yet.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

from .. import config


@dataclass
class Transcript:
    text: str
    language: str
    language_confidence: float = 0.0
    duration_s: float = 0.0
    compute_s: float = 0.0
    segments: list = field(default_factory=list)

    @property
    def realtime_factor(self) -> float:
        return self.duration_s / self.compute_s if self.compute_s else 0.0


class SpeechToText:
    """One loaded model, shared. Thread-safe: whisper is not re-entrant."""

    def __init__(self, model: str | None = None, device: str | None = None,
                 compute_type: str | None = None):
        self.model_name = model or config.STT_MODEL
        self.device = device or config.STT_DEVICE
        self.compute_type = compute_type or config.STT_COMPUTE
        self._model = None
        self._lock = threading.Lock()
        self.load_error: str | None = None

    @property
    def available(self) -> bool:
        try:
            import faster_whisper  # noqa: F401
            return True
        except Exception as exc:
            self.load_error = f"faster-whisper not installed: {exc}"
            return False

    def load(self) -> bool:
        """Load on first use. Downloads the model if it is not cached."""
        if self._model is not None:
            return True
        with self._lock:
            if self._model is not None:
                return True
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(self.model_name, device=self.device,
                                           compute_type=self.compute_type)
                self.load_error = None
                return True
            except Exception as exc:
                self.load_error = str(exc)
                return False

    def transcribe(self, path: str, *, language: str | None = None) -> Transcript:
        """Transcribe a wav/audio file.

        `language=None` lets Whisper detect, which is what Hinglish needs:
        forcing "hi" on a sentence that is 70% English makes it worse.
        """
        if not self.load():
            raise RuntimeError(f"STT unavailable: {self.load_error}")
        t0 = time.perf_counter()
        with self._lock:
            segments, info = self._model.transcribe(
                path, beam_size=5, language=language,
                vad_filter=True, vad_parameters={"min_silence_duration_ms": 400})
            segs = [{"start": s.start, "end": s.end, "text": s.text.strip()}
                    for s in segments]
        compute = time.perf_counter() - t0
        return Transcript(
            text=" ".join(s["text"] for s in segs).strip(),
            language=info.language,
            language_confidence=float(info.language_probability or 0.0),
            duration_s=float(info.duration or 0.0),
            compute_s=compute, segments=segs)

    def describe(self) -> dict:
        return {"engine": "faster-whisper", "model": self.model_name,
                "device": self.device, "compute_type": self.compute_type,
                "loaded": self._model is not None,
                "available": self.available, "error": self.load_error}
