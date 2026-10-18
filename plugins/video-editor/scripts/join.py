#!/usr/bin/env python3
"""Join several clips into one video so they can be edited as one.

Usage:
    python3 join.py raw/01.mp4 raw/02.mov raw/03.mp4 --out work/joined.mp4 [--width 1080 --height 1920]

Clips are joined in the order given. They can have different sizes, frame rates and audio
formats (phone clips with extra spatial-audio tracks are fine). Each clip is fitted to the
canvas (cropped to fill), set to 30 fps, and its first audio track converted to 48 kHz stereo.
A clip with no sound gets silence. Transcribe the joined file, not the originals.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--out", default="work/joined.mp4")
    ap.add_argument("--width", type=int, default=None, help="Default: the first clip's width (max 1080 short side)")
    ap.add_argument("--height", type=int, default=None)
    ap.add_argument("--fps", type=float, default=30)
    a = ap.parse_args()

    ffmpeg, ffprobe, _ = vtools.need_ffmpeg()
    infos = [vtools.probe(c, ffprobe) for c in a.clips]
    if a.width and a.height:
        W, H = a.width, a.height
    else:
        w0, h0 = infos[0]["width"], infos[0]["height"]
        short = min(w0, h0, 1080)
        W, H = (short, int(round(short * h0 / w0 / 2)) * 2) if w0 <= h0 else (int(round(short * w0 / h0 / 2)) * 2, short)

    inputs, fc, cat = [], [], []
    for i, (c, info) in enumerate(zip(a.clips, infos)):
        inputs += ["-i", c]
    n = len(a.clips)
    for i, info in enumerate(infos):
        fc.append(f"[{i}:v:0]fps={a.fps},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[v{i}]")
        if info["has_audio"]:
            fc.append(f"[{i}:a:0]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]")
        else:
            inputs += ["-f", "lavfi", "-t", f"{info['duration']:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
            fc.append(f"[{n}:a]asetpts=PTS-STARTPTS[a{i}]")
            n += 1
        cat.append(f"[v{i}][a{i}]")
    fc.append("".join(cat) + f"concat=n={len(a.clips)}:v=1:a=1[v][a]")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    script = out.with_suffix(".filter.txt")
    script.write_text(";\n".join(fc), encoding="utf-8")
    vtools.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error"] + inputs +
               ["-filter_complex_script", str(script), "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    script.unlink(missing_ok=True)
    total = sum(i["duration"] for i in infos)
    print(f"Joined {len(a.clips)} clips into {out} ({W}x{H}, about {vtools.hms(total)}). Transcribe this file next.")


if __name__ == "__main__":
    main()
