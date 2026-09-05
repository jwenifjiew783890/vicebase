"""End-to-end walkthrough with a stub model. Proves the pieces compose."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pai.memory import MemoryStore
from pai.obsidian import VaultIndex, TfidfEmbedder
from pai.orchestrator import Orchestrator
from pai.gateway import Action, Channel, Gateway
from pai.trust import Trust


class StubConversation:
    """Echoes what it was given so the plumbing is visible."""
    def respond(self, system, history, user, context):
        tag = "GROUNDED" if context else "internal"
        return f"<{tag} reply to {user!r}; ctx={len(context)}c; sys={len(system)}c>"


class StubPlanner:
    def plan(self, user, memory):
        u = user.lower()
        if "opencode" in u and ("fix" in u or "build" in u or "implement" in u):
            return [Action("code.delegate",
                           {"repo": "vicebase", "task": user}, reason="user asked")]
        if "open" in u:
            app = "opencode" if "opencode" in u else "obsidian"
            return [Action("app.open", {"app": app}, reason="user asked")]
        if "delete" in u:
            return [Action("file.delete", {"path": "/vault/old.md"}, reason="user asked")]
        return []


VAULT = {
 "Projects/ViceBase.md": "# ViceBase\n## Auth decisions\nWe chose passkeys over "
   "passwords. Codename Thornbury. See [[Passkey Rollout]].\n",
 "Projects/Passkey Rollout.md": "# Passkey Rollout\n\nPhase 1 ships in March.\n",
}

store = MemoryStore()
vault = VaultIndex(TfidfEmbedder())
for p, t in VAULT.items():
    vault.add_note(p, t)
vault.build_vectors()
store.assert_fact("muaz", "editor", "neovim", Trust.USER)
store.assert_fact("muaz", "timezone", "IST", Trust.USER)

orch = Orchestrator(store, vault, StubConversation(), StubPlanner())

TURNS = [
    ("hey", Channel.TEXT),
    ("what did we decide about auth", Channel.TEXT),
    ("what's a for loop", Channel.TEXT),
    ("what's the latest nextjs version", Channel.TEXT),
    ("kya haal hai", Channel.TEXT),
    ("open opencode and fix the failing test", Channel.TEXT),
    ("delete the old notes", Channel.VOICE),
    ("bhai thoda chhota rakho", Channel.TEXT),
]

print(f"{'USER':46} {'PATH':10} {'LANG':9} ACK / ACTION")
print("-" * 108)
for text, ch in TURNS:
    r = orch.handle("demo", text, ch)
    bits = []
    if r.ack:
        bits.append(f"ack={r.ack!r}")
    for a in r.actions:
        bits.append(f"ran {a.action.name}[{a.status.value}]")
    for d in r.pending:
        bits.append(f"{d.action.name} -> {d.verdict.name}")
    if r.route.inject:
        bits.append(f"vault x{len(r.route.inject)}")
    print(f"{text[:44]:46} {r.route.path.value:10} {r.route.lang:9} "
          f"{'; '.join(bits) or '-'}")

print(f"\nsystem prompt: {orch.build_system_prompt('en').__len__()} chars")
print(f"audit entries: {len(orch.gateway.audit)}")
print("\nrouting reasons:")
for text, ch in TURNS[:5]:
    print(f"  {text[:40]:42} {orch.router.route(text, vault.search(text, k=4)).why()}")
