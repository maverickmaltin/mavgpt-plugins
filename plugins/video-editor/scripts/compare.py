#!/usr/bin/env python3
"""Put your edit next to the videos it should look like: same moments, side by side, plus the
numbers that matter (cut rhythm, shot length, loudness).

Usage:
    python3 compare.py exports/NAME-preview.mp4 style-lab/STYLE/videos/03-x.mp4 [more...]
        --out work/NAME-compare.jpg [--at 0.5,1.5,2.5,3.5,5,8,12,16] [--analysis-root style-lab/STYLE/analysis]

The first video is yours; the rest are the references. Each row is one moment (the first
seconds of the hook, then the same points through each video), each column one video.
Look at it row by row: is the caption the same size and place, is the framing as tight,
is there as much on screen, does the hook look as strong?
"""
import argparse
import json
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402
import analyze as A  # noqa: E402

TW, TH = 216, 384


def quick_stats(ffmpeg, ffprobe, video, analysis_root, plan=None):
    if analysis_root:
        for d in Path(analysis_root).glob("*/analysis.json"):
            try:
                j = json.loads(d.read_text(encoding="utf-8"))
            except Exception:
                continue
            if j.get("file") == Path(video).name:
                dur = float(j.get("analyzed_seconds") or j.get("duration") or 0) or 1.0
                changes = (j.get("cuts") or 0) + len(j.get("soft_changes") or [])
                return {"length": j.get("duration"), "shots": j.get("shots"), "cut_every": j.get("cut_every_s"),
                        "changes_10s": round(changes / dur * 10, 1),
                        "first_cut": j.get("first_cut_s"), "cuts_3s": j.get("cuts_first_3s"),
                        "median_shot": (j.get("shot_length") or {}).get("median"),
                        "lufs": (j.get("loudness") or {}).get("lufs"),
                        "gaps": ((j.get("sound") or {}).get("pauses") or {}).get("sentence", {}).get("median")}
    info = vtools.probe(video, ffprobe)
    times, scores = A.scene_scores(ffmpeg, video, 0)
    cuts, soft = A.find_cuts(times, scores, info["fps"])
    ct = [c[0] for c in cuts]
    bounds = [0.0] + ct + [info["duration"]]
    lengths = [b - a for a, b in zip(bounds[:-1], bounds[1:]) if b - a > 0.01]
    loud = A.ebur128(ffmpeg, video, 0) if info["has_audio"] else {}
    gaps = None
    if plan and Path(plan).exists():
        cc = Path(plan).with_name(Path(plan).stem.replace("-plan", "") + "-cutcheck.json")
        if cc.exists():
            try:
                gaps = json.loads(cc.read_text(encoding="utf-8"))["gaps"]["sentence"]["median"]
            except Exception:
                gaps = None
    return {"length": round(info["duration"], 2), "shots": len(lengths),
            "changes_10s": round((len(ct) + len(soft)) / max(info["duration"], 0.1) * 10, 1),
            "cut_every": round(info["duration"] / max(1, len(lengths)), 2), "first_cut": round(ct[0], 2) if ct else None,
            "cuts_3s": sum(1 for c in ct if c < 3.0), "median_shot": round(statistics.median(lengths), 2) if lengths else None,
            "lufs": loud.get("lufs"), "gaps": gaps}


def grab(ffmpeg, video, t, dest, label):
    vf = (f"scale={TW}:{TH}:force_original_aspect_ratio=decrease,pad={TW}:{TH}:(ow-iw)/2:(oh-ih)/2:color=0x111111,"
          + A.label_filter(label.replace(":", "\\:"), 16))
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video),
           "-frames:v", "1", "-an", "-vf", vf, "-q:v", "4", str(dest)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0 or not dest.exists():
        vf = f"scale={TW}:{TH}:force_original_aspect_ratio=decrease,pad={TW}:{TH}:(ow-iw)/2:(oh-ih)/2:color=0x111111"
        cmd[cmd.index("-vf") + 1] = vf
        subprocess.run(cmd, capture_output=True, text=True)
    if not dest.exists():
        subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                        f"color=c=0x111111:s={TW}x{TH}", "-frames:v", "1", str(dest)], capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--at", default=None, help="Comma-separated seconds. Default: hook seconds, then 20%..95% through")
    ap.add_argument("--analysis-root", default=None, help="Reuse analyze.py results for the references")
    ap.add_argument("--plan", default=None, help="Your edit's plan.json, to show its measured sentence gaps (run checkcuts.py first)")
    a = ap.parse_args()
    if len(a.videos) < 2:
        sys.exit("Give your edit first, then at least one reference video.")
    ffmpeg, ffprobe, _ = vtools.need_ffmpeg()
    infos = [vtools.probe(v, ffprobe) for v in a.videos]

    tmp = Path(tempfile.mkdtemp(prefix="compare-"))
    try:
        if a.at:
            rows = [("abs", float(x)) for x in a.at.split(",") if x.strip()]
        else:
            rows = [("abs", x) for x in (0.3, 1.2, 2.2, 3.4, 4.6)] + [("pct", p) for p in (0.2, 0.35, 0.5, 0.65, 0.8, 0.95)]
        strips = []
        for vi, (v, info) in enumerate(zip(a.videos, infos)):
            frames = []
            for ri, (kind, x) in enumerate(rows):
                t = x if kind == "abs" else info["duration"] * x
                t = min(max(0.0, t), max(0.0, info["duration"] - 0.05))
                dest = tmp / f"v{vi}-r{ri:02d}.jpg"
                name = "YOURS" if vi == 0 else f"REF {vi}"
                grab(ffmpeg, v, t, dest, f"{name} {vtools.hms(t)}")
                frames.append(dest)
            strip = tmp / f"strip{vi}.jpg"
            subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-framerate", "1", "-i",
                            str(tmp / f"v{vi}-r%02d.jpg"), "-vf", f"tile=1x{len(rows)}:padding=4:color=0x000000",
                            "-frames:v", "1", "-q:v", "4", str(strip)], capture_output=True)
            strips.append(strip)
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error"]
        for s in strips:
            cmd += ["-i", str(s)]
        cmd += ["-filter_complex", "".join(f"[{i}:v]" for i in range(len(strips))) + f"hstack=inputs={len(strips)}",
                "-frames:v", "1", "-q:v", "3", str(out)]
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode != 0:
            sys.exit("Couldn't build the comparison image: " + p.stderr.strip().splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"Saved {out} (columns: yours, then the references; rows: the same moments).")
    print("\n| | " + " | ".join(["Yours"] + [f"Ref {i}" for i in range(1, len(a.videos))]) + " |")
    print("|---|" + "---|" * len(a.videos))
    stats = [quick_stats(ffmpeg, ffprobe, v, a.analysis_root if i else None, a.plan if i == 0 else None)
             for i, v in enumerate(a.videos)]
    for key, label in (("length", "Length (s)"), ("shots", "Shots"), ("cut_every", "A cut every (s)"),
                       ("changes_10s", "Visual changes per 10 s (cuts + pop-ins, zooms, cards)"),
                       ("median_shot", "Median shot (s)"), ("first_cut", "First cut (s)"), ("cuts_3s", "Cuts in first 3 s"),
                       ("lufs", "Loudness (LUFS)"), ("gaps", "Sentence gaps (ms)")):
        print(f"| {label} | " + " | ".join("-" if s.get(key) is None else str(s.get(key)) for s in stats) + " |")


if __name__ == "__main__":
    main()
