"""Vision's specialist agents.

Seven, not seventy. Each is here because it owns a distinct set of tools
and a distinct way of failing; jobs that share both are the same agent. A
"CalendarAgent" that would only ever call the file tools is a label, not a
specialist, and labels are what make agent traces fake.

Every agent runs real operations through `BaseAgent.step`, so its result is
computed from what happened rather than from what it says happened.
"""
from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

from .base import BaseAgent, AgentContext, AgentResult
from .registry import register


# --------------------------------------------------------------------------
# Web
# --------------------------------------------------------------------------
@register
class WebAgent(BaseAgent):
    name = "web"
    description = "Searches the live web and reads pages."
    capabilities = ["web.search", "web.fetch"]

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        from ..core.web import search, _get, strip_html

        outcome = self.step("web.search", task,
                            lambda: search(task, k=5), ctx)
        results = list(getattr(outcome, "results", []) or [])
        if not results:
            # Empty is a legitimate outcome and must be reported as one.
            # The failure this guards against is a confident answer with
            # nothing behind it.
            return self.result(
                f"Searched the web for {task!r} and got nothing back.",
                "No results. This is reported rather than filled in.")

        lines = []
        for r in results[:5]:
            lines.append(f"- {r.title} ({r.url})\n  {r.snippet[:300]}")
        return self.result(
            f"Found {len(results)} results for {task!r}.",
            "\n".join(lines),
            artifacts=[{"type": "links",
                        "items": [{"title": r.title, "url": r.url}
                                  for r in results[:5]]}])


# --------------------------------------------------------------------------
# Personal knowledge (Obsidian)
# --------------------------------------------------------------------------
@register
class KnowledgeAgent(BaseAgent):
    name = "knowledge"
    description = "Searches the user's Obsidian vault / personal notes."
    capabilities = ["vault.search"]

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        if ctx.vault is None:
            return self.result("No vault is connected.",
                               "Connect an Obsidian vault in Settings first.")
        hits = self.step("vault.search", task,
                         lambda: ctx.vault.search(task, k=5), ctx) or []
        if not hits:
            return self.result(f"Nothing in your notes about {task!r}.",
                               "The vault was searched and had no match.")
        body = "\n\n".join(f"**{h.chunk.path}**\n{h.chunk.text[:500]}"
                           for h in hits[:4])
        return self.result(f"Found {len(hits)} passages in your notes.", body,
                           artifacts=[{"type": "notes",
                                       "items": [h.chunk.path for h in hits[:5]]}])


# --------------------------------------------------------------------------
# Memory
# --------------------------------------------------------------------------
@register
class MemoryAgent(BaseAgent):
    name = "memory"
    description = "Reads and writes what Vision remembers about the user."
    capabilities = ["memory.search", "memory.facts", "memory.remember"]
    # This agent needs the verb: "remember X" is a write and "X" alone is
    # a read, and the two are the same words minus one.
    wants_utterance = True

    _REMEMBER = re.compile(r"^\s*(remember|yaad rakh|note that)\b[:,]?\s*(?P<v>.+)",
                           re.IGNORECASE)

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        if ctx.store is None:
            return self.result("No memory store is attached.")

        m = self._REMEMBER.match(task)
        if m:
            text = m.group("v").strip()
            from ..core.trust import Trust
            from ..core.extract import extract_facts
            now = time.time()

            # Two homes, because "remember X" arrives in two shapes. A
            # structured statement ("I use neovim") belongs in semantic
            # memory where it can be superseded and contradicted; anything
            # else is an episode, which is durable without pretending to
            # be a typed fact.
            facts = self.step("memory.extract", text,
                              lambda: extract_facts(text), ctx) or []
            for c in facts:
                self.step("memory.fact", f"{c.predicate}={c.object}",
                          lambda c=c: ctx.store.assert_fact(
                              c.subject, c.predicate, c.object, Trust.USER), ctx)
            self.step("memory.episode", text,
                      lambda: ctx.store.add_episode(
                          ctx.session_id, text, now, now, salience=0.9), ctx)
            kind = (f"stored as {len(facts)} fact(s) and a note"
                    if facts else "stored as a note")
            return self.result(f"Noted: {text}", f"Remembered -- {kind}.")

        rows = self.step("memory.search", task,
                         lambda: ctx.store.search_turns(task, limit=5), ctx) or []
        # A general "what do you remember about me" shares no content word
        # with "my thesis deadline is 21 November", so requiring overlap
        # returned nothing while the notes sat right there. An open
        # question gets the recent notes; a specific one gets the matching
        # ones.
        general = bool(re.search(
            r"\b(remember|know) about me\b|\bwhat do you (remember|know)\b"
            r"|\bmere baare mein\b", task, re.IGNORECASE))
        terms = [w for w in task.lower().split() if len(w) > 3]

        def _episodes():
            rows = ctx.store.recent_episodes(limit=20)
            if general:
                return [r["summary"] for r in rows]
            return [r["summary"] for r in rows
                    if any(w in r["summary"].lower() for w in terms)]

        episodes = self.step("memory.episodes", "recent notes", _episodes, ctx) or []
        facts = self.step("memory.facts", "current facts",
                          lambda: list(ctx.store.db.execute(
                              "SELECT subject,predicate,object FROM facts "
                              "WHERE valid_to IS NULL")), ctx) or []
        if not rows and not facts and not episodes:
            return self.result("I have no record of that.",
                               "Memory was searched and is empty on this.")
        body = []
        if facts:
            body.append("Known: " + "; ".join(
                f"{r['predicate']}={r['object']}" for r in facts[:8]))
        for e in episodes[:5]:
            body.append(f"[note] {e[:200]}")
        for r in rows[:5]:
            body.append(f"[{r['role']}] {r['text'][:200]}")
        return self.result(
            f"Found {len(rows)} turns, {len(episodes)} notes, {len(facts)} facts.",
            "\n".join(body))


