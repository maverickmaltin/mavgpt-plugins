#!/usr/bin/env python3
"""Pull still frames out of a video so Claude can look at it.

Usage:
    python3 frames.py exports/edit-preview.mp4 --every 2 --out work/check
    python3 frames.py exports/edit-preview.mp4 --at 1.5,4,9.2 --out work/check
    python3 frames.py raw/my-video.mp4 --sheet work/contact-sheet.jpg   # one grid image

Each frame is saved as a small JPG named with its timestamp (e.g. t0012.50.jpg).
"""
import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--every", type=float, default=None, help="One frame every N seconds")
    ap.add_argument("--at", default=None, help="Comma-separated timestamps in seconds")
    ap.add_argument("--out", default="work/frames")
    ap.add_argument("--width", type=int, default=480)
    ap.add_argument("--sheet", default=None, help="Write one contact-sheet image instead")
    a = ap.parse_args()

    ffmpeg, ffprobe, _ = vtools.need_ffmpeg()
    info = vtools.probe(a.video, ffprobe)
    dur = info["duration"]

    if a.sheet:
        n = 12 if dur > 12 else max(4, int(dur))
        cols = 4
        rows = math.ceil(n / cols)
        step = dur / n
        Path(a.sheet).parent.mkdir(parents=True, exist_ok=True)
        vtools.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", a.video, "-vf",
                    f"fps=1/{step:.3f},scale=320:-2,tile={cols}x{rows}:padding=6:color=white",
                    "-frames:v", "1", "-q:v", "3", a.sheet])
        print(f"Contact sheet: {a.sheet} ({n} frames, one every {step:.1f}s, left to right)")
        return

    if a.at:
        times = [float(x) for x in a.at.split(",") if x.strip()]
    else:
        every = a.every or max(1.0, dur / 12)
        times = [round(i * every, 2) for i in range(int(dur / every) + 1)]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    saved = []
    for t in times:
        t = min(max(0.0, t), max(0.0, dur - 0.05))
        f = out / f"t{t:07.2f}.jpg"
        vtools.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", a.video,
                    "-frames:v", "1", "-vf", f"scale={a.width}:-2", "-q:v", "4", str(f)])
        saved.append(str(f))
    print(f"Saved {len(saved)} frames to {out}/")
    for s in saved:
        print("  " + s)


if __name__ == "__main__":
    main()
