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
        mid = (w["start"] + w["end"]) / 2
        for a, b, off in segs:
            if a <= mid <= b:
                s = max(a, w["start"]) - a + off
                e = min(b, w["end"]) - a + off
                if e > s:
                    out.append({"text": w["text"], "start": s, "end": e})
                break
    return out


def clean_word(text, cfg):
    t = text.strip()
    for wrong, right in (cfg.get("fix") or {}).items():
        t = re.sub(r"(?i)\b" + re.escape(wrong) + r"\b", right, t)
    if not cfg.get("punctuation", False):
        t = re.sub(r"[,.;:]+$", "", t)
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

    hl = ass_color(cfg.get("highlight", "#FFD400"))
    base = ass_color(cfg.get("color", "#FFFFFF"))
    y = ypos(cfg.get("position"), 0.70 if H > W else 0.84) * H
    pop = cfg.get("animation", "pop") == "pop"
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
                if cfg.get("highlight") is not False and k == j:
                    parts.append("{\\c" + hl + "}" + t + "{\\c" + base + "}")
                else:
                    parts.append(t)
            anim = "\\fscx85\\fscy85\\t(0,90,\\fscx100\\fscy100)" if (pop and j == 0) else ""
            tag = "{\\an5\\pos(%d,%d)%s}" % (W // 2, int(y), anim)
            events.append(("Caption", s, e, tag + " ".join(parts)))
    return events


def title_events(titles, W, H):
    events = []
    for t in titles or []:
        s, e = float(t["start"]), float(t["end"])
        y = ypos(t.get("position"), 0.16) * H
        x = W * float(t.get("x", 0.5))
        style = t.get("style", "pop")
        style_name = "TitleBox" if t.get("box") else "Title"
        if style == "slide":
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
            extra += "\\c" + ass_color(t["color"])
        if t.get("size"):
            extra += "\\fs%d" % int(t["size"])
        text = t["text"].upper() if t.get("uppercase") else t["text"]
        events.append((style_name, s, e, "{\\an5%s%s%s}%s" % (pos, anim, extra, ass_text(text))))
    return events


def write_ass(path, plan, W, H, words, total):
    cap = plan.get("captions") or {}
    tdef = plan.get("title_style") or {}
    font = cap.get("font", "Arial Black")
    size = int(cap.get("size", 84 if H > W else 64))
    outline = int(cap.get("outline", 6))
    tfont = tdef.get("font", font)
    tsize = int(tdef.get("size", 96 if H > W else 80))
    box = ass_color(tdef.get("box", "#000000CC"))
    margin = int(W * 0.08)
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}",
        "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Caption,{font},{size},{ass_color(cap.get('color', '#FFFFFF'))},&H000000FF,{ass_color(cap.get('outline_color', '#000000'))},&H96000000,-1,0,0,0,100,100,0,0,1,{outline},2,5,{margin},{margin},0,1",
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


def fesc(path):
    """Escape a path for use inside an ffmpeg filter argument."""
    p = str(path).replace("\\", "/")
    return p.replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")


