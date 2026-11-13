#!/usr/bin/env python3
"""Render a video from an edit plan (plan.json). See skills/edit/reference/plan-format.md.

Usage:
    python3 render.py work/plan.json --preview   # fast half-size draft to exports/
    python3 render.py work/plan.json             # full-quality final

Everything is described in the plan: which parts to keep, the canvas (9:16, 16:9...),
zooms, captions, titles, image/video overlays, b-roll, music, loudness and a progress bar.
Re-run after every change to the plan. The original video is never modified.
"""
import argparse
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402

POSITIONS = {"top": 0.16, "upper": 0.3, "center": 0.5, "middle": 0.5, "lower": 0.7, "bottom": 0.84}


def even(x):
    return max(2, int(round(x / 2.0)) * 2)


def ass_color(hexstr, default="#FFFFFF"):
    """'#RRGGBB' or '#RRGGBBAA' (AA = opacity, FF solid) -> ASS &HAABBGGRR."""
    h = (hexstr or default).lstrip("#")
    if len(h) == 6:
        h += "FF"
    r, g, b, a = h[0:2], h[2:4], h[4:6], h[6:8]
    inv = 255 - int(a, 16)
    return f"&H{inv:02X}{b}{g}{r}".upper()


def ass_inline(hexstr):
    """'#RRGGBB(AA)' -> ('&HBBGGRR&', '&HAA&') for inline \\c / \\3c tags (AA in ASS is transparency)."""
    h = (hexstr or "#FFFFFF").lstrip("#")
    if len(h) == 6:
        h += "FF"
    r, g, b, a = h[0:2], h[2:4], h[4:6], h[6:8]
    return f"&H{b}{g}{r}&".upper(), f"&H{255 - int(a, 16):02X}&"


def ass_time(t):
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ass_text(s):
    return s.replace("\\", "⧵").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def ypos(value, default):
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    return POSITIONS.get(str(value).lower(), default)


def remap_words(words, segs):
    """Source-time words -> output-time words, dropping anything that was cut."""
    out = []
    for w in words:
        ws, we = float(w["start"]), float(w["end"])
        if we - ws < 0.05:
            we = ws + 0.08  # whisper sometimes gives a word no length; keep it
        mid = (ws + we) / 2
        for a, b, off in segs:
            if a <= mid <= b:
                s = max(a, ws) - a + off
                e = min(b, we) - a + off
                if e > s:
                    out.append({"text": w["text"], "start": s, "end": e})
                break
    return out


def _tok(t):
    return re.sub(r"[^\w/]", "", t.lower())


def apply_fixes(words, fixes):
    """Fix misheard words before captions: keys can be one word ("clod"), several words
    ("clog code") or start with punctuation ("/visual"). Case doesn't matter."""
    if not fixes:
        return words
    multi, single = [], {}
    for k, v in fixes.items():
        toks = [x for x in (_tok(x) for x in str(k).split()) if x]
        if len(toks) > 1:
            multi.append((toks, v))
        elif str(k).strip():
            single[str(k).strip()] = v
    multi.sort(key=lambda kv: -len(kv[0]))
    out, i = [], 0
    while i < len(words):
        hit = False
        for toks, v in multi:
            seg = words[i:i + len(toks)]
            if len(seg) == len(toks) and [_tok(w["text"]) for w in seg] == toks:
                trail = re.search(r"[,.;:!?]+[\"\u201d\u2019']*$", seg[-1]["text"].strip())
                out.append(dict(seg[0], text=v + (trail.group(0) if trail else ""), end=seg[-1]["end"]))
                i += len(toks)
                hit = True
                break
        if hit:
            continue
        w = dict(words[i])
        t = w["text"]
        for k, v in single.items():
            t = re.sub(r"(?i)(?<!\w)" + re.escape(k) + r"(?!\w)", v, t)
        w["text"] = t
        out.append(w)
        i += 1
    return out


QUOTES = "\"\u201c\u201d\u201e\u00ab\u00bb"


def clean_word(text, cfg):
    t = text.strip().strip(QUOTES)
    t = re.sub(r"^['\u2018]+|['\u2019]+$", "", t)
    if not cfg.get("punctuation", False):
        t = re.sub(r"[,.;:]+$", "", t).strip(QUOTES)
    if cfg.get("uppercase"):
        t = t.upper()
    return t


