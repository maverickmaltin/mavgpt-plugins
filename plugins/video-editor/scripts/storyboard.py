#!/usr/bin/env python3
"""Turn a storyboard (work/storyboard.json) into a page the user can open and approve.

Usage:
    python3 storyboard.py work/storyboard.json

storyboard.json:
{
  "title": "My video",
  "video": "raw/my-video.mp4",
  "sections": [
    {"start": 0.0, "end": 2.1, "said": "Claude can now edit videos for you.",
     "cut": "Nothing", "on_screen": "Big pop-in title, quick zoom", "asset": "None"}
  ],
  "assets_needed": ["App screenshot (from you)", "B-roll of the app (Claude records it)"]
}

Section start/end times are ORIGINAL-video seconds (the same times as in the transcript).
Writes work/storyboard.html next to the JSON, with one still frame per section.
"""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402

CSS = """
body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:0;background:#f6f6f4;color:#1a1a1a}
main{max-width:1000px;margin:0 auto;padding:28px 18px}
h1{font-size:26px;margin:0 0 6px} p.sub{color:#666;margin:0 0 22px}
.card{display:flex;gap:16px;background:#fff;border-radius:14px;padding:14px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.card img{width:150px;border-radius:10px;object-fit:cover;flex:none}
.num{font-weight:700;color:#e8743b;font-size:13px;letter-spacing:.06em}
.time{color:#888;font-size:13px;margin-left:8px}
.said{font-size:17px;margin:6px 0 10px}
dl{display:grid;grid-template-columns:110px 1fr;gap:4px 10px;margin:0;font-size:14px}
dt{color:#888} dd{margin:0}
.assets{background:#fff;border-radius:14px;padding:16px 20px;margin-top:18px}
@media(max-width:600px){.card{flex-direction:column}.card img{width:100%}}
"""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sb_path = Path(sys.argv[1]).resolve()
    sb = vtools.load_json(sb_path)
    if not sb.get("video"):
        sys.exit("storyboard.json needs a \"video\" (for example \"raw/my-video.mp4\").")
    base = vtools.project_root(sb_path)
    video = Path(sb["video"])
    video = video if video.is_absolute() else base / video
    ffmpeg, ffprobe, _ = vtools.need_ffmpeg()
    stills = sb_path.parent / f"{sb_path.stem}-stills"
    stills.mkdir(parents=True, exist_ok=True)

    cards = []
    for i, s in enumerate(sb.get("sections", []), 1):
        mid = (float(s["start"]) + float(s["end"])) / 2
        img = stills / f"section-{i:02d}.jpg"
        vtools.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{mid:.3f}", "-i", str(video),
                    "-frames:v", "1", "-vf", "scale=360:-2", "-q:v", "4", str(img)])
        rows = "".join(f"<dt>{label}</dt><dd>{html.escape(str(s.get(key, '') or '-'))}</dd>"
                       for label, key in (("Cut", "cut"), ("On screen", "on_screen"), ("Asset", "asset")))
        cards.append(
            f'<div class="card"><img src="{stills.name}/{img.name}" alt="Section {i}">'
            f'<div><span class="num">SECTION {i}</span><span class="time">{vtools.hms(float(s["start"]))} to {vtools.hms(float(s["end"]))}</span>'
            f'<div class="said">&ldquo;{html.escape(s.get("said", ""))}&rdquo;</div><dl>{rows}</dl></div></div>')
    assets = "".join(f"<li>{html.escape(a)}</li>" for a in sb.get("assets_needed", []))
    page = (f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>Storyboard</title><style>{CSS}</style></head><body><main>"
            f"<h1>{html.escape(sb.get('title', 'Storyboard'))}</h1>"
            f"<p class='sub'>Reply in the chat with changes by section number, or say it looks good.</p>"
            + "".join(cards)
            + (f"<div class='assets'><strong>Assets needed</strong><ul>{assets}</ul></div>" if assets else "")
            + "</main></body></html>")
    out = sb_path.with_suffix(".html")
    out.write_text(page, encoding="utf-8")
    print(f"Storyboard page: {out}")


if __name__ == "__main__":
    main()
