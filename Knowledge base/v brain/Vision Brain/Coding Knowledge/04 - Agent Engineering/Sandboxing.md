---
type: note
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# Sandboxing

Containing what an agent can reach, so that a mistake or an injection is survivable.

## What a sandbox is for

Permissions decide what the agent is *allowed* to do. A sandbox decides what it is *able* to do.
The second is what protects you when the first has a bug - and permission systems have bugs.

Design so that **the worst thing that can happen from inside the sandbox is acceptable.**

## Layers, weakest to strongest

| Layer | Contains | Escapes via |
| --- | --- | --- |
| **Application checks** | Path and argument validation | A bug in the check |
| **Process user** | OS file permissions | Misconfigured permissions, setuid |
| **Container** | Filesystem, process, network namespace | Kernel bugs, privileged mode, mounts |
| **VM** | Almost everything | Hypervisor bugs (rare) |
| **Separate machine / network** | Everything | Physical and network access |

Combine layers. A container running as root with the Docker socket mounted is not a sandbox -
it is a full-machine capability with extra steps.

## Practical containment

**Filesystem**: one working directory, mounted read-write; everything else read-only or absent.
Never mount the whole home directory, `/`, or credential directories. Reject `..` rather than
resolving it.

**Network**: deny by default; allowlist the hosts actually required. This is the control that
most directly prevents exfiltration, and it is the one most often skipped.

**Execution**: no shell unless the task genuinely requires one. A shell converts every other
restriction into a suggestion, because it can reach anything the process can.

**Resources**: memory, CPU and disk limits, and a wall-clock timeout. Prevents a runaway loop
from taking the machine down.

**Secrets**: not present in the sandbox at all. The strongest control available is that the
credential simply is not reachable. Where a call must be authenticated, proxy it through a
component outside the sandbox that holds the credential.

**Output**: treat everything produced inside as untrusted. Validate before it is used elsewhere.

## Sandboxing without containers

Not every environment can run one. Weaker but real controls:

- A dedicated OS user with minimal file permissions
- A dedicated directory tree, with the application refusing to operate outside it
- No shell tool exposed
- Network egress restricted at the firewall
- Credentials held by a separate process

*This stack takes that approach: OpenCode runs as a normal process with `bash`, `task`,
`webfetch` and `external_directory` denied in its own permission engine, and writes confined to
an allow-listed project root that is separately validated upstream. It is weaker than a
container and it is documented as such, rather than described as a sandbox it is not.*

## Failure modes

- **Calling a permission check a sandbox.** They are different controls; only one survives a bug
  in the other.
- **Mounting too much** - the home directory, SSH keys, the Docker socket.
- **Unrestricted network egress**, which makes every other control bypassable by exfiltration.
- **Secrets in environment variables** inside the sandbox, readable by anything running there.
- **No resource limits**, so a loop exhausts the host.
- **Trusting output** from inside the sandbox without validation.
- **Sandbox that is disabled "temporarily" for development** and never re-enabled.

---

## See also

- [[Coding Knowledge/04 - Agent Engineering/Permissions|Permissions]]
- [[Coding Knowledge/03 - AI Engineering/AI Safety & Guardrails|AI Safety & Guardrails]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Docker|Docker]]

## Sources

- Docker security documentation - <https://docs.docker.com/engine/security/>; OWASP Top 10 for LLM Applications - <https://owasp.org/www-project-top-10-for-large-language-model-applications/>. The description of this stack's actual containment is from the project itself.
