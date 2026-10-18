#!/usr/bin/env python3
"""Check that this computer has everything the video-editor plugin needs.

Usage:
    python3 check_setup.py          # readable report
    python3 check_setup.py --json   # machine-readable report

Exit code 0 means ready to edit. Exit code 1 means something is missing; the report
says exactly what to install and how.
"""
import importlib.util
import json
import shutil
import sys
import platform
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402


def main():
    as_json = "--json" in sys.argv
    osn = vtools.os_name()
    ffmpeg, ffprobe, filters = vtools.find_ffmpeg()
    report = {
        "os": osn,
        "python": platform.python_version(),
        "ffmpeg": ffmpeg,
        "ffprobe": ffprobe,
        "captions": bool(vtools.CAPTION_FILTERS & filters),
        "missing_filters": sorted(vtools.CORE_FILTERS - filters) if ffmpeg else sorted(vtools.CORE_FILTERS),
        "h264": False,
        "transcriber": None,
        "homebrew": bool(shutil.which("brew")) or Path("/opt/homebrew/bin/brew").exists() or Path("/usr/local/bin/brew").exists(),
        "todo": [],
    }
    if ffmpeg:
        enc = vtools.encoders_of(ffmpeg)
        report["h264"] = "libx264" in enc or "h264_videotoolbox" in enc or "h264_mf" in enc
    for mod in ("faster_whisper", "whisper"):
        if importlib.util.find_spec(mod):
            report["transcriber"] = mod
            break

    todo = report["todo"]
    if not ffmpeg or not report["captions"]:
        if osn == "mac":
            if not report["homebrew"]:
                todo.append("Install Homebrew: the user runs the one-line installer from https://brew.sh in the Terminal app (it asks for their Mac password, so they type it themselves).")
            todo.append("Install ffmpeg with captions support: brew install ffmpeg-full   (plain 'ffmpeg' from Homebrew can't burn in captions). It's keg-only, so this script finds it at /opt/homebrew/opt/ffmpeg-full/bin automatically.")
        elif osn == "windows":
            todo.append("Install ffmpeg: winget install --id Gyan.FFmpeg -e   then close and reopen the terminal.")
        else:
            todo.append("Install ffmpeg with libass (for example: sudo apt install ffmpeg).")
    elif report["missing_filters"]:
        todo.append("This ffmpeg is missing filters: " + ", ".join(report["missing_filters"]) + ". Install a full build (Mac: brew install ffmpeg-full, Windows: winget install --id Gyan.FFmpeg -e).")
    if ffmpeg and not report["h264"]:
        todo.append("This ffmpeg has no H.264 encoder. Install a full build (Mac: brew install ffmpeg-full, Windows: winget install --id Gyan.FFmpeg -e).")
    if not report["transcriber"]:
        py = "python3" if osn != "windows" else "python"
        todo.append(f"Install transcription: {py} -m pip install --user faster-whisper   (first run downloads a speech model of about 500 MB).")

    if ffmpeg and report["captions"] and not report["missing_filters"]:
        vtools.save_config(ffmpeg=ffmpeg, ffprobe=ffprobe)

    ready = not todo
    report["ready"] = ready
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print("Video editor setup check")
        print(f"  Computer:       {osn} (Python {report['python']})")
        print(f"  ffmpeg:         {ffmpeg or 'NOT FOUND'}")
        print(f"  Captions:       {'yes' if report['captions'] else 'NO'}")
        print(f"  H.264 export:   {'yes' if report['h264'] else 'NO'}")
        print(f"  Transcription:  {report['transcriber'] or 'NOT INSTALLED'}")
        if ready:
            print("\nREADY: everything needed is installed.")
        else:
            print("\nTO DO:")
            for i, t in enumerate(todo, 1):
                print(f"  {i}. {t}")
    sys.exit(0 if ready else 1)


if __name__ == "__main__":
    main()
