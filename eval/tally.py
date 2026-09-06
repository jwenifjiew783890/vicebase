"""Total conversations and turns actually run against the model.

Counts transcripts on disk rather than trusting a number in a document.
"""
from __future__ import annotations
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    txt = sorted(glob.glob(os.path.join(ROOT, "eval/transcripts/**/*.txt"),
                           recursive=True))
    turns = 0
    for path in txt:
        turns += open(path, encoding="utf-8").read().count("\nUSER:")
    print(f"transcripts on disk : {len(txt)}")
    print(f"user turns in them  : {turns}")
    by_dir: dict[str, int] = {}
    for path in txt:
        d = os.path.basename(os.path.dirname(path))
        by_dir[d] = by_dir.get(d, 0) + 1
    for d, n in sorted(by_dir.items()):
        print(f"   {d:<12} {n}")

if __name__ == "__main__":
    main()
