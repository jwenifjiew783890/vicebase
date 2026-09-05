---
type: MOC
domain: Desktop Automation Knowledge
section: root
created: 2026-09-04
---

# Desktop Automation Knowledge

The desktop-control domain of the Vision Brain. What Vision consults when a task needs it to
drive a native Windows application — reading the screen, grounding on UI elements, clicking,
typing, and verifying that the action landed.

Part of [[Vision Brain]].

> [!important] Reference knowledge, not a shipped executor
> Vision does **not** currently have a desktop-control executor wired in. The Phase 2 plan lists
> desktop control as *planned* (a stdio MCP behind `mcpo`, admin-only, off by default), and the
> preferred self-improving layer is Hermes but **nothing is selected or installed**
> (see [[Agents/Self-Improving Agent Layer — Requirements|the requirement]]). This domain exists
> so that when a desktop executor is added, Vision already knows *how to reason about desktop
> control*. It teaches method, not a specific product. Do not read it as a claim that Vision can
> control the desktop today.

> [!important] How this domain is meant to be used
> **Retrieval is on demand and scoped.** Nothing here is copied into Open WebUI Knowledge,
> embedded wholesale, or mirrored into a second store. It is reached live through the Obsidian
> MCP tools, and only the notes a task actually needs are read. The vault stays the source of
> truth.

## Knowledge hierarchy

This domain is layered on purpose; each layer feeds the one below it.

1. **Desktop Automation Knowledge** *(this domain)* — the reasoning an agent applies to any
   desktop-control task.
2. **Hermes computer-use methodology** — the **primary external reference** for that method:
   capture→act→verify, accessibility grounding, the escalation ladder, structured verdicts,
   recovery and safety. MIT-licensed; recorded in
   [[Desktop Automation Knowledge/99 - Sources & Provenance|Sources & Provenance]].
3. **Windows UI Automation + Windows specifics** — the platform layer the method is grounded on
   ([[Desktop Automation Knowledge/02 - Windows UI Automation|note 02]], plus the Windows detail in
   notes 03–05).
4. **Vision's eventual Desktop Agent / executor** — the runtime that would *apply* all of the
   above. **Not built, not selected, not installed.**

> [!warning] Hermes is the reference, not the runtime
> Vision uses the **Hermes computer-use SKILL as a knowledge source**. That is **not** a decision to
> install Hermes Agent as Vision's desktop executor. The SKILL informs *how to reason*; choosing and
> wiring an actual desktop runtime is a separate, later, approval-gated step
> ([[Agents/Self-Improving Agent Layer — Requirements|Requirements]]). Do not conflate "we read its
> SKILL" with "we run it."

## The shelf

These are the always-applicable notes. They are the only markdown files in the domain root,
because Vision's n8n Knowledge Retriever lists a domain folder non-recursively and takes at most
six notes. Anything an agent should have *by default* lives here.

| | Note | Read it when |
| --- | --- | --- |
| 01 | [[Desktop Automation Knowledge/01 - Computer Use Fundamentals\|Computer Use Fundamentals]] | Any desktop task — the capture→act→verify loop and why it exists |
| 02 | [[Desktop Automation Knowledge/02 - Windows UI Automation\|Windows UI Automation]] | Grounding on a real Windows control instead of guessing pixels |
| 03 | [[Desktop Automation Knowledge/03 - Mouse Keyboard & Clipboard\|Mouse, Keyboard & Clipboard]] | Choosing and issuing an input action |
| 04 | [[Desktop Automation Knowledge/04 - Windows Apps Windows & Files\|Windows Apps, Windows & Files]] | Targeting an app or window, or handling a file dialog |
| 05 | [[Desktop Automation Knowledge/05 - Verification Recovery & Safety\|Verification, Recovery & Safety]] | After every action, when something fails, and before anything sensitive |
| 99 | [[Desktop Automation Knowledge/99 - Sources & Provenance\|Sources & Provenance]] | Checking where a claim came from, or how strong it is |

## The one idea to carry out of here

**Capture first, ground on an element, act, then verify the effect.** Never act on a screen you
have not just observed, never target a raw pixel when a named element is available, and never
assume an action worked without a signal that it did. Everything else in this domain is a
consequence of those four moves. See [[Desktop Automation Knowledge/01 - Computer Use Fundamentals|Computer Use Fundamentals]].

## Three kinds of claim in this domain

Every note mixes these, and they carry different weight. **Never present one as another.**

| Kind | Weight | How it is marked |
| --- | --- | --- |
| **Upstream method** | A working reference design's approach. Reasoned, not guaranteed for Vision's future executor. | Attributed to the Hermes computer-use SKILL |
| **Platform fact** | Documented Windows behaviour. | Cited to Microsoft Learn (UI Automation) |
| **Project-verified** | Something Vision confirmed on this machine. | Labelled *Vision-verified* with the date — **currently empty; nothing has been tested** |

## Rules for adding to this domain

1. **Actionable or absent.** A note earns its place by changing what the agent would do.
2. **Method, not button locations.** UI positions change between versions; the reason to observe
   before acting does not.
3. **Provenance.** Upstream method cites the SKILL. Platform fact cites Microsoft. A thing learned
   on this machine is labelled *Vision-verified* and dated — and nothing is labelled that until it
   actually is.
4. **Safety is not optional.** Any note that issues input restates the hard boundaries in
   [[Desktop Automation Knowledge/05 - Verification Recovery & Safety|note 05]].
5. **Link, do not duplicate.** One concept, one note.

## Related domains

[[Browser Knowledge/00 - Browser Knowledge|Browser Knowledge]] — the same capture→act→verify
discipline for web pages, where Auto Browser is the production executor. ·
[[Coding Knowledge/04 - Agent Engineering/00 - Agent Engineering|Agent Engineering]] — planners,
permissions and sandboxing for the layer that would drive a desktop executor.