# --------------------------------------------------------------------------
# Files
# --------------------------------------------------------------------------
@register
class FilesAgent(BaseAgent):
    name = "files"
    description = "Finds, reads and writes files, through the capability gateway."
    capabilities = ["file.search", "file.read", "file.write"]
    dangerous = True

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        root = Path(os.environ.get("VISION_WORKSPACE", Path.home() / "vision-workspace"))
        root.mkdir(parents=True, exist_ok=True)
        words = [w for w in re.findall(r"[\w.\-*]+", task) if len(w) > 2][:4]
        pattern = words[-1] if words else "*"

        found = self.step("file.search", f"{pattern} under {root}",
                          lambda: [str(p) for p in root.rglob(f"*{pattern}*")
                                   if p.is_file()][:20], ctx) or []
        if not found:
            return self.result(f"No files matching {pattern!r} under {root}.",
                               f"Searched {root} recursively.")
        head = ""
        if len(found) == 1:
            head = self.step("file.read", found[0],
                             lambda: Path(found[0]).read_text(
                                 encoding="utf-8", errors="replace")[:2000], ctx) or ""
        return self.result(f"Found {len(found)} file(s) matching {pattern!r}.",
                           head or "\n".join(found),
                           artifacts=[{"type": "files", "items": found}])


# --------------------------------------------------------------------------
# Shell / coding
# --------------------------------------------------------------------------
@register
class ShellAgent(BaseAgent):
    name = "shell"
    description = "Runs allow-listed shell commands and reports real output."
    capabilities = ["shell.run"]
    dangerous = True

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        from ..core.gateway import SHELL_ALLOWLIST
        cmd = task.strip()
        allowed = any(cmd.startswith(a) for a in SHELL_ALLOWLIST)
        if not allowed:
            return self.result(
                f"Refused: {cmd!r} is not on the shell allow-list.",
                "Allowed prefixes: " + ", ".join(sorted(SHELL_ALLOWLIST)),
                needs_confirmation={"action": "shell.run", "command": cmd,
                                    "reason": "not on the allow-list"})
        # The user's workspace, never Vision's install directory. Found by
        # running the INSTALLED copy: cwd there is ~/.local/share/vision,
        # so `run git status` reported "not a git repository" -- correct,
        # and useless. Commands belong where the user's work is.
        from .. import config
        default = Path.home() / "vision-workspace"
        cwd = os.environ.get("VISION_WORKSPACE", str(default))
        Path(cwd).mkdir(parents=True, exist_ok=True)

        def _run():
            p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True,
                               text=True, timeout=120)
            if p.returncode != 0:
                raise RuntimeError(f"exit {p.returncode}: {p.stderr[:500]}")
            return p.stdout[:4000]

        out = self.step("shell.run", cmd, _run, ctx)
        if out is None:
            return self.result(f"`{cmd}` failed.", "See the step error.")
        return self.result(f"Ran `{cmd}`.", out or "(no output)")


