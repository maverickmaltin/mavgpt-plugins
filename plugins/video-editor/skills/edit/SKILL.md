---
name: edit
description: Edit a video in the person's own editing style with the Video Editor plugin. Use when someone runs /video-editor:edit, says "edit this video", "edit my video", "cut the dead space", "add captions", "make this a reel", "edit it like my style", "do the same to this one", or drops a raw video in. Cuts every pause without clipping a word, plans the edit as a storyboard for approval, renders a preview, checks its own work against their reference videos, takes changes in plain words, and exports the final MP4 (plus a captions file).
---

# Video Editor: edit a video

You're their editor. They describe what they want in plain words; you do every technical step. Keep messages short and visual: what you're doing, the storyboard, the preview, what you fixed, what you need from them.

SCRIPTS is this plugin's `scripts` folder: `${CLAUDE_PLUGIN_ROOT}/scripts` in Claude Code, `${PLUGIN_ROOT}/scripts` in Codex, otherwise two folders up from this SKILL.md (see `../start/SKILL.md`). Run with `python3` (Windows: `python` or `py`). Before writing a plan, read `reference/plan-format.md`. Every edit follows `reference/editing-rules.md` (the rules that hold whatever the style); their own style wins where they differ. If anything fails twice: `reference/troubleshooting.md`.

## Before you start

1. If `python3 SCRIPTS/check_setup.py` isn't READY, do `../start/SKILL.md` Step 2 first.
2. **Load their style.** Look in `styles/` for `*-editing-style/SKILL.md`. Several? Ask which (or pick the one that obviously fits). Read its `SKILL.md`, `plan-defaults.json`, the beat map in `formats/` for this kind of video, and the newest entries in `revisions.md`. No style yet? Ask: "Want to build your editing style first (about an hour, it learns from your videos), or should I use a starting style for now?" Build: `../start/SKILL.md`. For now: the closest one in `../style/reference/presets.md`.
3. Work in the project folder: originals in `raw/` (never modified), assets in `assets/`, working files in `work/`, finished videos in `exports/`. Name every working file after the video (`raw/beach-day.mov` -> NAME `beach-day`: `work/beach-day-words.json`, `-keep.json`, `-storyboard.json`, `-plan.json`) so videos never mix.

## Step 1: Quick intake

Ask only what you don't know yet, in one short message:
- Which video? (a file in `raw/`, or drag it in; several clips get joined in name order)
- Which format, if their style has several, and where it's going (default from their style).
- What it's about in one line, and the hook text if they want a title (their exact words, or should you suggest one?).
- Anything to show on screen: their screenshots, screen recordings, b-roll, product, logo (in `assets/`), or should you find or make it?
- Names, brands and words to spell exactly.
- Versions needed: a second hook, 16:9, a 30-second cut.
If they say "just edit it", use their style and go.

## Step 2: Cut the dead space first, across the whole video

Before planning anything visual, cut every pause in one pass and prove it. Everything after is planned on the cut timeline. Use the numbers in their `plan-defaults.json` ("cutting" and "check").

1. Several clips: `python3 SCRIPTS/join.py raw/01.mp4 raw/02.mov --out work/NAME-joined.mp4` and use the joined file from here on.
2. `python3 SCRIPTS/transcribe.py raw/VIDEO --out work/NAME-words.json --language en --vocab "NAMES, BRANDS"` (their language code; `--model small` is the default, `medium` for hard audio). Read `work/NAME-transcript.txt`; note misheard names for `captions.fix`.
3. `python3 SCRIPTS/silences.py raw/VIDEO --words work/NAME-words.json --out work/NAME-keep.json --min-silence [style] --pad-before [style] --pad-after [style] [--remove-fillers]`. It's the rough pass: in a noisy room it may find few cuts, and that's fine, because tighten.py (step 5) finds every pause on the audio. If it kept long stretches with no talking, look at them (`frames.py --at ...`): action, scenery or a demo usually stays; walking around or setting up usually goes. Ask when unsure.
4. **Retakes:** read the transcript for repeated or restarted sentences. Keep the last complete take; remove earlier ones and false starts ("wait, let me redo that") from the keep list. Unsure which take? Ask.
5. `python3 SCRIPTS/tighten.py raw/VIDEO --words work/NAME-words.json --keep work/NAME-keep.json --air [style air_ms] --max-pause [style max_pause]`. It re-sets every cut on the audio itself: each word's last sound and the next word's first sound stay, everything between goes, with the style's amount of air.
6. Write a first `work/NAME-plan.json` (input, output, keep, `captions.words`) and run `python3 SCRIPTS/checkcuts.py work/NAME-plan.json --max-sentence [style] --max-other [style] --retranscribe --vocab "NAMES, BRANDS"`. It must PASS before you plan anything else. For each flagged spot: dead space, trim it; clipped, move that cut point 0.03 to 0.05 s outward; a "missing" word, check the transcript (whisper sometimes mishears) and fix the keep list. Then check again.
7. No talking at all (a montage, action)? Skip 2 to 6: pick the best moments from frames (`frames.py --every 1`) and write `keep` by hand; lean on music, titles and the style's cut rhythm.
8. Long videos (over about 10 minutes): split into chapters and do the rest chapter by chapter.

## Step 3: Storyboard (wait for approval)

Plan the whole edit before rendering. Use the beat map for this format from their style, and their rules: when the hook title shows, when the first visual change comes, how often something changes, what gets zoomed, when screens or b-roll appear, which sound goes with which event. Plan each video from its own words: the style is a starting point, not a template to paste.

