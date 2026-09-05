---
type: note
domain: Coding Knowledge
section: 05 - Web & Application Engineering
created: 2026-09-03
---

# Web Performance

What users actually perceive, and where the time actually goes.

## Measure what users experience

Lab numbers on a fast machine on a fast network are not the experience. Measure field data,
across real devices and networks, and report percentiles - the p75 and p95 are the users who
leave.

**Core Web Vitals** are a reasonable shared vocabulary:

- **LCP** (Largest Contentful Paint) - when the main content appears. Loading.
- **INP** (Interaction to Next Paint) - responsiveness to input. Replaced FID.
- **CLS** (Cumulative Layout Shift) - visual stability.

## Where the time usually goes

In rough order of how often each is the culprit:

1. **Too much JavaScript** - download, parse, execute, hydrate. Usually the single largest cost.
2. **Unoptimised images** - the largest bytes on most pages.
3. **Render-blocking resources** in `<head>`.
4. **Waterfall requests** - each dependent on the previous, so latency multiplies.
5. **A slow server response** (TTFB) - often one slow query.
6. **Third-party scripts** - analytics, tag managers, chat widgets; frequently the worst
   offenders and the least examined.
7. **Layout thrash** - reading and writing layout properties alternately in a loop.

## The moves that matter most

- **Ship less JavaScript.** Audit dependencies, code-split by route, defer non-critical work,
  and question every third-party script. This is almost always the biggest lever.
- **Optimise images**: modern formats (AVIF/WebP), correct dimensions, `loading="lazy"` below
  the fold, explicit `width`/`height` to prevent layout shift, responsive `srcset`.
- **Compress** with Brotli or gzip; serve everything text-based compressed.
- **Cache aggressively with content-hashed filenames** - immutable assets can be cached for a
  year safely.
- **Preconnect and preload** critical resources; `font-display: swap` to avoid invisible text.
- **Fix the server**: the slow query is usually one query, and profiling finds it in minutes.
- **Stream HTML** so the browser can start work before the server has finished.

## Backend performance

- **Profile before optimising.** Intuition about where time goes is wrong more often than right.
- **Database first.** Missing indexes and N+1 queries dominate most slow endpoints.
- **Cache after fixing**, not instead - see [[Coding Knowledge/05 - Web & Application Engineering/Caching|Caching]].
- **Move slow work off the request path** onto a queue.
- **Measure percentiles.** An average latency of 200 ms with a p99 of 8 seconds is a broken
  service for one request in a hundred.

## Budgets

Set explicit budgets - total JavaScript, total page weight, LCP target - and enforce them in CI.
Without a budget, size grows monotonically and nobody is responsible for it. With one, the cost
of a new dependency becomes a visible decision rather than a silent regression.

## Failure modes

- **Optimising without measuring**, and shipping effort that changes nothing.
- **Micro-optimising code** while a 2 MB image loads.
- **Lab-only measurement**, missing the real device and network distribution.
- **Averages instead of percentiles.**
- **No regression check**, so every release is slightly slower than the last.

---

## See also

- [[Coding Knowledge/05 - Web & Application Engineering/Frontend Architecture|Frontend Architecture]]
- [[Coding Knowledge/05 - Web & Application Engineering/Caching|Caching]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Performance Profiling|Performance Profiling]]

## Sources

- web.dev Core Web Vitals - <https://web.dev/articles/vitals>; MDN performance documentation - <https://developer.mozilla.org/> (CC BY-SA 2.5, facts restated).
