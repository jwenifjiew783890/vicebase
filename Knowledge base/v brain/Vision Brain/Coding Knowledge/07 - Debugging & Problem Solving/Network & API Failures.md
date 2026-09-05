---
type: note
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Network & API Failures

Diagnosing calls that fail, hang, or succeed with the wrong result.

## The four outcomes, not two

Success, failure, **timeout with unknown state**, and **success the caller never learned about**.
Designs and diagnoses that consider only the first two are the source of duplicate charges,
lost writes and stuck workflows.

A timeout means *you do not know* whether the work happened. Treat it as unknown, not as failed.

## Reading the failure

| Symptom | Means | Next check |
| --- | --- | --- |
| Connection **refused** | Reached the host, nothing listening | Is the process up? Right port? |
| **Timeout** | Packets dropped silently | Firewall, security group, wrong address |
| **DNS failure** | Name problem, not connectivity | `dig`, hosts file, resolver config |
| **TLS handshake failure** | Certificate, version, SNI, cipher | `openssl s_client -connect` |
| **Reset by peer** | Something closed it deliberately | Proxy, idle timeout, protocol mismatch |
| **502 / 504** | Upstream failed or was slow | The upstream's own logs |
| **429** | Rate limited | Respect `Retry-After`; check the limit dimension |
| **401 vs 403** | Not authenticated vs not permitted | Token validity vs permissions |
| Intermittent | One bad backend behind a load balancer | Hit each backend directly |

**Refused versus timeout is the highest-value distinction** and it takes one command to obtain.

## The elimination sequence

1. Is the process listening, and **on which interface**? `127.0.0.1` versus `0.0.0.0` explains a
   large share of "it's running but unreachable", especially across container and WSL boundaries.
2. Does it work from the same host? `curl -v http://127.0.0.1:port`
3. Does the name resolve, and to the expected address?
4. Is the port reachable from the caller? `nc -vz` / `Test-NetConnection`
5. Firewall, security group, proxy.
6. TLS - chain, expiry, hostname, protocol version.
7. Application - status, headers, body.

## API-specific diagnosis

- **`curl -v`** shows the request as sent, the redirects followed, the response headers and the
  status. Reproduce the failing call with curl before anything else - it eliminates the client
  library as a variable in one step.
- **Compare the working and failing request** header by header. The difference is almost always
  authentication, content type, or a header the client library adds silently.
- **Check the response body on errors.** Many clients discard it, and it usually contains the
  actual reason.
- **Check `finish_reason` / status semantics.** A 200 with an error in the body defeats every
  retry policy.
- **Verify the version and the endpoint.** "OpenAI-compatible" and similar claims describe the
  request shape, not the feature set. *(Measured here: a compatible endpoint that did not
  implement the newer response API returned a silent empty reply rather than an error.)*

## Hangs

An unbounded call will wait for as long as the peer allows. When something hangs:

- Check whether a timeout is configured **at all** - most libraries default to none or to
  minutes.
- Check retries: a default of two retries turns one stall into three.
- Get a stack dump of the hung process (`py-spy dump`, `jstack`, `dlv`) to see exactly where it
  is blocked.
- Check the *other* side's logs - it may be working very slowly rather than being stuck.

*Measured in this project: an unbounded model call hung for 302 seconds against a degraded
provider, and a retry was still hanging past ten minutes. Setting `timeout: 60000` and
`maxRetries: 1` converted an indefinite freeze into a clean 61-second failure.*

## Intermittent failures

- **One bad instance** behind a load balancer - test each directly.
- **DNS round-robin** to a stale address.
- **Connection pool** holding a connection the server has already closed - the first request
  after an idle period fails.
- **MTU / fragmentation** - large responses fail while small ones succeed. Distinctive and easy
  to miss.
- **Clock skew** breaking token validation.
- **Rate limiting** that only engages at peak.

## Design fixes

Timeouts everywhere; bounded retries with exponential backoff and jitter; idempotency keys so a
retry after an unknown outcome is safe; circuit breakers so a failing dependency fails fast; and
a defined degraded behaviour rather than a 500.

---

## See also

- [[Coding Knowledge/06 - DevOps & Infrastructure/Networking|Networking]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]
- [[Coding Knowledge/03 - AI Engineering/LLM APIs|LLM APIs]]

## Sources

- RFC 9110 HTTP semantics - <https://www.rfc-editor.org/rfc/rfc9110>; AWS Builders' Library on timeouts and retries - <https://aws.amazon.com/builders-library/>. The 302-second stall was measured in this project.
