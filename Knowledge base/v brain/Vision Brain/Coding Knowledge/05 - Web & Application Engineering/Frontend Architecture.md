---
type: note
domain: Coding Knowledge
section: 05 - Web & Application Engineering
created: 2026-09-03
---

# Frontend Architecture

Where state lives, when things render, and what the user waits for.

## State is the whole problem

Almost every frontend difficulty is a state problem wearing a costume. Categorise it, because
each kind wants a different mechanism:

| Kind | Example | Belongs in |
| --- | --- | --- |
| **Server state** | Data fetched from an API | A data-fetching layer with caching (TanStack Query, SWR, load functions) |
| **URL state** | Filters, page, selected item | The URL - so it is shareable, bookmarkable and survives reload |
| **Local UI state** | Is this dropdown open | The component |
| **Shared UI state** | Theme, sidebar collapsed | A small store or context |
| **Form state** | In-progress input | A form library or local state |

**The most common architectural mistake is putting server state in a global store.** It then
needs manual invalidation, manual loading flags, manual error handling and manual refetching -
all of which a data-fetching library already does correctly.

**The second most common is not putting filter state in the URL**, after which the back button
and sharing both break.

## Rendering strategies

| Strategy | Good for | Cost |
| --- | --- | --- |
| **Static (SSG)** | Content that rarely changes | Rebuild to update |
| **Server-rendered (SSR)** | Dynamic, SEO-relevant, fast first paint | Server cost per request |
| **Client-rendered (SPA)** | App-like, highly interactive | Slow first paint, JS required |
| **Streaming / progressive** | Large pages with slow parts | More complexity |

Most applications are best served by server rendering with selective client interactivity.
A full SPA for a content site is a common and expensive mistake.

## Components

- **Separate presentational from data-fetching.** A component that both queries and renders is
  hard to test and hard to reuse.
- **Push state as far down as it will go.** State at the root re-renders the world.
- **Props flow down, events flow up.** Consistency here is what keeps data flow traceable.
- **Composition over configuration.** A component with fifteen boolean props should be several
  components.
- **Keys must be stable and unique.** Index-as-key is a real bug: reorder a list and component
  state attaches to the wrong item.

## Performance

- **Bundle size is the first-load cost.** Measure it, budget it, and check what each dependency
  adds. A date library can be larger than the application.
- **Code-split by route** at minimum.
- **Lazy-load below the fold**, and set explicit image dimensions to avoid layout shift.
- **Virtualise long lists.** Rendering 10,000 rows is never necessary.
- **Memoise only after profiling.** `useMemo` everywhere adds cost and hides the real problem.
- **Debounce input-driven requests**, and cancel superseded ones.

## Accessibility, briefly and non-negotiably

Semantic HTML first - a `<button>` is a button. Keyboard navigation for everything clickable.
Visible focus. Labels on inputs. Sufficient contrast. ARIA only where semantics genuinely fall
short; incorrect ARIA is worse than none.

## Failure modes

- **Server state in a global store**, hand-synchronised.
- **Filter and pagination state not in the URL.**
- **Waterfall requests** - each component fetching on mount, sequentially.
- **No loading or error states**, so a slow network looks broken.
- **Unbounded bundle growth**, unnoticed because nobody measures it.
- **Index as key** in a reorderable list.
- **State updates after unmount**, leaking and warning.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/JavaScript|JavaScript]]
- [[Coding Knowledge/05 - Web & Application Engineering/Web Performance|Web Performance]]
- [[Coding Knowledge/01 - Software Engineering/Modularity & Abstraction|Modularity & Abstraction]]

## Sources

- MDN Web Docs - <https://developer.mozilla.org/> (CC BY-SA 2.5; facts restated). WCAG - <https://www.w3.org/WAI/standards-guidelines/wcag/>. Practitioner synthesis otherwise.
