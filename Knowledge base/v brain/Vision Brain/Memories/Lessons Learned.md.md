# Lessons Learned

## 1. Do Not Put Everything Into Core

A feature being useful does not mean it belongs in Vision Core.

Before adding something, ask:

- Core?
- Plugin?
- Service?
- Adapter?
- External system?

## 2. Keep Integrations Removable

External integrations such as Obsidian or Blender should be removable
without requiring Vision Core to be rewritten.

## 3. Do Not Confuse the Model With the Agent

A model provides intelligence.

An agent provides a role, tools, permissions, context and workflow.

They should remain separate concepts.

## 4. Do Not Confuse the Product With the Runtime

Vision is the product.

Ollama or another inference runtime is infrastructure.

Do not architect Vision as an Ollama-only application.

## 5. Do Not Build Mature Infrastructure From Scratch

When a mature system already solves a difficult problem well, prefer
using or adapting it.

Examples:

- terminal/PTY
- local inference
- agent protocols
- UI primitives
- 3D rendering

## 6. Prove the Application Runs Early

Do not build deep services before proving the application itself can
start.

Every major implementation phase should produce something runnable.

## 7. Test Real Behavior

Compilation does not prove functionality.

Test:

- actual launch
- actual user flows
- actual integrations
- failure cases
- recovery
- regressions

## 8. Control Scope

Future ideas should be recorded rather than immediately implemented.

A feature planned for a later phase should not destabilize the current
phase.

## 9. Keep Hardware Out of Core Architecture

Hardware constraints should influence recommendations and performance
warnings.

They should not permanently remove capabilities from Vision.

## 10. Protect Security Boundaries

The renderer, terminal, filesystem, credentials, plugins and agents
must have explicit boundaries.

Never grant broad access simply because implementation is easier.

## 11. Avoid Giant Memory Files

Long-term knowledge should be structured into:

- identity
- preferences
- projects
- decisions
- memories
- lessons
- knowledge

rather than one enormous memory document.

## 12. Record Why Decisions Were Made

Future maintainers/agents need to understand not only what was chosen,
but why it was chosen.

## 13. Separate Body From Engine

Vision's UI/body should remain useful even when individual model,
runtime or agent systems are unavailable.

## 14. Follow the Development Discipline

PLAN
→ APPROVE
→ IMPLEMENT
→ TEST
→ VERIFY
→ STOP

Do not skip the verification stage.