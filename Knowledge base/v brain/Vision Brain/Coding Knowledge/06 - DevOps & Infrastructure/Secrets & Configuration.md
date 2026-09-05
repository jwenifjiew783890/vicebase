---
type: note
domain: Coding Knowledge
section: 06 - DevOps & Infrastructure
created: 2026-09-03
---

# Secrets & Configuration

Keeping credentials out of code, logs, images and prompts - and making configuration fail fast when it is wrong.

## The rules for secrets

1. **Never in source control.** Once committed and pushed, treat it as compromised and **rotate
   it**. Rewriting history does not recall what was already cloned, forked or indexed.
2. **Never in logs, error messages or exception text.** Redact at the logging boundary by field
   name, not by remembering at each call site.
3. **Never in a container image layer.** Layers are permanent; deleting the file later does not
   remove it.
4. **Never in a prompt or a model context.** It leaves the machine and may be retained by the
   provider.
5. **Never in a URL or query string.** URLs appear in logs, proxies, browser history and
   referrer headers.
6. **Never in workflow names, node labels, registry metadata or documentation.** *(An explicit
   constraint in this stack: credentials live in n8n's encrypted credential store and nowhere
   else.)*
7. **Rotate on a schedule and on any suspicion.** A secret that cannot be rotated quickly is an
   incident waiting to be long.

## Where they should live

| Mechanism | Suits |
| --- | --- |
| Managed secret store (Vault, cloud secret manager) | Production, with audit and rotation |
| The platform's own encrypted store (n8n credentials, CI secrets) | Tool-specific credentials |
| Environment variables injected at runtime | Simple deployments |
| An encrypted file with a key from elsewhere | Single-host setups |
| A `.env` file **in `.gitignore`**, local only | Development only |

Environment variables are visible to anything running as that user and often appear in crash
dumps and process listings - acceptable for many cases, not for the highest-value secrets.

## Configuration

**Configuration comes from the environment; the artefact is identical everywhere.** That is what
makes "build once, promote" possible.

- **Validate everything at startup and fail immediately** if something required is missing or
  malformed. A service that starts happily and fails on the first request that needs a missing
  value has turned a deploy-time error into a production incident.
- **No secrets in defaults.** A default password is a vulnerability that ships.
- **Log the configuration at startup** - names and non-sensitive values, so "which config is this
  instance actually running?" is answerable.
- **One source of truth per value.** The same setting in a file, an environment variable and a
  database will drift, and the drift is discovered during an outage.

> [!warning] Know your precedence rules
> Some systems persist a configuration value into a database on first run, after which the
> environment variable is ignored. **Open WebUI's PersistentConfig behaves this way**: changing
> the environment variable alone appears to do nothing, because the stored value wins.
>
> Whenever a config change "has no effect", check whether something else holds a stored copy.

## Practical hygiene

- **Secret scanning in CI and as a pre-commit hook.** Catching it before the push is worth far
  more than detecting it after.
- **Least privilege per credential** - a read-only database user for a reporting job.
- **Separate credentials per environment.** Production credentials must never work from a
  developer machine.
- **Short-lived credentials** where the platform supports them.
- **Audit access** to the secret store; who read what, and when.

## Failure modes

- **Secrets committed**, then "removed" in a later commit and never rotated.
- **The same credential everywhere**, so rotating it means coordinating every consumer.
- **Config validated lazily**, failing in production.
- **A stored value silently overriding the environment**, so the change appears to do nothing.
- **Secrets in CI logs** because a script echoed a command.
- **No rotation path**, so a leaked key stays valid indefinitely.

---

## See also

- [[Coding Knowledge/06 - DevOps & Infrastructure/Deployment|Deployment]]
- [[Coding Knowledge/05 - Web & Application Engineering/Web Security|Web Security]]
- [[Coding Knowledge/11 - Vision & OpenCode/Known Constraints|Known Constraints]]

## Sources

- The Twelve-Factor App, config - <https://12factor.net/config> (repository CC BY 4.0, verified 2026-09-03); OWASP Secrets Management Cheat Sheet - <https://cheatsheetseries.owasp.org/> (CC BY-SA 4.0, synthesised). The PersistentConfig behaviour was observed in this project.
