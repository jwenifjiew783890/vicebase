---
type: note
domain: Browser Knowledge
created: 2026-09-04
---

# Browser Sessions & Lifecycle

How Auto Browser sessions are created, reused, isolated, and handed to a human. Getting the session
model right is what makes browser work repeatable instead of flaky.

Part of [[Browser Knowledge/00 - Browser Knowledge|Browser Knowledge]].

## What a session owns

Each Auto Browser session owns:

- **one browser context and a primary page**,
- **one artifact directory** (where screenshots and captured downloads land),
- an **optional auth-state file** and a reference to a reusable **auth profile**,
- **one lock** that serialises actions — so actions within a session run in order, not concurrently.

The base ("POC") setup allows **one active session per node**. Plan browser work as a sequence
within a session, not as parallel clicks.

## Creating and driving a session

Start with `browser.create_session`, then navigate and act within it
([[Browser Knowledge/02 - Auto Browser Tools & Actions|Tools & Actions]]). Because actions are
locked/sequential, the mental model is a single operator working one page at a time — capture, act,
verify, repeat.

## Auth profiles — reusing a logged-in state

Rather than logging in every run, Auto Browser can **save auth state as a named profile**
(`browser.save_auth_profile`) and reuse it for a later session scoped to that account. Profiles are:

- **encrypted at rest** (`AUTH_STATE_ENCRYPTION_KEY`; can be *required* via
  `REQUIRE_AUTH_STATE_ENCRYPTION`),
- **max-age enforced** — stale auth state expires rather than lingering.

This is the sanctioned way to handle logged-in sessions. Two disciplines:

- **The user logs in, not the agent.** Credential entry is a human step (hand-over via noVNC,
  below); the agent reuses the resulting profile. The agent never types passwords
  ([[Browser Knowledge/05 - Navigation Downloads & Security|note 05]]).
- **Treat a profile as a secret.** It is a logged-in session in a file — the same handling class as
  the Obsidian API key stored in Vision's `webui.db` ([[Integrations/00 - Integrations|Integrations]]).

## Isolation — `docker_ephemeral`

For stronger separation, the `docker_ephemeral` mode provisions **a fresh browser-node container
per session**, each with its own Playwright endpoint and its own noVNC port. Use it when sessions
must not share cookies/state, or when running something you don't want touching a persistent
profile.

## Human takeover (noVNC) — the recovery path

Auto Browser exposes the live browser over **noVNC** so a human can take over. It is explicitly the
**recovery path** for the cases automation should *not* push through:

- a login that needs credentials,
- an MFA / 2FA challenge,
- genuine model uncertainty about what to click.

The philosophy is "keep the workflow moving" by handing control to a person at the hard moment —
not to eliminate the human. When you hit one of these, **hand over**; do not try to automate around
a login wall or a 2FA prompt (also a hard rule — [[Browser Knowledge/05 - Navigation Downloads & Security|note 05]]).

## Tabs and pages

A session has a primary page; additional pages/tabs are managed within the session. General
browser-automation tab discipline (one task per tab, discover tabs before assuming which is
active, first navigation opens the task's tab) is in
[[Browser Knowledge/10 - Reference Methodology/00 - Reference Methodology|Reference Methodology]].

> [!warning] Not yet Vision-verified
> Session ownership, one-active-session, auth-profile behaviour, `docker_ephemeral` and noVNC
> takeover are **upstream capability** from Auto Browser's docs. Vision has not exercised them.
> Verify the actual session limits and profile lifetimes on this machine before depending on them.

> [!info] Provenance
> **Upstream capability** from the **Auto Browser** `docs/architecture.md` (MIT, © LvcidPsyche;
> ~v1.5.0), retrieved 2026-09-04. Config keys (`AUTH_STATE_ENCRYPTION_KEY`,
> `REQUIRE_AUTH_STATE_ENCRYPTION`, `docker_ephemeral`) quoted as identifiers. **Derived, not
> copied.** Record: [[Browser Knowledge/99 - Sources & Provenance|Sources & Provenance]].