def build(plan_path, preview):
    plan = vtools.load_json(plan_path)
    root = Path(plan_path).resolve().parent
    base_dir = root.parent if root.name == "work" else root

    def P(p):
        q = Path(p)
        return q if q.is_absolute() else (base_dir / q)

    ffmpeg, ffprobe, filters = vtools.need_ffmpeg()
    src = P(plan["input"])
    if not src.exists():
        sys.exit(f"Input video not found: {src}")
    info = vtools.probe(src, ffprobe)
    dur = info["duration"]

    canvas = plan.get("canvas") or {}
    W = int(canvas.get("width", 1080))
    H = int(canvas.get("height", 1920))
    fps = float(canvas.get("fps", 30))
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

    inputs = ["-i", str(src)]
    n_in = 1
    fc = []
    has_audio = info["has_audio"]

    # 1. Cut and join the kept parts.
    cat = []
    for i, (a, b, _) in enumerate(segs):
        fc.append(f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]")
        cat.append(f"[v{i}]")
        if has_audio:
            d = b - a
            fd = min(0.012, d / 4)
            fc.append(f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,"
                      f"afade=t=in:d={fd:.3f},afade=t=out:st={max(0, d - fd):.3f}:d={fd:.3f}[a{i}]")
            cat.append(f"[a{i}]")
    fc.append("".join(cat) + f"concat=n={len(segs)}:v=1:a={1 if has_audio else 0}[vcat]" + ("[acat]" if has_audio else ""))

    # 2. Fit to the canvas.
    if fit == "contain":
        fc.append(f"[vcat]fps={fps},scale={OW}:{OH}:force_original_aspect_ratio=decrease,"
                  f"pad={OW}:{OH}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1[vfit]")
    elif fit == "blur":
        fc.append(f"[vcat]fps={fps},split=2[bg0][fg0]")
        fc.append(f"[bg0]scale={OW}:{OH}:force_original_aspect_ratio=increase,crop={OW}:{OH},gblur=sigma=30,eq=brightness=-0.08[bg1]")
        fc.append(f"[fg0]scale={OW}:{OH}:force_original_aspect_ratio=decrease[fg1]")
        fc.append("[bg1][fg1]overlay=(W-w)/2:(H-h)/2,setsar=1[vfit]")
    else:
        fc.append(f"[vcat]fps={fps},scale={OW}:{OH}:force_original_aspect_ratio=increase,"
                  f"crop={OW}:{OH}:(iw-{OW})*{fx}:(ih-{OH})*{fy},setsar=1[vfit]")
    cur = "vfit"

    # 3. Zooms (output timeline).
    zooms = plan.get("zooms") or []
    if zooms:
        terms, fxe, fye = [], "0.5", "0.42"
        for z in zooms:
            a, b, s = float(z["start"]), float(z["end"]), float(z.get("scale", 1.12))
            e = float(z.get("ease", 0.0))
            if e > 0:
                env = f"clip(min(it-{a:.3f},{b:.3f}-it)/{e:.3f},0,1)"
            else:
                env = f"between(it,{a:.3f},{b:.3f})"
            terms.append(f"{s - 1:.4f}*{env}")
            zf = z.get("focus") or {}
            fxe = f"if(between(it,{a:.3f},{b:.3f}),{float(zf.get('x', 0.5)):.3f},{fxe})"
            fye = f"if(between(it,{a:.3f},{b:.3f}),{float(zf.get('y', 0.42)):.3f},{fye})"
        zexpr = "1+" + "+".join(terms)
        fc.append(f"[{cur}]zoompan=z='{zexpr}':x='(iw-iw/zoom)*{fxe}':y='(ih-ih/zoom)*{fye}':"
                  f"d=1:s={OW}x{OH}:fps={fps}[vzoom]")
        cur = "vzoom"

    # 4. B-roll (video cut-aways) and image/video overlays.
    for k, br in enumerate(plan.get("broll") or []):
        f = P(br["file"])
        a, b = float(br["start"]), float(br["end"])
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
        a, b = float(ov["start"]), float(ov["end"])
        is_img = f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")
        if is_img:
            inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", str(f)]
        else:
            inputs += ["-i", str(f)]
        idx = n_in
        n_in += 1
        pw = even(OW * float(ov.get("width", 0.7)))
        fade = float(ov.get("fade", 0.2))
        shift = "" if is_img else f",setpts=PTS-STARTPTS+{a:.3f}/TB"
        fc.append(f"[{idx}:v]format=rgba,scale={pw}:-2{shift},"
                  f"fade=t=in:st={a:.3f}:d={fade:.3f}:alpha=1,fade=t=out:st={max(a, b - fade):.3f}:d={fade:.3f}:alpha=1[ov{k}]")
        cx, cy = float(ov.get("x", 0.5)), ypos(ov.get("y"), 0.35)
        anim = ov.get("anim", "slide-up")
        y_expr = f"{cy:.4f}*H-h/2"
        x_expr = f"{cx:.4f}*W-w/2"
        if anim == "slide-up":
            y_expr += f"+{OH * 0.04:.1f}*(1-clip((t-{a:.3f})/0.25,0,1))"
        elif anim == "slide-left":
            x_expr += f"+{OW * 0.08:.1f}*(1-clip((t-{a:.3f})/0.25,0,1))"
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
        wsrc = vtools.load_json(P(cap["words"]))["words"]
        words = remap_words(wsrc, segs)
    workdir = P(plan.get("work_dir", "work"))
    workdir.mkdir(parents=True, exist_ok=True)
    ass_path = workdir / ("captions-preview.ass" if preview else "captions.ass")
    n_text = 0
    if words or plan.get("titles"):
        if not (vtools.CAPTION_FILTERS & filters):
            sys.exit("This ffmpeg can't draw captions (no libass). Install ffmpeg-full (Mac) or the Gyan build (Windows), then run again.")
        n_text = write_ass(ass_path, plan, W, H, words, total)
        fonts = plan.get("fonts_dir")
        fdir = f":fontsdir='{fesc(P(fonts))}'" if fonts else ""
        fc.append(f"[{cur}]subtitles=filename='{fesc(ass_path)}'{fdir}[vtxt]")
        cur = "vtxt"
    fc.append(f"[{cur}]format=yuv420p[vout]")

    # 7. Audio: clean up, music, loudness.
    aud = plan.get("audio") or {}
    if has_audio:
        fc.append("[acat]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[ast]")
        acur = "ast"
        if aud.get("denoise"):
            fc.append(f"[{acur}]highpass=f=70,afftdn=nf=-25[aden]")
            acur = "aden"
        mus = plan.get("music") or {}
        if mus.get("file"):
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
        if aud.get("loudnorm", True):
            lufs = float(aud.get("target_lufs", -14))
            fc.append(f"[{acur}]loudnorm=I={lufs}:TP=-1.5:LRA=11,aresample=48000,"
                      "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[aout]")
        else:
            fc.append(f"[{acur}]aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[aout]")

    out = P(plan.get("output", "exports/edit.mp4"))
    if preview:
        out = out.with_name(out.stem + "-preview" + out.suffix)
    out.parent.mkdir(parents=True, exist_ok=True)
    script = workdir / ("filter-preview.txt" if preview else "filter.txt")
    script.write_text(";\n".join(fc), encoding="utf-8")

    enc = vtools.encoders_of(ffmpeg)
    if "libx264" in enc:
        venc = ["-c:v", "libx264", "-preset", "veryfast" if preview else "medium",
                "-crf", "28" if preview else str(plan.get("crf", 18))]
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
    took = time.time() - t0
    size = out.stat().st_size / 1e6
    print(f"{'Preview' if preview else 'Final'} saved: {out}")
    print(f"  {OW}x{OH}, {vtools.hms(total)} long (from {vtools.hms(dur)}), {len(segs) - 1} cuts, "
          f"{len(zooms)} zooms, {n_text} caption/title events, {size:.1f} MB, rendered in {took:.0f}s")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--preview", action="store_true", help="Half-size fast draft")
    a = ap.parse_args()
    build(a.plan, a.preview)


if __name__ == "__main__":
    main()
