"""Drive the real Vision UI in a real browser.

The end-to-end API test proves the server works. This proves the thing the
user actually touches works: the page renders, the WebSocket connects, a
typed turn produces a reply on screen, and the TTS request is issued.

Audio itself cannot be verified here -- this container has no sound card,
so the browser's speaker output goes nowhere. What IS verified is that the
page asks for the audio and that the server answers with real wav bytes.
"""
from __future__ import annotations

import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"


def main() -> int:
    results = []

    def check(name, ok, detail=""):
        results.append((name, bool(ok), detail))
        print(f"  {'PASS' if ok else 'FAIL'}  {name}\n        {detail}", flush=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
            args=["--no-sandbox", "--use-fake-ui-for-media-stream",
                  "--use-fake-device-for-media-stream"])
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        console, requests = [], []
        page.on("console", lambda m: console.append(f"{m.type}: {m.text}"))
        page.on("request", lambda r: requests.append(r.url))

        page.goto(BASE, wait_until="networkidle", timeout=60000)
        check("1. page loads", page.title() == "Vision", f"title={page.title()!r}")

        errors = [c for c in console if c.startswith("error")]
        check("2. no javascript errors", not errors, errors[:3] or "clean console")

        page.wait_for_function("() => document.querySelector('#pilltext')"
                               "?.textContent === 'ready'", timeout=30000)
        check("3. websocket connected", True,
              f"state pill reads {page.inner_text('#pilltext')!r}")

        nodes = page.eval_on_selector_all("#nodes .node", "els => els.map(e => e.textContent)")
        check("4. agent ring rendered", len(nodes) == 8, f"{nodes}")

        page.fill("#input", "hey, keep it short")
        page.click("#send")
        page.wait_for_selector(".msg .bubble", timeout=20000)
        check("5. user message appears", "hey" in page.inner_text(".msg"),
              page.inner_text(".msg")[:60].replace("\n", " "))

        page.wait_for_function(
            "() => document.querySelectorAll('.msg').length >= 2", timeout=240000)
        msgs = page.eval_on_selector_all(".msg", "els => els.map(e => e.innerText)")
        reply = msgs[-1]
        check("6. assistant replies in the UI", len(reply) > 5,
              reply[:100].replace("\n", " | "))

        page.wait_for_timeout(3000)
        tts = [u for u in requests if "/api/tts" in u]
        check("7. UI requests spoken audio", bool(tts),
              tts[0][:90] if tts else "no /api/tts request was made")

        # Playback itself is NOT verifiable here: this container has no
        # sound card, so the browser's audio output goes nowhere and
        # play() rejects. What is verifiable is that the page asked for
        # the audio (check 7) and that the server answered with real wav
        # bytes (the API suite's check P). The last link -- speaker --
        # needs the user's machine.
        state = page.inner_text("#pilltext").lower()
        check("8. UI returns to a usable state after speaking",
              state in ("ready", "speaking — tap to stop", "stopped"),
              f"pill={state!r} (audio playback unverifiable: no sound card)")

        page.screenshot(path="/tmp/vision_ui.png", full_page=False)
        check("9. screenshot captured", True, "/tmp/vision_ui.png")

        page.click(".tabs button[data-tab='memory']")
        page.wait_for_timeout(1500)
        mem = page.inner_text("#rightpane")
        # The panel uppercases its headings in CSS, so match case-insensitively.
        check("10. memory panel renders", "facts" in mem.lower(),
              mem[:70].replace("\n", " | "))

        browser.close()

    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n{'='*60}\n  {passed}/{len(results)} browser checks passed\n{'='*60}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
