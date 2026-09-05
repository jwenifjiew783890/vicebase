---
type: note
domain: Coding Knowledge
section: 10 - Engineering Experience
created: 2026-09-03
---

# Production Incident Lessons

What published postmortems keep teaching, and how to respond when it is your turn.

## What the public record repeats

Summarised in our own words from the companies' own published reports.

**A change deployed everywhere at once, with no staged rollout.** Cloudflare's 2 July 2019
outage was a WAF rule containing a regular expression with catastrophic backtracking, which
consumed CPU globally. The deployment path deliberately bypassed the staged DOG/PIG/Canary
pipeline in order to respond quickly to threats - so a bad rule reached the whole fleet in
seconds. **Lesson: the fast path around your safety mechanism is where the outage comes from.**

**A routine operation performed on the wrong target.** AWS's S3 outage on 28 February 2017 began
with a command run during debugging that removed more capacity than intended.
**Lesson: destructive tooling needs guard rails, not care.**

**Backups that had never been tested.** GitLab's database incident of 31 January 2017 combined
an accidental deletion with the discovery that several recovery procedures did not work when
needed. **Lesson: an untested backup is a hypothesis, and you will test it at the worst moment.**

**A partial deployment leaving versions inconsistent.** Knight Capital's 2012 failure involved
new code not reaching every server, with a repurposed flag activating dormant legacy behaviour
on the ones left behind. **Lesson: verify that a deploy actually reached everything, and never
reuse a flag whose old meaning still exists in code.**

**Losing the ability to fix it.** Facebook's 4 October 2021 outage withdrew BGP routes, which
also removed the remote access engineers needed to undo it. **Lesson: out-of-band access must
not depend on the system it recovers.**

**A dependency failing in an unanticipated direction.** Repeatedly: a "non-critical" service
being slow rather than down, holding threads until the critical path starved.
**Lesson: slow is worse than down, and it is the case nobody tests.**

## The patterns underneath

1. **The trigger is usually small and routine.** A config change, a rule, a command, a
   certificate. The damage comes from amplification, not from the size of the mistake.
2. **The failure is rarely single.** Several safeguards were absent, disabled, or untested at
   once.
3. **Recovery took longer than the failure** - and recovery time is what determines the impact.
4. **Detection was slow.** The largest improvements available are usually in noticing, not in
   preventing.
5. **The safety mechanism was bypassed for good reasons.** Speed, urgency, an exception "just
   this once".

## Responding to your own incident

**During**
1. **Stop the bleeding first.** Restore service; understand it afterwards. Rolling back is the
   correct first move even when the cause is unknown.
2. **Preserve evidence before restarting** - logs, a thread dump, a heap dump, the process list,
   the current config. Sixty seconds here is the difference between fixing it and waiting for it
   to recur.
3. **One person coordinates**, one communicates, others investigate. Everyone investigating in
   parallel produces duplicated work and no shared picture.
4. **Write a timeline as you go.** Nobody remembers it accurately afterwards.
5. **Do not make unrelated changes** during an incident.

**After**
- **Blameless.** The question is what made the mistake possible and undetected, not who made it.
- **Timeline with detection and recovery times** as first-class facts.
- **Causes at every layer** - see
  [[Coding Knowledge/07 - Debugging & Problem Solving/Root Cause Analysis|Root Cause Analysis]].
- **Actions with owners**, and a bias toward *detection* improvements, which usually pay more
  than prevention.
- **A regression test**, so this exact failure cannot return silently.

## The uncomfortable pattern

Most incidents were **known risks that nobody had prioritised**. The postmortem action item
"add a staged rollout" often already existed as a ticket. The value of an incident is that it
converts a theoretical risk into a funded one - so write the finding down while that is true.

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Incident Management|Incident Management]]
- [[Coding Knowledge/12 - Reliability Engineering/Postmortems|Postmortems]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Root Cause Analysis|Root Cause Analysis]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Backups|Backups]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]
- [[Coding Knowledge/10 - Engineering Experience/Common Failure Patterns|Common Failure Patterns]]

## Sources

- Cloudflare, "Details of the Cloudflare outage on July 2, 2019" - <https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/> (fetched and verified 2026-09-03). AWS, "Summary of the Amazon S3 Service Disruption" (28 Feb 2017) - <https://aws.amazon.com/message/41926/>. GitLab, "Postmortem of database outage of January 31" - <https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/> (cited; not re-fetched - the URL returned 403 on 2026-09-03, so only the widely-reported headline finding is stated here). Knight Capital: SEC administrative proceeding 34-70694 (2013). Meta, "More details about the October 4 outage" - <https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/>. Index of further postmortems: <https://github.com/danluu/post-mortems>. All summarised in our own words; no report text reproduced.
