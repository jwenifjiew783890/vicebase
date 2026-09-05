# Important Long-Term Memories

## Vision Is the Primary Long-Term Project

Vision is the user's major long-term AI platform project.

The objective is to create a unified AI environment that can eventually
replace the need for separate AI applications for normal AI work,
coding, local models, agents, tools and integrations.

## Vision Product Philosophy

Vision is the platform/interface.

Models, runtimes, agents, tools, memory systems and integrations are
replaceable components.

## Modular Architecture

Vision Core should remain stable and relatively small.

Optional functionality should be isolated through plugins, adapters or
services whenever practical.

## External Knowledge

Obsidian is intended to serve as an external knowledge/memory layer.

The Obsidian vault is independent from Vision Core.

## Development Philosophy

Important development decisions should be deliberate rather than rushed.

Preferred workflow:

PLAN → REVIEW → APPROVE → IMPLEMENT → TEST → VERIFY

## Infrastructure Philosophy

Prefer mature, proven infrastructure instead of unnecessarily
reimplementing difficult systems.

## Model Independence

Vision should remain capable of using:

- local models
- remote models
- API providers
- different runtimes
- future inference systems

No single model or runtime should define Vision.

## Agent Independence

Agents are replaceable workers.

Different agents/models may be used for different purposes.

## Long-Term Extensibility

New capabilities should be addable without repeatedly rewriting the
Vision Core architecture.

## Hardware Neutrality

Hardware should influence recommendations and performance expectations,
not permanently define what Vision can support.