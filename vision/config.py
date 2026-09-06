"""Where Vision keeps its state, and what it is configured to use.

One place, so nothing else has to guess a path. Everything is overridable
by environment variable because the two machines this runs on (a developer
container and the user's Windows laptop) agree on nothing else.
"""
from __future__ import annotations

import os
from pathlib import Path


def _env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name)
    return Path(raw).expanduser() if raw else default


# Everything Vision persists lives under one directory, so "where is my
# data" and "how do I back it up" have one answer.
HOME = _env_path("VISION_HOME", Path.home() / ".vision")

DB_PATH      = _env_path("VISION_DB",      HOME / "vision.db")
VOICES_DIR   = _env_path("VISION_VOICES",  HOME / "voices")
MODELS_DIR   = _env_path("VISION_MODELS",  HOME / "models")
AUDIO_TMP    = _env_path("VISION_AUDIO",   HOME / "audio")
TASKS_DIR    = _env_path("VISION_TASKS",   HOME / "tasks")

# The conversational model. Absent means text-only mode: the app still
# runs, and says so, rather than refusing to start.
LLM_PATH     = os.environ.get("VISION_LLM", str(MODELS_DIR / "Qwen3.5-4B-Q4_K_M.gguf"))
LLM_CTX      = int(os.environ.get("VISION_LLM_CTX", "4096"))
LLM_THREADS  = int(os.environ.get("VISION_LLM_THREADS", "4"))
LLM_MAX_TOK  = int(os.environ.get("VISION_LLM_MAX_TOKENS", "220"))
LLM_GPU_LAYERS = int(os.environ.get("VISION_LLM_GPU_LAYERS", "0"))

# Speech. Both are optional at import time and report their own absence.
STT_MODEL    = os.environ.get("VISION_STT_MODEL", "small")
STT_DEVICE   = os.environ.get("VISION_STT_DEVICE", "cpu")
STT_COMPUTE  = os.environ.get("VISION_STT_COMPUTE", "int8")
TTS_VOICE_EN = os.environ.get("VISION_TTS_EN", "en_US-lessac-medium")
TTS_VOICE_HI = os.environ.get("VISION_TTS_HI", "")   # see voice/tts.py

# The personal knowledge base. Empty means "not connected yet"; the UI
# offers to connect it and writes the path back here via settings.
OBSIDIAN_VAULT = os.environ.get("VISION_VAULT", "")

HOST = os.environ.get("VISION_HOST", "127.0.0.1")
PORT = int(os.environ.get("VISION_PORT", "8765"))


def ensure_dirs() -> None:
    for d in (HOME, VOICES_DIR, MODELS_DIR, AUDIO_TMP, TASKS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def describe() -> dict:
    """What the app will actually use, for the UI's settings panel."""
    return {
        "home": str(HOME), "db": str(DB_PATH),
        "llm": LLM_PATH, "llm_present": os.path.exists(LLM_PATH),
        "llm_ctx": LLM_CTX, "llm_threads": LLM_THREADS,
        "llm_gpu_layers": LLM_GPU_LAYERS,
        "stt_model": STT_MODEL, "stt_device": STT_DEVICE,
        "tts_voice_en": TTS_VOICE_EN, "tts_voice_hi": TTS_VOICE_HI or None,
        "vault": OBSIDIAN_VAULT or None,
        "host": HOST, "port": PORT,
    }
