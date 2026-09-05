---
type: note
domain: WhatsApp Communication Knowledge
section: n8n / Manager / Plan Integration
created: 2026-09-04
---

# n8n / Manager / Plan Integration

How the WhatsApp capability plugs into the **existing** Vision hub — following the
established registry architecture, adding **no** second orchestrator.

## Source of truth

`D:\n8n\workflows\agent-registry.json` is the **generated source of truth**. The hub
(`VISION - AGENTS`), every specialist agent, the tool dispatcher and the MCP surface
are all **generated from it by `_generate_hub.py`**. Therefore:

- **Add** a WhatsApp **agent entry + its tools** to `agent-registry.json`, then
  **regenerate** — do **not** hand-edit the generated `vision-*.json` workflows.
- The architecture block is **locked** (`locked: true`); we add an agent within the
  existing hierarchy, we do not change the hierarchy.

## The registry entry (follows the existing schema)

A new agent (mirroring the shape of the browser/desktop/research agents):

```jsonc
// agents[] += 
{
  "agent_id": "whatsapp",
  "agent_name": "WhatsApp Agent",
  "domain": "whatsapp",
  "description": "Sends and reads WhatsApp messages through Vision's own logged-in number via the local WPPConnect bridge. Messaging only — no calls.",
  "capabilities": ["whatsapp_send_message", "whatsapp_send_media", "whatsapp_get_contact"],
  "workflow_id": "visionAgtWhatsapp",
  "input_schema": { "task": "string", "context": "string" },
  "output_schema": { "ok": "boolean", "agent_id": "string", "tool_id": "string", "result": "string" },
  "status": "poc", "enabled": false,
  "risk_level": "write",
  "permissions": ["outbound_whatsapp_loopback"],
  "executor": "wppconnect-bridge",
  "version": "0.1",
  "knowledge_domains": ["WhatsApp Communication Knowledge"],
  "knowledge_mode": "inject",
  "architecture_group": "comms"
}
```

```jsonc
// tools[] += (only operations the backend actually supports — NO call ops, see 07)
{ "tool_id": "whatsapp_send_message", "name": "WhatsApp Send Message", "agent": "whatsapp",
  "description": "Send a WhatsApp text to a resolved, trusted contact via the local bridge.",
  "inputs": { "to": "resolved WhatsApp id / number (never raw text)", "text": "message body" },
  "output": "sent/failed + message id", "workflow_id": "visionWhatsappSend",
  "enabled": false, "risk_level": "write", "typical_seconds": 5, "version": "0.1",
  "accepts_knowledge": true, "material_field": "text" }
// + whatsapp_send_media, whatsapp_get_contact (same shape)
```

- `enabled:false`, `status:"poc"` until the live PoC passes — nothing routes to it by
  accident.
- **No `start_call` / `end_call` / `get_call_state`** — call support is unverified
  and blocked ([[WhatsApp Communication Knowledge/07 - WhatsApp Calling\|07]]);
  fabricating those tools is forbidden.

## Regeneration procedure (safe, backed up)

1. Back up: copy `agent-registry.json` → `agent-registry.json.bak-prewhatsapp-<ts>`.
2. Add the agent + tool entries above.
3. `python _generate_hub.py` (regenerates the hub, agents, dispatcher, MCP surface).
4. Import the regenerated workflows into n8n; smoke-test the hub still routes the
   existing agents.

> [!warning] Concurrency
> As of 2026-09-04 the registry and `_generate_hub.py` are being actively edited by
> another session (backups timestamped ~03:39–03:42). **Do not regenerate during that
> window** — it would clobber in-flight changes. Apply this in a clean window, after
> re-reading the current registry, with a fresh backup.

## Incoming entry point

The bridge's webhook → an **n8n Webhook node** → allowlist gate
([[WhatsApp Communication Knowledge/10 - Security and Trust Model\|10]]) → the
**existing Manager** (`VISION - AGENTS`) with the message text as task material. The
Manager plans and routes exactly as for a typed request — WhatsApp is just another
entry door, not a new planner.

## Plan Registry

`D:\n8n\workflows\plan-registry.json` holds reusable plans. WhatsApp appears as
**stages**, not as its own plan engine:

```
PLAN "Remote Vision Chat":  WhatsApp event → Intent → Manager decides
                            → execute (Browser/Desktop/LLM) → WhatsApp reply
PLAN "Contact Person":      resolve contact (05) → prepare message → send → report
PLAN "WhatsApp Voice Call": DEFERRED — blocked at call audio (07/08); not built
```

Build only the **capability boundary** now; the voice-call plan stays documented-only
until the blocker is lifted.
