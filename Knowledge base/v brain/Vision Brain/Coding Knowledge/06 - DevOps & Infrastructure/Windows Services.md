---
type: note
domain: Coding Knowledge
section: 06 - DevOps & Infrastructure
created: 2026-09-03
---

# Windows Services

Keeping something running on Windows, and diagnosing it when it does not.

## The options

| Mechanism | Runs | Good for |
| --- | --- | --- |
| **Windows Service** | At boot, before login, as a chosen account | True background services |
| **Scheduled Task** | On a trigger - logon, boot, schedule, event | The pragmatic choice for user-context apps |
| **Startup folder / Run key** | At user logon, interactive | Desktop applications |
| **Docker `restart: unless-stopped`** | With the Docker daemon | Containerised services |

A real service requires a service-aware executable (or a wrapper such as NSSM or WinSW). For
ordinary applications, a **scheduled task triggered at logon** is usually the right answer and
far less work.

## Scheduled tasks in practice

- **Trigger**: at logon, at startup, or on a schedule. A **delay** (30-120 s) avoids racing other
  startup work and is worth setting by default.
- **Run whether user is logged on or not** requires stored credentials and gives no interactive
  desktop - services needing a UI or a user profile must run in the user context.
- **Set the working directory** explicitly. A task's default working directory is not what you
  expect, and this is a common cause of "it works when I run it manually".
- **Environment differs from an interactive shell** - `PATH` in particular. Use absolute paths.
- **Set restart-on-failure** and a sensible retry count.

Diagnostics:

| Command | Shows |
| --- | --- |
| `Get-ScheduledTask -TaskName X` | Definition and state |
| `Get-ScheduledTaskInfo -TaskName X` | **Last run time and last result** - the useful one |
| `schtasks /query /tn X /v /fo LIST` | Everything, verbosely |

`LastTaskResult` of `0` is success. `0x41301` means currently running. `0xFFFFFFFF` (-1) means
the task lost track of its process.

> [!note] Measured in this project
> A `Vision Backend` task showed state `Ready` with `LastTaskResult = 0xFFFFFFFF` while the
> process was in fact running - started outside the task's control, so the scheduler no longer
> owned it. **A task's reported state describes the scheduler's view, not the world.** Verify the
> process independently (`Get-Process`, or the port) rather than trusting the task state.

## Services

| Command | Does |
| --- | --- |
| `Get-Service X` | State |
| `Start-Service` / `Stop-Service` / `Restart-Service` | Lifecycle |
| `sc.exe qc X` | Configuration, including the binary path and account |
| `sc.exe failure X ...` | Recovery actions |

Service accounts matter: `LocalSystem` is powerful and usually excessive; `NetworkService` and
`LocalService` are lower-privilege; a dedicated account with the minimum rights is best practice.
A service running as a user account **fails after that user's password changes**, which presents
as a mysterious post-password-change outage.

## Diagnosing a service that will not start

1. Event Viewer -> Windows Logs -> System and Application; the service's own log if it has one.
2. Run the executable manually **as the service account**, from the service's working directory.
   This reproduces the environment and usually reveals the problem immediately.
3. Check the account's rights - "log on as a service", file permissions on the install
   directory, network access if it needs it.
4. Check for a port conflict: `Get-NetTCPConnection -LocalPort <n>` or `netstat -ano`.
5. Check dependencies: `sc.exe qc` lists them, and a dependency that starts slowly can look like
   a failure.

## Failure modes

- **Working directory assumed**, so relative paths resolve elsewhere.
- **`PATH` differences** between an interactive shell and the task environment.
- **Task credentials broken** by a password change.
- **Two mechanisms starting the same thing** - a scheduled task and a startup entry - producing
  duplicate processes competing for a port.
- **Orphaned tasks** whose process was started manually, so state and reality diverge.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/Bash & PowerShell|Bash & PowerShell]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Processes & Resources|Processes & Resources]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Deployment|Deployment]]

## Sources

- Microsoft documentation on Task Scheduler and Windows services - <https://learn.microsoft.com/>. The orphaned-task observation was measured in this project on 2026-09-03.
