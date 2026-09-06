"""Launch Vision.

    python -m vision            # start the app, open http://127.0.0.1:8765
    python -m vision --check    # report what is and is not available, and exit
"""
from __future__ import annotations

import argparse
import sys

from . import config


def check() -> int:
    config.ensure_dirs()
    from .voice.stt import SpeechToText
    from .voice.tts import TextToSpeech
    from pathlib import Path

    rows = []
    llm_ok = Path(config.LLM_PATH).exists()
    rows.append(("model", llm_ok, config.LLM_PATH))
    stt = SpeechToText(); tts = TextToSpeech()
    rows.append(("stt", stt.available, f"faster-whisper '{stt.model_name}' on {stt.device}"))
    rows.append(("tts", tts.available, ", ".join(tts.installed_voices()) or "no voices installed"))
    rows.append(("memory", True, str(config.DB_PATH)))
    rows.append(("vault", bool(config.OBSIDIAN_VAULT), config.OBSIDIAN_VAULT or "not connected"))
    width = max(len(r[0]) for r in rows)
    print("Vision preflight\n")
    for name, ok, detail in rows:
        print(f"  {'OK ' if ok else '-- '} {name.ljust(width)}  {detail}")
    print(f"\n  home: {config.HOME}")
    if not llm_ok:
        print("\n  Without a model Vision still starts, and says so instead of "
              "pretending to talk.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="vision")
    ap.add_argument("--check", action="store_true", help="report availability and exit")
    ap.add_argument("--host", default=config.HOST)
    ap.add_argument("--port", type=int, default=config.PORT)
    a = ap.parse_args()
    if a.check:
        return check()
    import uvicorn
    print(f"Vision -> http://{a.host}:{a.port}")
    uvicorn.run("vision.server.app:app", host=a.host, port=a.port, log_level="warning")
    return 0


if __name__ == "__main__":
    sys.exit(main())
