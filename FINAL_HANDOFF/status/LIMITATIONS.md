<!-- Extracted verbatim from reports/01-FINAL-REPORT-R3.md.
     Do not edit here; edit the report and re-extract. -->

# Known limitations and unresolved issues

Two sections, verbatim from the final report. The first is the twelve
limitations of *this build*. The second is what a 4B model cannot do at
all, which no amount of further engineering here would fix.

---

## 15. Limitations — the honest list

Twelve of them, ordered by how much they would matter to you in daily
use.

**1. Latency on this hardware is not the latency you would get, and I
cannot prove the number you care about.** 6 tok/s on CPU. The GPU
projection is RESEARCHED. Until it runs on the 4050, "fast enough for
conversation" is an expectation, not a result.

**2. Voice is untested where it is hardest.** Code-switched Hindi-English
ASR is the single biggest open risk in the design (~42% WER for
monolingual models, RESEARCHED). Everything above the transcript is tested;
the transcript itself is not.

**3. Fact extraction covers seven predicates.** The extractor exists now
(§12) and it is a keyhole: editor, employer, city, study topic, name,
working hours, stated preferences. Anything else you tell it in
conversation is not stored, and you will not be told that it wasn't. This
is a deliberate precision trade — the alternative is a wider extractor that
occasionally writes something false into permanent memory — but it is a
limit, not a design victory.

**4. The model is still a 4B model.** It gets things wrong that no
architecture can fix:

```
USER: aur 02:00?
AI:   Haan, 02:00 bhi raat ka hai.

USER: ab dar lag raha hai kuch toot na jaye
AI:   Haha, bhai ab production mein khud ko chhota kar liya hai!
```

The first is wrong. The second is close to nonsense. Neither is a routing,
gating or honesty failure — they are capacity failures, and the honest
answer is that they will keep happening at this size.

**5. The router decides "is this a question about the world" with a
list, and lists have holes.** F2, F23 and F43 are one failure — a personal
remark treated as a query — caught by three different gates, each written
after the previous one let a phrasing through: *"aaj bahut thak gaya
hoon"*, then *"kal wala kaam"*, then *"yaar aaj bahut kaam tha"*. The gates
are individually correct and the approach has a ceiling. A small
classifier would not have holes in the same places, and this is where one
would earn its keep before it would anywhere else.

**6. Language identification is a wordlist.** ~90% on realistic mixed
input. It should be a small statistical LID model, or the conversational
model should tag its own turn. The heuristic exists so the deterministic
layer has an answer without a model round-trip.

**7. The honesty guards are blunt.** When they fire, they replace the whole
reply. If a reply contains one fabricated citation and three good
sentences, all four go. This is a deliberate trade and it is the wrong
trade in some cases.

**8. One guard extension is speculative.** The source-claim check was
measured on the web and vault paths and then extended to the fast path by
reasoning, not measurement. It is flagged in the code and watched in
round 3.

**9. Anaphora resolution is one turn deep.** *"Iska latest answer web se
check kar"* now falls back to the previous user turn (F34) and a short
follow-up keeps the previous turn's evidence (F41). Neither reaches further
back than one turn, and neither resolves *which* of several things "iska"
refers to. It is a fallback, not a resolver.

**10. Question restraint is only achievable by editing the output.** The
model will not obey an instruction about the shape of its own reply (§22).
The strip and the retry between them keep a third consecutive question off
the screen most of the time; neither reduces how often the model wants to
ask one. If you find it asks too much, that is the honest state of it.

**11. Memory search is a keyword scan.** `search_turns` walks the last 400
stored turns and ranks by content-word overlap. That is enough to answer
"do you remember X" honestly at the scale of one person's conversations and
it is not a retrieval system. It should share the vault's hybrid index; it
does not yet.

**12. Everything here is single-user and local.** No multi-user isolation,
no sync, no mobile. Out of scope by design, but worth stating so the scope
is not overread.

---

---

## 29. What a 4B model cannot do, no matter the architecture

Stated plainly, because the rest of this report is about things that were
fixable.

**It gets facts wrong.** *"Haan, 02:00 bhi raat ka hai"* is simply
incorrect. No router, guard or gate helps.

**It loses the thread on emotionally complex turns.** *"ab dar lag raha hai
kuch toot na jaye"* (now I'm scared something will break) got *"Haha, bhai
ab production mein khud ko chhota kar liya hai!"* — a reply that is close
to nonsense.

**It cannot be calibrated by instruction.** §5 is the measured version of
this: it obeys "never X" and ignores "not too much X".

**Knowledge capacity is roughly 2 bits per parameter** (RESEARCHED,
arXiv:2404.05405). At 4B that is a hard ceiling on what can live in the
weights, which is the whole reason retrieval exists in this design rather
than being an optional extra.

**Multi-turn degradation is real** (RESEARCHED, arXiv:2505.06120: 39%
average drop across models). Every conversation in the mandatory set is
multi-turn for exactly this reason — single-turn probes measure the model
at its best and the product at its least representative.

---
