<!-- Extracted verbatim from reports/01-FINAL-REPORT-R3.md.
     Do not edit here; edit the report and re-extract. -->

# What remains

## 17. What I would build next, in order

1. **Widen the fact extractor.** It exists now and covers seven
   predicates. Each new one is pattern work with a precision requirement,
   and each is a new way to write something false into permanent memory —
   which is why this is careful work rather than a lot of work.
2. **Run it on the 4050.** Turns the biggest RESEARCHED number in this
   report into a MEASURED one, and it is a day of work.
3. **Code-switched ASR evaluation.** Not a fix — a measurement. Until the
   WER on your actual speech is known, the voice design is built on a
   published number about somebody else's speech.
4. **A classifier for "is this a question about the world".** F2, F23 and
   F43 are one failure caught by three list-based gates, each written after
   the last let a phrasing through. This is where a small model earns its
   keep before it does anywhere else, and it is a bounded, supervised
   problem with a labelled corpus already sitting in `eval/transcripts/`.
5. **Statistical LID.** Replaces the wordlist. The interface —
   `detect_language(text, default)` — already exists, so nothing else has
   to change.
6. **Selective honesty guards.** Replace the offending sentence rather than
   the whole reply. Needs sentence-level attribution, which is why it is
   sixth and not first.

Deliberately **not** on this list: fine-tuning, a bigger model, and more
prompt engineering. The measured evidence says none of the three would fix
what is actually broken.

---

---

## Also outstanding, from elsewhere in the record

- **`eval/asr_test.py` has never been run.** No `asr_hi.json` exists.
  Every WER figure in every report is RESEARCHED. This is roadmap item 3
  and the largest untested risk in the design.
- **OpenCode is not installed** in this environment. The client is tested
  against a real local HTTP server, but never against OpenCode itself.
  (Completion bar row 9, PARTIAL.)
- **No GPU.** Every latency figure for the RTX 4050 is a projection.
  (Completion bar rows 10 and 19.)
- **No audio device.** Voice policy is fully tested; every audio *model*
  is untested.

None of these four can be resolved by further work in this environment.
All four are hardware or environment limits, not design questions.
