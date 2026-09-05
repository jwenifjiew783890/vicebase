"""Round 2 vs round 3, on the frozen mandatory set.

Same twenty conversations, same persona, same model, same seed -- the only
difference is the eight defences added between the runs. Anything that
moved, moved because of those.

Prints the aggregate table and, more usefully, every turn whose ROUTE
changed, since a routing change is the mechanism most of the fixes work
through.
"""
from __future__ import annotations
import json, os, statistics as st, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    with open(os.path.join(ROOT, path)) as fh:
        return json.load(fh)


def agg(data):
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
    routes = {}
    for t in turns:
        routes[t["route"]] = routes.get(t["route"], 0) + 1
    ms = [c["metrics"] for c in data if "metrics" in c]

    def m(k):
        v = [x[k] for x in ms if isinstance(x.get(k), (int, float))]
        return sum(v) / len(v) if v else float("nan")

    return {
        "conversations": len(data),
        "turns": len(turns),
        "mean words": round(st.mean(words), 1),
        "median words": st.median(words),
        "max words": max(words),
        "ends with ?": f"{sum(ends_q)}/{len(turns)} = {100*sum(ends_q)//len(turns)}%",
        "max question run": max(runs),
        "convs over the cap": sum(1 for r in runs if r > 2),
        "language match": round(m("lang_match_rate"), 3),
        "assistant tells": round(m("ai_tells"), 3),
        "opener variety": round(m("opener_variety"), 3),
        "repetition": round(m("repetition_score"), 3),
        "routes": routes,
        "acks emitted": sum(1 for t in turns if t.get("ack")),
        "evidence>0 turns": sum(1 for t in turns if t.get("evidence", 0)),
        "guards tripped": sum(1 for t in turns if t.get("guard")),
    }


def main():
    a = load("eval/transcripts/final2/v3_results.json")
    b = load("eval/transcripts/final3/v3_results.json")
    ka, kb = agg(a), agg(b)

    print(f"{'metric':<22} {'round 2 (pre-fix)':<28} {'round 3 (post-fix)':<28}")
    print("-" * 80)
    for k in ka:
        print(f"{k:<22} {str(ka[k]):<28} {str(kb[k]):<28}")

    print("\nturns whose ROUTE changed")
    print("-" * 80)
    ib = {c["id"]: c for c in b}
    for c in a:
        other = ib.get(c["id"])
        if not other:
            continue
        for t1, t2 in zip(c["turns"], other["turns"]):
            if t1["route"] != t2["route"] or bool(t1["ack"]) != bool(t2["ack"]):
                print(f"  [{c['id']}] {t1['user'][:44]!r}")
                print(f"        r2: route={t1['route']:<9} ack={t1['ack']!r}")
                print(f"        r3: route={t2['route']:<9} ack={t2['ack']!r}"
                      f" evidence={t2.get('evidence', 0)}"
                      f"{' GUARD=' + t2['guard'] if t2.get('guard') else ''}")

    print("\nturns where a guard fired in round 3")
    print("-" * 80)
    for c in b:
        for t in c["turns"]:
            if t.get("guard"):
                print(f"  [{c['id']}] {t['user'][:44]!r} -> {t['guard']}")
                print(f"        {t['ai'][:100]!r}")


if __name__ == "__main__":
    main()
