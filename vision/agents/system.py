"""Computer automation, and MCP tools.

Both are here because they share one property: they reach outside Vision
into something that can do real damage, so both go through the capability
gateway and both refuse rather than guess.

DesktopAgent needs a graphical session. On a headless machine it says so
instead of pretending -- an automation agent that silently no-ops is worse
than one that is absent, because the user believes the work was done.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from .base import BaseAgent, AgentContext, AgentResult
from .registry import register


# --------------------------------------------------------------------------
@register
class DesktopAgent(BaseAgent):
    name = "desktop"
    description = ("Controls the computer: launches apps, types, clicks, "
                   "takes screenshots. Requires a graphical session.")
    capabilities = ["app.launch", "screen.shot", "input.type", "input.click"]
    dangerous = True
    wants_utterance = True

    def available(self) -> tuple[bool, str]:
        """Honest about the two ways this can be unavailable."""
        if os.name != "nt" and not (os.environ.get("DISPLAY")
                                    or os.environ.get("WAYLAND_DISPLAY")):
            return False, ("no graphical session (no DISPLAY). Desktop "
                           "automation needs a desktop; this machine is "
                           "headless.")
        try:
            import pyautogui  # noqa: F401
        except Exception as exc:
            return False, (f"pyautogui not installed: {exc}. "
                           f"`pip install pyautogui`")
        return True, ""

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        ok, why = self.available()
        if not ok:
            # Not a failure of the request -- a fact about the machine.
            return self.result("I can't drive the desktop here.", why)

        import pyautogui
        pyautogui.FAILSAFE = True
        low = task.lower()

        if "screenshot" in low or "what's on screen" in low:
            from .. import config
            out = config.HOME / "shots" / "desktop.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            self.step("screen.shot", str(out),
                      lambda: pyautogui.screenshot(str(out)), ctx)
            return self.result("Took a screenshot of the desktop.",
                               str(out),
                               artifacts=[{"type": "image", "path": str(out)}])

        launch = None
        for verb in ("open ", "launch ", "start "):
            if low.startswith(verb) or f" {verb}" in low:
                launch = task.split(verb, 1)[1].strip().strip(".!")
                break
        if launch:
            app = launch.split()[0]
            path = shutil.which(app)
            if not path and os.name != "nt":
                return self.result(
                    f"I couldn't find an application called {app!r}.",
                    "Nothing was launched.")
            # Launching a program is IRREVERSIBLE-adjacent: it is confirmed,
            # never assumed, and the confirmation is the user's to give.
            return self.result(
                f"Ready to launch {app!r}.", f"Resolved to {path or app}.",
                needs_confirmation={"action": "app.launch", "app": app,
                                    "path": path or app,
                                    "reason": "launching a program"})

        return self.result(
            "I understood that as desktop automation but not what to do.",
            "I can take a screenshot, or launch an application. Typing and "
            "clicking need a target I can see first.")


# --------------------------------------------------------------------------
@register
class McpAgent(BaseAgent):
    name = "mcp"
    description = "Calls tools provided by connected MCP servers."
    capabilities = ["mcp.list", "mcp.call"]
    dangerous = True
    wants_utterance = True

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        registry = getattr(ctx, "mcp", None)
        if registry is None or not registry.servers:
            return self.result(
                "No MCP servers are connected.",
                "Connect one in Settings -> Plugins, or with "
                "POST /api/mcp/connect.")

        tools = registry.tools()
        listing = "\n".join(f"- `{t.name}` ({t.server}): {t.description[:110]}"
                            for t in tools[:30])
        low = task.lower()
        if any(w in low for w in ("what tools", "list tools", "which tools",
                                  "what can you", "available tools")):
            self.step("mcp.list", f"{len(tools)} tools",
                      lambda: [t.name for t in tools], ctx)
            return self.result(f"{len(tools)} MCP tools are connected.", listing)

        # Pick the tool by name mentioned in the request. Deliberately
        # literal: guessing which tool the user meant, and guessing its
        # arguments, is how an agent deletes the wrong thing.
        named = next((t for t in tools if t.name.lower() in low), None)
        if named is None:
            return self.result(
                "I couldn't tell which MCP tool you meant.",
                "Name it explicitly. Connected tools:\n" + listing)

        args: dict = {}
        props = (named.schema or {}).get("properties", {})
        required = (named.schema or {}).get("required", [])
        for key in required:
            if key in ("path", "file", "filename"):
                token = next((w for w in task.split()
                              if "/" in w or "." in w), None)
                if token:
                    args[key] = token.strip("`'\"")
        missing = [k for k in required if k not in args]
        if missing:
            return self.result(
                f"`{named.name}` needs {', '.join(missing)}.",
                f"Schema: {list(props)}. Say it explicitly and I'll run it.")

        out = self.step("mcp.call", f"{named.name} {args}",
                        lambda: registry.call(named.name, args), ctx)
        if out is None:
            return self.result(f"`{named.name}` failed.", "See the step error.")
        return self.result(f"Ran MCP tool `{named.name}`.", str(out)[:3000])
