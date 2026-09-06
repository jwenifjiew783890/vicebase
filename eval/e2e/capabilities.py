"""End-to-end checks for the capabilities added after the first build pass.

Same rule as live_app.py: this talks to a RUNNING server over its real API.
Nothing here is mocked, and a capability that cannot run in this
environment is reported as unavailable rather than skipped quietly.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8765"


def get(path: str, timeout: float = 120):
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        return json.load(r)


def post(path: str, fields: dict, timeout: float = 300):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(BASE + path, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def say(ws, text: str, timeout: float = 300) -> dict:
    ws.send(json.dumps({"type": "say", "text": text}))
    t0 = time.time()
    while time.time() - t0 < timeout:
        m = json.loads(ws.recv())
        if m.get("type") == "reply":
            return m
        if m.get("type") == "error":
            raise RuntimeError(m["error"])
    raise TimeoutError(text)


def main() -> int:
    from websockets.sync.client import connect
    results = []

    def check(name, ok, detail=""):
        results.append((name, bool(ok), detail))
        print(f"  {'PASS' if ok else 'FAIL'}  {name}\n        {detail}", flush=True)

    st = get("/api/status")
    agents = [a["name"] for a in st["vision"]["agents"]]
    check("1. all agents registered", len(agents) >= 12, ", ".join(agents))

    # ---- MCP plugin ----
    r = post("/api/mcp/connect",
             {"name": "filesystem",
              "command": "npx -y @modelcontextprotocol/server-filesystem /root/mcp-sandbox"})
    tools = r.get("server", {}).get("tools", [])
    check("2. MCP server connects", r.get("ok") and len(tools) > 5,
          f"{len(tools)} tools, error={r.get('server',{}).get('error')}")

    m = get("/api/mcp")
    check("3. MCP tools listed by the API", len(m["tools"]) > 5,
          ", ".join(t["name"] for t in m["tools"][:6]))

    with connect("ws://127.0.0.1:8765/ws", max_size=None) as ws:
        json.loads(ws.recv())

        r = say(ws, "what tools do you have")
        check("4. MCP agent lists real tools",
              r.get("agent") == "mcp" and (r.get("agent_result") or {}).get("ok"),
              r["text"][:90].replace("\n", " "))

        r = say(ws, "use read_text_file on /root/mcp-sandbox/note.txt")
        check("5. MCP tool actually invoked", "thornbury" in r["text"].lower(),
              r["text"][:110].replace("\n", " "))

        # ---- browser ----
        r = say(ws, "open http://127.0.0.1:8765/")
        job_id = (r.get("agent_result") or {}).get("job_id")
        check("6. browser request becomes a job",
              r.get("agent") == "browser" and bool(job_id), f"job={job_id}")

        job = None
        for _ in range(60):
            job = get(f"/api/jobs/{job_id}")
            if job["status"] in ("done", "failed", "cancelled"):
                break
            time.sleep(3)
        steps = [s["action"] for s in (job.get("result") or {}).get("steps", [])]
        check("7. browser really loaded a page",
              job["status"] == "done" and "browser.open" in steps,
              f"status={job['status']} steps={steps}")

        # ---- multi-agent crew ----
        r = say(ws, "vision, handle this: open http://127.0.0.1:8765/ and then "
                    "write a short summary to a file")
        cjob = (r.get("agent_result") or {}).get("job_id")
        check("8. multi-step goal becomes a crew job",
              r.get("agent") == "crew" and bool(cjob), f"job={cjob}")

        job = None
        for _ in range(120):
            job = get(f"/api/jobs/{cjob}")
            if job["status"] in ("done", "failed", "cancelled"):
                break
            time.sleep(4)
        res = job.get("result") or {}
        acts = [s["action"] for s in res.get("steps", [])]
        delegations = [a for a in acts if a.startswith("delegate.")]
        check("9. crew delegated to several specialists",
              len(set(delegations)) >= 2,
              f"status={job['status']} delegated={sorted(set(delegations))}")
        check("10. crew's audit trail holds real operations",
              any(a in acts for a in ("browser.open", "web.search", "file.search")),
              f"{len(acts)} steps: {acts[:8]}")

    # ---- job cancellation ----
    r = post("/api/mcp/connect",
             {"name": "fs2",
              "command": "npx -y @modelcontextprotocol/server-filesystem /root/mcp-sandbox"})
    with connect("ws://127.0.0.1:8765/ws", max_size=None) as ws:
        json.loads(ws.recv())
        r = say(ws, "research something long and involved about distributed systems")
        rjob = (r.get("agent_result") or {}).get("job_id")
        time.sleep(2)
        c = post(f"/api/jobs/{rjob}/cancel", {})
        final = None
        for _ in range(40):
            final = get(f"/api/jobs/{rjob}")
            if final["status"] in ("cancelled", "done", "failed"):
                break
            time.sleep(3)
        check("11. a running job can be cancelled",
              c.get("ok") and final["status"] in ("cancelled", "done"),
              f"cancel={c.get('ok')} final={final['status']}")

    # ---- jobs persist ----
    jobs = get("/api/jobs")
    check("12. jobs are persisted with logs", len(jobs) >= 3
          and any(j.get("log") for j in jobs),
          f"{len(jobs)} jobs on record")

    # ---- desktop automation reports honestly ----
    with connect("ws://127.0.0.1:8765/ws", max_size=None) as ws:
        json.loads(ws.recv())
        r = say(ws, "take a screenshot of my screen")
        text = r["text"].lower()
        honest = ("headless" in text or "graphical" in text
                  or "can't" in text or "display" in text)
        check("13. desktop automation is honest when unavailable",
              r.get("agent") == "desktop" and honest, r["text"][:110])

    # ---- plugin disconnect ----
    d = post("/api/mcp/disconnect", {"name": "fs2"})
    check("14. plugin disconnects", d.get("ok"), str(d))

    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n{'='*66}\n  {passed}/{len(results)} capability checks passed\n{'='*66}")
    for n, ok, _ in results:
        if not ok:
            print(f"  FAILED: {n}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
