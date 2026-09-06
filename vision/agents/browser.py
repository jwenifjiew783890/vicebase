"""Browser automation: a real headless browser, driven for real.

Playwright rather than an HTTP client, because the point of a browser agent
is the pages an HTTP client cannot read -- ones that render their content
with JavaScript. `web.search` handles the cheap case; this handles the case
where you have to actually load the page.

Every navigation and extraction is a Step, so a page that failed to load
cannot be reported as a page that was read.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from .base import BaseAgent, AgentContext, AgentResult
from .registry import register

# Where the sandboxed Chromium lives. Overridable because the path differs
# between this container and a normal install.
CHROME = os.environ.get(
    "VISION_CHROME",
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")

_URL = re.compile(r"https?://[^\s'\"<>]+")


@register
class BrowserAgent(BaseAgent):
    name = "browser"
    description = "Opens real web pages in a browser and reads what renders."
    capabilities = ["browser.open", "browser.read", "browser.screenshot"]
    dangerous = True          # it fetches and executes remote content
    # The URL is the whole request, and the dispatcher's trigger pattern
    # overlaps it: "open http://x" matched "open http://" and stripping the
    # trigger left "x" with no scheme, so the agent saw no URL and ran
    # nothing. Same shape as the "run git status" -> "status" bug.
    wants_utterance = True

    def available(self) -> tuple[bool, str]:
        try:
            import playwright  # noqa: F401
        except Exception as exc:
            return False, f"playwright not installed: {exc}"
        if not Path(CHROME).exists():
            return False, (f"no browser at {CHROME}. Install one with "
                           f"`playwright install chromium`, or set "
                           f"VISION_CHROME.")
        return True, ""

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        ok, why = self.available()
        if not ok:
            return self.result("The browser isn't available.", why)

        m = _URL.search(task)
        if not m:
            return self.result(
                "I need a URL to open.",
                "Give me a link, or ask the web agent to search first.")
        url = m.group(0)

        from playwright.sync_api import sync_playwright

        payload: dict = {}

        def _visit():
            with sync_playwright() as pw:
                browser = pw.chromium.launch(
                    executable_path=CHROME,
                    args=["--no-sandbox", "--disable-dev-shm-usage"])
                try:
                    page = browser.new_page(
                        viewport={"width": 1280, "height": 900})
                    page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    page.wait_for_timeout(1200)
                    payload["title"] = page.title()
                    payload["url"] = page.url
                    payload["text"] = page.evaluate(
                        "() => document.body ? document.body.innerText : ''"
                    )[:6000]
                    payload["links"] = page.eval_on_selector_all(
                        "a[href]",
                        "els => els.slice(0,25).map(e => "
                        "({text: e.innerText.trim().slice(0,80), href: e.href}))")
                    from .. import config
                    shot = config.HOME / "shots"
                    shot.mkdir(parents=True, exist_ok=True)
                    path = shot / f"page_{abs(hash(url)) % 10**8}.png"
                    page.screenshot(path=str(path))
                    payload["shot"] = str(path)
                    return f"{payload['title']} ({len(payload['text'])} chars)"
                finally:
                    browser.close()

        out = self.step("browser.open", url, _visit, ctx)
        if out is None:
            return self.result(f"Couldn't open {url}.",
                               "The navigation failed -- see the step error.")

        text = payload.get("text", "").strip()
        summary = f"Opened {payload.get('title') or url}."
        body = text[:2500]
        if ctx.llm is not None and text:
            digest = self.step(
                "llm.summarise", f"{len(text)} chars",
                lambda: ctx.llm(
                    "Summarise this page in 4 sentences. Use only what is "
                    "here.\n\n" + text[:5000], max_tokens=220), ctx)
            if digest:
                body = digest.strip() + "\n\n---\n" + text[:1200]

        return self.result(summary, body, artifacts=[
            {"type": "page", "url": payload.get("url"),
             "title": payload.get("title"), "screenshot": payload.get("shot")},
            {"type": "links", "items": [
                {"title": l["text"], "url": l["href"]}
                for l in payload.get("links", [])[:10] if l["text"]]},
        ])