def caption_events(words, cfg, W, H, total):
    if not words:
        return []
    per = int(cfg.get("words_per_caption", 3))
    max_chars = int(cfg.get("max_chars", 22 if H > W else 34))
    chunks, cur = [], []
    for i, w in enumerate(words):
        txt = clean_word(w["text"], cfg)
        if not txt:
            continue
        item = dict(w, text=txt)
        if cur:
            gap = item["start"] - cur[-1]["end"]
            chars = sum(len(c["text"]) + 1 for c in cur) + len(txt)
            if len(cur) >= per or gap > 0.45 or chars > max_chars or re.search(r"[.?!]$", words[i - 1]["text"]):
                chunks.append(cur)
                cur = []
        cur.append(item)
    if cur:
        chunks.append(cur)

    hl, _ = ass_inline(cfg.get("highlight") or "#FFD400")
    base, _ = ass_inline(cfg.get("color", "#FFFFFF"))
    oc, _ = ass_inline(cfg.get("outline_color", "#000000"))
    ob = int(cfg.get("outline", 6))
    size = int(cfg.get("size", 100 if H > W else 68))
    mode = cfg.get("highlight_mode", "color")
    ht = ass_inline(cfg["highlight_text"])[0] if cfg.get("highlight_text") else None
    y = ypos(cfg.get("position"), 0.70 if H > W else 0.84) * H
    anim_name = cfg.get("animation", "pop")
    ANIMS = {"pop": "\\fscx85\\fscy85\\t(0,90,\\fscx100\\fscy100)",
             "bounce": "\\fscx70\\fscy70\\t(0,80,\\fscx112\\fscy112)\\t(80,150,\\fscx100\\fscy100)",
             "fade": "\\fad(90,0)", "slide": "", "none": ""}
    events = []
    for ci, chunk in enumerate(chunks):
        c_start = chunk[0]["start"]
        nxt = chunks[ci + 1][0]["start"] if ci + 1 < len(chunks) else total
        c_end = min(nxt, chunk[-1]["end"] + 0.35)
        for j, w in enumerate(chunk):
            s = c_start if j == 0 else w["start"]
            e = chunk[j + 1]["start"] if j + 1 < len(chunk) else c_end
            if e - s < 0.02:
                continue
            parts = []
            for k, x in enumerate(chunk):
                t = ass_text(x["text"])
                if cfg.get("highlight") is not False and mode != "none" and k == j:
                    if mode == "box":
                        bb = max(ob + 10, int(size * 0.2))
                        on = "{\\3c" + hl + "\\bord" + str(bb) + ("\\c" + ht if ht else "") + "}"
                        off = "{\\3c" + oc + "\\bord" + str(ob) + "\\c" + base + "}"
                    elif mode == "scale":
                        on = "{\\c" + hl + "\\fscx115\\fscy115}"
                        off = "{\\c" + base + "\\fscx100\\fscy100}"
                    else:
                        on = "{\\c" + hl + "}"
                        off = "{\\c" + base + "}"
                    parts.append(on + t + off)
                else:
                    parts.append(t)
            anim = ANIMS.get(anim_name, "") if j == 0 else ""
            if anim_name == "slide" and j == 0:
                tag = "{\\an5\\move(%d,%d,%d,%d,0,120)}" % (W // 2, int(y + H * 0.02), W // 2, int(y))
            else:
                tag = "{\\an5\\pos(%d,%d)%s}" % (W // 2, int(y), anim)
            events.append(("Caption", s, e, tag + " ".join(parts)))
    return events


def is_dark(hexstr):
    if not hexstr:
        return False
    h = str(hexstr).lstrip("#")[:6]
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        return False
    return 0.2126 * r + 0.7152 * g + 0.0722 * b < 90


def title_events(titles, W, H):
    events = []
    for t in titles or []:
        s, e = float(t["start"]), float(t["end"])
        y = ypos(t.get("position"), 0.16) * H
        x = W * float(t.get("x", 0.5))
        style = t.get("style", "pop")
        style_name = "TitleBox" if t.get("box") else "Title"
        if style == "none":
            anim, pos = "", "\\pos(%d,%d)" % (x, y)
        elif style == "slide":
            anim = "\\move(%d,%d,%d,%d,0,220)\\fad(0,150)" % (x, y + H * 0.04, x, y)
            pos = ""
        else:
            pos = "\\pos(%d,%d)" % (x, y)
            if style == "fade":
                anim = "\\fad(200,200)"
            else:
                anim = "\\fad(60,120)\\fscx60\\fscy60\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)"
        extra = ""
        if t.get("color"):
            c, a_ = ass_inline(t["color"])
            extra += "\\c" + c + "\\1a" + a_
        if t.get("box_color"):
            c, a_ = ass_inline(t["box_color"])
            extra += "\\3c" + c + "\\3a" + a_
        elif t.get("outline_color"):
            extra += "\\3c" + ass_inline(t["outline_color"])[0]
        elif not t.get("box") and is_dark(t.get("color")):
            extra += "\\3c&HFFFFFF&"  # dark text needs a light outline to show up
        if t.get("size"):
            extra += "\\fs%d" % int(t["size"])
        text = t["text"].upper() if t.get("uppercase") else t["text"]
        events.append((style_name, s, e, "{\\an5%s%s%s}%s" % (pos, anim, extra, ass_text(text))))
    return events


FONT_ALIASES = {
    "arialblack": ["Arial Black", "ariblk"], "arial": ["Arial", "arial"], "arialbold": ["Arial Bold", "arialbd"],
    "helveticaneue": ["HelveticaNeue"], "helvetica": ["Helvetica"], "impact": ["Impact", "impact"],
}


def _fkey(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def find_font_file(name, fonts_dir=None):
    """The .ttf/.otf/.ttc file for a font name, in fonts_dir or the computer's font folders."""
    key = _fkey(name)
    wanted = {key} | {_fkey(a) for a in FONT_ALIASES.get(key, [])}
    home = Path.home()
    dirs = ([Path(fonts_dir)] if fonts_dir else []) + [
        home / "Library/Fonts", Path("/Library/Fonts"), Path("/System/Library/Fonts"),
        Path("/System/Library/Fonts/Supplemental"), Path("C:/Windows/Fonts"),
        home / "AppData/Local/Microsoft/Windows/Fonts", home / ".local/share/fonts", home / ".fonts",
        Path("/usr/share/fonts")]
    loose = None
    for d in dirs:
        if not d.is_dir():
            continue
        for f in d.rglob("*"):
            if f.suffix.lower() not in (".ttf", ".otf", ".ttc"):
                continue
            k = _fkey(f.stem)
            if k in wanted:
                return f
            if loose is None and k.startswith(key):
                loose = f
    return loose


def hex_rgba(hexstr, default="#FFFFFF"):
    h = (hexstr or default).lstrip("#")
    if len(h) == 6:
        h += "FF"
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))


def rounded_title_png(t, ts, fonts_dir, dest):
    """Draw a title as a rounded box (TikTok style: each line its own width) into a PNG at full
    canvas scale. Returns (width, height) or None when Pillow or the font isn't available."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    name = t.get("font") or ts.get("font") or "Arial Black"
    size = int(t.get("size") or ts.get("size") or 80)
    ff = find_font_file(name, fonts_dir)
    if not ff:
        return None
    try:
        font = ImageFont.truetype(str(ff), size)
    except Exception:
        return None
    text = t["text"].upper() if t.get("uppercase") else t["text"]
    lines = text.split("\n")
    padx = int(t.get("pad_x", size * 0.42))
    pady = int(t.get("pad_y", size * 0.2))
    radius = int(t.get("radius", size * 0.3))
    asc, desc = font.getmetrics()
    lh = asc + desc
    widths = [font.getlength(l) for l in lines]
    img_w = int(max(widths) + 2 * padx) + 4
    img_h = int(len(lines) * lh + 2 * pady) + 4
    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    box = hex_rgba(t.get("box_color") or ts.get("box") or "#FFFFFF")
    col = hex_rgba(t.get("color") or ts.get("color") or "#000000", "#000000")
    y = 2
    n = len(lines)
    for i, (line, w) in enumerate(zip(lines, widths)):
        h = lh + (pady if i == 0 else 0) + (pady if i == n - 1 else 0)
        x0 = (img_w - (w + 2 * padx)) / 2
        extend = radius if i < n - 1 else 0  # overlap the next line so the shape has no notch
        d.rounded_rectangle([x0, y, x0 + w + 2 * padx, y + h + extend], radius=radius, fill=box)
        y += h
    y = 2
    for i, (line, w) in enumerate(zip(lines, widths)):
        top = y + (pady if i == 0 else 0)
        d.text(((img_w - w) / 2, top), line, font=font, fill=col)
        y += lh + (pady if i == 0 else 0) + (pady if i == n - 1 else 0)
    img.save(dest)
    return img_w, img_h


def write_ass(path, plan, W, H, words, total):
    cap = plan.get("captions") or {}
    tdef = plan.get("title_style") or {}
    font = cap.get("font", "Arial Black")
    size = int(cap.get("size", 100 if H > W else 68))
    outline = int(cap.get("outline", 6))
    tfont = tdef.get("font", font)
    tsize = int(tdef.get("size", 96 if H > W else 80))
    box = ass_color(tdef.get("box", "#000000CC"))
    margin = int(W * 0.08)
    shadow = int(cap.get("shadow", 2))
    shadow_c = ass_color(cap.get("shadow_color", "#00000069"))
    cap_border_style, cap_outline_c = 1, ass_color(cap.get('outline_color', '#000000'))
    if cap.get("box"):
        cap_border_style, cap_outline_c, outline = 3, ass_color(cap["box"]), max(outline, int(size * 0.18))
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}",
        "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Caption,{font},{size},{ass_color(cap.get('color', '#FFFFFF'))},&H000000FF,{cap_outline_c},{shadow_c},{-1 if cap.get('bold', True) else 0},0,0,0,100,100,{float(cap.get('spacing', 0))},0,{cap_border_style},{outline},{shadow},5,{margin},{margin},0,1",
        f"Style: Title,{tfont},{tsize},{ass_color(tdef.get('color', '#FFFFFF'))},&H000000FF,{ass_color(tdef.get('outline_color', '#000000'))},&H96000000,-1,0,0,0,100,100,0,0,1,{int(tdef.get('outline', 7))},3,5,{margin},{margin},0,1",
        f"Style: TitleBox,{tfont},{tsize},{ass_color(tdef.get('color', '#FFFFFF'))},&H000000FF,{box},{box},-1,0,0,0,100,100,0,0,3,{int(tsize * 0.18)},0,5,{margin},{margin},0,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    events = []
    if cap.get("enabled", True) and words:
        events += [(1,) + e for e in caption_events(words, cap, W, H, total)]
    events += [(2,) + e for e in title_events(plan.get("titles"), W, H)]
    for layer, style, s, e, text in sorted(events, key=lambda x: x[2]):
        lines.append(f"Dialogue: {layer},{ass_time(s)},{ass_time(e)},{style},,0,0,0,,{text}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(events)


def srt_time(t):
    t = max(0.0, t)
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s_, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s_:02d},{ms:03d}"


def write_srt(path, words, cfg, total):
    """A plain captions file (.srt) for the edited video: upload it to YouTube, or import it into
    CapCut, Premiere, Final Cut or DaVinci."""
    cfg = dict(cfg or {}, uppercase=False)
    lines, cur = [], []
    for i, w in enumerate(words):
        txt = clean_word(w["text"], dict(cfg, punctuation=True))
        if not txt:
            continue
        if cur and (len(cur) >= 7 or w["start"] - cur[-1]["end"] > 0.6 or re.search(r"[.?!]$", cur[-1]["text"])):
            lines.append(cur)
            cur = []
        cur.append(dict(w, text=txt))
    if cur:
        lines.append(cur)
    out = []
    for n, chunk in enumerate(lines, 1):
        s0 = chunk[0]["start"]
        e0 = min(total, chunk[-1]["end"] + 0.2)
        if n < len(lines):
            e0 = min(e0, lines[n][0]["start"])
        out.append(f"{n}\n{srt_time(s0)} --> {srt_time(e0)}\n" + " ".join(x["text"] for x in chunk) + "\n")
    Path(path).write_text("\n".join(out), encoding="utf-8")
    return len(lines)


def fesc(path):
    """Escape a path for use inside an ffmpeg filter argument."""
    p = str(path).replace("\\", "/")
    return p.replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")


def fix_loudness(ffmpeg, path, target):
    """One-pass loudnorm can land 1 to 2 LU off on short clips. Measure and correct the gain."""
    p = vtools.run([ffmpeg, "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"])
    found = re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", p.stderr, re.M)
    if not found:
        return
    gain = target - float(found[-1])
    if abs(gain) < 0.7:
        return
    tmp = path.with_name(path.stem + ".tmp" + path.suffix)
    vtools.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(path), "-map", "0", "-c:v", "copy",
                "-af", f"volume={gain:.2f}dB,alimiter=limit=0.89:level=false", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", str(tmp)])
    os.replace(tmp, path)


def build(plan_path, preview):
    plan = vtools.load_json(plan_path)
    base_dir = vtools.project_root(plan_path)

    def P(p):
        q = Path(p)
        return q if q.is_absolute() else (base_dir / q)

    ffmpeg, ffprobe, filters = vtools.need_ffmpeg()
    if not plan.get("input"):
        sys.exit("The plan has no \"input\" video. Add \"input\": \"raw/YOUR-VIDEO.mp4\".")
    src = P(plan["input"])
    if not src.exists():
        sys.exit(f"Input video not found: {src}\nPaths in the plan are relative to the project folder {base_dir}.")
    info = vtools.probe(src, ffprobe)
    dur = info["duration"]

    canvas = plan.get("canvas") or {}
    W = int(canvas.get("width", 1080))
    H = int(canvas.get("height", 1920))
    fps_cfg = canvas.get("fps", "source")
    if fps_cfg in (None, "source", "auto"):
        fps = round(min(60.0, info["fps"]), 3) if info["fps"] >= 23 else 30.0
    else:
        fps = float(fps_cfg)
    sf = 0.5 if preview else 1.0
    OW, OH = even(W * sf), even(H * sf)
    fit = canvas.get("fit", "cover")
    focus = canvas.get("focus") or {}
    fx, fy = float(focus.get("x", 0.5)), float(focus.get("y", 0.4))

    keep = plan.get("keep") or [[0, dur]]
    segs, t = [], 0.0
    for a, b in keep:
        a, b = max(0.0, float(a)), min(dur, float(b))
        if b - a > 0.04:
            segs.append((a, b, t))
            t += b - a
    if not segs:
        sys.exit("Nothing to keep: check the 'keep' list in the plan.")
    total = t

    # Place titles, zooms, overlays and b-roll on the original video's timeline by default, so
    # changing "keep" never shifts them. "times": "edited" uses the edited timeline instead.
    use_src = plan.get("times", "source") != "edited"

    def to_out(t):
        t = float(t)
        if not use_src:
            return t
        for a, b, off in segs:
            if t < a:
                return off
            if t <= b:
                return off + (t - a)
        return total

    def span(item, kind):
        if "start" not in item:
            sys.exit(f"A {kind} in the plan has no \"start\" time: {item}")
        s0 = float(item["start"])
        e0 = float(item.get("end", s0 + 2.0))
        s1, e1 = to_out(s0), to_out(e0)
        if e1 - s1 < 0.05:
            print(f"Note: skipped a {kind} at {s0:.2f}-{e0:.2f}s because that part of the video was cut.")
            return None
        return s1, e1

    # Rounded box titles are drawn as images (exact font, rounded corners) and placed as overlays.
    rtitles, keep_titles = [], []
    ts = plan.get("title_style") or {}
    wdir = P(plan.get("work_dir", "work"))
    for i, t_ in enumerate(plan.get("titles") or []):
        if t_.get("box") and t_.get("rounded") and t_.get("text"):
            wdir.mkdir(parents=True, exist_ok=True)
            dest = wdir / f"{Path(plan_path).stem}-title-{i + 1:02d}.png"
            fdir = P(plan["fonts_dir"]) if plan.get("fonts_dir") else None
            made = rounded_title_png(t_, ts, fdir, dest)
            if made:
                quick = t_.get("style", "pop") == "none"
                rtitles.append({"file": str(dest), "start": t_["start"], "end": t_.get("end", float(t_["start"]) + 2),
                                "x": float(t_.get("x", 0.5)), "y": ypos(t_.get("position"), 0.16),
                                "width": made[0] / float(min(W, H)), "fade": 0 if quick else 0.08, "anim": "none"})
                continue
            print("Note: rounded titles need Pillow (python3 -m pip install --user pillow) and the font file; "
                  f"drew \"{str(t_['text'])[:30]}\" as a square box instead.")
        keep_titles.append(t_)
    if rtitles:
        plan = dict(plan, titles=keep_titles, overlays=rtitles + list(plan.get("overlays") or []))

    seek0 = max(0.0, segs[0][0] - 1.0)
    inputs = (["-ss", f"{seek0:.3f}"] if seek0 > 0 else []) + ["-i", str(src)]
    n_in = 1
    fc = []
    has_audio = info["has_audio"]

    # 1. Cut and join the kept parts.
    cat = []
    for i, (a0, b0, _) in enumerate(segs):
        a, b = a0 - seek0, b0 - seek0
        fc.append(f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]")
        cat.append(f"[v{i}]")
        if has_audio:
            d = b - a
            fd = min(0.012, d / 4)
            fc.append(f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,"
                      f"afade=t=in:d={fd:.3f},afade=t=out:st={max(0, d - fd):.3f}:d={fd:.3f}[a{i}]")
            cat.append(f"[a{i}]")
    fc.append("".join(cat) + f"concat=n={len(segs)}:v=1:a={1 if has_audio else 0}[vcat]" + ("[acat]" if has_audio else ""))

    # 1b. HDR (iPhone "HDR video" and others) looks grey and washed out unless converted to SDR.
    if info.get("hdr") and plan.get("hdr_to_sdr", True):
        if {"zscale", "tonemap"} <= filters:
            fc.append("[vcat]zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
                      "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p[vsdr]")
            vin = "vsdr"
        else:
            print("Note: this video is HDR, and this ffmpeg can't convert HDR, so colors may look washed out. "
                  "Install ffmpeg-full (Mac) or the Gyan build (Windows), or turn off HDR video in the camera settings.")
            vin = "vcat"
    else:
        vin = "vcat"

    # 2. Fit to the canvas.
    if fit == "contain":
        fc.append(f"[{vin}]fps={fps},scale={OW}:{OH}:force_original_aspect_ratio=decrease,"
                  f"pad={OW}:{OH}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1[vfit]")
    elif fit == "blur":
        fc.append(f"[{vin}]fps={fps},split=2[bg0][fg0]")
        fc.append(f"[bg0]scale={OW}:{OH}:force_original_aspect_ratio=increase,crop={OW}:{OH},gblur=sigma=30,eq=brightness=-0.08[bg1]")
        fc.append(f"[fg0]scale={OW}:{OH}:force_original_aspect_ratio=decrease[fg1]")
        fc.append("[bg1][fg1]overlay=(W-w)/2:(H-h)/2,setsar=1[vfit]")
    else:
        fc.append(f"[{vin}]fps={fps},scale={OW}:{OH}:force_original_aspect_ratio=increase,"
                  f"crop={OW}:{OH}:(iw-{OW})*{fx}:(ih-{OH})*{fy},setsar=1[vfit]")
    cur = "vfit"

    # 3. Zooms (output timeline).
    zooms = plan.get("zooms") or []
    pi = plan.get("punch_ins") or {}
    pterms = []
    pat = [float(x) for x in (pi.get("pattern") or [])]
    if pat and len(segs) > 1:
        for i, (a0, b0, off) in enumerate(segs):
            sc = pat[i % len(pat)]
            if abs(sc - 1.0) > 0.001:
                pterms.append(f"{sc - 1:.4f}*gte(it,{off:.3f})*lt(it,{off + (b0 - a0):.3f})")
    if zooms or pterms:
        pf = pi.get("focus") or {}
        terms = list(pterms)
        fxe, fye = f"{float(pf.get('x', 0.5)):.3f}", f"{float(pf.get('y', 0.42)):.3f}"
        for z in zooms:
            sp = span(z, "zoom")
            if not sp:
                continue
            a, b = sp
            s = float(z.get("scale", 1.12))
            e = float(z.get("ease", 0.0))
            if e > 0:
                env = f"clip(min(it-{a:.3f},{b:.3f}-it)/{e:.3f},0,1)"
            else:
                env = f"between(it,{a:.3f},{b:.3f})"
            terms.append(f"{s - 1:.4f}*{env}")
            zf = z.get("focus") or {}
            fxe = f"if(between(it,{a:.3f},{b:.3f}),{float(zf.get('x', 0.5)):.3f},{fxe})"
            fye = f"if(between(it,{a:.3f},{b:.3f}),{float(zf.get('y', 0.42)):.3f},{fye})"
        zexpr = "1+" + "+".join(terms or ["0"])
        fc.append(f"[{cur}]zoompan=z='{zexpr}':x='(iw-iw/zoom)*{fxe}':y='(ih-ih/zoom)*{fye}':"
                  f"d=1:s={OW}x{OH}:fps={fps}[vzoom]")
        cur = "vzoom"

    # 3b. Color: a simple grade and/or a LUT (.cube) on your footage (not on b-roll or overlays).
    gr = plan.get("grade") or {}
    if gr:
        chain = []
        if any(k in gr for k in ("contrast", "saturation", "brightness", "gamma")):
            chain.append("eq=contrast={:.3f}:saturation={:.3f}:brightness={:.3f}:gamma={:.3f}".format(
                float(gr.get("contrast", 1.0)), float(gr.get("saturation", 1.0)),
                float(gr.get("brightness", 0.0)), float(gr.get("gamma", 1.0))))
        if gr.get("temperature"):
            tv = max(-1.0, min(1.0, float(gr["temperature"]))) * 0.12
            chain.append(f"colorbalance=rs={tv:.3f}:rm={tv:.3f}:bs={-tv:.3f}:bm={-tv:.3f}")
        if gr.get("vignette"):
            chain.append(f"vignette=angle={0.3 + 0.7 * max(0.0, min(1.0, float(gr['vignette']))):.3f}")
        if gr.get("grain"):
            chain.append(f"noise=alls={int(max(0.0, min(1.0, float(gr['grain']))) * 30)}:allf=t")
        if chain:
            fc.append(f"[{cur}]" + ",".join(chain) + "[vgrade]")
            cur = "vgrade"
        if gr.get("lut"):
            lutp = P(gr["lut"])
            if not lutp.exists():
                sys.exit(f"LUT file not found: {lutp}")
            strength = max(0.0, min(1.0, float(gr.get("strength", 1.0))))
            if strength >= 0.99:
                fc.append(f"[{cur}]lut3d=file='{fesc(lutp)}'[vlut]")
            else:
                fc.append(f"[{cur}]split=2[lg0][lg1]")
                fc.append(f"[lg1]lut3d=file='{fesc(lutp)}'[lg2]")
                fc.append(f"[lg0][lg2]blend=all_mode=normal:all_opacity={strength:.3f}[vlut]")
            cur = "vlut"

    # 4. B-roll (video cut-aways) and image/video overlays.
    for k, br in enumerate(plan.get("broll") or []):
        f = P(br["file"])
        if not f.exists():
            sys.exit(f"B-roll file not found: {f}")
        sp = span(br, "b-roll clip")
        if not sp:
            continue
        a, b = sp
        ss = float(br.get("from", 0))
        inputs += ["-i", str(f)]
        idx = n_in
        n_in += 1
        mode = br.get("mode", "full")
        if mode == "pip":
            pw = even(OW * float(br.get("width", 0.42)))
            chain = f"scale={pw}:-2"
            pos = (f"x='W-w-{int(OW * 0.05)}'", f"y='{int(OH * 0.08)}'")
        else:
            chain = f"scale={OW}:{OH}:force_original_aspect_ratio=increase,crop={OW}:{OH}"
            pos = ("x=0", "y=0")
        fc.append(f"[{idx}:v]trim=start={ss:.3f}:duration={b - a:.3f},setpts=PTS-STARTPTS+{a:.3f}/TB,"
                  f"fps={fps},{chain},setsar=1[br{k}]")
        fc.append(f"[{cur}][br{k}]overlay={pos[0]}:{pos[1]}:enable='between(t,{a:.3f},{b:.3f})':eof_action=pass[vb{k}]")
        cur = f"vb{k}"

    for k, ov in enumerate(plan.get("overlays") or []):
        f = P(ov["file"])
        if not f.exists():
            sys.exit(f"Overlay file not found: {f}")
        sp = span(ov, "overlay")
        if not sp:
            continue
        a, b = sp
        is_img = f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")
        if is_img:
            inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", str(f)]
        else:
            inputs += ["-i", str(f)]
        idx = n_in
        n_in += 1
        # width is a fraction of the frame's shorter side, so a logo looks the same in 9:16 and 16:9.
        pw = even(min(OW, OH) * float(ov.get("width", 0.7)))
        fade = float(ov.get("fade", 0.2))
        shift = "" if is_img else f",setpts=PTS-STARTPTS+{a:.3f}/TB"
        fades = (f",fade=t=in:st={a:.3f}:d={fade:.3f}:alpha=1,fade=t=out:st={max(a, b - fade):.3f}:d={fade:.3f}:alpha=1"
                 if fade > 0.001 else "")
        fc.append(f"[{idx}:v]format=rgba,scale={pw}:-2{shift}{fades}[ov{k}]")
        cx, cy = float(ov.get("x", 0.5)), ypos(ov.get("y"), 0.35)
        anim = ov.get("anim", "slide-up")
        y_expr = f"{cy:.4f}*H-h/2"
        x_expr = f"{cx:.4f}*W-w/2"
        if anim == "slide-up":
            y_expr += f"+{OH * 0.04:.1f}*(1-clip((t-{a:.3f})/0.25,0,1))"
        elif anim == "slide-left":
            x_expr += f"+{OW * 0.08:.1f}*(1-clip((t-{a:.3f})/0.25,0,1))"
        x_expr = f"clip({x_expr},0,W-w)"
        y_expr = f"clip({y_expr},0,H-h)"
        fc.append(f"[{cur}][ov{k}]overlay=x='{x_expr}':y='{y_expr}':enable='between(t,{a:.3f},{b:.3f})':eof_action=pass[vo{k}]")
        cur = f"vo{k}"

    # 5. Progress bar.
    pb = plan.get("progress_bar") or {}
    if pb.get("enabled"):
        bh = even(max(4, OH * float(pb.get("height", 0.006))))
        col = (pb.get("color") or "#FFD400").lstrip("#")[:6]
        inputs += ["-f", "lavfi", "-i", f"color=c=0x{col}:s={OW}x{bh}:r={fps}:d={total:.3f}"]
        idx = n_in
        n_in += 1
        y = 0 if pb.get("position", "top") == "top" else OH - bh
        fc.append(f"[{cur}][{idx}:v]overlay=x='-W+W*t/{total:.3f}':y={y}:shortest=1[vpb]")
        cur = "vpb"

    # 6. Captions and titles.
    words = []
    cap = plan.get("captions") or {}
    if cap.get("enabled", True) and cap.get("words"):
        wdata = vtools.load_json(P(cap["words"]))
        wfile = Path(str(wdata.get("source", ""))).name
        wdur = float(wdata.get("duration") or 0)
        if wfile and (wfile != src.name or (wdur and abs(wdur - dur) > 0.5)):
            sys.exit(f"The captions file {cap['words']} was made from {wfile}, but this plan edits {src.name}. "
                     f"Transcribe {plan['input']} (for example to work/{src.stem}-words.json) and point "
                     "captions.words at that file.")
        words = apply_fixes(remap_words(wdata["words"], segs), cap.get("fix"))
        if not words:
            print("Note: the transcript has no words in the kept parts, so there are no captions.")
    elif cap.get("enabled", True) and not cap.get("words") and plan.get("captions"):
        print("Note: captions are on but captions.words isn't set, so there are no captions.")
    workdir = P(plan.get("work_dir", "work"))
    workdir.mkdir(parents=True, exist_ok=True)
    tag = Path(plan_path).stem + ("-preview" if preview else "")
    ass_path = workdir / f"{tag}-captions.ass"
    n_text = 0
    if words or plan.get("titles"):
        if not (vtools.CAPTION_FILTERS & filters):
            sys.exit("This ffmpeg can't draw captions (no libass). Install ffmpeg-full (Mac) or the Gyan build (Windows), then run again.")
        titles = []
        for t_ in plan.get("titles") or []:
            if not t_.get("text"):
                sys.exit(f"A title in the plan has no \"text\": {t_}")
            sp = span(t_, "title")
            if sp:
                titles.append(dict(t_, start=sp[0], end=sp[1]))
        n_text = write_ass(ass_path, dict(plan, titles=titles), W, H, words, total)
        fonts = plan.get("fonts_dir")
        if fonts and not P(fonts).is_dir():
            print(f"Note: fonts_dir {fonts} doesn't exist, so only installed fonts are used.")
            fonts = None
        fdir = f":fontsdir='{fesc(P(fonts))}'" if fonts else ""
        fc.append(f"[{cur}]subtitles=filename='{fesc(ass_path)}'{fdir}[vtxt]")
        cur = "vtxt"
    fc.append(f"[{cur}]format=yuv420p[vout]")

    # 7. Audio: clean up, music, loudness.
    aud = plan.get("audio") or {}
    if not has_audio and ((plan.get("sfx") or []) or (plan.get("music") or {}).get("file")):
        # No sound of its own: start from silence so music and sound effects can go on top.
        fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{total:.3f}[acat]")
        has_audio = True
        silent_src = True
    else:
        silent_src = False
    if has_audio:
        fc.append("[acat]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[ast]")
        acur = "ast"
        if aud.get("denoise"):
            fc.append(f"[{acur}]highpass=f=70,afftdn=nf=-25[aden]")
            acur = "aden"
        mus = plan.get("music") or {}
        if mus.get("file"):
            if not P(mus["file"]).exists():
                sys.exit(f"Music file not found: {P(mus['file'])}")
            inputs += ["-stream_loop", "-1", "-i", str(P(mus["file"]))]
            idx = n_in
            n_in += 1
            vol = float(mus.get("volume", 0.15))
            fc.append(f"[{idx}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,volume={vol},"
                      f"afade=t=out:st={max(0, total - 1.5):.3f}:d=1.5,aformat=sample_rates=48000:channel_layouts=stereo[mus]")
            fc.append(f"[{acur}]asplit=2[vo1][vo2]")
            if mus.get("duck", True):
                fc.append("[mus][vo2]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[mduck]")
                fc.append("[vo1][mduck]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[amix]")
            else:
                fc.append("[vo2]anullsink")
                fc.append("[vo1][mus]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[amix]")
            acur = "amix"
        sfx = plan.get("sfx") or []
        if sfx:
            sdir = P(plan.get("sfx_dir") or "assets/sfx")
            groups = {}
            for ev in sfx:
                if ev.get("file"):
                    f = P(ev["file"])
                else:
                    name = str(ev.get("name", "")).strip()
                    hits = [x for x in (sorted(sdir.glob(name + ".*")) if sdir.is_dir() and name else [])
                            if x.suffix.lower() in (".wav", ".mp3", ".m4a", ".aiff", ".aif", ".flac", ".ogg", ".caf")]
                    if not hits:
                        sys.exit(f"Sound effect \"{name}\" not found in {sdir}. Make the starter pack with "
                                 f"sfx.py --out {plan.get('sfx_dir') or 'assets/sfx'}, or use \"file\".")
                    f = hits[0]
                if not f.exists():
                    sys.exit(f"Sound effect file not found: {f}")
                if "at" not in ev:
                    sys.exit(f"A sound effect in the plan has no \"at\" time: {ev}")
                t_out = to_out(ev["at"])
                if use_src and not any(a0 <= float(ev["at"]) <= b0 for a0, b0, _ in segs):
                    print(f"Note: skipped a sound effect at {float(ev['at']):.2f}s because that part was cut.")
                    continue
                t_out = max(0.0, t_out + float(ev.get("offset", 0.0)))
                groups.setdefault(str(f), []).append((t_out, float(ev.get("volume", 0.6))))
            mix = []
            for gi, (f, evs) in enumerate(groups.items()):
                inputs += ["-i", f]
                idx = n_in
                n_in += 1
                labels = [f"sx{gi}x{k}" for k in range(len(evs))]
                head = f"[{idx}:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"
                if len(evs) > 1:
                    fc.append(head + f",asplit={len(evs)}" + "".join(f"[{l}i]" for l in labels))
                else:
                    fc.append(head + f"[{labels[0]}i]")
                for lab, (t_, vol) in zip(labels, evs):
                    ms = int(round(t_ * 1000))
                    fc.append(f"[{lab}i]volume={vol:.3f},adelay={ms}|{ms}[{lab}]")
                    mix.append(f"[{lab}]")
            if mix:
                fc.append(f"[{acur}]" + "".join(mix) +
                          f"amix=inputs={1 + len(mix)}:duration=first:dropout_transition=0:normalize=0[asfx]")
                acur = "asfx"
        if aud.get("loudnorm", True) and not (silent_src and not (plan.get("music") or {}).get("file")):
            lufs = float(aud.get("target_lufs", -14))
            fc.append(f"[{acur}]loudnorm=I={lufs}:TP=-1.5:LRA=11,aresample=48000,"
                      "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[aout]")
        else:
            fc.append(f"[{acur}]aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[aout]")
    elif (plan.get("music") or {}).get("file"):
        # A silent video with music: the music becomes the soundtrack.
        mus = plan["music"]
        mf = P(mus["file"])
        if not mf.exists():
            sys.exit(f"Music file not found: {mf}")
        inputs += ["-stream_loop", "-1", "-i", str(mf)]
        idx = n_in
        n_in += 1
        fc.append(f"[{idx}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,volume={float(mus.get('volume', 0.5))},"
                  f"afade=t=out:st={max(0, total - 1.5):.3f}:d=1.5,"
                  "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[aout]")
        has_audio = True

    out = P(plan.get("output", "exports/edit.mp4"))
    if preview:
        stem = out.stem[:-6] if out.stem.endswith("-final") else out.stem
        out = out.with_name(stem + "-preview" + out.suffix)
    out.parent.mkdir(parents=True, exist_ok=True)
    script = workdir / f"{tag}-filter.txt"
    script.write_text(";\n".join(fc), encoding="utf-8")

    enc = vtools.encoders_of(ffmpeg)
    vb = str(plan.get("video_bitrate") or "").upper().rstrip("BPS").strip()
    if "libx264" in enc:
        venc = ["-c:v", "libx264", "-preset", "veryfast" if preview else "medium",
                "-crf", "28" if preview else str(plan.get("crf", 20))]
        if not preview:
            if vb:
                mbps = float(vb.rstrip("M")) if vb.endswith("M") else float(vb) / 1e6
                venc = ["-c:v", "libx264", "-preset", "medium", "-b:v", f"{mbps:.1f}M",
                        "-maxrate", f"{mbps * 1.5:.1f}M", "-bufsize", f"{mbps * 2:.1f}M"]
            else:
                venc += ["-maxrate", "16M", "-bufsize", "32M"]
    elif "h264_videotoolbox" in enc:
        venc = ["-c:v", "h264_videotoolbox", "-b:v", "3M" if preview else "12M"]
    else:
        venc = ["-c:v", "mpeg4", "-q:v", "3"]
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error"] + inputs + [
        "-filter_complex_script", str(script), "-map", "[vout]"]
    if has_audio:
        cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
    cmd += venc + ["-r", str(fps), "-t", f"{total:.3f}", "-movflags", "+faststart", str(out)]

    t0 = time.time()
    vtools.run(cmd)
    if has_audio and not preview and aud.get("loudnorm", True):
        fix_loudness(ffmpeg, out, float(aud.get("target_lufs", -14)))
    took = time.time() - t0
    if words and not preview and plan.get("srt", True):
        n_srt = write_srt(out.with_suffix(".srt"), words, cap, total)
        print(f"Captions file: {out.with_suffix('.srt')} ({n_srt} lines)")
    size = out.stat().st_size / 1e6
    for note in safe_zone_notes(plan, W, H):
        print("Note: " + note)
    print(f"{'Preview' if preview else 'Final'} saved: {out}")
    print(f"  {OW}x{OH}, {vtools.hms(total)} long (from {vtools.hms(dur)}), {len(segs) - 1} cuts, "
          f"{len(zooms)} zooms, {n_text} caption/title events, {size:.1f} MB, rendered in {took:.0f}s")
    return out


def safe_zone_notes(plan, W, H):
    """Vertical videos: the app's own buttons and caption cover the bottom ~20%, the right edge
    from about the middle down, and a strip at the top. Warn when text sits there."""
    notes = []
    if H <= W:
        return notes
    cap = plan.get("captions") or {}
    if cap.get("enabled", True) and cap.get("words"):
        y = ypos(cap.get("position"), 0.70)
        if y > 0.82:
            notes.append(f"captions sit at {y:.2f} of the height, where the app's own caption and buttons can cover "
                         "them (bottom ~20%). 0.62 to 0.8 is safe. Keep it if it matches their references on purpose.")
        if y < 0.12:
            notes.append("captions sit in the top strip that the app's header covers. Move them below 0.15.")
    for t in plan.get("titles") or []:
        y = ypos(t.get("position"), 0.16)
        if y > 0.82 or y < 0.1:
            notes.append(f"the title \"{str(t.get('text'))[:30]}\" sits at {y:.2f} of the height, where the app's "
                         "own text and buttons go. Keep titles between 0.12 and 0.78.")
    for ov in plan.get("overlays") or []:
        x, y = float(ov.get("x", 0.5)), ypos(ov.get("y"), 0.35)
        if x > 0.86 and 0.45 < y < 0.9:
            notes.append(f"the overlay {Path(str(ov.get('file'))).name} is under the like/comment/share buttons "
                         "(right edge, lower half).")
    return notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--preview", action="store_true", help="Half-size fast draft")
    a = ap.parse_args()
    build(a.plan, a.preview)


if __name__ == "__main__":
    main()
