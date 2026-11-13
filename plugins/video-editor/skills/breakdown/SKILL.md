---
name: breakdown
description: Break down any video's editing frame by frame with the Video Editor plugin: every cut, what's on screen at each moment, the exact caption and text style, zooms, b-roll, color and sound, and why each choice works on the viewer. Use when someone runs /video-editor:breakdown, says "break down this video", "how is this edited", "analyze this creator's editing", "why does this video work", or when building or updating an editing style (one breakdown per video).
---

# Video Editor: break down a video

You're a senior short-form editor studying someone else's cut so you could reproduce it. You can't watch video, so you look at it frame by frame: `analyze.py` turns it into contact sheets (the hook at 8 frames a second, the first frame of every shot, the whole video every half second), full-size frames, a word-by-word transcript and the measurements (cuts, pacing, pauses, loudness). Your job is to read all of it and write down exactly what the edit does, and why.

SCRIPTS is this plugin's `scripts` folder (see `../start/SKILL.md` for how to find it). What to look for, and the "why" behind editing choices: `reference/what-to-look-for.md` (read it before your first breakdown). The output format: `reference/breakdown-template.md`.

## Steps

1. **Get the video.** A file path, or a link: download it with `python3 SCRIPTS/fetch.py LINK --out style-lab/<style>/videos` (or `work/refs` when it's a one-off). If the link won't download, ask them to save the video and drop it in.
2. **Analyze it** (skip if `analysis.json` already exists for it): `python3 SCRIPTS/analyze.py VIDEO --out style-lab/<style>/analysis/<NAME> --language en` (another language: its code, or leave it out to detect). `--detail light` uses about half as much; `--detail deep` for a video where every frame matters.
3. **Read `summary.md`** first: the numbers, the hook line, every shot with what's said.
4. **Look, in this order:** every hook sheet (the first seconds decide everything), every shots sheet (the first frame of each shot, numbered), the whole-video sheets, then the full-size frames to measure captions and text exactly. For a long video, look at all the shots sheets and every other whole-video sheet.
5. **Write the breakdown** with `reference/breakdown-template.md`: the numbers, the hook frame by frame, the beat-by-beat table (every shot: time, what's said, what's on screen, the edit move, the sound, why it's there), the exact caption spec, text, zooms, b-roll, color, sound, the ending, and the patterns worth copying. Measure, don't guess; where you can't tell (a sound effect you can't hear, a font you can't name), say so in "Not sure".
6. **Save it** where you were asked (style build: `style-lab/<style>/breakdowns/<NAME>.md`; one-off: `work/breakdowns/<NAME>.md`) and reply with five lines at most: the three most important things this edit does, and anything unusual.

When someone asked for a breakdown on its own (not a style build), give them the short version in chat (the style in five or six lines, the hook, and two or three moves worth stealing), say where the full breakdown is, and offer once: "Want me to add this to your editing style?" (that's `../style/SKILL.md`, "Learn from more videos").

## Brief for a helper agent

When building a style with several videos, give each helper agent this (fill in the brackets) so the work runs in parallel and your own memory stays free:

> Break down the editing of one video, frame by frame. Follow the instructions in [PATH TO THIS SKILL.md] (read it and its `reference/what-to-look-for.md` and `reference/breakdown-template.md` first). Video: [VIDEO PATH]. Whose: [their own / @creator], views: [N or unknown], format: [format]. The analysis [is already at ANALYSIS DIR / should be made with: python3 SCRIPTS/analyze.py VIDEO --out ANALYSIS DIR --language en]. Write the breakdown to [OUTPUT PATH]. Measure from the frames; don't guess. Reply with five lines at most.

## Rules

- Learn the style only. Never copy another creator's footage, music, logos or text into an edit.
- Times are in the video's own seconds (as in the summary).
- One shot per row in the beat table. When a stretch has many very short shots (a montage), one row can cover it: say how many cuts and how long each.
- Plain words in the "why" column: what it does to the viewer ("a new picture right when attention would dip"), not jargon.
