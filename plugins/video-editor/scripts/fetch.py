#!/usr/bin/env python3
"""Download videos from links (TikTok, YouTube, Instagram, X and most other sites) so they can be
studied frame by frame.

Usage:
    python3 fetch.py URL [URL ...] --out style-lab/NAME/videos
    python3 fetch.py --list links.txt --out style-lab/NAME/videos
    python3 fetch.py PROFILE_OR_CHANNEL_URL --latest 30 --top 10 --out style-lab/NAME/videos
        (the 10 most-viewed of the last 30 videos, when the site shares view counts)
    Add --browser chrome (or safari, firefox, edge) to use that browser's login, only if the
    person says yes. Some sites (often Instagram) only share videos with a logged-in visitor.

Needs yt-dlp. Install: Mac  brew install yt-dlp  (or  python3 -m pip install --user -U yt-dlp)
                      Windows  winget install yt-dlp.yt-dlp
Saves each video as an .mp4 plus a .json next to it with the title, creator, date, length and
views/likes when the site shares them (handy for picking the videos that did best).

Only download videos you're allowed to: your own, or other people's public videos to study
privately. Never repost or reuse someone else's footage. When a link won't download (private,
login needed, blocked), it says so and moves on: save that video yourself instead.
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402


def find_ytdlp():
    for d in [""] + vtools.EXTRA_DIRS:
        c = shutil.which("yt-dlp") if not d else os.path.join(d, vtools.exe("yt-dlp"))
        if c and os.path.isfile(c):
            return [c]
    if importlib.util.find_spec("yt_dlp"):
        return [sys.executable, "-m", "yt_dlp"]
    return None


def slug(text, n=50):
    t = re.sub(r"[^\w\s-]", "", (text or "").strip(), flags=re.UNICODE)
    t = re.sub(r"[\s_]+", "-", t).strip("-").lower()
    return t[:n].strip("-") or "video"


def explain(err):
    e = err.lower()
    if "login" in e or "sign in" in e or "cookies" in e or "rate-limit" in e or "rate limit" in e:
        return ("this site only shares it with a logged-in visitor. Either save it yourself (the app's "
                "Download/Save button, or a screen recording), or run again with --browser chrome to use your "
                "own Chrome login (only if you're OK with that)")
    if "private" in e:
        return "it's private. Save it yourself from the app, or pick another video"
    if "unsupported url" in e:
        return "that link isn't a video page yt-dlp knows. Open the video itself and copy its link"
    if "403" in e or "forbidden" in e:
        return "the site blocked the download. Update yt-dlp (brew upgrade yt-dlp, or pip install -U yt-dlp) and try again, or save it yourself"
    if "not available" in e or "unavailable" in e or "404" in e or "removed" in e:
        return "the video isn't available anymore"
    return "it didn't download. Save it yourself (the app's Download/Save button, or a screen recording)"


def list_profile(cmd, url, latest, browser):
    args = cmd + ["--flat-playlist", "-J", "--playlist-end", str(latest), "--no-warnings"]
    if browser:
        args += ["--cookies-from-browser", browser]
    p = subprocess.run(args + [url], capture_output=True, text=True)
    if p.returncode != 0:
        return None, p.stderr
    data = json.loads(p.stdout or "{}")
    entries = [e for e in (data.get("entries") or []) if e]
    out = []
    for e in entries:
        u = e.get("url") or e.get("webpage_url")
        if u and not u.startswith("http"):
            u = e.get("webpage_url") or u
        out.append({"url": u, "title": e.get("title"), "views": e.get("view_count"), "duration": e.get("duration")})
    return out, None


def download(cmd, url, out_dir, n, ffmpeg_dir, browser, max_height):
    tmpl = str(out_dir / f"_dl-{n:02d}.%(ext)s")
    fmt = (f"bv*[height<={max_height}][ext=mp4]+ba[ext=m4a]/bv*[height<={max_height}]+ba/"
           f"b[height<={max_height}]/bv*+ba/b")
    args = cmd + ["-f", fmt, "--merge-output-format", "mp4", "--no-playlist", "--write-info-json",
                  "--no-write-comments", "--no-warnings", "--newline", "-o", tmpl]
    if ffmpeg_dir:
        args += ["--ffmpeg-location", ffmpeg_dir]
    if browser:
        args += ["--cookies-from-browser", browser]
    p = subprocess.run(args + [url], capture_output=True, text=True)
    files = sorted(out_dir.glob(f"_dl-{n:02d}.*"))
    vids = [f for f in files if f.suffix.lower() in (".mp4", ".mov", ".webm", ".mkv", ".m4v")]
    infos = [f for f in files if f.name.endswith(".info.json")]
    if p.returncode != 0 or not vids:
        for f in files:
            f.unlink(missing_ok=True)
        return None, (p.stderr or p.stdout)
    info = {}
    if infos:
        try:
            info = json.loads(infos[0].read_text(encoding="utf-8"))
        except Exception:
            info = {}
        for f in infos:
            f.unlink(missing_ok=True)
    who = info.get("uploader") or info.get("channel") or info.get("uploader_id") or ""
    name = f"{n:02d}-{slug(who, 24)}-{slug(info.get('title') or info.get('description') or 'video', 40)}"
    final = out_dir / (name + vids[0].suffix.lower())
    i = 2
    while final.exists():
        final = out_dir / f"{name}-{i}{vids[0].suffix.lower()}"
        i += 1
    vids[0].rename(final)
    for extra in vids[1:]:
        extra.unlink(missing_ok=True)
    meta = {k: info.get(k) for k in ("title", "uploader", "channel", "upload_date", "duration", "view_count",
                                     "like_count", "comment_count", "repost_count", "webpage_url", "extractor_key")}
    meta["source_url"] = url
    final.with_suffix(".json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return final, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--list", default=None, help="A text file with one link per line")
    ap.add_argument("--out", required=True)
    ap.add_argument("--latest", type=int, default=0, help="For a profile/channel link: look at its last N videos")
    ap.add_argument("--top", type=int, default=0, help="...and download the N most-viewed of them")
    ap.add_argument("--browser", default=None, help="chrome, safari, firefox, edge: use that browser's login")
    ap.add_argument("--max-height", type=int, default=1920)
    a = ap.parse_args()

    urls = list(a.urls)
    if a.list:
        urls += [l.strip() for l in Path(a.list).read_text(encoding="utf-8").splitlines()
                 if l.strip().startswith("http")]
    if not urls:
        sys.exit("Give at least one link (or --list links.txt).")
    cmd = find_ytdlp()
    if not cmd:
        osn = vtools.os_name()
        how = ("brew install yt-dlp   (or: python3 -m pip install --user -U yt-dlp)" if osn == "mac"
               else "winget install yt-dlp.yt-dlp" if osn == "windows" else "python3 -m pip install --user -U yt-dlp")
        sys.exit(f"yt-dlp isn't installed, so links can't be downloaded yet. Install it with:\n  {how}\n"
                 "Or save the videos yourself and put the files in the folder.")
    ffmpeg, _, _ = vtools.find_ffmpeg()
    ffmpeg_dir = os.path.dirname(ffmpeg) if ffmpeg else None
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    n = len([f for f in out_dir.iterdir() if f.suffix.lower() in (".mp4", ".mov", ".webm", ".mkv", ".m4v")]) + 1

    queue = []
    for u in urls:
        if a.latest:
            items, err = list_profile(cmd, u, a.latest, a.browser)
            if items is None:
                print(f"Couldn't list {u}: {explain(err)}")
                continue
            if a.top and any(i.get("views") for i in items):
                items = sorted(items, key=lambda i: i.get("views") or 0, reverse=True)[: a.top]
                print(f"{u}: picked the {len(items)} most-viewed of the last {a.latest}.")
            elif a.top:
                items = items[: a.top]
                print(f"{u}: the site doesn't share view counts here, so these are the latest {len(items)}.")
            queue += [i["url"] for i in items if i.get("url")]
        else:
            queue.append(u)

    ok, failed = [], []
    for u in queue:
        print(f"Downloading {u} ...")
        f, meta = download(cmd, u, out_dir, n, ffmpeg_dir, a.browser, a.max_height)
        if f is None:
            failed.append(u)
            print(f"  Skipped: {explain(meta or '')}")
            continue
        views = meta.get("view_count")
        print(f"  Saved {f.name}" + (f" ({views:,} views)" if isinstance(views, int) else ""))
        ok.append(f)
        n += 1
    print(f"\n{len(ok)} downloaded, {len(failed)} skipped. Folder: {out_dir}")
    if failed:
        print("Skipped links (save these yourself, then drop the files in the folder):")
        for u in failed:
            print("  " + u)


if __name__ == "__main__":
    main()
