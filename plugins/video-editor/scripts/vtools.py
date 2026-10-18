"""Shared helpers for the video-editor scripts. Python 3.8+, standard library only."""
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

CONFIG = Path.home() / ".video-editor" / "config.json"

# Homebrew keeps ffmpeg-full outside the PATH ("keg-only"), so look there too.
EXTRA_DIRS = [
    "/opt/homebrew/opt/ffmpeg-full/bin",
    "/usr/local/opt/ffmpeg-full/bin",
    "/opt/homebrew/bin",
    "/usr/local/bin",
]
if os.name == "nt":
    local = os.environ.get("LOCALAPPDATA", "")
    EXTRA_DIRS += [
        os.path.join(local, "Microsoft", "WinGet", "Links"),
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
    ]

CAPTION_FILTERS = {"subtitles", "ass"}
CORE_FILTERS = {"loudnorm", "silencedetect", "overlay", "zoompan", "concat", "trim"}


def exe(name):
    return name + (".exe" if os.name == "nt" else "")


def filters_of(ffmpeg):
    try:
        out = subprocess.run([ffmpeg, "-hide_banner", "-filters"], capture_output=True,
                             text=True, timeout=60).stdout
    except Exception:
        return set()
    names = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3 and "->" in parts[2]:
            names.add(parts[1])
    return names


def encoders_of(ffmpeg):
    try:
        out = subprocess.run([ffmpeg, "-hide_banner", "-encoders"], capture_output=True,
                             text=True, timeout=60).stdout
    except Exception:
        return set()
    names = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and len(parts[0]) == 6 and parts[0][0] in "VAS":
            names.add(parts[1])
    return names


def candidates():
    seen = []
    env = os.environ.get("VIDEO_EDITOR_FFMPEG")
    if env:
        seen.append(env)
    if CONFIG.exists():
        try:
            saved = json.loads(CONFIG.read_text()).get("ffmpeg")
            if saved:
                seen.append(saved)
        except Exception:
            pass
    for d in EXTRA_DIRS:
        seen.append(os.path.join(d, exe("ffmpeg")))
    found = shutil.which("ffmpeg")
    if found:
        seen.append(found)
    out = []
    for c in seen:
        if c and os.path.isfile(c) and c not in out:
            out.append(c)
    return out


def find_ffmpeg(require_captions=True):
    """Return (ffmpeg, ffprobe, filters). Prefers an ffmpeg that can burn in captions."""
    best = None
    for c in candidates():
        f = filters_of(c)
        if not f:
            continue
        if CAPTION_FILTERS & f:
            best = (c, f)
            break
        if best is None:
            best = (c, f)
    if best is None:
        return None, None, set()
    ffmpeg, f = best
    if require_captions and not (CAPTION_FILTERS & f):
        pass  # caller decides what to do; check_setup reports it
    probe = os.path.join(os.path.dirname(ffmpeg), exe("ffprobe"))
    if not os.path.isfile(probe):
        probe = shutil.which("ffprobe") or ""
    return ffmpeg, probe, f


def save_config(**values):
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if CONFIG.exists():
        try:
            data = json.loads(CONFIG.read_text())
        except Exception:
            data = {}
    data.update(values)
    CONFIG.write_text(json.dumps(data, indent=2))


def need_ffmpeg():
    ffmpeg, ffprobe, f = find_ffmpeg()
    if not ffmpeg or not ffprobe:
        sys.exit("ffmpeg/ffprobe not found. Run check_setup.py and install ffmpeg first.")
    return ffmpeg, ffprobe, f


def run(cmd, cwd=None, quiet=True):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        tail = "\n".join(p.stderr.strip().splitlines()[-25:])
        sys.exit(f"Command failed ({p.returncode}): {' '.join(str(c) for c in cmd[:6])} ...\n{tail}")
    if not quiet:
        print(p.stdout)
    return p


def probe(path, ffprobe=None):
    if ffprobe is None:
        _, ffprobe, _ = need_ffmpeg()
    p = run([ffprobe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    data = json.loads(p.stdout)
    info = {"duration": float(data.get("format", {}).get("duration") or 0), "has_audio": False,
            "width": 0, "height": 0, "fps": 30.0}
    for s in data.get("streams", []):
        if s.get("codec_type") == "video" and not info["width"]:
            w, h = int(s.get("width") or 0), int(s.get("height") or 0)
            rot = 0
            for sd in s.get("side_data_list", []) or []:
                if "rotation" in sd:
                    rot = int(float(sd["rotation"]))
            if "rotate" in (s.get("tags") or {}):
                rot = int(float(s["tags"]["rotate"]))
            if abs(rot) % 180 == 90:
                w, h = h, w
            info["width"], info["height"] = w, h
            rate = s.get("avg_frame_rate") or s.get("r_frame_rate") or "30/1"
            try:
                n, d = rate.split("/")
                fps = float(n) / float(d) if float(d) else 30.0
                info["fps"] = fps if 1 < fps < 241 else 30.0
            except Exception:
                pass
            if not info["duration"] and s.get("duration"):
                info["duration"] = float(s["duration"])
        if s.get("codec_type") == "audio":
            info["has_audio"] = True
    return info


def hms(t):
    t = max(0.0, t)
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:05.2f}"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def os_name():
    s = platform.system()
    return {"Darwin": "mac", "Windows": "windows"}.get(s, "linux")
