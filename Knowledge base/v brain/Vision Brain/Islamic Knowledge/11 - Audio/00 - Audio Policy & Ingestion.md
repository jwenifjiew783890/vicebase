---
type: Policy
category: Audio
items_imported: 0
retrieved_at: 2026-09-03
---

# Audio - Policy and Ingestion

> [!danger] Nothing has been imported here, and no audio entry has been invented.
> The scholar audio folders are **empty by design**. Inventing plausible lecture titles or
> audio URLs would be exactly the fabrication this library forbids, so none exist.

## Why empty

Two separate blockers, both real:

1. **Copyright.** Audio being reachable is not permission to copy it. Recordings on the
   official sites are not published under any licence that permits redistribution.
2. **Verification.** A correct audio entry needs a real title, a real date, a real URL and a
   real speaker attribution. None of that can be produced from memory, and this library
   does not guess.

## What is permitted

| Action | Allowed? |
| --- | --- |
| Store metadata + a link to the official page | **Yes** |
| Embed or hotlink an official streaming URL | Yes, if the site permits it |
| Download audio because the file is reachable | **No** |
| Download from a mirror or re-upload | **No** |
| Transcribe audio you are not licensed to copy | **No** |
| Invent a title, date, duration or URL | **Never** |

## Required fields for any audio entry

```yaml
type: Audio
scholar:            # exact attribution
title:              # as published, not paraphrased
topic:
date:               # or UNKNOWN
duration:           # or UNKNOWN
series:
source_site:
original_url:       # the page, always
audio_url:          # only if lawfully linkable
transcript:         # only if lawfully available
language:
category:           # lecture / lesson / fatwa / bayan / recitation
license_status:     # must be explicit
retrieved_at:
```

## Verified starting points

| Scholar | Audio library | Status |
| --- | --- | --- |
| Ibn Baz | https://binbaz.org.sa/audios | Verified reachable 2026-09-03; robots.txt allows crawling except `/index.php` |
| Ibn Uthaymeen | https://binothaimeen.net/ | Verified reachable; **express EU Art. 4 rights reservation** - link only |
| Al-Fawzan | https://alfawzan.af.org.sa/ | **Offline** when checked 2026-09-03 |
| Al-Albani | UNKNOWN | No official repository verified |

## Ingestion procedure (for when you want items added)

1. Identify the item on the **official** site; capture the page URL.
2. Record metadata **from the page**, never from recall.
3. Check the site's terms and `robots.txt` for that path.
4. If redistribution is not clearly permitted -> store metadata + link, and stop.
5. Only if explicitly authorised -> store the file, and record the authorisation.
6. Never transcribe without a licence; never fabricate a transcript.

Rate-limit any fetching, honour `robots.txt`, and do not crawl in bulk.

[[Islamic Knowledge/99 - Source & Authenticity Rules|Source & Authenticity Rules]].