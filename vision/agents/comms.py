"""Communication: WhatsApp and email.

The honest position on WhatsApp, stated in code because it decides the
design:

There are three ways to reach WhatsApp programmatically.

1. **The official Cloud API** (graph.facebook.com). Supported, legitimate,
   and needs credentials the user creates: a Meta app, a business phone
   number id, and a token. This is what is implemented.
2. **Unofficial web libraries** (whatsapp-web.js, Baileys) which drive a
   logged-in WhatsApp Web session. They work, they violate WhatsApp's terms,
   and they get numbers banned. The brief said never bypass security
   mechanisms, so this is not implemented and will not be.
3. **Driving the WhatsApp desktop app** through the computer-automation
   layer. Legitimate -- it is the user operating their own client -- and
   available through the `desktop` agent on a machine with a screen.

So: without credentials this agent reports EXTERNAL DEPENDENCY and does
nothing. It never claims a message was sent. Sending always requires an
explicit confirmation, because an assistant that can message people on your
behalf without asking is a different and much worse product.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

from .base import BaseAgent, AgentContext, AgentResult
from .registry import register

GRAPH = "https://graph.facebook.com/v21.0"


def whatsapp_config() -> dict:
    return {
        "token": os.environ.get("VISION_WHATSAPP_TOKEN", ""),
        "phone_id": os.environ.get("VISION_WHATSAPP_PHONE_ID", ""),
        "default_to": os.environ.get("VISION_WHATSAPP_TO", ""),
    }


def smtp_config() -> dict:
    return {
        "host": os.environ.get("VISION_SMTP_HOST", ""),
        "port": int(os.environ.get("VISION_SMTP_PORT", "587")),
        "user": os.environ.get("VISION_SMTP_USER", ""),
        "password": os.environ.get("VISION_SMTP_PASSWORD", ""),
        "from": os.environ.get("VISION_SMTP_FROM", ""),
    }


@register
class WhatsAppAgent(BaseAgent):
    name = "whatsapp"
    description = "Sends WhatsApp messages through the official Cloud API."
    capabilities = ["whatsapp.send"]
    dangerous = True
    wants_utterance = True

    def available(self) -> tuple[bool, str]:
        cfg = whatsapp_config()
        missing = [k for k in ("token", "phone_id") if not cfg[k]]
        if missing:
            return False, (
                "WhatsApp needs credentials that only you can create. Set "
                "VISION_WHATSAPP_TOKEN and VISION_WHATSAPP_PHONE_ID from a "
                "Meta Cloud API app (developers.facebook.com -> WhatsApp). "
                "Until then I will not pretend to send anything.")
        return True, ""

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        ok, why = self.available()
        if not ok:
            return self.result("WhatsApp isn't connected.", why)

        cfg = whatsapp_config()
        # Recipient: an explicit number in the message, else the configured one.
        digits = [w.strip("+ ,.") for w in task.split()
                  if w.strip("+ ,.").isdigit() and len(w.strip("+ ,.")) >= 8]
        to = digits[0] if digits else cfg["default_to"]
        if not to:
            return self.result(
                "I need a recipient.",
                "Include the number, or set VISION_WHATSAPP_TO.")

        body = task
        for marker in (" saying ", " that says ", ": "):
            if marker in task:
                body = task.split(marker, 1)[1].strip()
                break

        confirmed = ctx and getattr(ctx, "confirmed", False)
        if not confirmed:
            # Outbound messages to real people are confirmed, always.
            return self.result(
                f"Ready to WhatsApp {to}.",
                f"Message: {body!r}\n\nNothing has been sent. Confirm and I "
                f"will send exactly this.",
                needs_confirmation={"action": "whatsapp.send", "to": to,
                                    "body": body,
                                    "reason": "messaging a real person"})

        def _send():
            payload = json.dumps({
                "messaging_product": "whatsapp", "to": to,
                "type": "text", "text": {"body": body[:4000]}}).encode()
            req = urllib.request.Request(
                f"{GRAPH}/{cfg['phone_id']}/messages", data=payload,
                method="POST",
                headers={"Authorization": f"Bearer {cfg['token']}",
                         "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)

        out = self.step("whatsapp.send", f"to {to}", _send, ctx)
        if out is None:
            return self.result("The message did not send.",
                               "See the step error. Nothing was delivered.")
        return self.result(f"Sent to {to}.", json.dumps(out)[:500])


@register
class EmailAgent(BaseAgent):
    name = "email"
    description = "Drafts and sends email over SMTP."
    capabilities = ["email.draft", "email.send"]
    dangerous = True
    wants_utterance = True

    def available(self) -> tuple[bool, str]:
        cfg = smtp_config()
        if not cfg["host"] or not cfg["user"]:
            return False, ("Email needs an SMTP account. Set VISION_SMTP_HOST, "
                           "VISION_SMTP_USER, VISION_SMTP_PASSWORD and "
                           "VISION_SMTP_FROM. Drafting works without them.")
        return True, ""

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        recipients = [w.strip("<>,;") for w in task.split() if "@" in w]
        drafting = ("draft" in task.lower() or not recipients)

        if drafting or ctx.llm is not None:
            draft = None
            if ctx.llm is not None:
                draft = self.step("email.draft", task[:70], lambda: ctx.llm(
                    "Write a short email for this request. Give a Subject: "
                    "line then the body. No commentary.\n\n" + task,
                    max_tokens=320), ctx)
            if drafting:
                return self.result(
                    "Drafted it -- nothing sent.",
                    draft or "No model is loaded, so I could not draft.")

        ok, why = self.available()
        if not ok:
            return self.result("Email isn't connected.", why)
        if not recipients:
            return self.result("I need a recipient address.")

        return self.result(
            f"Ready to email {recipients[0]}.",
            "Nothing has been sent. Confirm and I will send it.",
            needs_confirmation={"action": "email.send", "to": recipients[0],
                                "reason": "sending mail to a real person"})
