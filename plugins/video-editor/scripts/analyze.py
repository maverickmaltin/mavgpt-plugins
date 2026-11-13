#!/usr/bin/env python3
"""Break a finished video down frame by frame so its editing style can be studied.

Usage:
    python3 analyze.py VIDEO --out style-lab/NAME/analysis/VIDEO-NAME
        [--detail light|normal|deep] [--no-transcribe] [--language en] [--max-seconds 180]

Writes into --out:
    summary.md          read this first: the numbers, the hook, and every shot with what's said
    analysis.json       the same numbers for scripts
    sheets/hook-NN.jpg  the first seconds, frame by frame (the hook)
    sheets/shots-NN.jpg the first frame of every shot, numbered, with its time
    sheets/all-NN.jpg   the whole video every half second (light: every second)
    frames/full-*.jpg   a few full-size frames, for reading caption fonts and sizes exactly
    words.json, transcript.txt   what's said, word by word (if there's speech)

It measures: length, size, frame rate, every cut and shot length, cuts in the first seconds,
words per minute, how tight the pauses between sentences are, loudness, whether there's a
steady sound under the voice (music), and likely sound effects (and how many land on cuts).
What's ON screen (captions, text, zooms, b-roll, colors) you read from the sheets.
"""
import argparse
import importlib.util
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402

DETAIL = {
    "light": {"all_fps": 1.0, "hook_fps": 6, "hook_s": 2.0, "full": 3},
    "normal": {"all_fps": 2.0, "hook_fps": 8, "hook_s": 3.0, "full": 4},
    "deep": {"all_fps": 4.0, "hook_fps": 12, "hook_s": 4.0, "full": 6},
}


def font_file():
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf",
              "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"):
        if os.path.isfile(f):
            return f
    return None


def esc(p):
    return str(p).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def label_filter(text_expr, size):
    f = font_file()
    ff = f"fontfile='{esc(f)}':" if f else ""
    return (f"drawtext={ff}text='{text_expr}':x=8:y=8:fontsize={size}:fontcolor=white:"
            f"box=1:boxcolor=black@0.65:boxborderw=6")


def run_ff(cmd, allow_fail=False):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0 and not allow_fail:
        tail = "\n".join(p.stderr.strip().splitlines()[-8:])
        raise RuntimeError(tail)
    return p


def tile_geom(w, h):
    """Columns, rows and tile width for contact sheets."""
    if h >= w:  # vertical or square
        return 4, 3, 240
    return 3, 4, 360


def make_proxy(ffmpeg, video, dest, W, H, max_s):
    """A small copy of the picture (540p, same frame rate, a keyframe every 15 frames) so every
    pass after this one is fast. The original is still used for the full-size frames."""
    scale = "scale=-2:960" if H >= W else "scale=960:-2"
    base = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error"]
    tail = (["-t", str(max_s)] if max_s else []) + ["-an", "-vf", scale + ",format=yuv420p", "-c:v", "libx264",
            "-preset", "ultrafast", "-crf", "20", "-g", "15", str(dest)]
    for hw in (["-hwaccel", "auto"], []):
        p = subprocess.run(base + hw + ["-i", str(video)] + tail, capture_output=True, text=True)
        if p.returncode == 0 and dest.exists() and dest.stat().st_size > 1000:
            return dest
    return None


def scene_scores(ffmpeg, video, max_s):
    """Per-frame scene-change score (0..1) for every frame."""
    base = [ffmpeg, "-hide_banner", "-nostats"]
    tail = (["-t", str(max_s)] if max_s else []) + ["-an", "-vf",
            "scale=128:-2,select='gte(scene,0)',metadata=mode=print:file=-", "-f", "null", "-"]
    for hw in (["-hwaccel", "auto"], []):
        p = subprocess.run(base + hw + ["-i", str(video)] + tail, capture_output=True, text=True)
        if p.returncode == 0 and "scene_score" in p.stdout:
            break
    times, scores = [], []
    t = None
    for line in p.stdout.splitlines():
        if line.startswith("frame:"):
            m = re.search(r"pts_time:([\d.]+)", line)
            t = float(m.group(1)) if m else None
        elif "scene_score=" in line and t is not None:
            times.append(t)
            scores.append(float(line.split("=")[1]))
    return times, scores


