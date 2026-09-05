---
type: MOC
domain: Browser Knowledge
created: 2026-09-03
updated: 2026-09-04
---

# Browser Knowledge

The browser-control domain of the Vision Brain. What Vision consults when a task needs it to drive
a real web browser — navigating, observing a page, grounding on elements, clicking, typing, and
downloading — safely and verifiably.

Part of [[Vision Brain]].

> [!important] Vision's browser executor is Auto Browser
> **[Auto Browser](https://github.com/LvcidPsyche/auto-browser) is the production browser executor
> for Vision.** It is a local-first, MCP-native browser control plane (Playwright under the hood).
> The always-on notes below describe *how to reason about driving it*. The supplemental
> [[Browser Knowledge/10 - Reference Methodology/00 - Reference Methodology|Reference Methodology]]
> subfolder holds general browser-automation method and a **reference-only** summary of Browser
> Use — which Vision does **not** use as an executor.

> [!important] How this domain is meant to be used
> **Retrieval is on demand and scoped.** Nothing here is copied into Open WebUI Knowledge or
> mirrored into a second store. It is reached live through the Obsidian MCP tools, and only the
> notes a task actually needs are read. The vault stays the source of truth.

## The shelf

The always-applicable notes. They are the only markdown files in the domain root, because Vision's
n8n Knowledge Retriever lists a domain folder non-recursively and takes at most six notes.

| | Note | Read it when |
| --- | --- | --- |
| 01 | [[Browser Knowledge/01 - Auto Browser Architecture\|Auto Browser Architecture]] | Understanding what the executor actually is and how to reach it |
| 02 | [[Browser Knowledge/02 - Auto Browser Tools & Actions\|Auto Browser Tools & Actions]] | Choosing which tool/action to call |
| 03 | [[Browser Knowledge/03 - Browser Sessions & Lifecycle\|Browser Sessions & Lifecycle]] | Starting, reusing, isolating or handing over a session |
| 04 | [[Browser Knowledge/04 - Observation & Element Grounding\|Observation & Element Grounding]] | Reading page state and targeting an element |
| 05 | [[Browser Knowledge/05 - Navigation Downloads & Security\|Navigation, Downloads & Security]] | Navigating, submitting forms, downloading, and the approval rails |
| 99 | [[Browser Knowledge/99 - Sources & Provenance\|Sources & Provenance]] | Checking where a claim came from, or how strong it is |

Reached by search (the second shelf):
[[Browser Knowledge/10 - Reference Methodology/00 - Reference Methodology|10 - Reference Methodology]]
— general browser-automation reasoning and the Browser Use reference.

## The one idea to carry out of here

**Observe the page, ground on an element, act, then verify — and don't open a browser you don't
need.** A plain HTTP fetch beats a browser session for reading public content; a browser earns its
cost only when a task needs interaction, a logged-in session, JavaScript rendering, or a
bot-protected page. See
[[Browser Knowledge/10 - Reference Methodology/00 - Reference Methodology|Reference Methodology]].

## Three kinds of claim in this domain

| Kind | Weight | How it is marked |
| --- | --- | --- |
| **Upstream capability** | What Auto Browser's repo/docs describe | Attributed to the Auto Browser docs + version |
| **Reference method** | General or Browser-Use methodology, informational only | Labelled *reference only* |
| **Project-verified** | Confirmed by Vision's own integration testing | Labelled *Vision-verified* + date — **currently empty; not yet integration-tested** |

## Rules for adding to this domain

1. **Actionable or absent.** A note earns its place by changing what the agent would do.
2. **Auto Browser is the executor.** Method notes may cite other tools, but keep them clearly
   labelled reference-only; the production path is Auto Browser.
3. **Provenance.** Upstream capability cites the repo + version. A thing learned in our own testing
   is labelled *Vision-verified* and dated — and nothing is, yet.
4. **Security rails are part of the capability.** Any note that acts on a page respects the
   approvals and boundaries in [[Browser Knowledge/05 - Navigation Downloads & Security|note 05]].
5. **Link, do not duplicate.** One concept, one note.

## Related domains

[[Desktop Automation Knowledge/00 - Desktop Automation Index|Desktop Automation Knowledge]] — the
same capture→act→verify discipline for native apps. ·
[[Integrations/00 - Integrations|Integrations]] — where Auto Browser is registered as an external
system. · [[Coding Knowledge/04 - Agent Engineering/00 - Agent Engineering|Agent Engineering]] —
permissions and sandboxing for tool-using agents.