1. Write `work/NAME-storyboard.json` (format in the docstring of `SCRIPTS/storyboard.py`; times are original-video seconds, like the transcript) and run `python3 SCRIPTS/storyboard.py work/NAME-storyboard.json`. It makes `work/NAME-storyboard.html` with a still per section; tell them they can click it to open.
2. Also show a compact table in chat: Section, Time, What they say, On screen, Sound, Asset.
3. List the assets: for each, whether you'll make or find it, or need it from them.
4. Ask for changes (point at a section number) or "looks good". Wait. Apply changes and re-show only what changed. (Their style may say to skip approval for routine videos after the first few. Then show the table and go.)

## Step 4: Plan and preview

1. Start `work/NAME-plan.json` from their `plan-defaults.json` "plan" block, then add input, output, keep, `captions.words` and `captions.fix`, and the storyboard's titles, zooms, overlays, b-roll, sound effects (by name from their sound folder) and music. Place everything at ORIGINAL-video times (the times in `NAME-words.json`), so changing `keep` later never moves them.
2. Make what you said you'd make: graphics as PNG or transparent .mov (Python and Pillow if installed, or ffmpeg), screen recordings, found images. Real beats fake: use real screens and real results; anything you recreate must look exactly like the real thing, and say what you recreated when you deliver.
3. `python3 SCRIPTS/render.py work/NAME-plan.json --preview` (a fast half-size draft in `exports/`).
4. **Check your own work before they see it:**
   - `python3 SCRIPTS/frames.py exports/NAME-preview.mp4 --every 1 --out work/check-NAME` and look at every frame; then the hook up close: `python3 SCRIPTS/analyze.py exports/NAME-preview.mp4 --out work/NAME-preview-analysis --no-transcribe` and look at its hook and shots sheets.
   - Next to their references: `python3 SCRIPTS/compare.py exports/NAME-preview.mp4 [two or three of their style's source videos] --out work/NAME-compare.jpg --analysis-root style-lab/<style>/analysis --plan work/NAME-plan.json`. Same caption size and position, same framing, similar rhythm ("visual changes per 10 s" counts cards and pop-ins too, not just cuts) and loudness?
   - The checklist in `reference/editing-rules.md` ("Before they see it") and the "Check before showing a draft" list in their SKILL.md.
   - Any "Note:" lines render.py printed (safe zones, skipped items).
   Fix what you find, render again, then give them the preview path (they click it to watch with sound) and one line on what you fixed.

## Step 5: Changes

They'll say things like "captions bigger", "the cut at 0:14 is too sudden", "zoom when I say insane", "put the pricing part back". Change only what they named: everything else stays exactly as it was, length included. Times they give are from the preview (the edited video): find the words they mean in the transcript to get the original time. Render the preview again and say what changed.

When a note sounds like it should apply to every video ("always", "never", "I hate when", or the same note twice), ask "just this video, or always?" If always (or they say "add that to my style"), follow `../style/SKILL.md` "Update". Their style gets better with every video this way.

## Step 6: Final export

1. `python3 SCRIPTS/render.py work/NAME-plan.json` (full quality, the style's frame rate and quality). It also writes `exports/NAME-final.srt`, a captions file for YouTube or their editing app.
2. Name it the way their style says, report the path, length, size and shape, and list anything recreated or missing (screens you rebuilt, a typo you noticed in text they gave you).
3. Offer, one line each: other versions their style lists (16:9: copy the plan to `work/NAME-16x9-plan.json`, change `canvas` and `output`, `"fit": "blur"` for vertical footage, then check logo size and title positions), shorts from it (`../clips/SKILL.md`), or saving any new preferences to their style.
4. **Rough cut for their editing app** (if their style or they ask): render with captions, titles, zooms and sound effects off (`"captions": {"enabled": false}`, empty `titles`, `zooms`, `sfx`), and give them the video, the .srt (most editing apps import it: CapCut, Premiere, Final Cut, DaVinci) and the storyboard page as notes.
5. Never post or upload anything.

## Extra powers (when asked, or when the storyboard needs them)

- **AI b-roll with Higgsfield:** if a Higgsfield connector is available, plan each clip (prompt, length, shape; use Seedance 2.5 for video unless they want another model) and show the list with the estimated credits first. Wait for their OK. Save results into `assets/` and use them under `broll`. If it isn't connected: in Claude, **Customize > Connectors**, add a custom connector named Higgsfield with `https://mcp.higgsfield.ai/mcp`, then Connect; in ChatGPT, look for Higgsfield in **Plugins**. It needs a paid Higgsfield plan.
- **Screen recordings:** for a website, a scripted browser (for example Python Playwright with video recording) scrolls and clicks smoothly; save to `assets/`. On a Mac, `screencapture -v -V SECONDS assets/recording.mov` records the screen (macOS asks for Screen Recording permission the first time). Ask them to close private windows and turn on Do Not Disturb first.
- **Custom graphics:** anything the plan can't express (a chart, an animated lower third with an image, a stylised end card): render frames with Python into a transparent .mov or a PNG and place it with `overlays`. Match their style's fonts and colors.
- **Audio cleanup:** `"audio": {"denoise": true}` for hum and background noise.
- **Music:** only tracks they have the rights to (in `assets/`), at the level their style says. For Reels and TikTok, many creators add trending sounds in the app instead.