def find_cuts(times, scores, fps):
    """Hard cuts = spikes that stand far above the frames around them. Also returns softer
    changes (a zoom step, a pop-in, a big text change) for a person to look at."""
    cuts, soft = [], []
    n = len(scores)
    win = max(4, int(fps * 0.5))
    min_gap = max(0.15, 6.0 / max(fps, 1))
    for i in range(1, n):
        s = scores[i]
        if s < 0.012:
            continue
        lo, hi = max(0, i - win), min(n, i + win + 1)
        around = sorted(scores[lo:i] + scores[i + 1:hi])
        med = around[len(around) // 2] if around else 0.0
        ratio = s / (med + 0.004)
        if (s >= 0.30) or (s >= 0.05 and ratio >= 5.0) or (s >= 0.035 and ratio >= 9.0):
            if not cuts or times[i] - cuts[-1][0] >= min_gap:
                cuts.append((times[i], s))
            elif s > cuts[-1][1]:
                cuts[-1] = (times[i], s)
        elif s >= 0.02 and ratio >= 4.0:
            soft.append((times[i], s))
    soft = [x for x in soft if all(abs(x[0] - c[0]) > 0.2 for c in cuts)]
    return cuts, soft


def ebur128(ffmpeg, video, max_s):
    cmd = [ffmpeg, "-hide_banner", "-nostats"] + (["-t", str(max_s)] if max_s else []) + [
        "-i", str(video), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = {}
    m = re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", p.stderr, re.M)
    if m:
        out["lufs"] = float(m[-1])
    m = re.findall(r"^\s+LRA:\s+(-?[\d.]+) LU", p.stderr, re.M)
    if m:
        out["lra"] = float(m[-1])
    m = re.findall(r"^\s+Peak:\s+(-?[\d.inf]+) dBFS", p.stderr, re.M)
    if m:
        try:
            out["true_peak"] = float(m[-1])
        except ValueError:
            pass
    return out


def contact_sheets(ffmpeg, video, out_dir, prefix, fps, cols, rows, tw, start=0.0, dur=None, labels=True):
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = out_dir / f"{prefix}-%02d.jpg"
    for old in out_dir.glob(f"{prefix}-*.jpg"):
        old.unlink()
    vf = f"fps={fps},scale={tw}:-2"
    if labels:
        vf += "," + label_filter("%{pts\\:hms}", 18 if tw <= 260 else 20)
    vf += f",tile={cols}x{rows}:padding=4:margin=4:color=0x222222"
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error"]
    if start:
        cmd += ["-ss", f"{start:.3f}"]
    cmd += ["-i", str(video)]
    if dur:
        cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-an", "-vf", vf, "-q:v", "4", str(pattern)]
    p = run_ff(cmd, allow_fail=True)
    if p.returncode != 0 and labels:
        return contact_sheets(ffmpeg, video, out_dir, prefix, fps, cols, rows, tw, start, dur, labels=False)
    return sorted(out_dir.glob(f"{prefix}-*.jpg")), labels


def shot_sheets(ffmpeg, video, out_dir, shots, cols, rows, tw, fps):
    tmp = Path(tempfile.mkdtemp(prefix="shots-"))
    try:
        labels_ok = True
        for i, sh in enumerate(shots, 1):
            t = min(sh["start"] + 2.5 / max(fps, 1), max(sh["start"], sh["end"] - 0.02))
            dest = tmp / f"s{i:04d}.jpg"
            vf = f"scale={tw}:-2"
            if labels_ok:
                vf += "," + label_filter(f"{i}  {vtools.hms(sh['start'])}".replace(":", "\\:"), 20)
            cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video),
                   "-frames:v", "1", "-an", "-vf", vf, "-q:v", "4", str(dest)]
            p = run_ff(cmd, allow_fail=True)
            if p.returncode != 0 and labels_ok:
                labels_ok = False
                cmd = [c for c in cmd]
                cmd[cmd.index("-vf") + 1] = f"scale={tw}:-2"
                run_ff(cmd, allow_fail=True)
        for old in out_dir.glob("shots-*.jpg"):
            old.unlink()
        if not list(tmp.glob("s*.jpg")):
            return []
        cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-framerate", "1", "-i", str(tmp / "s%04d.jpg"),
               "-vf", f"tile={cols}x{rows}:padding=4:margin=4:color=0x222222", "-q:v", "4",
               str(out_dir / "shots-%02d.jpg")]
        run_ff(cmd, allow_fail=True)
        return sorted(out_dir.glob("shots-*.jpg"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def full_frames(ffmpeg, video, out_dir, times):
    out_dir.mkdir(parents=True, exist_ok=True)
    made = []
    for t in times:
        dest = out_dir / f"full-{t:06.2f}s.jpg"
        p = run_ff([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video),
                    "-frames:v", "1", "-an", "-vf", "scale='min(1080,iw)':-2", "-q:v", "3", str(dest)],
                   allow_fail=True)
        if p.returncode == 0 and dest.exists():
            made.append(dest)
    return made


def transcribe(video, out_dir, language, model, vocab=""):
    if not (importlib.util.find_spec("faster_whisper") or importlib.util.find_spec("whisper")):
        return None, "transcription not installed (faster-whisper), so no speech stats"
    out = out_dir / "words.json"
    cmd = [sys.executable, str(Path(__file__).with_name("transcribe.py")), str(video), "--out", str(out)]
    if language:
        cmd += ["--language", language]
    if vocab:
        cmd += ["--vocab", vocab]
    if model:
        if language == "en" and model in ("tiny", "base", "small", "medium"):
            model += ".en"
        cmd += ["--model", model]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0 or not out.exists():
        return None, "transcription failed: " + " ".join(p.stderr.strip().splitlines()[-2:])
    tx = out_dir / "words-transcript.txt"
    if tx.exists():
        tx.replace(out_dir / "transcript.txt")
    return json.loads(out.read_text(encoding="utf-8")), None


def audio_stats(video, ffmpeg, words, cuts, dur):
    try:
        import gaps as G
    except Exception:
        return {}
    if G.np is None:
        return {"note": "numpy missing, so no pause or sound-effect measurement"}
    np = G.np
    lvl = G.audio_levels(video, ffmpeg)
    tr = G.Track(lvl)
    st = {"room_db": round(tr.floor, 1)}
    if words is None:
        st["bed"] = "not measured (no transcript, so pauses, music and sound effects weren't measured)"
        return st
    speech = [w for w in (words or []) if w.get("text", "").strip()]
    if len(speech) >= 2:
        res = G.boundary_gaps(tr, speech)
        summ = G.summarize(res)
        st["pauses"] = summ
        st["pauses_feel"] = G.describe(summ)
        # Music bed or not: look only at real pauses (120 ms or more of measured silence). In a
        # tightly cut video there may be none, and then the audio can't tell us: ask instead.
        voice = [tr.peak(w["start"], max(w["start"] + 0.03, w["end"])) for w in speech]
        vmed = float(np.median(voice))
        st["voice_db"] = round(vmed, 1)
        real = [r["min_db"] for r in res if r.get("ms", 0) >= 120 and "min_db" in r]
        if len(real) >= 5:
            bed = float(np.median(real))
            under = vmed - bed
            st["between_words_db"] = round(bed, 1)
            if under < 26:
                st["bed"] = (f"steady sound in the pauses about {under:.0f} dB under the voice: "
                             "probably a music bed (or a noisy room). Confirm with the creator")
            else:
                st["bed"] = f"quiet in the pauses (about {under:.0f} dB under the voice): no music bed under the talking"
        else:
            st["bed"] = ("can't tell from the audio (the cuts leave almost no pauses to listen in). "
                         "Ask whether there's music")
    elif dur > 0:
        st["bed"] = "no speech found: music, sound effects or silence only"
    # Possible sound effects: sudden jumps well away from any word starting.
    jumps = []
    look = int(0.03 * tr.fr)
    near_word = np.zeros(tr.n, dtype=bool)
    for w in speech:
        a_, b_ = tr.k(w["start"] - 0.12), tr.k(w["start"] + 0.15)
        near_word[a_:b_ + 1] = True
    rise = np.zeros(tr.n, dtype=bool)
    if tr.n > look:
        rise[look:] = (lvl[look:] - lvl[:-look] >= 18) & (lvl[look:] > tr.floor + 20)
    for k in np.nonzero(rise & ~near_word)[0]:
        t = tr.t(int(k))
        if jumps and t - jumps[-1] < 0.25:
            continue
        jumps.append(t)
    on_cuts = sum(1 for t in jumps if any(abs(t - c) <= 0.1 for c in cuts))
    st["likely_sfx"] = {"count": len(jumps), "on_cuts": on_cuts, "times": [round(t, 2) for t in jumps[:80]]}
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--detail", default="normal", choices=list(DETAIL))
    ap.add_argument("--no-transcribe", action="store_true")
    ap.add_argument("--language", default=None)
    ap.add_argument("--vocab", default="", help="Names and words to spell right, comma separated (Claude, Cowork...)")
    ap.add_argument("--model", default="base",
                    help="Whisper model: base (default, fast, fine for timing) or small (more accurate words)")
    ap.add_argument("--max-seconds", type=float, default=0,
                    help="Only analyze the first N seconds (long videos). 0 = whole video")
    a = ap.parse_args()

    ffmpeg, ffprobe, _ = vtools.need_ffmpeg()
    video = Path(a.video)
    info = vtools.probe(video, ffprobe)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    d = DETAIL[a.detail]
    full_dur = info["duration"]
    max_s = a.max_seconds or (0 if full_dur <= 240 else 180)
    dur = min(full_dur, max_s) if max_s else full_dur
    fps = info["fps"]
    W, H = info["width"], info["height"]
    cols, rows, tw = tile_geom(W, H)
    print(f"Analyzing {video.name}: {vtools.hms(full_dur)}, {W}x{H}, {fps:.2f} fps"
          + (f" (first {vtools.hms(dur)} only)" if dur < full_dur else ""))

    # Extra stream facts (HDR, codec, bitrate).
    p = run_ff([ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries",
                "stream=codec_name,pix_fmt,color_transfer,bit_rate", "-show_entries", "format=bit_rate",
                "-of", "json", str(video)], allow_fail=True)
    extra = {}
    try:
        j = json.loads(p.stdout or "{}")
        s0 = (j.get("streams") or [{}])[0]
        extra = {"codec": s0.get("codec_name"), "pix_fmt": s0.get("pix_fmt"),
                 "hdr": s0.get("color_transfer") in ("arib-std-b67", "smpte2084"),
                 "bitrate_mbps": round(float((j.get("format") or {}).get("bit_rate") or 0) / 1e6, 1)}
    except Exception:
        pass

    print("  1/5 finding every cut...")
    proxy = make_proxy(ffmpeg, video, out / ".proxy.mp4", W, H, max_s)
    vis = proxy or video
    times, scores = scene_scores(ffmpeg, vis, 0 if proxy else max_s)
    cuts, soft = find_cuts(times, scores, fps)
    cut_times = [c[0] for c in cuts]
    bounds = [0.0] + cut_times + [dur]
    shots = [{"n": i + 1, "start": round(bounds[i], 3), "end": round(bounds[i + 1], 3),
              "length": round(bounds[i + 1] - bounds[i], 3)} for i in range(len(bounds) - 1)
             if bounds[i + 1] - bounds[i] > 0.01]
    lengths = [s["length"] for s in shots]

    print("  2/5 making contact sheets...")
    sheets_dir = out / "sheets"
    hook_s = min(d["hook_s"], dur)
    hook, labels = contact_sheets(ffmpeg, vis, sheets_dir, "hook", d["hook_fps"], cols, rows, tw, 0.0, hook_s)
    all_fps = d["all_fps"]
    if dur > 120:
        all_fps = min(all_fps, 1.0)
    if dur > 300:
        all_fps = 0.5
    allsheets, _ = contact_sheets(ffmpeg, vis, sheets_dir, "all", all_fps, cols, rows, tw, 0.0, dur if max_s else None)
    shotsheets = shot_sheets(ffmpeg, vis, sheets_dir, shots, cols, rows, tw, fps)
    ft = sorted(set([min(1.0, dur / 2)] + [round(dur * f, 2) for f in
                                           ([0.25, 0.5, 0.75] if d["full"] <= 4 else [0.15, 0.3, 0.45, 0.6, 0.75, 0.9])]))
    fulls = full_frames(ffmpeg, video, out / "frames", ft[: d["full"]])

    words = None
    note = None
    if info["has_audio"] and not a.no_transcribe:
        print("  3/5 transcribing (on this computer)...")
        wd, note = transcribe(video, out, a.language, a.model, a.vocab)
        if wd:
            words = [w for w in wd["words"] if w["start"] < dur]
    else:
        note = "no audio" if not info["has_audio"] else "transcription skipped"

    print("  4/5 measuring sound...")
    loud = ebur128(ffmpeg, video, max_s) if info["has_audio"] else {}
    snd = audio_stats(video, ffmpeg, words, cut_times, dur) if info["has_audio"] else {}

    if proxy and proxy.exists():
        proxy.unlink()
    print("  5/5 writing the summary...")
    speech = [w for w in (words or []) if w.get("text", "").strip()]
    wpm = None
    if speech:
        talk = max(1.0, speech[-1]["end"] - speech[0]["start"])
        wpm = round(len(speech) / talk * 60)
    hook_line, hook_end = "", None
    abbrev = {"mr.", "mrs.", "ms.", "dr.", "st.", "vs.", "jr.", "sr.", "no.", "u.s.", "etc."}
    for w in speech:
        hook_line += w["text"] + " "
        t_ = w["text"].strip()
        ends = re.search(r"[.?!]$", t_) and t_.lower() not in abbrev and len(hook_line.split()) >= 3
        if ends or len(hook_line.split()) >= 22:
            hook_end = w["end"]
            break
    for sh in shots:
        said = [w["text"] for w in speech if sh["start"] <= (w["start"] + w["end"]) / 2 < sh["end"]]
        sh["said"] = " ".join(said)

    def cuts_before(t):
        return sum(1 for c in cut_times if c < t)

    stats = {
        "file": video.name, "duration": round(full_dur, 3), "analyzed_seconds": round(dur, 3),
        "width": W, "height": H, "aspect": f"{W}:{H}", "fps": round(fps, 3), **extra,
        "shots": len(shots), "cuts": len(cut_times),
        "cut_every_s": round(dur / max(1, len(shots)), 2),
        "shot_length": {"median": round(statistics.median(lengths), 2) if lengths else None,
                        "min": round(min(lengths), 2) if lengths else None,
                        "max": round(max(lengths), 2) if lengths else None},
        "first_cut_s": round(cut_times[0], 2) if cut_times else None,
        "cuts_first_3s": cuts_before(3.0), "cuts_first_5s": cuts_before(5.0),
        "cuts_per_10s": round(len(cut_times) / max(dur, 0.1) * 10, 2),
        "words": len(speech), "wpm": wpm, "hook": hook_line.strip(), "hook_ends_s": round(hook_end, 2) if hook_end else None,
        "loudness": loud, "sound": snd, "transcript_note": note,
        "soft_changes": [{"t": round(t, 2), "score": round(s, 3)} for t, s in soft[:120]],
        "cut_list": [{"t": round(t, 3), "score": round(s, 3)} for t, s in cuts],
        "shots_detail": shots,
        "files": {"hook": [str(p.relative_to(out)) for p in hook], "shots": [str(p.relative_to(out)) for p in shotsheets],
                  "all": [str(p.relative_to(out)) for p in allsheets], "full": [str(p.relative_to(out)) for p in fulls]},
        "sheet_labels": labels,
    }
    vtools.write_json(out / "analysis.json", stats)

    L = []
    L.append(f"# Analysis: {video.name}")
    L.append("")
    L.append(f"{vtools.hms(full_dur)} long, {W}x{H}, {fps:.0f} fps" + (", HDR" if extra.get("hdr") else "")
             + (f". Only the first {vtools.hms(dur)} were analyzed." if dur < full_dur else "."))
    L.append("Measured by analyze.py. What's on screen (captions, text, zooms, b-roll, colors) is in the sheets.")
    L.append("")
    L.append("## At a glance")
    L.append("")
    L.append("| What | Measured |")
    L.append("| --- | --- |")
    L.append(f"| Shots | {len(shots)} (a cut every {stats['cut_every_s']} s on average; median shot {stats['shot_length']['median']} s, "
             f"shortest {stats['shot_length']['min']} s, longest {stats['shot_length']['max']} s) |")
    L.append(f"| First cut | {vtools.hms(cut_times[0]) if cut_times else 'none'} |")
    L.append(f"| Cuts in the first 3 s / 5 s | {stats['cuts_first_3s']} / {stats['cuts_first_5s']} |")
    if speech:
        L.append(f"| Talking speed | {wpm} words a minute |")
        L.append(f"| Hook (first sentence) | \"{stats['hook']}\" (ends {vtools.hms(hook_end) if hook_end else '?'}) |")
    if snd.get("pauses_feel"):
        L.append(f"| Silence between sentences | {snd['pauses_feel']} |")
    if snd.get("bed"):
        L.append(f"| Sound under the voice | {snd['bed']} |")
    if snd.get("likely_sfx"):
        L.append(f"| Possible sound effects | {snd['likely_sfx']['count']} sudden sounds away from any word "
                 f"({snd['likely_sfx']['on_cuts']} near cuts). A hint only: confirm with the creator |")
    if loud.get("lufs") is not None:
        L.append(f"| Loudness | {loud['lufs']} LUFS integrated, true peak {loud.get('true_peak', '?')} dBFS |")
    if note:
        L.append(f"| Note | {note} |")
    L.append("")
    L.append("## Look at these (in this order)")
    L.append("")
    L.append(f"1. The hook, frame by frame ({d['hook_fps']} frames a second, first {hook_s:.0f} s): "
             + ", ".join(f"`{p.relative_to(out)}`" for p in hook))
    L.append("2. The first frame of every shot, numbered: " + ", ".join(f"`{p.relative_to(out)}`" for p in shotsheets))
    L.append(f"3. The whole video, {('one frame every ' + str(round(1 / all_fps, 2)) + ' s')}: "
             + ", ".join(f"`{p.relative_to(out)}`" for p in allsheets))
    L.append("4. Full-size frames for exact caption font, size and position: "
             + ", ".join(f"`{p.relative_to(out)}`" for p in fulls))
    if not labels:
        L.append("(This ffmpeg can't draw labels, so sheet tiles aren't timestamped: tiles run left to right, top to bottom, "
                 "at the rate above.)")
    L.append("")
    L.append("## Shot by shot")
    L.append("")
    L.append("| # | Time | Length | Said during the shot |")
    L.append("| --- | --- | --- | --- |")
    for sh in shots:
        L.append(f"| {sh['n']} | {vtools.hms(sh['start'])} - {vtools.hms(sh['end'])} | {sh['length']:.2f} | {sh['said'][:160]} |")
    if soft:
        L.append("")
        L.append("## Smaller changes (not counted as cuts)")
        L.append("")
        L.append("Moments where the picture changed a little at once: maybe a zoom step, a pop-in, a sticker, a big caption change. "
                 "Check them on the sheets: " + ", ".join(vtools.hms(t) for t, _ in soft[:60]))
    if snd.get("likely_sfx", {}).get("times"):
        L.append("")
        L.append("Possible sound-effect moments: " + ", ".join(vtools.hms(t) for t in snd["likely_sfx"]["times"][:60]))
    (out / "summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Done: {out / 'summary.md'}")
    print(f"  {len(shots)} shots, cut every {stats['cut_every_s']} s"
          + (f", {wpm} wpm" if wpm else "") + (f", {snd.get('pauses_feel')}" if snd.get("pauses_feel") else ""))


if __name__ == "__main__":
    main()
