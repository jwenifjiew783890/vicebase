"""Recompute conversation metrics from a stored run, under the CURRENT
definitions.

Needed because metric definitions changed after some runs were recorded --
`lang_match_rate` used to score turns where the user had not committed to a
language at all (see the measurement note in
docs/CONVERSATION-FAILURES.md). Comparing a round measured under the old
definition with one measured under the new is meaningless, so every
comparison in the final report is recomputed from the stored turns.

Usage:  python3 eval/recompute_metrics.py <results.json> [<results.json> ...]
"""
from __future__ import annotations
import json, os, statistics as st, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eval.convmetrics import analyse


def summarise(path: str) -> dict:
    data = json.load(open(path))
    turns = [t for c in data for t in c["turns"]]
    words = [t["words"] for t in turns]
    ends_q = [t["ai"].rstrip().endswith("?") for t in turns]
    runs = []
    for c in data:
        best = cur = 0
        for t in c["turns"]:
            cur = cur + 1 if t["ai"].rstrip().endswith("?") else 0
            best = max(best, cur)
        runs.append(best)
    ms = [analyse([t["user"] for t in c["turns"]],
                  [t["ai"] for t in c["turns"]]) for c in data]
    scored = sum(m.lang_scored_turns for m in ms)
    matched = sum(m.lang_match_rate * m.lang_scored_turns for m in ms)
    routes: dict = {}
    for t in turns:
        routes[t["route"]] = routes.get(t["route"], 0) + 1
    return {
        "conversations": len(data),
        "turns": len(turns),
        "mean words": round(st.mean(words), 1),
        "median words": st.median(words),
        "max words": max(words),
        "ends with ?": f"{sum(ends_q)}/{len(turns)} "
                       f"({round(100*sum(ends_q)/len(turns))}%)",
        "max question run": max(runs),
        "convs over the cap": sum(1 for r in runs if r > 2),
        "language match": f"{round(matched)}/{scored} "
                          f"({round(100*matched/scored) if scored else 0}%)",
        "assistant tells": sum(m.ai_tells for m in ms),
        "opener variety": round(sum(m.opener_variety for m in ms)/len(ms), 3),
        "repetition": round(sum(m.repetition_score for m in ms)/len(ms), 3),
        "acks": sum(1 for t in turns if t.get("ack")),
        # Distinguish "zero" from "this run predates the field". Reporting
        # a missing column as 0 would make round 2 look like it retrieved
        # nothing on purpose rather than not recording it.
        "evidence>0": (sum(1 for t in turns if t.get("evidence", 0))
                       if any("evidence" in t for t in turns) else "n/r"),
        "guards fired": (sum(1 for t in turns if t.get("guard"))
                         if any("guard" in t for t in turns) else "n/r"),
        "tool runs": sum(len(t.get("actions") or []) for t in turns),
        "gated actions": sum(len(t.get("pending") or []) for t in turns),
        "routes": routes,
    }


def main():
    paths = sys.argv[1:]
    cols = [summarise(p) for p in paths]
    names = [os.path.basename(os.path.dirname(p)) for p in paths]
    width = max((len(str(v)) for c in cols for v in c.values()), default=20) + 2
    print(f"{'metric':<20}" + "".join(f"{n:<{width}}" for n in names))
    print("-" * (20 + width * len(names)))
    for k in cols[0]:
        print(f"{k:<20}" + "".join(f"{str(c[k]):<{width}}" for c in cols))


if __name__ == "__main__":
    main()
