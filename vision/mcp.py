"""A Model Context Protocol client, over stdio.

Written directly against the JSON-RPC wire format rather than pulling in a
framework: MCP is a small protocol, and a dependency that can break the
plugin layer is worse than eighty lines of transport code.

An MCP server is a subprocess speaking newline-delimited JSON-RPC on stdin
and stdout. Vision starts it, negotiates, lists its tools, and exposes them
through the same capability gateway everything else goes through -- an MCP
tool is not more trusted for having arrived over a protocol.
"""
from __future__ import annotations

import json
import subprocess
import threading
import time
from dataclasses import dataclass, field

PROTOCOL = "2025-06-18"


@dataclass
class McpTool:
    name: str
    description: str = ""
    schema: dict = field(default_factory=dict)
    server: str = ""

    def as_dict(self) -> dict:
        return {"name": self.name, "description": self.description,
                "server": self.server, "schema": self.schema}


class McpServer:
    """One MCP subprocess."""

    def __init__(self, name: str, command: list[str], env: dict | None = None,
                 cwd: str | None = None):
        self.name = name
        self.command = command
        self.env = env or {}
        self.cwd = cwd
        self.proc: subprocess.Popen | None = None
        self.tools: list[McpTool] = []
        self.error: str | None = None
        self._id = 0
        self._lock = threading.Lock()

    # ------------------------------------------------------------ wire
    def _rpc(self, method: str, params: dict | None = None,
             timeout: float = 30.0, notify: bool = False) -> dict | None:
        if self.proc is None or self.proc.poll() is not None:
            raise RuntimeError(f"MCP server {self.name!r} is not running")
        with self._lock:
            msg = {"jsonrpc": "2.0", "method": method}
            if params is not None:
                msg["params"] = params
            if not notify:
                self._id += 1
                msg["id"] = self._id
            self.proc.stdin.write(json.dumps(msg) + "\n")
            self.proc.stdin.flush()
            if notify:
                return None
            deadline = time.time() + timeout
            while time.time() < deadline:
                line = self.proc.stdout.readline()
                if not line:
                    raise RuntimeError(f"{self.name}: server closed the pipe")
                try:
                    got = json.loads(line)
                except json.JSONDecodeError:
                    continue                      # servers log to stdout too
                if got.get("id") == msg["id"]:
                    if "error" in got:
                        raise RuntimeError(f"{self.name}: {got['error']}")
                    return got.get("result", {})
            raise TimeoutError(f"{self.name}: no reply to {method}")

    # ------------------------------------------------------------ life
    def start(self, timeout: float = 45.0) -> bool:
        import os
        try:
            self.proc = subprocess.Popen(
                self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, text=True, bufsize=1,
                env={**os.environ, **self.env}, cwd=self.cwd)
            self._rpc("initialize", {
                "protocolVersion": PROTOCOL,
                "capabilities": {},
                "clientInfo": {"name": "vision", "version": "1.0"},
            }, timeout=timeout)
            self._rpc("notifications/initialized", {}, notify=True)
            result = self._rpc("tools/list", {}, timeout=timeout) or {}
            self.tools = [
                McpTool(name=t["name"], description=t.get("description", ""),
                        schema=t.get("inputSchema", {}), server=self.name)
                for t in result.get("tools", [])]
            self.error = None
            return True
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"
            self.stop()
            return False

    def call(self, tool: str, arguments: dict, timeout: float = 60.0) -> str:
        res = self._rpc("tools/call", {"name": tool, "arguments": arguments},
                        timeout=timeout) or {}
        parts = []
        for block in res.get("content", []):
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
            else:
                parts.append(f"[{block.get('type')}]")
        if res.get("isError"):
            raise RuntimeError("\n".join(parts) or "tool reported an error")
        return "\n".join(parts).strip()

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=5)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
        self.proc = None

    def describe(self) -> dict:
        return {"name": self.name, "command": self.command,
                "running": bool(self.proc and self.proc.poll() is None),
                "tools": [t.as_dict() for t in self.tools],
                "error": self.error}


class McpRegistry:
    """Every connected MCP server, and the tools they expose."""

    def __init__(self):
        self.servers: dict[str, McpServer] = {}

    def connect(self, name: str, command: list[str], env: dict | None = None,
                cwd: str | None = None) -> dict:
        self.disconnect(name)
        srv = McpServer(name, command, env, cwd)
        ok = srv.start()
        self.servers[name] = srv
        return {"ok": ok, "server": srv.describe()}

    def disconnect(self, name: str) -> dict:
        srv = self.servers.pop(name, None)
        if srv:
            srv.stop()
        return {"ok": bool(srv)}

    def tools(self) -> list[McpTool]:
        return [t for s in self.servers.values() for t in s.tools]

    def find(self, tool_name: str) -> tuple[McpServer, McpTool] | None:
        for s in self.servers.values():
            for t in s.tools:
                if t.name == tool_name:
                    return s, t
        return None

    def call(self, tool_name: str, arguments: dict) -> str:
        found = self.find(tool_name)
        if not found:
            raise KeyError(f"no MCP tool named {tool_name!r}")
        server, _ = found
        return server.call(tool_name, arguments)

    def describe(self) -> list[dict]:
        return [s.describe() for s in self.servers.values()]

    def stop_all(self) -> None:
        for s in list(self.servers.values()):
            s.stop()
        self.servers.clear()
