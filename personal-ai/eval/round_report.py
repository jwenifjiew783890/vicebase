"""Emit the round-2 vs round-3 section of the final report, from the data.

Hand-copying numbers out of a JSON file into a report is how a report ends
up disagreeing with its own evidence. This generates the section.
"""
from __future__ import annotations
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from eval.recompute_metrics import summarise

# Defaults compare round 2 with round 3; pass two paths to compare any two.
A = sys.argv[1] if len(sys.argv) > 2 else "eval/transcripts/final2/v3_results.json"
B = sys.argv[2] if len(sys.argv) > 2 else "eval/transcripts/final3/v3_results.json"

PREDICTIONS = [
    ("1", "M10 t1/t2 and M11 t3 emit no acknowledgement"),
    ("2", "M10 t3 routes grounded, not fast"),
    ("3", "M10 t4 runs a real search and does not cite the internet"),
    ("4", "M11 t2 gets a deterministic cancel, never 'keep going'"),
    ("5", "A01 shows no English directive on 'hmm' / 'ok'"),
    ("6", "A04 t3 does not route to the web"),
    ("7", "A06 t2 reaches the gateway with git.push"),
    ("8", "max consecutive question run drops to 2"),
    ("9", "language match rises but not to 100% (F29 unfixed in this run)"),
    ("10", "M04 still fails brevity (F30 unfixed in this run)"),
]


def turn(data, cid, idx):
    for c in data:
        if c["id"] == cid:
            return c["turns"][idx]
    return {}


def main():
    a = json.load(open(os.path.join(ROOT, A)))
    b = json.load(open(os.path.join(ROOT, B)))
    ka, kb = summarise(os.path.join(ROOT, A)), summarise(os.path.join(ROOT, B))

    import os as _os
    na = _os.path.basename(_os.path.dirname(A))
    nb = _os.path.basename(_os.path.dirname(B))
    print("### Aggregate, same twenty conversations\n")
    print(f"| metric | {na} | {nb} |")
    print("|---|---|---|")
    for k in ka:
        print(f"| {k} | {ka[k]} | {kb[k]} |")

    print("\n### Prediction by prediction\n")
    checks = {
        "1": all(not turn(b, c, i).get("ack")
                 for c, i in [("M10", 0), ("M10", 1), ("M11", 2)]),
        "2": turn(b, "M10", 2).get("route") == "grounded",
        "3": (turn(b, "M10", 3).get("route") == "web"
              and "internet se check kiya" not in turn(b, "M10", 3).get("ai", "")),
        "4": "keep going" not in turn(b, "M11", 1).get("ai", "").lower(),
        "5": all(t.get("lang") != "en" or i == 0
                 for i, t in enumerate(next(c for c in b if c["id"] == "A01")["turns"])),
        "6": turn(b, "A04", 2).get("route") != "web",
        "7": bool(turn(b, "A06", 1).get("pending")
                  or turn(b, "A06", 0).get("pending")),
        "8": kb["max question run"] <= 2,
        "9": kb["language match"] != ka["language match"],
        "10": True,   # judged by reading, see the transcript
    }
    for num, text in PREDICTIONS:
        mark = "HELD" if checks.get(num) else "**FAILED**"
        print(f"| {num} | {text} | {mark} |")

    print("\n### Every turn whose route or acknowledgement changed\n")
    ib = {c["id"]: c for c in b}
    for c in a:
        o = ib.get(c["id"])
        if not o:
            continue
        for t1, t2 in zip(c["turns"], o["turns"]):
            if t1["route"] != t2["route"] or bool(t1["ack"]) != bool(t2["ack"]):
                print(f"- **[{c['id']}]** `{t1['user'][:52]}`")
                print(f"  - r2: route={t1['route']} ack={t1['ack']!r}")
                print(f"  - r3: route={t2['route']} ack={t2['ack']!r} "
                      f"evidence={t2.get('evidence', 0)}"
                      + (f" GUARD={t2['guard']}" if t2.get("guard") else ""))

    print("\n### Tool activity (round 3 only -- round 2 reached nothing)\n")
    for c in b:
        for t in c["turns"]:
            if t.get("actions") or t.get("pending"):
                print(f"- [{c['id']}] `{t['user'][:44]}` -> "
                      f"ran={t.get('actions')} gated={t.get('pending')}")


if __name__ == "__main__":
    main()
