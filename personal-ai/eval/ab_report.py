"""Turn ab.json into the comparison the report needs.

Reports per-case deltas on the metrics each case was designed to expose,
plus a check for the specific defects: invented personal detail, fabricated
citations, and whether the brevity correction was obeyed.
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PATH = sys.argv[1] if len(sys.argv) > 1 else "eval/transcripts/ab/ab.json"

# Textual markers for the round-1 defects.
FAKE_CITATION = re.compile(r"\(\s*source\s*:", re.IGNORECASE)
THIRD_PERSON = re.compile(r"\bMuaz\b")
INVENTED = re.compile(r"\b(that|the) (new |recent )?(thriller|movie|book|show|"
                      r"article|podcast) (you|he|Muaz) mentioned\b", re.IGNORECASE)

FOCUS = {
 "001": ("invention + brevity", ["mean_words", "ai_tells", "question_rate"]),
 "002": ("question tic + language", ["question_rate", "lang_match_rate", "mean_words"]),
 "003": ("verbosity growth + citation", ["max_words", "mean_words"]),
 "004": ("brevity obeyed after correction", ["mean_words", "max_words"]),
 "008": ("honest unknown", ["honest_unknown", "mean_words"]),
 "009": ("disagreement vs agreement", ["disagree_turns", "agreement_rate"]),
}
HIGHER_BETTER = {"lang_match_rate", "honest_unknown", "disagree_turns"}


def main():
    d = json.load(open(PATH))
    v1, v2 = d["v1"], d["v2"]
    print(f"{'case':5} {'focus':30} {'metric':16} {'v1':>7} {'v2':>7}  verdict")
    print("-" * 76)
    wins = losses = same = 0
    for cid in sorted(set(v1) & set(v2)):
        focus, keys = FOCUS.get(cid, ("", ["mean_words"]))
        for i, k in enumerate(keys):
            a = v1[cid]["metrics"].get(k, 0) or 0
            b = v2[cid]["metrics"].get(k, 0) or 0
            better = (b > a) if k in HIGHER_BETTER else (b < a)
            if abs(b - a) < 1e-9:
                verd = "same"; same += 1
            elif better:
                verd = "BETTER"; wins += 1
            else:
                verd = "worse"; losses += 1
            print(f"{cid if i==0 else '':5} {focus if i==0 else '':30} "
                  f"{k:16} {a:7.2f} {b:7.2f}  {verd}")
    print("-" * 76)
    print(f"metric comparisons: {wins} better, {losses} worse, {same} unchanged")

    print("\nDEFECT MARKERS (count of replies containing each)")
    print(f"{'defect':32} {'v1':>5} {'v2':>5}")
    for label, rx in [("fabricated '(Source: ...)'", FAKE_CITATION),
                      ("third-person 'Muaz'", THIRD_PERSON),
                      ("invented personal detail", INVENTED)]:
        c1 = sum(1 for c in v1.values() for r in c["replies"] if rx.search(r))
        c2 = sum(1 for c in v2.values() for r in c["replies"] if rx.search(r))
        print(f"{label:32} {c1:5} {c2:5}")

    print("\nBREVITY AFTER CORRECTION (case 004: turns 3-4 follow the correction)")
    for side, data in (("v1", v1), ("v2", v2)):
        if "004" not in data:
            continue
        reps = data["004"]["replies"]
        pre = len(re.findall(r"\w+", reps[0])) if reps else 0
        post = [len(re.findall(r"\w+", r)) for r in reps[2:]]
        avg = sum(post) / len(post) if post else 0
        print(f"  {side}: before correction {pre}w -> after {avg:.0f}w "
              f"({'OBEYED' if avg < pre * 0.6 else 'IGNORED'})")

    print("\nSAMPLE REPLIES")
    for cid in ("001", "004", "009"):
        if cid not in v2:
            continue
        print(f"\n  --- {cid} ---")
        for side, data in (("v1", v1), ("v2", v2)):
            r = data[cid]["replies"]
            print(f"  {side} last: {r[-1][:160]!r}" if r else f"  {side}: -")


if __name__ == "__main__":
    main()
