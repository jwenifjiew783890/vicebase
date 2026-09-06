"""Fetch the models Vision needs, with progress and resume.

Kept separate from the installer scripts so that the same code runs on
Windows, macOS and Linux, and so a user whose download died can re-run
`python -m vision.setup_models` without re-running an installer.

Nothing here is bundled: the conversational model alone is 2.7 GB, which
does not belong in a repository. What IS here is one command that gets
everything and tells you honestly how far it got.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

from . import config

HF = "https://huggingface.co"

# name -> (url, destination, approximate bytes)
LLM_DEFAULT = "Qwen3.5-4B-Q4_K_M.gguf"
LLM_URL = f"{HF}/unsloth/Qwen3.5-4B-GGUF/resolve/main/{LLM_DEFAULT}"

VOICES = {
    "en_US-lessac-medium": f"{HF}/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium",
    "hi_IN-pratham-medium": f"{HF}/rhasspy/piper-voices/resolve/main/hi/hi_IN/pratham/medium/hi_IN-pratham-medium",
}


def _human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def download(url: str, dest: Path, expect_min: int = 0) -> bool:
    """Download with a progress line. Verifies size rather than trusting it.

    A truncated GGUF or ONNX fails deep inside a C++ parser with an
    unhelpful message -- this project hit exactly that with a 49 MB voice
    file that should have been 63 MB -- so the size is checked here where
    the error can still say something useful.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size >= expect_min > 0:
        print(f"  have  {dest.name} ({_human(dest.stat().st_size)})")
        return True
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "vision-setup"})
        with urllib.request.urlopen(req, timeout=120) as r:
            total = int(r.headers.get("content-length") or 0)
            done = 0
            with open(tmp, "wb") as fh:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    fh.write(chunk)
                    done += len(chunk)
                    if total:
                        pct = 100 * done / total
                        print(f"\r  get   {dest.name}  {pct:5.1f}%  "
                              f"{_human(done)}/{_human(total)}", end="", flush=True)
            print()
        size = tmp.stat().st_size
        if expect_min and size < expect_min:
            tmp.unlink(missing_ok=True)
            print(f"  FAIL  {dest.name}: got {_human(size)}, expected at least "
                  f"{_human(expect_min)} -- truncated download")
            return False
        tmp.replace(dest)
        return True
    except urllib.error.HTTPError as e:
        tmp.unlink(missing_ok=True)
        print(f"  FAIL  {dest.name}: HTTP {e.code} from {url}")
        return False
    except Exception as e:
        tmp.unlink(missing_ok=True)
        print(f"  FAIL  {dest.name}: {type(e).__name__}: {e}")
        return False


def get_voices(only: list[str] | None = None) -> bool:
    ok = True
    for name, base in VOICES.items():
        if only and name not in only:
            continue
        onnx = config.VOICES_DIR / f"{name}.onnx"
        meta = config.VOICES_DIR / f"{name}.onnx.json"
        ok &= download(base + ".onnx", onnx, expect_min=40_000_000)
        ok &= download(base + ".onnx.json", meta, expect_min=500)
    return ok


def get_llm() -> bool:
    dest = config.MODELS_DIR / LLM_DEFAULT
    return download(LLM_URL, dest, expect_min=2_000_000_000)


def get_stt() -> bool:
    """faster-whisper fetches its own weights on first load."""
    try:
        from faster_whisper import WhisperModel
        print(f"  get   whisper '{config.STT_MODEL}' (cached after first run)")
        WhisperModel(config.STT_MODEL, device=config.STT_DEVICE,
                     compute_type=config.STT_COMPUTE)
        print(f"  have  whisper '{config.STT_MODEL}'")
        return True
    except Exception as e:
        print(f"  FAIL  whisper: {type(e).__name__}: {e}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="vision.setup_models",
        description="Download the models Vision needs.")
    ap.add_argument("--skip-llm", action="store_true",
                    help="skip the 2.7 GB conversational model")
    ap.add_argument("--voices-only", action="store_true")
    a = ap.parse_args()

    config.ensure_dirs()
    print(f"Vision models -> {config.HOME}\n")
    ok = True
    print("Speech out (Piper voices, ~63 MB each)")
    ok &= get_voices()
    if not a.voices_only:
        print("\nSpeech in (faster-whisper)")
        ok &= get_stt()
        if not a.skip_llm:
            print(f"\nConversation ({LLM_DEFAULT}, ~2.7 GB)")
            ok &= get_llm()

    free = shutil.disk_usage(config.HOME).free
    print(f"\n{'All set.' if ok else 'Some downloads failed -- re-run to resume.'}"
          f"  {_human(free)} free at {config.HOME}")
    if not ok:
        print("If the model URL 404s, search huggingface.co for "
              f"'{LLM_DEFAULT}' and set VISION_LLM to the file you get.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
