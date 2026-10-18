#!/usr/bin/env python3
"""Transcribe a video with word-level timestamps.

Usage:
    python3 transcribe.py raw/my-video.mp4 --out work/my-video-words.json
        [--model small] [--language en] [--vocab "Claude, Opus, Higgsfield"]

Writes:
    work/NAME-words.json      every word with start/end seconds (original video timeline)
    work/NAME-transcript.txt  readable transcript, one line per phrase with timestamps

Uses faster-whisper (pip install --user faster-whisper). Falls back to openai-whisper if
that's what is installed. Runs on the user's own computer.
"""
import argparse
import importlib.util
import os
import sys
import tempfile
import warnings
from pathlib import Path

# numpy prints harmless "divide by zero in matmul" warnings on some Macs. Hide them.
warnings.filterwarnings("ignore", category=RuntimeWarning)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402


def extract_audio(video, ffmpeg, dest):
    vtools.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(video),
                "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(dest)])


def with_faster_whisper(wav, model_name, language, vocab):
    from faster_whisper import WhisperModel
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(wav), language=language, word_timestamps=True,
                                      initial_prompt=vocab or None, vad_filter=True,
                                      vad_parameters={"min_silence_duration_ms": 300},
                                      beam_size=5)
    words, segs = [], []
    for s in segments:
        segs.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip()})
        for w in s.words or []:
            words.append({"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3),
                          "p": round(getattr(w, "probability", 1.0), 3)})
    return words, segs, info.language


def with_openai_whisper(wav, model_name, language, vocab):
    import whisper
    model = whisper.load_model(model_name.replace(".en", "") if language != "en" else model_name)
    r = model.transcribe(str(wav), language=language, word_timestamps=True, initial_prompt=vocab or None)
    words, segs = [], []
    for s in r.get("segments", []):
        segs.append({"start": round(s["start"], 3), "end": round(s["end"], 3), "text": s["text"].strip()})
        for w in s.get("words", []):
            words.append({"text": w["word"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3),
                          "p": round(w.get("probability", 1.0), 3)})
    return words, segs, r.get("language", language)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", default="work/words.json")
    ap.add_argument("--model", default=None, help="tiny, base, small (default), medium, large-v3")
    ap.add_argument("--language", default=None, help="e.g. en, es, fr. Default: detect")
    ap.add_argument("--vocab", default="", help="Names and words to spell right, comma separated")
    a = ap.parse_args()

    ffmpeg, ffprobe, _ = vtools.need_ffmpeg()
    info = vtools.probe(a.video, ffprobe)
    if not info["has_audio"]:
        sys.exit("This video has no audio track, so there is nothing to transcribe.")
    model = a.model or ("small.en" if a.language == "en" else "small")
    vocab = f"Vocabulary: {a.vocab}." if a.vocab else ""

    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "audio.wav"
        extract_audio(a.video, ffmpeg, wav)
        if importlib.util.find_spec("faster_whisper"):
            words, segs, lang = with_faster_whisper(wav, model, a.language, vocab)
        elif importlib.util.find_spec("whisper"):
            words, segs, lang = with_openai_whisper(wav, model, a.language, vocab)
        else:
            sys.exit("No transcription engine installed. Run: python3 -m pip install --user faster-whisper")

    out = Path(a.out)
    vtools.write_json(out, {"source": os.path.abspath(a.video), "duration": info["duration"],
                            "language": lang, "model": model, "words": words, "segments": segs})
    lines = [f"[{vtools.hms(s['start'])} - {vtools.hms(s['end'])}] {s['text']}" for s in segs]
    name = out.stem[:-6] if out.stem.endswith("-words") else out.stem
    txt = out.with_name(f"{name}-transcript.txt")
    txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Transcribed {vtools.hms(info['duration'])} of video: {len(words)} words, language {lang}.")
    print(f"Words: {out}\nTranscript: {txt}")
    if not words:
        print("No speech found. That's normal for action or scenery footage: skip captions and "
              "silence cuts, and pick moments by looking at frames (frames.py --every 1).")
    low = [w["text"] for w in words if w.get("p", 1) < 0.5]
    if low:
        print("Low-confidence words to double-check: " + ", ".join(sorted(set(low))[:30]))


if __name__ == "__main__":
    main()
