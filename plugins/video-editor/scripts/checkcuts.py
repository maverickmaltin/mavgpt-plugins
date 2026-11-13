#!/usr/bin/env python3
"""Prove an edit has no dead space and no clipped words.

Usage:
    python3 checkcuts.py work/NAME-plan.json [--max-sentence 80] [--max-other 150] [--retranscribe]

It rebuilds the voice exactly as the plan cuts it (the original sound, the plan's keep list,
nothing else: no music, no sound effects, no loudness change), then checks every cut:
  - DEAD SPACE: silence left between sentences longer than --max-sentence ms (use your style's
    number), or longer than --max-other ms anywhere else.
  - CLIPPED: a cut that lands while a word is still sounding (its s, t or k chopped off), or a
    word that starts abruptly at a cut (its first sound chopped).
  - --retranscribe: transcribes the cut voice again and lists any word that went missing.
Times printed are EDITED-video times (what you see in the player). Saves work/NAME-cutcheck.json.
"""
import argparse
import difflib
import importlib.util
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402
import gaps as G  # noqa: E402


def norm(t):
    return re.sub(r"[^a-z0-9']", "", t.lower())


def cut_voice(x, keep, sr):
    np = G.np
    parts = []
    for a, b in keep:
        seg = x[int(round(a * sr)):int(round(b * sr))].copy()
        n = len(seg)
        fd = min(int(0.012 * sr), n // 4)
        if fd > 1:
            seg[:fd] *= np.linspace(0, 1, fd, dtype=np.float32)
            seg[-fd:] *= np.linspace(1, 0, fd, dtype=np.float32)
        parts.append(seg)
    return np.concatenate(parts) if parts else np.zeros(1, dtype=np.float32)


def write_wav(path, x, sr):
    np = G.np
    y = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(y.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--max-sentence", type=float, default=80, help="ms of silence allowed after a sentence")
    ap.add_argument("--max-other", type=float, default=150, help="ms of silence allowed between other words")
    ap.add_argument("--retranscribe", action="store_true", help="Also re-transcribe and compare (slower)")
    ap.add_argument("--vocab", default="", help="Names and words to spell right (same as for transcribe.py)")
    a = ap.parse_args()
    G.need_numpy()

    plan = vtools.load_json(a.plan)
    root = vtools.project_root(a.plan)
    P = lambda p: Path(p) if Path(p).is_absolute() else root / p  # noqa: E731
    wfile = (plan.get("captions") or {}).get("words") or plan.get("words")
    if not wfile:
        sys.exit("The plan has no transcript (captions.words). Point it at work/NAME-words.json.")
    words = [w for w in vtools.load_json(P(wfile))["words"] if w.get("text", "").strip()]
    ffmpeg, ffprobe, _ = vtools.need_ffmpeg()
    src = P(plan["input"])
    src_dur = vtools.probe(src, ffprobe)["duration"]
    keep = plan.get("keep") or [[0, src_dur]]
    keep = [[max(0.0, float(x)), min(src_dur, float(y))] for x, y in keep if float(y) - float(x) > 0.04]
    wout, segs = G.words_out(words, keep)
    cuts = [off for (_, _, off) in segs[1:]]

    print("Rebuilding the cut voice and measuring it...")
    x = G.load_audio(src, ffmpeg)
    y = cut_voice(x, keep, G.SR)
    # Measure against the ORIGINAL's room level: a tightly cut voice has almost no silence left,
    # so its own quietest moments aren't the room anymore.
    room = G.Track(G.levels(x)).floor
    tr = G.Track(G.levels(y), floor=room)
    res = G.boundary_gaps(tr, wout)
    summ = G.summarize(res)
    problems = []
    for r in res:
        limit = a.max_sentence if r["punct"] in (".", "?", "!") else a.max_other
        if r["ms"] > limit:
            problems.append({"t": r["t"], "kind": "DEAD SPACE",
                             "what": f"{r['ms']} ms of silence between \"{r['before']}\" and \"{r['after']}\" (limit {limit:.0f})"})
    for c in cuts:
        k = tr.k(c)
        before = [w for w in wout if w["start"] < c - 0.02 and w["end"] > c - 0.8]
        after = [w for w in wout if w["end"] > c + 0.02 and w["start"] < c + 0.8]
        if before:
            w1 = before[-1]
            p1 = tr.peak(w1["start"], max(w1["start"] + 0.03, min(w1["end"], c)))
            lv = float(tr.lvl[max(0, k - 8):max(1, k - 3)].max())
            if lv > max(p1 - 20.0, tr.floor + 12):
                problems.append({"t": round(c, 3), "kind": "CLIPPED",
                                 "what": f"the cut lands while \"{w1['text']}\" is still sounding (ending chopped?)"})
        if after:
            w2 = after[0]
            p2 = tr.peak(max(c, w2["start"]), max(w2["start"] + 0.03, w2["end"]))
            lv = float(tr.lvl[min(tr.n - 1, k + 3):min(tr.n, k + 7)].max())
            if lv > max(p2 - 10.0, tr.floor + 12):
                problems.append({"t": round(c, 3), "kind": "CLIPPED",
                                 "what": f"\"{w2['text']}\" starts at full strength right at the cut (first sound chopped?)"})

    missing = []
    if a.retranscribe:
        if not (importlib.util.find_spec("faster_whisper") or importlib.util.find_spec("whisper")):
            print("Skipping --retranscribe: no transcription engine installed.")
        else:
            with tempfile.TemporaryDirectory() as tmp:
                wav = Path(tmp) / "cut-voice.wav"
                write_wav(wav, y, G.SR)
                out = Path(tmp) / "re-words.json"
                lang = vtools.load_json(P(wfile)).get("language") or "en"
                cmd = [sys.executable, str(Path(__file__).with_name("transcribe.py")), str(wav),
                       "--out", str(out), "--language", lang]
                if a.vocab:
                    cmd += ["--vocab", a.vocab]
                p = subprocess.run(cmd, capture_output=True, text=True)
                if p.returncode == 0 and out.exists():
                    new = [norm(w["text"]) for w in vtools.load_json(out)["words"]]
                    new = [t for t in new if t]
                    old = [norm(w["text"]) for w in wout]
                    sm = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
                    for tag, i1, i2, j1, j2 in sm.get_opcodes():
                        if tag not in ("delete", "replace") or not 0 < i2 - i1 <= 6:
                            continue
                        gone = [wout[i] for i in range(i1, i2)]
                        # A cut can only remove words right at it; elsewhere it's whisper hearing it differently.
                        if not any(abs(w["start"] - c) < 0.6 or abs(w["end"] - c) < 0.6 for w in gone for c in cuts):
                            continue
                        exp = re.sub(r"slash", "", "".join(old[i1:i2]))
                        got = re.sub(r"slash", "", "".join(new[j1:j2]))
                        if got and difflib.SequenceMatcher(a=exp, b=got).ratio() >= 0.7:
                            continue  # the same words, spelled a little differently
                        missing.append({"t": round(gone[0]["start"], 2),
                                        "expected": " ".join(w["text"] for w in gone),
                                        "heard": " ".join(new[j1:j2]) or "(nothing)"})
                else:
                    print("Re-transcription failed, so that check was skipped.")

    problems.sort(key=lambda r: r["t"])
    stem = Path(a.plan).stem
    stem = stem[:-5] if stem.endswith("-plan") else stem
    vtools.write_json(Path(a.plan).with_name(f"{stem}-cutcheck.json"),
                      {"plan": str(a.plan), "cuts": len(cuts), "gaps": summ, "problems": problems,
                       "missing_words": missing, "limits_ms": {"sentence": a.max_sentence, "other": a.max_other}})
    print(f"{len(cuts)} cuts checked. Pacing: {G.describe(summ)}.")
    if not problems and not missing:
        print("PASS: no dead space over the limits and no clipped words.")
        return
    print(f"CHECK: {len(problems)} spot(s)" + (f", {len(missing)} possibly missing word(s)" if missing else "") + ":")
    for pr in problems[:60]:
        print(f"  {vtools.hms(pr['t'])}  {pr['kind']}: {pr['what']}")
    for m in missing[:30]:
        print(f"  {vtools.hms(m['t'])}  MISSING?: expected \"{m['expected']}\", heard \"{m['heard']}\"")
    print("Fixes: dead space -> run tighten.py with a lower --air or --max-pause, or trim that part of keep. "
          "Clipped -> move that cut point 0.03-0.05 s outward (or a higher --air). Then check again. "
          "Whisper sometimes mishears: a 'missing' word is only real if it's gone when you listen.")
    sys.exit(1)


if __name__ == "__main__":
    main()
