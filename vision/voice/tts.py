"""Text to speech, via Piper.

Piper was chosen for three practical reasons: it runs ~20x realtime on CPU
(so it costs nothing next to a 4B model generating at 8 tok/s), it is a
single self-contained ONNX file per voice, and it has usable Hindi.

The voice is chosen by SCRIPT, not by language, and that is a measured
decision rather than an obvious one -- see pick_voice.
"""
from __future__ import annotations

import io
import re
import threading
import time
import wave
from dataclasses import dataclass
from pathlib import Path

from .. import config

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")


@dataclass
class Speech:
    wav: bytes
    voice: str
    sample_rate: int
    duration_s: float
    compute_s: float

    @property
    def realtime_factor(self) -> float:
        return self.duration_s / self.compute_s if self.compute_s else 0.0


def pick_voice(text: str, lang_hint: str = "en") -> str:
    """Which voice should say this?

    MEASURED, and the result is not what the language label suggests. The
    runtime replies to Hindi in ROMANISED Hindi ("Haan yaar, main theek
    hoon") because that is how the user writes. Sent to the Hindi voice,
    whose phonemizer expects Devanagari, that came back as

        'हान्या मेंही कुन, तम्किज हो'

    Sent to the English voice it came back as

        'Hanyar Main Thik Hoon, Thum Kays Ho'

    -- an English accent, but the right words, and Whisper could read it
    back. So the question is not "what language is this?" but "what script
    is this written in?". Devanagari goes to the Hindi voice; Latin goes to
    the English one whatever language it encodes.
    """
    if _DEVANAGARI.search(text):
        return config.TTS_VOICE_HI or config.TTS_VOICE_EN
    return config.TTS_VOICE_EN


class TextToSpeech:
    def __init__(self, voices_dir: Path | None = None):
        self.voices_dir = Path(voices_dir or config.VOICES_DIR)
        self._voices: dict[str, object] = {}
        self._lock = threading.Lock()
        self.load_error: str | None = None

    @property
    def available(self) -> bool:
        try:
            import piper  # noqa: F401
        except Exception as exc:
            self.load_error = f"piper-tts not installed: {exc}"
            return False
        return bool(self.installed_voices())

    def installed_voices(self) -> list[str]:
        if not self.voices_dir.exists():
            return []
        return sorted(p.stem for p in self.voices_dir.glob("*.onnx")
                      if (self.voices_dir / (p.stem + ".onnx.json")).exists())

    def _voice(self, name: str):
        if name in self._voices:
            return self._voices[name]
        with self._lock:
            if name in self._voices:
                return self._voices[name]
            from piper import PiperVoice
            path = self.voices_dir / f"{name}.onnx"
            if not path.exists():
                raise FileNotFoundError(
                    f"voice {name!r} not in {self.voices_dir}. "
                    f"Installed: {self.installed_voices() or 'none'}")
            self._voices[name] = PiperVoice.load(str(path))
            return self._voices[name]

    def speak(self, text: str, *, lang: str = "en",
              voice: str | None = None) -> Speech:
        name = voice or pick_voice(text, lang)
        v = self._voice(name)
        buf = io.BytesIO()
        t0 = time.perf_counter()
        with self._lock:
            with wave.open(buf, "wb") as w:
                v.synthesize_wav(text, w)
        compute = time.perf_counter() - t0
        data = buf.getvalue()
        with wave.open(io.BytesIO(data)) as r:
            rate = r.getframerate()
            duration = r.getnframes() / rate
        return Speech(wav=data, voice=name, sample_rate=rate,
                      duration_s=duration, compute_s=compute)

    def describe(self) -> dict:
        return {"engine": "piper", "voices_dir": str(self.voices_dir),
                "installed": self.installed_voices(),
                "default_en": config.TTS_VOICE_EN,
                "default_hi": config.TTS_VOICE_HI or None,
                "available": self.available, "error": self.load_error}
