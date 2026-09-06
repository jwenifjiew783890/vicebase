"""Multi-agent work: plan, delegate, execute, verify, report.

The rule that makes this real rather than a trace: every delegated step is
an actual specialist run, and the verification is computed from those runs
rather than asked of the model. A crew that "coordinated four agents" and
produced no steps coordinated nothing.

Kept deliberately shallow -- one level of delegation, no agents spawning
agents. Depth is where multi-agent systems become impossible to audit, and
an unauditable agent is exactly what this project refuses to ship.
"""
from __future__ import annotations

import re

from .base import BaseAgent, AgentContext, AgentResult
from .registry import register, get as get_agent

# What a plan step may be routed to. The planner proposes; this decides.
_ROUTABLE = ("research", "web", "browser", "knowledge", "memory",
             "files", "shell", "coding", "planner")

_HINTS = [
    (re.compile(r"\b(search|google|look up|find out|current|latest|news)\b", re.I), "research"),
    (re.compile(r"\b(open|visit|browse|scrape|page at|https?://)\b", re.I), "browser"),
    (re.compile(r"\b(my notes?|vault|obsidian)\b", re.I), "knowledge"),
    (re.compile(r"\b(remember|recall|what i told|memory)\b", re.I), "memory"),
    (re.compile(r"\b(file|folder|directory|save to|write to disk)\b", re.I), "files"),
    (re.compile(r"\b(run|execute|command|terminal|git )\b", re.I), "shell"),
    (re.compile(r"\b(code|script|program|implement|function)\b", re.I), "coding"),
]


def route_step(text: str) -> str:
    for pattern, agent in _HINTS:
        if pattern.search(text):
            return agent
    return "research"


@register
class CrewAgent(BaseAgent):
    name = "crew"
    description = ("Plans a multi-step goal, delegates each step to a "
                   "specialist, and verifies what actually ran.")
    capabilities = ["llm.plan", "agent.delegate", "verify"]

    MAX_STEPS = 4

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        if ctx.llm is None:
            return self.result("No model is loaded, so nothing was planned.")

        # 1. PLAN
        raw = self.step("llm.plan", task[:80], lambda: ctx.llm(
            "Break this goal into at most 4 concrete steps a computer can "
            "carry out. One per line, starting with a verb. No numbering, "
            "no preamble, no explanation.\n\nGoal: " + task,
            max_tokens=200), ctx)
        if not raw:
            return self.result("The planner produced nothing.")
        steps = [re.sub(r"^[\s\-\*\d.)]+", "", l).strip()
                 for l in raw.splitlines() if len(l.strip()) > 8][:self.MAX_STEPS]
        if not steps:
            return self.result("The plan came back empty.", raw[:400])

        # 2. DELEGATE + 3. EXECUTE
        transcript, delegated = [], []
        for i, line in enumerate(steps, 1):
            if ctx.emit:
                ctx.emit({"type": "agent_progress",
                          "message": f"crew step {i}/{len(steps)}: {line[:80]}"})
            agent_name = route_step(line)
            specialist = get_agent(agent_name)
            if specialist is None:
                continue
            sub = self.step(
                f"delegate.{agent_name}", line[:90],
                lambda s=specialist, l=line: s.run(l, ctx), ctx)
            if sub is None:
                transcript.append(f"**{i}. {line}** -> {agent_name}: the "
                                  f"delegation itself failed.")
                continue
            delegated.append((agent_name, sub))
            # The sub-agent's own steps are folded in, so the audit trail is
            # of real operations rather than of delegations.
            self._steps.extend(sub.steps)
            mark = "ok" if sub.ok else "FAILED"
            transcript.append(
                f"**{i}. {line}**\n   -> {agent_name} [{mark}, "
                f"{len(sub.steps)} steps]: {sub.summary}")

        # 4. VERIFY -- computed, not claimed
        ran = sum(len(s.steps) for _, s in delegated)
        worked = [n for n, s in delegated if s.ok]
        failed = [n for n, s in delegated if not s.ok]
        verdict = (f"{len(worked)}/{len(delegated)} specialists succeeded "
                   f"across {ran} real operations.")
        if failed:
            verdict += f" Failed: {', '.join(failed)}."

        # 5. REPORT
        body = "\n\n".join(transcript)
        if ctx.llm is not None and delegated:
            findings = "\n".join(
                f"{n}: {s.summary} {s.detail[:400]}" for n, s in delegated if s.ok)
            if findings.strip():
                digest = self.step("llm.report", f"{len(delegated)} results",
                                   lambda: ctx.llm(
                                       "Write a 4-sentence report answering the "
                                       "goal, using ONLY these results. If they "
                                       "do not answer it, say so.\n\nGoal: "
                                       + task + "\n\nResults:\n" + findings[:3000],
                                       max_tokens=260), ctx)
                if digest:
                    body = digest.strip() + "\n\n---\n\n" + body

        return self.result(
            f"Ran {len(delegated)} specialists for {task!r}. {verdict}", body,
            artifacts=[{"type": "plan", "items": steps}])
