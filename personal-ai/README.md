# Personal AI — deterministic runtime

The parts of the personal-AI architecture that are ordinary software, built
and tested first because they are where the project actually lives or dies.

    pai/trust.py      provenance + the privilege invariant
    pai/memory.py     four-tier store (bitemporal T2, capped T3)
    pai/signals.py    feedback detection, EN / HI / Hinglish
    pai/learning.py   candidate -> evidence -> review -> promote -> decay
    pai/gateway.py    permission tiers, taint tracking, injection defence
    pai/obsidian.py   heading-aware chunking + hybrid BM25/dense retrieval

Stdlib only (Python 3.11, sqlite3 + FTS5). No torch, no numpy: the core runs
on the target laptop without a dependency tree, and the model-facing pieces
are behind interfaces.

Run the tests:

    python3 -m unittest discover -s tests -v
