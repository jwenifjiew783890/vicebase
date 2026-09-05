"""Trust levels for content provenance.

The single most important security invariant in this system:

    Content that came from outside the user can never cause a memory write
    and can never cause an action to execute.

Prompt injection in a web page or an Obsidian note is only dangerous if the
component that reads it can also write memory or emit actions. This module
makes that a type-level property rather than a convention.
"""
from __future__ import annotations

from enum import IntEnum


class Trust(IntEnum):
    """Ordered by privilege. Higher = more trusted."""

    RETRIEVED = 0   # web pages, Obsidian notes, tool output. NEVER privileged.
    AGENT = 1       # output of a delegated agent (OpenCode etc). Still untrusted.
    MODEL = 2       # the local LLM's own generation. May propose, never commit.
    USER = 3        # something the user actually said or typed.
    SYSTEM = 4      # operator config, protected rules. Highest.

    @property
    def may_write_memory(self) -> bool:
        """Only the user (or system config) can cause a durable memory write.

        The model may *propose* a memory (that is what the learning loop does),
        but the proposal must be anchored to a USER-trust turn and pass the
        review pipeline before it is committed.
        """
        return self >= Trust.USER

    @property
    def may_emit_action(self) -> bool:
        """Only a user request can cause an action to be considered.

        Note this is about *origination*. The orchestrator adapter emits the
        action, but it is only ever invoked on a USER-trust utterance, never
        on retrieved content.
        """
        return self >= Trust.USER

    @property
    def is_untrusted_content(self) -> bool:
        """True for anything that arrived from outside and may be adversarial."""
        return self <= Trust.AGENT


class TrustViolation(Exception):
    """Raised when a component attempts a privileged operation without trust.

    This is deliberately an exception rather than a silent no-op: a trust
    violation is a bug or an attack, and either way it must be loud and
    it must appear in the audit log.
    """

    def __init__(self, operation: str, actual: Trust, required: Trust):
        self.operation = operation
        self.actual = actual
        self.required = required
        super().__init__(
            f"{operation!r} requires trust>={required.name}, got {actual.name}"
        )


def require(operation: str, actual: Trust, required: Trust) -> None:
    """Guard a privileged operation. Raises TrustViolation if not permitted."""
    if actual < required:
        raise TrustViolation(operation, actual, required)
