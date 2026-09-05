---
type: note
domain: Coding Knowledge
section: 06 - DevOps & Infrastructure
created: 2026-09-03
---

# WSL

The Windows/Linux boundary: how it consumes resources, where the filesystem cost is, and the controls that exist.

## What it is

WSL 2 runs a real Linux kernel in a lightweight utility VM managed by Hyper-V. That single fact
explains its resource behaviour: it is a VM, so it has its own memory, its own filesystem, and a
network boundary with the host.

Docker Desktop on Windows normally runs its engine inside WSL 2, so **WSL's resource limits are
Docker's resource limits**.

## Memory behaviour

WSL 2 claims memory on demand up to a maximum and has historically been reluctant to give it
back - Linux uses free memory for page cache, which is correct behaviour that looks like a leak
from the Windows side.

Controls live in `%UserProfile%\.wslconfig` and apply after `wsl --shutdown`:

```ini
[wsl2]
memory=4GB
swap=2GB

[experimental]
autoMemoryReclaim=gradual
sparseVhd=true
```

- **`memory`** caps the VM. Without it, WSL may claim a large share of host RAM.
- **`autoMemoryReclaim`** returns unused memory to Windows over time (`gradual` is the safe
  setting; `dropcache` is more aggressive).
- **`sparseVhd`** lets the virtual disk shrink as data is deleted. Without it, the VHDX only
  ever grows - a disk that reached 60 GB once stays 60 GB after everything is deleted.

*These exact settings were applied in this project to bound WSL's contribution to idle memory.*

## Filesystem performance - the big one

**Crossing the filesystem boundary is expensive.** Working on `/mnt/c/...` from Linux, or on
`\\wsl$\...` from Windows, goes through a translation layer and is dramatically slower for
many small files - which is exactly what `npm install`, `git status` and build tools do.

**Keep a project on the side that works on it.** Linux tooling -> Linux filesystem
(`~/project`). Windows tooling -> Windows filesystem. A repository on `/mnt/c` built from
inside WSL is the single most common WSL performance complaint, and it is entirely avoidable.

Also: Linux file permissions and case sensitivity do not survive the boundary cleanly. Git will
report spurious permission changes, and a case-only rename can behave unexpectedly.

## Networking

WSL 2 has its own virtual network adapter and its own IP, which changes across restarts in the
default NAT mode.

- From WSL, reach a Windows service via the host IP (available in `/etc/resolv.conf` under NAT)
  or via `localhost` where localhost forwarding applies.
- From Windows, `localhost` reaches services listening in WSL for most cases.
- A service inside WSL bound to `127.0.0.1` is not reachable from Windows; bind `0.0.0.0`.
- **Mirrored networking mode** (newer WSL) removes most of this friction by sharing the host's
  network interfaces - worth enabling if available.
- The **Windows firewall** applies, and is a frequent cause of "the port is open but nothing
  connects".

## Operational commands

| Command | Does |
| --- | --- |
| `wsl -l -v` | List distributions, versions, state |
| `wsl --shutdown` | Stop all distributions - required for `.wslconfig` to apply |
| `wsl --status` | Version and default distribution |
| `wsl --update` | Update the WSL kernel |
| `wsl --export` / `--import` | Back up and restore a distribution |

## Failure modes

- **`.wslconfig` edited without `wsl --shutdown`** - no effect, and it looks like the setting
  does nothing.
- **Projects on `/mnt/c`** built from Linux - slow for reasons nobody suspects.
- **Unbounded memory** with no `[wsl2] memory` cap.
- **VHDX growth** with `sparseVhd` off.
- **Binding to `127.0.0.1` inside WSL** and expecting Windows to reach it.
- **Assuming the WSL IP is stable** in NAT mode.

---

## See also

- [[Coding Knowledge/06 - DevOps & Infrastructure/Docker|Docker]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Processes & Resources|Processes & Resources]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Networking|Networking]]

## Sources

- Microsoft WSL documentation - <https://learn.microsoft.com/windows/wsl/>, particularly the `.wslconfig` reference. The specific configuration above was applied and verified in this project on WSL 2.7.12.
