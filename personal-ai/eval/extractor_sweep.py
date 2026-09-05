"""Run the fact extractor over every real user turn on disk.

The extractor is the one component that writes to long-term memory without
a human in the loop, so the question that matters is not "does it extract"
but "does it ever extract something the user did not say". That is a
negative claim, and the only way to support it is to run the thing over
every turn actually spoken to the model and read what comes out.

Prints one line per extraction so the output can be eyeballed; the count at
the end is what the report cites.
"""
from __future__ import annotations
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pai.extract import extract_facts, extract_retractions  # noqa: E402


def user_turns() -> list[tuple[str, str]]:
    """(transcript, turn text) for every USER: block in every transcript."""
    out: list[tuple[str, str]] = []
    for path in sorted(glob.glob(os.path.join(ROOT, "eval/transcripts/**/*.txt"),
                                 recursive=True)):
        name = os.path.relpath(path, ROOT)
        blocks = re.split(r"^USER:\s*$", open(path, encoding="utf-8").read(),
                          flags=re.MULTILINE)[1:]
        for block in blocks:
            # a USER: block runs until the next unindented label
            body: list[str] = []
            for line in block.splitlines():
                if line and not line.startswith(("  ", "\t")):
                    break
                body.append(line.strip())
            text = " ".join(b for b in body if b).strip()
            if text:
                out.append((name, text))
    return out


def main() -> int:
    turns = user_turns()
    facts = 0
    retractions = 0
    for name, text in turns:
        for c in extract_facts(text):
            facts += 1
            print(f"FACT  {c.predicate:<12} {c.object:<24} <- {text[:60]!r}")
        for pred in extract_retractions(text):
            retractions += 1
            print(f"RETRACT {pred:<10} <- {text[:60]!r}")
    print("=" * 70)
    print(f"user turns swept    : {len(turns)}")
    print(f"facts extracted     : {facts}")
    print(f"retractions found   : {retractions}")
    print()
    print("Every line above must be a fact the user actually stated in that")
    print("turn. Anything else is an invented memory and a defect.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
