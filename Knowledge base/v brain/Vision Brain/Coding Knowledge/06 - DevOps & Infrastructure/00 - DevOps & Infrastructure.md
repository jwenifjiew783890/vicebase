---
type: MOC
domain: Coding Knowledge
section: 06 - DevOps & Infrastructure
created: 2026-09-03
---

# DevOps & Infrastructure

Running software: containers, hosts, networks, processes, deployment and the signals that tell you it is alive.

Part of [[Coding Knowledge/00 - Coding Knowledge|Coding & Engineering Knowledge]].

| Note | Covers |
| --- | --- |
| [[Coding Knowledge/06 - DevOps & Infrastructure/Docker\|Docker]] | Images, layers, volumes, networking, the failure modes |
| [[Coding Knowledge/06 - DevOps & Infrastructure/WSL\|WSL]] | The Windows/Linux boundary and its resource behaviour |
| [[Coding Knowledge/06 - DevOps & Infrastructure/Linux\|Linux]] | The commands and concepts used during diagnosis |
| [[Coding Knowledge/06 - DevOps & Infrastructure/Windows Services\|Windows Services]] | Services, scheduled tasks, autostart |
| [[Coding Knowledge/06 - DevOps & Infrastructure/Networking\|Networking]] | Diagnosing connectivity, layer by layer |
| [[Coding Knowledge/06 - DevOps & Infrastructure/Processes & Resources\|Processes & Resources]] | Measuring CPU, memory and I/O honestly |
| [[Coding Knowledge/06 - DevOps & Infrastructure/Deployment\|Deployment]] | Getting a change to production safely |
| [[Coding Knowledge/06 - DevOps & Infrastructure/Logging\|Logging]] | Producing logs worth reading |
| [[Coding Knowledge/06 - DevOps & Infrastructure/Monitoring\|Monitoring]] | Knowing before the user tells you |
| [[Coding Knowledge/06 - DevOps & Infrastructure/Backups\|Backups]] | The only thing that matters is the restore |
| [[Coding Knowledge/06 - DevOps & Infrastructure/Secrets & Configuration\|Secrets & Configuration]] | Keeping credentials out of everything |

## The operating principle

**Measure before changing, and change one thing at a time.** Infrastructure work is
disproportionately prone to the "I changed five things and now it works" outcome, which teaches
nothing and cannot be repeated.
