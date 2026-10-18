---
name: edit
description: Edit a video with the Video Editor plugin. Use when someone says "edit this video", "add captions", "cut the silences", "make this a reel", "animate the key moments", or runs /video-editor:edit. Transcribes the video, plans the edit as a storyboard for approval, renders a preview, checks its own work, takes changes in plain words and exports the final MP4 in the user's saved style.
---

# Video Editor: edit a video

You are the editor. The user describes what they want in plain words; you do every technical step. Keep messages short and visual: tell them what you're doing, show the storyboard, show the preview, ask for changes.

SCRIPTS = `${CLAUDE_PLUGIN_ROOT}/scripts/` (if that shows a literal `${...}`, find `render.py` under a `video-editor` folder with `find ~ -path "*video-editor*/scripts/render.py" 2>/dev/null | head -1`). Run with `python3` (Windows: `python` or `py`). The plan format is in `${CLAUDE_PLUGIN_ROOT}/skills/edit/reference/plan-format.md`; read it before writing a plan.

## Before you start

- If `python3 SCRIPTS/check_setup.py` isn't READY, follow `${CLAUDE_PLUGIN_ROOT}/skills/start/SKILL.md` Step 2 first.
- Load their style: read `~/.claude/skills/my-video-style/SKILL.md`. If it doesn't exist, ask: "Want to set up your editing style first (5 minutes), or should I use clean defaults for now?" Use the start skill's Step 3 if they want a style.
- Work inside the project folder: originals in `raw/`, assets in `assets/`, working files in `work/`, finished videos in `exports/`. Never modify `raw/`.

## Step 1: Quick intake

Ask only what you don't already know (one short message):
- Which video? (file name in `raw/`, or drag it in. Several clips: they're joined in name order.)
- Where is it going and what shape? (default from their style)
- What's the video about, in one line? What should the viewer feel or do at the end?
- Anything to feature: logo, screenshots, b-roll, a product, music? (files in `assets/`)
- Names, brands or words that must be spelled exactly.

If they're in a hurry, use their style and defaults and go.

## Step 2: Prepare

1. Several clips? Join them first into `work/joined.mp4` with ffmpeg (re-encode to one size and frame rate so they join cleanly) and use that as the input.
2. Transcribe: `python3 SCRIPTS/transcribe.py raw/VIDEO --out work/words.json --vocab "NAMES, BRANDS"` (add `--language en` when you know it's English; it's faster and more accurate). Read `work/transcript.txt`. Fix obvious misheard names in a `captions.fix` map (for example `{"clog code": "Claude Code"}`).
3. Find the keepers: `python3 SCRIPTS/silences.py raw/VIDEO --words work/words.json --out work/keep.json` with their style's settings (`--min-silence`, `--pad-before`, `--pad-after`, `--remove-fillers`).
4. Retakes: read the transcript for repeated or restarted sentences. Keep the last complete take and remove the earlier ones from the keep list. Also remove false starts and "wait, let me redo that" moments.
5. Long videos (over about 10 minutes): split into chapters and plan/render chapter by chapter. Checking frames on a long video uses a lot of usage.

## Step 3: Storyboard (always wait for approval)

Plan the whole edit before rendering anything. Split the video into sections (hook, each point, ending). For each section decide: what's cut, what goes on screen (caption style, title text, zoom, overlay, b-roll, screen recording) and which assets are needed.

1. Write `work/storyboard.json` (format in the docstring of `SCRIPTS/storyboard.py`) and run `python3 SCRIPTS/storyboard.py work/storyboard.json`. It makes `work/storyboard.html` with a still frame per section. Tell them they can click that path to open it.
2. Also show a compact table in the chat: Section, Time, What they say, On screen, Asset.
3. List assets needed, and for each say whether you'll make it or need it from them.
4. Ask: "Any changes? Point at a section number, or say it looks good." Wait. Apply changes and re-show only what changed.

Editing judgment to use:
- The first second matters most: open on the strongest line, with a short title that matches what they say.
- Something should change on screen every few seconds (cut, zoom, title, overlay), but follow their style's limits. Don't stack effects.
- Titles are short (2 to 5 words). Captions are a few words at a time and never cover the face.
- Zooms land on emphasized words. Overlays and b-roll appear exactly when the thing is mentioned.

## Step 4: Build the plan and render a preview

Write `work/plan.json` from the approved storyboard (see the plan format reference). Then:

`python3 SCRIPTS/render.py work/plan.json --preview`

It makes a fast half-size draft in `exports/`. Then check your own work before showing them:
- `python3 SCRIPTS/frames.py exports/NAME-preview.mp4 --every 2 --out work/check` and look at the frames. Check: captions readable and not on the face, no typos, titles on screen at the right moments, overlays not covering anything important, nothing cut off at the edges, the right shape.
- Spot-check caption timing against `work/words.json` for three or four words.
- Check the cut list: no part shorter than about 0.3 seconds unless intended, no cut landing mid-sentence.
Fix what you find, re-render, then tell them what you fixed in one line and give the preview path (they click it to watch with sound).

## Step 5: Changes

They'll say things like "captions bigger", "the cut at 0:14 is too sudden", "zoom when I say insane", "put back the part about pricing". Translate each into plan changes (times in the plan are in the edited video's timeline, except `keep`, which uses the original video's times). Re-render the preview. Repeat until they're happy. If they say "add that to my style", update `~/.claude/skills/my-video-style/SKILL.md` (see the style skill).

## Step 6: Final export

`python3 SCRIPTS/render.py work/plan.json` (full quality). Then report: file path, length, size, and shape. Offer, in one line each: another shape (16:9 or 9:16 from the same plan), shorts from it (`/video-editor:clips`), or saving any new preferences to their style. Never post or upload it.

## Extra powers (use when asked or when the storyboard needs them)

- **AI b-roll with Higgsfield:** if a Higgsfield connector is available, plan each clip (prompt, length, 9:16 or 16:9) and show the list with estimated credits first. Wait for OK. Download results into `assets/` and add them under `broll` in the plan. If Higgsfield isn't connected, tell them how: Claude desktop app > Settings > Connectors (or Customize > Connectors) > Add custom connector > name Higgsfield, URL https://mcp.higgsfield.ai/mcp > Connect. It needs a paid Higgsfield plan.
- **Screen recordings:** for a website, use a scripted browser (for example Python Playwright with video recording) to scroll and click smoothly, then save to `assets/`. For the Mac screen, `screencapture -v -V SECONDS assets/recording.mov` records it (macOS asks for Screen Recording permission the first time). For clicking through an app, computer use can drive it while recording. Ask them to close private windows and turn on Do Not Disturb first.
- **Custom graphics:** for anything the plan can't express (a chart, a custom animated graphic, a lower third with an image), make it yourself, for example render frames with Python and Pillow into a transparent `.mov`, or an image, then place it with `overlays`. Keep it consistent with their style.
- **Audio cleanup:** `"audio": {"denoise": true}` for hum and background noise.

If anything fails twice, read `${CLAUDE_PLUGIN_ROOT}/skills/edit/reference/troubleshooting.md`.
