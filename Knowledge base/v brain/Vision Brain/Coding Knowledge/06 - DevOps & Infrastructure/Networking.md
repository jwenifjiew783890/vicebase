---
type: note
domain: Coding Knowledge
section: 06 - DevOps & Infrastructure
created: 2026-09-03
---

# Networking

Diagnosing connectivity by eliminating layers, in the order that costs least.

## The elimination sequence

Work outward. Each step is cheap and eliminates a whole class of cause.

1. **Is the process running and listening?** `ss -tlnp` (Linux) / `Get-NetTCPConnection`,
   `netstat -ano` (Windows). If nothing is listening, nothing else matters.
2. **On which interface?** `127.0.0.1` is reachable only from the same host; `0.0.0.0` is all
   interfaces. This alone explains a large share of "the service is up but I cannot connect",
   especially across a container or WSL boundary.
3. **Can you connect locally?** `curl -v http://127.0.0.1:port`. Works locally but not remotely
   -> firewall, binding, or routing.
4. **Does the name resolve?** `nslookup`/`dig`. Resolves to the address you expect? Stale DNS,
   a hosts-file entry and split-horizon DNS all live here.
5. **Is the port reachable?** `nc -vz host port` / `Test-NetConnection host -Port n`. Refused
   means something answered and said no; timeout means a firewall dropped it silently. **That
   distinction is the most useful single signal in network debugging.**
6. **Firewall** - host firewall, cloud security group, corporate proxy.
7. **TLS** - `openssl s_client -connect host:443` shows the certificate chain, the negotiated
   version, and the exact failure.
8. **Application layer** - `curl -v` for status, headers and redirects.

## Reading the failure

| Symptom | Usually means |
| --- | --- |
| Connection **refused** | Reached the host; nothing listening on that port |
| Connection **timed out** | Packets dropped - firewall, wrong address, no route |
| **DNS resolution failed** | Name problem, not connectivity |
| **TLS handshake failure** | Certificate, version, SNI or cipher mismatch |
| **Reset by peer** | Something closed it deliberately mid-connection |
| Works by IP, not by name | DNS |
| Works locally, not remotely | Binding or firewall |
| Intermittent | Load balancer with one bad backend, DNS round-robin, or MTU |

## HTTPS and certificates

The common failures, and their correct fixes:

- **Self-signed or private CA** - *trust the CA*, do not disable verification. Point the client
  at the CA bundle (`NODE_EXTRA_CA_CERTS`, `REQUESTS_CA_BUNDLE`, `SSL_CERT_FILE`).
  *(This stack does exactly that for Obsidian's local HTTPS API. Disabling verification is not
  an option.)*
- **Hostname mismatch** - the certificate does not cover the name used. Connecting by IP to a
  name-based certificate always fails.
- **Expired** - check `notAfter`, and set an expiry alert; certificate expiry is one of the most
  common self-inflicted outages there is.
- **Incomplete chain** - works in a browser (which fetches intermediates) and fails in `curl` or
  a library. Serve the full chain.

## Proxies

Corporate proxies intercept TLS and re-sign with their own CA, which breaks clients that do not
trust it. Respect `HTTP_PROXY`, `HTTPS_PROXY` and `NO_PROXY`, and note that not every library
does automatically.

## Localhost is not one address

`localhost` may resolve to `::1` before `127.0.0.1`. A service bound only to IPv4 is then
unreachable by name while reachable by address. When a connection to `localhost` fails
inexplicably, try `127.0.0.1` explicitly - it is a five-second test that resolves it.

## Timeouts

Distinguish **connect**, **read** and **total** timeouts; a library that sets only one leaves
the others unbounded. A slow response and an unreachable host are different failures and should
be configured differently.

---

## See also

- [[Coding Knowledge/06 - DevOps & Infrastructure/Linux|Linux]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/WSL|WSL]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Network & API Failures|Network & API Failures]]

## Sources

- Standard networking tooling documentation (`ss`, `dig`, `curl`, `openssl`, `Test-NetConnection`). The CA-trust approach is this project's configured behaviour for Obsidian's local HTTPS API.
