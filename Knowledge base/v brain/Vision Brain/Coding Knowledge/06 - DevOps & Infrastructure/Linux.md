---
type: note
domain: Coding Knowledge
section: 06 - DevOps & Infrastructure
created: 2026-09-03
---

# Linux

The concepts and commands that actually get used when something is wrong on a Linux host.

## Diagnostic sequence

When a Linux box is misbehaving, this order finds most problems quickly:

1. `uptime` / `top` - load average versus core count; is anything running hot?
2. `free -h` - memory, and importantly `available`, not `free`
3. `df -h` and `df -i` - disk space **and inodes**; a full inode table looks like a full disk
   with space remaining
4. `dmesg -T | tail -50` - OOM kills, disk errors, hardware problems
5. `journalctl -u <service> -n 100 --no-pager` - what the service says
6. `ss -tlnp` - what is listening on which port, and which process
7. `ps aux --sort=-%mem | head` - the memory consumers

## Processes and signals

- **SIGTERM (15)** asks politely and can be handled - always try this first.
  **SIGKILL (9)** cannot be caught, so cleanup does not run: temporary files remain, locks are
  not released, buffers are not flushed.
- A **zombie** is a finished process whose parent has not reaped it - harmless individually,
  a bug in the parent if they accumulate.
- **Orphans** are re-parented to init and keep running. A background process whose parent shell
  exited is still there, and is easy to overlook when accounting for resource use.
- `kill -0 <pid>` tests existence without signalling.

## Files and permissions

- Permission bits `rwx` for user/group/other. On a **directory**, `x` means "may traverse" and
  `r` means "may list" - a directory with `r` but not `x` is listable and unusable, which
  produces confusing errors.
- **Deleting a file that a process still has open frees no space** until the process closes it.
  `lsof +L1` finds these; it explains "I deleted the logs and the disk is still full".
- File descriptor limits (`ulimit -n`) cause "too many open files" - usually a leak, occasionally
  a genuinely low limit.

## Memory reality

`free -h` distinguishing:
- **used** - genuinely in use
- **buff/cache** - page cache, reclaimable, and *correct* behaviour rather than waste
- **available** - the number that matters: what a new process could get

**Do not panic about low `free`.** Linux uses spare memory for cache by design.

The **OOM killer** terminates a process when memory is exhausted; `dmesg` records which and why.
A container exiting with code 137 is this.

## Text processing that earns its keep

`grep -r`, `grep -n`, `grep -A/-B/-C` for context; `rg` where available (faster, respects
ignore files); `awk '{print $2}'` for columns; `sed -n '10,20p'` for line ranges; `sort | uniq
-c | sort -rn` for frequency - the single most useful log-analysis idiom there is;
`jq` for JSON; `tail -f` with `grep --line-buffered` for live filtering.

## Systemd

| Command | Does |
| --- | --- |
| `systemctl status <svc>` | State, recent logs, PID |
| `systemctl restart/stop/start` | Lifecycle |
| `systemctl enable --now` | Start now and at boot |
| `journalctl -u <svc> -f` | Follow the log |
| `journalctl -u <svc> --since "1 hour ago"` | Time-bounded |
| `systemctl list-units --failed` | What is broken right now |

`enable` and `start` are different: a service can be running now and not come back after reboot,
or be enabled and currently stopped. Check both.

## Failure modes

- **`kill -9` first**, skipping cleanup and leaving locks and temporary state.
- **Disk full by inodes**, not bytes.
- **Deleted-but-open files** holding space.
- **`enable` without `start`**, or the reverse - it works until the reboot.
- **Reading `free` as though cache were waste.**
- **Editing a config without reloading** the service.

---

## See also

- [[Coding Knowledge/06 - DevOps & Infrastructure/Processes & Resources|Processes & Resources]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Networking|Networking]]
- [[Coding Knowledge/02 - Programming & Languages/Bash & PowerShell|Bash & PowerShell]]

## Sources

- Linux man pages and systemd documentation - <https://www.freedesktop.org/software/systemd/man/>; Brendan Gregg, "Linux Performance Analysis in 60 Seconds" - <https://www.brendangregg.com/>.
