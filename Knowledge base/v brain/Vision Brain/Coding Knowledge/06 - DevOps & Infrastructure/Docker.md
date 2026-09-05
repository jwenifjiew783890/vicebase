---
type: note
domain: Coding Knowledge
section: 06 - DevOps & Infrastructure
created: 2026-09-03
---

# Docker

Containers as a packaging and isolation mechanism, and the operational details that cause most of the trouble.

## The model

An **image** is an immutable stack of filesystem layers plus metadata. A **container** is a
running process using that image with a thin writable layer on top. Containers share the host
kernel - this is process isolation, not virtualisation, and it is why a container is not by
itself a security boundary against a determined attacker.

## Images

- **Pin base image tags** to a digest or a specific version. `FROM node:latest` means the build
  is not reproducible and can break without any change from you.
- **Order layers by change frequency**: system packages, then dependency manifests, then
  `install`, then application source. Copying source before installing dependencies invalidates
  the dependency cache on every code change - the most common reason builds are slow.
- **Multi-stage builds**: compile in a full image, copy only artefacts into a slim runtime.
  Often reduces the image by an order of magnitude.
- **`.dockerignore`** matters as much as `.gitignore` - without it, `node_modules`, `.git` and
  build output enter the build context and the image.
- **Never put secrets in a layer.** Layers are permanent; deleting a file in a later layer does
  not remove it from the image, and anyone with the image can extract it. Use build secrets or
  runtime environment injection.
- **Run as a non-root user.**
- **One concern per container.**

## Runtime

- **Volumes for data that must survive**, bind mounts for development. Anything in the container's
  writable layer is gone when it is removed.
- **Set resource limits** (`--memory`, `--cpus`). Without them, one container can take the host
  down. A container OOM-killed by the kernel exits with code 137, which is the fastest
  identification of that failure.
- **Restart policies**: `unless-stopped` for services you want back after a reboot or a daemon
  restart; `on-failure` with a limit where a crash loop should stop.
- **Health checks** so orchestration knows the difference between running and working.
- **Handle SIGTERM** for graceful shutdown, or every restart drops in-flight work. A process
  running as PID 1 does not get default signal handling - use an init (`--init`) or handle it
  explicitly.
- **Logs go to stdout/stderr**, and need a rotation policy or they will fill the disk.

## Networking

- Containers on a user-defined bridge network reach each other **by container name**. On the
  default bridge they do not.
- **`localhost` inside a container is the container**, not the host. To reach the host, use
  `host.docker.internal` (Docker Desktop) or the gateway address.
- Publishing a port (`-p 8080:80`) binds on the host; by default that can be all interfaces.
  Bind to `127.0.0.1:8080:80` for anything that should not be exposed on the network.

## Failure modes

- **`latest` tags**, producing unreproducible builds and surprise breakage.
- **Data in the container**, lost on `docker rm`.
- **No resource limits**, so one container exhausts the host.
- **Secrets baked into layers.**
- **Huge images** from single-stage builds and a missing `.dockerignore`.
- **Clock and timezone assumptions** - containers are UTC unless configured.
- **Mounting the Docker socket** into a container, which is equivalent to giving it root on the
  host.

> [!danger] Do not force-kill the Docker daemon
> Measured in this project: force-killing Docker Desktop left a stale `sailor-ingest.sock` and
> caused roughly 20 minutes of downtime before containers returned (they came back on their own
> because of `unless-stopped`). **Stop the daemon through its own shutdown path.** Killing a
> daemon that owns sockets and mounts leaves state that the next start has to reconcile - the
> same lesson applies to any daemon of this kind.

---

## See also

- [[Coding Knowledge/06 - DevOps & Infrastructure/WSL|WSL]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Processes & Resources|Processes & Resources]]
- [[Coding Knowledge/04 - Agent Engineering/Sandboxing|Sandboxing]]

## Sources

- Docker documentation - <https://docs.docker.com/>. The Docker Desktop force-kill incident was observed in this project on 2026-09-03.
