---
type: working-context
category: environment
last_verified: 2026-09-03
confidence: high
---

# 10 — Technical Environment

> **WORKING CONTEXT.** Verified on the machine 2026-09-03. Re-verify before
> relying on it — running/stopped states change.

## Hardware `[verified 2026-09-03]`

| | |
| --- | --- |
| GPU | **NVIDIA GeForce RTX 4050 Laptop GPU — 6141 MiB (~6 GB VRAM)** |
| iGPU | Intel UHD Graphics |
| OS | Windows 11 Home Single Language (10.0.26200) |

The 6 GB VRAM ceiling is the practical constraint on local model size. Per
ADR-010 and the user's stated principle, hardware **advises** model
recommendations — it must never permanently remove models from Vision's
catalogue. `[vault]` `[user 2026-09-03]`

## Running services `[verified 2026-09-03]`

| Service | Address | State |
| --- | --- | --- |
| Vision (Open WebUI 0.11.3) | `127.0.0.1:8080` | running, autostarts via "Vision Backend" scheduled task |
| Obsidian Local REST API + MCP | `127.0.0.1:27124` (HTTPS) | running, loopback only |
| n8n | `127.0.0.1:5678` | running |
| Ollama | `localhost:11434` | **installed but not running** |

Ollama is present at
`C:\Users\muazm\AppData\Local\Programs\Ollama\ollama.exe` and configured in
Vision, but the service was down at verification time — so no local models
were being served.

## Platform tooling `[verified 2026-09-03]`

- **Docker** 29.7.2 (Docker Desktop)
- **WSL2** — `Ubuntu` (stopped), `docker-desktop` (running)
- **Obsidian** 1.13.7, vault at `D:\v brain\Vision Brain`
- Python 3.12 and Node 22 pinned project-locally in the Vision repo

## Model provider

Vision's OpenAI-compatible endpoint is **TokenRouter**
(`https://api.tokenrouter.com/...`), exposing ~86 models including
NVIDIA-hosted ones. `[verified 2026-09-03]`

**Credentials are not recorded in this vault** and must never be. They live in
Vision's own config store. See
[[Memory/99 - Memory Rules|99 — Memory Rules]].

## Stability note

Hardware and the Obsidian/vault paths are stable facts. Everything about
*running state*, provider choice and installed versions is working context
with a short half-life.
