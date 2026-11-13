#!/usr/bin/env python3
"""Make a small starter pack of sound effects (made from scratch, so free to use anywhere).

Usage:
    python3 sfx.py --out assets/sfx          # writes pop, click, whoosh, swoosh, riser, ding, hit, typing
    python3 sfx.py --list assets/sfx         # lists every sound in a folder with its length

Use them in plan.json:
    "sfx": [{"name": "whoosh", "at": 3.2}, {"name": "pop", "at": 5.0, "volume": 0.4}]
"name" looks in assets/sfx/ (any .wav/.mp3/.m4a/.aiff with that name), or use "file" for any path.
Your own sound effect packs work the same way: drop the files in assets/sfx/.
These starter sounds are simple. For richer ones, download a free pack (for example from
pixabay.com/sound-effects) and drop the files in assets/sfx/.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402

SR = 48000
SOUNDS = {
    # name: (lavfi source, extra filters, description)
    "pop": ("aevalsrc='0.8*sin(2*PI*(950-650*t/0.09)*t)*exp(-38*t)':d=0.09:s=48000", "",
            "short bubbly pop: text or a sticker popping in"),
    "click": ("aevalsrc='0.6*(random(0)*2-1)*exp(-900*t)+0.4*sin(2*PI*2400*t)*exp(-320*t)':d=0.04:s=48000",
              "highpass=f=700", "UI click: a cursor click, a button, a screen appearing"),
    "whoosh": ("anoisesrc=d=0.5:c=pink:a=0.9:r=48000",
               "highpass=f=250,lowpass=f=5500,afade=t=in:st=0:d=0.24:curve=qsin,afade=t=out:st=0.24:d=0.26:curve=qsin",
               "soft whoosh: a transition, a zoom, b-roll sliding in"),
    "swoosh": ("anoisesrc=d=0.28:c=white:a=0.7:r=48000",
               "highpass=f=1600,lowpass=f=9000,afade=t=in:st=0:d=0.1:curve=qsin,afade=t=out:st=0.1:d=0.18:curve=exp",
               "quick bright swoosh: a fast swipe or a title flying in"),
    "riser": ("aevalsrc='0.25*sin(2*PI*(180*t+260*t*t))+0.35*(random(0)*2-1)*(t/1.2)^2':d=1.2:s=48000",
              "highpass=f=200,lowpass=f=7000,afade=t=in:st=0:d=1.0:curve=exp",
              "rising build-up: under a hook, ending right on the first big moment"),
    "ding": ("aevalsrc='0.55*sin(2*PI*1318*t)*exp(-6*t)+0.25*sin(2*PI*2637*t)*exp(-9*t)':d=0.9:s=48000", "",
             "bright ding: a number, a result, a notification"),
    "hit": ("aevalsrc='0.95*sin(2*PI*(70-25*t)*t)*exp(-7*t)+0.3*(random(0)*2-1)*exp(-45*t)':d=0.7:s=48000",
            "lowpass=f=2500", "low impact: a big reveal or a hard cut to black"),
    "typing": ("aevalsrc='(lt(mod(t,0.113),0.007)+lt(mod(t+0.051,0.167),0.006)+lt(mod(t+0.023,0.231),0.006))"
               "*(random(0)*2-1)*0.6':d=2.5:s=48000",
               "highpass=f=900,lowpass=f=6500", "keyboard typing loop (2.5 s): while text types on screen"),
}
AUDIO_EXT = (".wav", ".mp3", ".m4a", ".aiff", ".aif", ".flac", ".ogg", ".caf")


def make(ffmpeg, out_dir, names):
    out_dir.mkdir(parents=True, exist_ok=True)
    made = []
    for name in names:
        src, extra, _ = SOUNDS[name]
        dest = out_dir / f"{name}.wav"
        af = (extra + "," if extra else "") + "aformat=sample_rates=48000:channel_layouts=stereo"
        tmp = out_dir / f".{name}.tmp.wav"
        vtools.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", src, "-af", af, str(tmp)])
        # Peak-normalize to -6 dBFS so every sound starts at the same level.
        p = vtools.run([ffmpeg, "-hide_banner", "-nostats", "-i", str(tmp), "-af", "volumedetect", "-f", "null", "-"])
        m = re.search(r"max_volume:\s*(-?[\d.]+) dB", p.stderr)
        gain = -6.0 - float(m.group(1)) if m else 0.0
        vtools.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(tmp), "-af", f"volume={gain:.2f}dB",
                    "-c:a", "pcm_s16le", str(dest)])
        tmp.unlink(missing_ok=True)
        made.append(dest)
    readme = out_dir / "README.txt"
    lines = ["Starter sound effects made by the Video Editor plugin (free to use anywhere).",
             "Use them by name in plan.json, for example {\"name\": \"whoosh\", \"at\": 3.2}.", ""]
    lines += [f"{n}.wav  {SOUNDS[n][2]}" for n in names]
    lines += ["", "Add your own: drop .wav or .mp3 files here and use their names the same way."]
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return made


def list_dir(ffprobe, folder):
    files = sorted(f for f in Path(folder).iterdir() if f.suffix.lower() in AUDIO_EXT)
    if not files:
        print(f"No sounds in {folder} yet.")
        return
    for f in files:
        p = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                           capture_output=True, text=True)
        try:
            d = float(p.stdout.strip())
        except ValueError:
            d = 0.0
        print(f"  {f.stem:<24} {d:5.2f} s   {f.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="Folder to write the starter pack into (e.g. assets/sfx)")
    ap.add_argument("--only", default=None, help="Comma-separated names to make")
    ap.add_argument("--list", default=None, help="List the sounds in a folder")
    a = ap.parse_args()
    ffmpeg, ffprobe, _ = vtools.need_ffmpeg()
    if a.list:
        list_dir(ffprobe, a.list)
        return
    if not a.out:
        sys.exit("Use --out assets/sfx to make the starter pack, or --list FOLDER.")
    names = [n.strip() for n in a.only.split(",")] if a.only else list(SOUNDS)
    bad = [n for n in names if n not in SOUNDS]
    if bad:
        sys.exit("Unknown sound(s): " + ", ".join(bad) + ". Available: " + ", ".join(SOUNDS))
    made = make(ffmpeg, Path(a.out), names)
    print(f"Made {len(made)} sounds in {a.out}: " + ", ".join(f.stem for f in made))


if __name__ == "__main__":
    main()
