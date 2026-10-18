#!/usr/bin/env python3
"""Find the parts of a video to keep: removes silences (and optionally ums), never cuts a word.

Usage:
    python3 silences.py raw/my-video.mp4 --words work/words.json --out work/keep.json
        [--min-silence 0.2] [--noise auto] [--pad-before 0.05] [--pad-after 0.1]
        [--remove-fillers]

Writes work/keep.json: {"keep": [[start, end], ...]} in source seconds. Put that list in
plan.json under "keep". Edit it by hand (or ask Claude) to drop retakes.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402

FILLERS = {"um", "uh", "uhm", "umm", "erm", "er", "ah", "hmm", "mm", "eh"}


def detect_noise_floor(ffmpeg, video):
    p = vtools.run([ffmpeg, "-hide_banner", "-nostats", "-i", str(video), "-vn",
                    "-af", "volumedetect", "-f", "null", "-"])
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", p.stderr)
    mean = float(m.group(1)) if m else -25.0
    return max(-55.0, min(-28.0, mean - 18.0))


def detect_silences(ffmpeg, video, noise, min_silence):
    p = vtools.run([ffmpeg, "-hide_banner", "-nostats", "-i", str(video), "-vn",
                    "-af", f"silencedetect=noise={noise}dB:d={min_silence}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*(-?[\d.]+)", p.stderr)]
    out = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else None
        out.append((max(0.0, s), e))
    return out


def merge(segs, gap=0.0):
    segs = sorted([list(s) for s in segs if s[1] - s[0] > 0.001])
    out = []
    for s in segs:
        if out and s[0] <= out[-1][1] + gap:
            out[-1][1] = max(out[-1][1], s[1])
        else:
            out.append(s)
    return out


def subtract(keep, holes):
    out = []
    for a, b in keep:
        pieces = [[a, b]]
        for h0, h1 in holes:
            nxt = []
            for p0, p1 in pieces:
                if h1 <= p0 or h0 >= p1:
                    nxt.append([p0, p1])
                    continue
                if h0 > p0:
                    nxt.append([p0, h0])
                if h1 < p1:
                    nxt.append([h1, p1])
            pieces = nxt
        out += pieces
    return out


def norm(word):
    return re.sub(r"[^a-z]", "", word.lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--words", default=None)
    ap.add_argument("--out", default="work/keep.json")
    ap.add_argument("--min-silence", type=float, default=0.2, help="Cut pauses longer than this (seconds)")
    ap.add_argument("--noise", default="auto", help="Silence threshold in dB, or auto")
    ap.add_argument("--pad-before", type=float, default=0.05, help="Air kept before speech starts")
    ap.add_argument("--pad-after", type=float, default=0.10, help="Air kept after speech ends")
    ap.add_argument("--min-cut", type=float, default=0.12, help="Ignore cuts shorter than this")
    ap.add_argument("--remove-fillers", action="store_true", help="Also cut um/uh")
    ap.add_argument("--max-gap", type=float, default=2.0,
                    help="Stretches without talking longer than this that aren't quiet (action, scenery, "
                         "music) are KEPT and listed, so a person can decide")
    ap.add_argument("--cut-long-gaps", action="store_true", help="Cut those long stretches too")
    a = ap.parse_args()

    ffmpeg, ffprobe, _ = vtools.need_ffmpeg()
    info = vtools.probe(a.video, ffprobe)
    dur = info["duration"]
    if not info["has_audio"]:
        vtools.write_json(a.out, {"source": a.video, "duration": round(dur, 3), "keep": [[0.0, round(dur, 3)]],
                                  "kept_seconds": round(dur, 3), "removed_seconds": 0.0, "long_gaps_kept": []})
        print(f"This video has no sound, so there are no silences to cut. Kept all {vtools.hms(dur)}. "
              f"Pick moments by looking at frames instead (frames.py --every 1). Saved {a.out}")
        return
    noise = detect_noise_floor(ffmpeg, a.video) if a.noise == "auto" else float(a.noise)
    silences = detect_silences(ffmpeg, a.video, noise, a.min_silence)

    quiet = [[s, e if e is not None else dur] for s, e in silences]
    words = vtools.load_json(a.words)["words"] if a.words else []
    speech = [w for w in words if not (a.remove_fillers and norm(w["text"]) in FILLERS)]

    cuts, long_gaps = [], []
    if speech:
        # Pauses come from the transcript, so noisy footage (wind, music, a street) still gets
        # tightened. Where the audio is truly quiet inside a pause, use those exact edges.
        # Otherwise keep extra air, because transcript word edges can be a little early.
        bounds = [(0.0, None)] + [(w["end"], w["start"]) for w in speech] + [(None, dur)]
        gaps = []
        for (prev_end, _), (_, next_start) in zip(bounds[:-1], bounds[1:]):
            if prev_end is None:
                prev_end = 0.0
            if next_start is None:
                next_start = dur
            if next_start - prev_end > a.min_silence:
                gaps.append((prev_end, next_start))
        gaps = [(0.0, speech[0]["start"])] + gaps[1:] if gaps and gaps[0][0] == 0.0 else gaps
        for g0, g1 in gaps:
            lead = 0.0 if g0 <= 0.001 else None
            tail = 0.0 if g1 >= dur - 0.001 else None
            inside = [[max(g0, q0), min(g1, q1)] for q0, q1 in quiet if q1 > g0 and q0 < g1]
            if inside:
                for q0, q1 in inside:
                    c0 = q0 + (a.pad_after if q0 > g0 + 0.001 or lead is None else 0.0)
                    c1 = q1 - (a.pad_before if q1 < g1 - 0.001 or tail is None else 0.0)
                    c0 = max(c0, g0 + (0 if lead == 0.0 else a.pad_after))
                    c1 = min(c1, g1 - (0 if tail == 0.0 else a.pad_before))
                    if c1 - c0 > a.min_cut:
                        cuts.append([c0, c1])
            else:
                if g1 - g0 > a.max_gap and not a.cut_long_gaps:
                    long_gaps.append([round(g0, 2), round(g1, 2)])
                    continue
                c0 = g0 + (0.0 if lead == 0.0 else max(a.pad_after, 0.2))
                c1 = g1 - (0.0 if tail == 0.0 else max(a.pad_before, 0.1))
                if c1 - c0 > a.min_cut:
                    cuts.append([c0, c1])
    else:
        for q0, q1 in quiet:
            c0 = q0 + (a.pad_after if q0 > 0.001 else 0.0)
            c1 = q1 - (a.pad_before if q1 < dur - 0.001 else 0.0)
            if c1 - c0 > a.min_cut:
                cuts.append([c0, c1])

    keep = merge(subtract([[0.0, dur]], merge(cuts)), gap=a.min_cut)
    if words:
        # Never start or end a part inside a word.
        for seg in keep:
            for w in speech:
                if w["start"] < seg[0] < w["end"]:
                    seg[0] = max(0.0, w["start"] - 0.03)
                if w["start"] < seg[1] < w["end"]:
                    seg[1] = min(dur, w["end"] + 0.06)
        keep = merge(keep, gap=a.min_cut)
        if a.remove_fillers:
            holes = [[w["start"], w["end"]] for w in words if norm(w["text"]) in FILLERS]
            keep = merge(subtract(keep, holes), gap=a.min_cut)
        # Drop leftover slivers that hold no words (for example the air around a removed "um").
        keep = [k for k in keep if k[1] - k[0] > a.max_gap or
                any(w["start"] < k[1] and w["end"] > k[0] for w in speech)]
    keep = [[round(k0, 3), round(k1, 3)] for k0, k1 in keep if k1 - k0 >= 0.08]

    kept = sum(k1 - k0 for k0, k1 in keep)
    vtools.write_json(a.out, {
        "source": a.video, "duration": round(dur, 3), "keep": keep,
        "kept_seconds": round(kept, 3), "removed_seconds": round(max(0.0, dur - kept), 3),
        "long_gaps_kept": long_gaps,
        "settings": {"noise_db": round(noise, 1), "min_silence": a.min_silence, "pad_before": a.pad_before,
                     "pad_after": a.pad_after, "remove_fillers": a.remove_fillers},
    })
    print(f"Silence threshold {noise:.1f} dB. {len(keep)} parts kept, {max(0, len(keep) - 1)} cuts.")
    print(f"{vtools.hms(dur)} -> {vtools.hms(kept)} (removed {max(0.0, dur - kept):.1f}s). Saved {a.out}")
    if words and not speech:
        print("No speech found in the transcript, so only truly quiet parts were cut.")
    if long_gaps:
        spots = ", ".join(f"{vtools.hms(g0)}-{vtools.hms(g1)}" for g0, g1 in long_gaps)
        print(f"Kept {len(long_gaps)} long stretch(es) with no talking that aren't quiet: {spots}. "
              "Look at them (frames.py --at ...) and ask the user whether to keep them; "
              "re-run with --cut-long-gaps to cut them all.")


if __name__ == "__main__":
    main()
