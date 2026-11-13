#!/usr/bin/env python3
"""Re-set every cut on the audio so no word is clipped and no dead space is left.

Usage:
    python3 tighten.py raw/VIDEO --words work/NAME-words.json --keep work/NAME-keep.json
        [--air 20] [--max-pause 0.25] [--end-air 0.25] [--out work/NAME-keep.json]

Run it after silences.py (and again after you remove retakes or ums from the keep list).
For every cut it:
  - finds the real pause between the last word before the cut and the next word, on the audio
    (the longest quiet stretch between them, so a word's own s, t or k stays with the word),
  - leaves --air milliseconds of silence across the cut (about 20 = very tight, 60 = tight,
    120 = natural, 200 = relaxed; the person's style says which),
  - splits pauses inside a kept part that are longer than --max-pause seconds (0 = don't),
  - leaves a cut alone when the sound never drops there (a retake join, a cut inside a phrase),
    and undoes it if it removed 0.15 s or less, because it would chop a word.
Parts with no words (action, scenery, a demo) are left exactly as they were.

Writes the same format as silences.py ({"keep": [[start, end], ...]}, source-video seconds).
Then render and prove it with checkcuts.py.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402
import gaps as G  # noqa: E402


def mid(w):
    return (w["start"] + w["end"]) / 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--words", required=True)
    ap.add_argument("--keep", required=True, help="keep.json from silences.py (or a plan.json with a keep list)")
    ap.add_argument("--out", default=None, help="Default: overwrite --keep")
    ap.add_argument("--air", type=float, default=20, help="Silence left across each cut, in ms")
    ap.add_argument("--max-pause", type=float, default=0.25,
                    help="Also cut pauses inside a kept part longer than this (seconds). 0 = off")
    ap.add_argument("--end-air", type=float, default=0.25, help="Seconds kept after the very last word")
    ap.add_argument("--start-air", type=float, default=0.02, help="Seconds kept before the very first word")
    a = ap.parse_args()

    ffmpeg, ffprobe, _ = vtools.need_ffmpeg()
    info = vtools.probe(a.video, ffprobe)
    dur = info["duration"]
    if not info["has_audio"]:
        sys.exit("This video has no sound, so there's nothing to tighten.")
    kdata = vtools.load_json(a.keep)
    keep = sorted([float(x), float(y)] for x, y in kdata.get("keep", []))
    if not keep:
        sys.exit(f"{a.keep} has no keep list.")
    words = [dict(w) for w in vtools.load_json(a.words)["words"] if w.get("text", "").strip()]
    if not words:
        sys.exit("The transcript has no words, so there's nothing to tighten (a video without talking).")
    words.sort(key=lambda w: w["start"])
    for w in words:
        if w["end"] <= w["start"]:
            w["end"] = w["start"] + 0.04
    pos = {id(w): i for i, w in enumerate(words)}

    print("Measuring the audio...")
    tr = G.Track(G.audio_levels(a.video, ffmpeg))
    air = max(0.0, a.air) / 1000.0
    tail, lead = air * 0.6, air * 0.4

    def words_in(seg):
        return [w for w in words if seg[0] <= mid(w) <= seg[1]]

    # 1. Split long pauses inside kept parts.
    pieces, splits = [], 0
    for seg in keep:
        ws = words_in(seg)
        cur0 = seg[0]
        if a.max_pause > 0:
            for w1, w2 in zip(ws[:-1], ws[1:]):
                if pos[id(w2)] != pos[id(w1)] + 1:
                    continue
                e, o, ok, quiet = tr.between(w1, w2)
                if ok and quiet > a.max_pause:
                    cut = (e + o) / 2
                    # Only split where whisper agrees the words are on either side (it can be wrong
                    # about where a word starts, but not about the order of words).
                    if not (mid(w1) < cut < mid(w2)) or cut - cur0 < 0.08:
                        continue
                    pieces.append([cur0, cut])
                    cur0 = cut
                    splits += 1
        pieces.append([cur0, seg[1]])

    # 2. Re-set each part's edges on the audio.
    new, rescued, no_pause = [], 0, 0
    for seg in pieces:
        ws = words_in(seg)
        if not ws:
            new.append(list(seg))  # no talking here: leave it exactly as it is
            continue
        first, last = ws[0], ws[-1]
        prv = words[pos[id(first)] - 1] if pos[id(first)] > 0 else None
        nxt = words[pos[id(last)] + 1] if pos[id(last)] + 1 < len(words) else None
        if prv is None:
            start = max(0.0, tr.word_start(first, 0.0) - a.start_air)
        else:
            e, o, ok, _ = tr.between(prv, first)
            if ok:
                start = max(e, o - lead)
            else:
                start = seg[0]
                no_pause += 1
        if nxt is None:
            end = min(dur, tr.word_end(last, dur) + a.end_air)
        else:
            e, o, ok, _ = tr.between(last, nxt)
            if ok:
                end = min(o, e + tail)
                if e > seg[1] + 0.005:
                    rescued += 1
            else:
                end = seg[1]
        if end - start >= 0.04:
            new.append([start, end])

    # 3. Merge overlaps, and undo tiny cuts that have no real pause in them.
    new.sort()
    merged, undone = [], 0
    for s in new:
        if merged:
            gap = s[0] - merged[-1][1]
            if gap <= 0.0:
                merged[-1][1] = max(merged[-1][1], s[1])
                continue
            removed = [w for w in words if merged[-1][1] < mid(w) < s[0]]
            if gap <= 0.15 and not removed:
                before = words_in(merged[-1])
                after = words_in(s)
                if before and after and pos[id(after[0])] == pos[id(before[-1])] + 1:
                    if not tr.between(before[-1], after[0])[2]:
                        merged[-1][1] = s[1]
                        undone += 1
                        continue
        merged.append(list(s))
    merged = [[round(x, 3), round(y, 3)] for x, y in merged if y - x >= 0.04]

    kept = sum(y - x for x, y in merged)
    data = dict(kdata)
    data.update({"keep": merged, "kept_seconds": round(kept, 3), "removed_seconds": round(max(0.0, dur - kept), 3),
                 "tightened": {"air_ms": a.air, "max_pause": a.max_pause, "cuts": max(0, len(merged) - 1)}})
    out_path = a.out or a.keep
    vtools.write_json(out_path, data)
    print(f"{len(merged)} parts, {max(0, len(merged) - 1)} cuts. {vtools.hms(dur)} -> {vtools.hms(kept)}.")
    print(f"  split {splits} pause(s) longer than {a.max_pause:.2f} s, kept {rescued} word ending(s) the old cut "
          f"had clipped, undid {undone} tiny cut(s) with no real pause, {a.air:.0f} ms of air at every cut.")
    if no_pause:
        print(f"  {no_pause} cut(s) sit where the sound never drops (a retake join, or a cut inside a phrase). "
              "They were left as they were: listen to them in the preview.")
    print(f"Saved {out_path}. Put the keep list in the plan, render, then run checkcuts.py on the export.")


if __name__ == "__main__":
    main()
