"""Vision's application server.

One process serves the UI, the conversation, the agents and the voice
endpoints, because the brief asked for one application rather than a set of
services the user has to start in the right order.

The voice split is deliberate and is what makes the microphone real: the
BROWSER captures audio and plays it back, because that is where the user's
hardware is; the SERVER runs Whisper and Piper, because that is where the
models are. A headless server has no microphone, and pretending otherwise
is how a voice feature ends up mocked.
"""
from __future__ import annotations

import asyncio
import json
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles

from .. import config
from ..assistant import Vision
from ..voice.stt import SpeechToText
from ..voice.tts import TextToSpeech
from ..tasks import TaskStore

WEB = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(title="Vision")
state: dict = {}


@app.on_event("startup")
def _startup() -> None:
    config.ensure_dirs()
    t0 = time.time()
    state["vision"] = Vision()
    state["stt"] = SpeechToText()
    state["tts"] = TextToSpeech()
    state["tasks"] = TaskStore(config.DB_PATH)
    state["started"] = time.time()
    print(f"[vision] ready in {time.time()-t0:.1f}s :: "
          f"llm={'yes' if state['vision'].conversation else 'NO'} "
          f"stt={'yes' if state['stt'].available else 'NO'} "
          f"tts={'yes' if state['tts'].available else 'NO'}")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (WEB / "index.html").read_text(encoding="utf-8")


@app.get("/api/status")
def api_status() -> dict:
    v: Vision = state["vision"]
    return {"vision": v.status(),
            "stt": state["stt"].describe(),
            "tts": state["tts"].describe(),
            "config": config.describe(),
            "uptime_s": round(time.time() - state["started"], 1)}


@app.post("/api/vault")
async def api_vault(path: str = Form(...)) -> dict:
    return state["vision"].connect_vault(path)


@app.get("/api/tasks")
def api_tasks() -> list:
    return state["tasks"].recent()


@app.get("/api/memory")
def api_memory() -> dict:
    v: Vision = state["vision"]
    facts = [dict(r) for r in v.store.db.execute(
        "SELECT subject,predicate,object,recorded_at FROM facts "
        "WHERE valid_to IS NULL ORDER BY recorded_at DESC LIMIT 50")]
    eps = [dict(r) for r in v.store.recent_episodes(limit=25)]
    rules = [{"key": r.rule_key, "text": r.text, "status": r.status}
             for r in v.store.active_rules()]
    return {"facts": facts, "notes": eps, "rules": rules}


@app.delete("/api/memory/fact")
def api_forget(subject: str, predicate: str) -> dict:
    """Deletion is the user's, always. Retiring keeps the history."""
    v: Vision = state["vision"]
    v.store.retire_fact(subject, predicate, reason="user asked Vision to forget")
    return {"ok": True}


# --------------------------------------------------------------------- voice
@app.post("/api/stt")
async def api_stt(audio: UploadFile = File(...)) -> dict:
    """Browser sends a recorded blob; Whisper transcribes it."""
    stt: SpeechToText = state["stt"]
    if not stt.available:
        return JSONResponse({"error": stt.load_error or "STT unavailable"}, 503)
    raw = await audio.read()
    tmp = config.AUDIO_TMP / f"in_{uuid.uuid4().hex}"
    tmp.write_bytes(raw)
    try:
        tr = await asyncio.to_thread(stt.transcribe, str(tmp))
        return {"text": tr.text, "language": tr.language,
                "confidence": round(tr.language_confidence, 3),
                "audio_s": round(tr.duration_s, 2),
                "compute_s": round(tr.compute_s, 2),
                "realtime_factor": round(tr.realtime_factor, 1)}
    finally:
        tmp.unlink(missing_ok=True)


@app.get("/api/tts")
async def api_tts(text: str, lang: str = "en") -> Response:
    """Returns real wav bytes. The browser plays them."""
    tts: TextToSpeech = state["tts"]
    if not tts.available:
        return JSONResponse({"error": tts.load_error or "no voices installed"}, 503)
    sp = await asyncio.to_thread(tts.speak, text[:1200], lang=lang)
    return Response(content=sp.wav, media_type="audio/wav",
                    headers={"X-Vision-Voice": sp.voice,
                             "X-Vision-Duration": f"{sp.duration_s:.2f}",
                             "X-Vision-Compute": f"{sp.compute_s:.2f}"})


# ----------------------------------------------------------------- websocket
@app.websocket("/ws")
async def ws(sock: WebSocket) -> None:
    await sock.accept()
    v: Vision = state["vision"]
    session = f"ws-{uuid.uuid4().hex[:8]}"
    await sock.send_json({"type": "hello", "session": session,
                          "status": await asyncio.to_thread(v.status)})
    loop = asyncio.get_running_loop()
    try:
        while True:
            msg = await sock.receive_json()
            if msg.get("type") != "say":
                continue
            text = (msg.get("text") or "").strip()
            if not text:
                continue
            sid = msg.get("session") or session
            await sock.send_json({"type": "thinking", "text": text})

            # Agent progress is emitted from a worker thread; hop it back
            # onto the event loop so the UI sees steps as they happen
            # rather than all at once at the end.
            def emit(ev: dict) -> None:
                asyncio.run_coroutine_threadsafe(sock.send_json(ev), loop)

            reply = await asyncio.to_thread(
                v.respond, sid, text, emit, channel=msg.get("channel", "text"))
            state["tasks"].record(sid, text, reply)
            await sock.send_json({"type": "reply", **reply.as_dict()})
    except WebSocketDisconnect:
        return
    except Exception as exc:  # never die silently on the user
        try:
            await sock.send_json({"type": "error", "error": f"{type(exc).__name__}: {exc}"})
        except Exception:
            pass


if WEB.exists():
    app.mount("/static", StaticFiles(directory=str(WEB)), name="static")
