---
type: MOC
domain: Coding Knowledge
section: 05 - Web & Application Engineering
created: 2026-09-03
---

# Web & Application Engineering

Building the thing users actually touch, and the server behind it.

Part of [[Coding Knowledge/00 - Coding Knowledge|Coding & Engineering Knowledge]].

| Note | Covers |
| --- | --- |
| [[Coding Knowledge/05 - Web & Application Engineering/Frontend Architecture\|Frontend Architecture]] | State, rendering, components, bundle size |
| [[Coding Knowledge/05 - Web & Application Engineering/Backend Architecture\|Backend Architecture]] | Layers, boundaries, background work |
| [[Coding Knowledge/05 - Web & Application Engineering/REST\|REST]] | HTTP semantics as an interface |
| [[Coding Knowledge/05 - Web & Application Engineering/WebSockets\|WebSockets]] | Real-time, and its operational cost |
| [[Coding Knowledge/05 - Web & Application Engineering/Databases\|Databases]] | Choosing, modelling, migrating, operating |
| [[Coding Knowledge/05 - Web & Application Engineering/Authentication\|Authentication]] | Proving who someone is |
| [[Coding Knowledge/05 - Web & Application Engineering/Authorization\|Authorization]] | Deciding what they may do |
| [[Coding Knowledge/05 - Web & Application Engineering/Caching\|Caching]] | The fastest win and the subtlest bugs |
| [[Coding Knowledge/05 - Web & Application Engineering/Web Performance\|Web Performance]] | What users actually perceive |
| [[Coding Knowledge/05 - Web & Application Engineering/Web Security\|Web Security]] | The attack classes that matter |

## The shape most applications should have

A boring, well-separated three-tier application with a real database, sessions or tokens handled
by a library, background work on a queue, and caching added only where measurement demanded it.
Novelty in this layer buys very little and costs a great deal.
