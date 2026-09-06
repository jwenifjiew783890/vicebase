"""Hindi ASR harness. NOT RUN in this environment -- no committed result.

Read that label carefully: this file measures nothing until someone runs
it. It requires network access to the HuggingFace datasets server and a
Whisper model, and neither was available here, so `eval/transcripts/
asr_hi.json` does not exist and no WER figure in any report comes from
this script. Every ASR number in the reports is RESEARCHED (published
figures for other people's speech), which is why §11 and §15 of the final
report list code-switched ASR as the single biggest untested risk.

Running this is item 3 on the "what I would build next" list (§17).

Source when run: google/fleurs hi_in (read speech, clean audio). That is
the OPTIMISTIC case -- clean, read, monolingual Hindi. Conversational
Hinglish on a laptop mic will be materially worse, which is the point: if
clean read Hindi is already marginal, the code-switched case needs work.
"""
import io, json, os, re, sys, time, urllib.request

OUT = sys.argv[1] if len(sys.argv) > 1 else "eval/transcripts/asr_hi.json"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 12
MODEL = sys.argv[3] if len(sys.argv) > 3 else "openai/whisper-small"

def fetch_rows(n):
    url = ("https://datasets-server.huggingface.co/first-rows?"
           "dataset=google%2Ffleurs&config=hi_in&split=validation")
    with urllib.request.urlopen(url, timeout=90) as r:
        d = json.load(r)
    out = []
    for row in d.get("rows", [])[:n]:
        rr = row["row"]
        a = rr.get("audio")
        src = a[0]["src"] if isinstance(a, list) and a else (a or {}).get("src")
        txt = rr.get("transcription") or rr.get("raw_transcription")
        if src and txt:
            out.append((src, txt))
    return out

def normalise(s):
    s = re.sub(r"[।.,!?;:\"'()\[\]—–-]", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()

def wer(ref, hyp):
    r, h = normalise(ref).split(), normalise(hyp).split()
    if not r: return 1.0
    d = [[0]*(len(h)+1) for _ in range(len(r)+1)]
    for i in range(len(r)+1): d[i][0] = i
    for j in range(len(h)+1): d[0][j] = j
    for i in range(1, len(r)+1):
        for j in range(1, len(h)+1):
            d[i][j] = min(d[i-1][j]+1, d[i][j-1]+1,
                          d[i-1][j-1] + (r[i-1] != h[j-1]))
    return d[len(r)][len(h)] / len(r)

def main():
    import soundfile as sf, numpy as np, torch
    from transformers import pipeline
    rows = fetch_rows(N)
    print(f"fetched {len(rows)} FLEURS hi_in samples", flush=True)
    print(f"loading {MODEL} ...", flush=True)
    t0 = time.time()
    asr = pipeline("automatic-speech-recognition", model=MODEL, device=-1)
    print(f"loaded in {time.time()-t0:.0f}s", flush=True)

    results, wers = [], []
    for i, (src, ref) in enumerate(rows):
        try:
            with urllib.request.urlopen(src, timeout=90) as r:
                audio_bytes = r.read()
            data, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32")
            if data.ndim > 1: data = data.mean(axis=1)
            if sr != 16000:
                idx = np.round(np.arange(0, len(data), sr/16000)).astype(int)
                data = data[idx[idx < len(data)]]
            t = time.time()
            hyp = asr({"array": data, "sampling_rate": 16000},
                      generate_kwargs={"language": "hindi", "task": "transcribe"})["text"]
            rtf = (time.time()-t) / (len(data)/16000)
            w = wer(ref, hyp)
            wers.append(w)
            results.append({"ref": ref, "hyp": hyp, "wer": w, "rtf": rtf,
                            "dur_s": len(data)/16000})
            print(f"[{i+1}/{len(rows)}] WER={w:.1%} rtf={rtf:.2f}\n"
                  f"   REF: {ref[:90]}\n   HYP: {hyp.strip()[:90]}", flush=True)
            # Write after EVERY sample. An earlier version only wrote at
            # the end, so hitting the timeout lost the entire run.
            os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
            _srt = sorted(wers)
            json.dump({"summary": {"model": MODEL, "n": len(wers),
                                   "mean_wer": sum(wers) / len(wers),
                                   "median_wer": _srt[len(wers) // 2],
                                   "mean_rtf": sum(x["rtf"] for x in results) / len(results),
                                   "partial": True},
                       "results": results},
                      open(OUT, "w"), indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[{i+1}] failed: {type(e).__name__}: {e}", flush=True)

    if wers:
        wers_sorted = sorted(wers)
        summary = {"model": MODEL, "n": len(wers),
                   "mean_wer": sum(wers)/len(wers),
                   "median_wer": wers_sorted[len(wers)//2],
                   "mean_rtf": sum(r["rtf"] for r in results)/len(results)}
        print("\n=== SUMMARY ===")
        for k, v in summary.items():
            print(f"  {k}: {v:.3f}" if isinstance(v, float) else f"  {k}: {v}")
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump({"summary": summary, "results": results}, open(OUT, "w"),
                  indent=2, ensure_ascii=False)
        print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