# --------------------------------------------------------------------------
# Coding
# --------------------------------------------------------------------------
@register
class CodingAgent(BaseAgent):
    name = "coding"
    description = "Writes code to a file and verifies it by executing it."
    capabilities = ["file.write", "python.run"]
    dangerous = True

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        """Write, then RUN. A coding agent that only emits text is the
        thing the brief specifically forbids, so the verification step is
        not optional -- if the code does not execute, the result is not ok.
        """
        if ctx.llm is None:
            return self.result("No model is loaded, so nothing was written.")
        root = Path(os.environ.get("VISION_WORKSPACE", Path.home() / "vision-workspace"))
        root.mkdir(parents=True, exist_ok=True)

        prompt = ("Write a single self-contained Python script for this task. "
                  "Output ONLY code, no prose, no markdown fence.\n\nTask: " + task)
        code = self.step("llm.generate", task[:80],
                         lambda: ctx.llm(prompt, max_tokens=700), ctx) or ""
        code = re.sub(r"^```(?:python)?\s*|\s*```$", "", code.strip(),
                      flags=re.MULTILINE)
        if not code.strip():
            return self.result("The model produced no code.")

        path = root / f"vision_task_{int(time.time())}.py"
        self.step("file.write", str(path), lambda: path.write_text(code), ctx)

        def _exec():
            p = subprocess.run(["python3", str(path)], capture_output=True,
                               text=True, timeout=60, cwd=str(root))
            if p.returncode != 0:
                raise RuntimeError(f"exit {p.returncode}: {p.stderr[-800:]}")
            return p.stdout[:2000]

        out = self.step("python.run", str(path), _exec, ctx)
        if out is None:
            return self.result(
                f"Wrote {path.name} but it failed to run.",
                f"```python\n{code[:1500]}\n```",
                artifacts=[{"type": "file", "path": str(path)}])
        return self.result(
            f"Wrote and ran {path.name}.",
            f"```python\n{code[:1500]}\n```\n\nOutput:\n```\n{out}\n```",
            artifacts=[{"type": "file", "path": str(path)}])


# --------------------------------------------------------------------------
# Research -- the multi-step one
# --------------------------------------------------------------------------
@register
class ResearchAgent(BaseAgent):
    name = "research"
    description = "Plans a question into sub-queries, searches each, synthesises."
    capabilities = ["web.search", "llm.synthesise"]

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        from ..core.web import search

        subqueries = [task]
        if ctx.llm is not None:
            raw = self.step("llm.plan", task[:80], lambda: ctx.llm(
                "Break this research question into 2 short web search queries. "
                "One per line, no numbering, no prose.\n\n" + task,
                max_tokens=80), ctx) or ""
            extra = [l.strip(" -•") for l in raw.splitlines()
                     if 3 < len(l.strip()) < 120][:2]
            subqueries = extra or subqueries

        findings, sources = [], []
        for q in subqueries:
            out = self.step("web.search", q, lambda q=q: search(q, k=4), ctx)
            for r in list(getattr(out, "results", []) or [])[:4]:
                findings.append(f"- {r.title}: {r.snippet[:240]}")
                sources.append({"title": r.title, "url": r.url})

        if not findings:
            return self.result(
                "Research produced nothing -- every search came back empty.",
                "Reported rather than filled in. If the network is "
                "restricted, that is the cause.")

        body = "\n".join(findings[:12])
        if ctx.llm is not None:
            summary = self.step("llm.synthesise", f"{len(findings)} findings",
                                lambda: ctx.llm(
                                    "Summarise these search findings in 4 sentences. "
                                    "Only use what is here.\n\n" + body,
                                    max_tokens=220), ctx)
            if summary:
                body = summary.strip() + "\n\nSources:\n" + body
        return self.result(f"Researched {task!r} across {len(subqueries)} queries.",
                           body, artifacts=[{"type": "links", "items": sources[:8]}])


# --------------------------------------------------------------------------
# Planner
# --------------------------------------------------------------------------
@register
class PlannerAgent(BaseAgent):
    name = "planner"
    description = "Breaks a goal into concrete ordered steps."
    capabilities = ["llm.plan"]

    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        if ctx.llm is None:
            return self.result("No model is loaded, so no plan was produced.")
        plan = self.step("llm.plan", task[:80], lambda: ctx.llm(
            "Break this into 3-6 concrete ordered steps. One per line, "
            "starting with a verb. No preamble.\n\n" + task, max_tokens=260), ctx)
        if not plan:
            return self.result("The model produced no plan.")
        return self.result(f"Planned {task!r}.", plan.strip())


# Agents that live in their own modules because they carry real
# dependencies of their own.
from . import browser  # noqa: E402,F401
from . import crew  # noqa: E402,F401
from . import system  # noqa: E402,F401
