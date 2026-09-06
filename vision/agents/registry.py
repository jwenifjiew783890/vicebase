"""The agent roster.

Kept small and honest on purpose. The brief asked for coverage of a great
many capabilities; the answer is not one class per bullet point. An agent
earns its place when specialisation makes it more reliable, not when it
makes the diagram look fuller. Where several jobs share the same tools and
the same failure modes, they are one agent.
"""
from __future__ import annotations

# name -> agent CLASS. get() returns a fresh instance per call, because an
# agent accumulates steps while it runs and two concurrent tasks sharing one
# instance would interleave each other's evidence.
REGISTRY: dict[str, type] = {}


def register(cls: type) -> type:
    REGISTRY[cls.name] = cls
    return cls


def get(name: str):
    cls = REGISTRY.get(name)
    return cls() if cls else None


def all_agents() -> list[type]:
    return list(REGISTRY.values())


def describe() -> list[dict]:
    return [{"name": c.name, "description": c.description,
             "dangerous": getattr(c, "dangerous", False),
             "capabilities": getattr(c, "capabilities", [])}
            for c in REGISTRY.values()]
