# Video Editor

Your own AI video editor, in Claude or ChatGPT. It studies your videos (or the creators you want to edit like) frame by frame, writes your personal editing skill from them, then edits every new video in that style, on your own computer.

Full guide: https://mavgpt.ai/resources/ai-can-now-edit-videos-for-you

## Install

**Claude desktop app** (paid plan): Customize > Plugins > + Add > Add marketplace > Add from a repository, paste `maverickmaltin/mavgpt-plugins` into URL, click Sync, then add **Video Editor**. Use it in the **Code** tab, opened on a folder for your videos.

**Claude Code:** `/plugin install video-editor --marketplace maverickmaltin/mavgpt-plugins`

**ChatGPT (Codex in the ChatGPT desktop app):** ask Codex to run `codex plugin marketplace add maverickmaltin/mavgpt-plugins` and `codex plugin add video-editor@mavgpt` (or run them in a terminal), then restart the ChatGPT app. To update later: `codex plugin marketplace upgrade mavgpt`.

## Commands

| Claude | Codex | What it does |
| --- | --- | --- |
| `/video-editor:start` | `$video-editor:start` | First time: installs the tools, asks whether to copy your style or build a new one, studies your videos frame by frame, writes your editing skill, edits a first video with you |
| `/video-editor:edit` | `$video-editor:edit` | Edits a video in your style: dead space cut first, storyboard for your OK, preview checked against your references, changes, final MP4 and captions file |
| `/video-editor:style` | `$video-editor:style` | Shows, updates ("add that to my style"), extends or shares your style; builds more styles (a client, a second channel) |
| `/video-editor:breakdown` | `$video-editor:breakdown` | Breaks down any video's editing frame by frame, and why it works |
| `/video-editor:clips` | `$video-editor:clips` | Turns a long video or podcast into short vertical clips |

Your style is a folder you own: `styles/<name>-editing-style/` in your video folder (SKILL.md, a full STYLE-GUIDE.md you can hand a human editor, the exact settings, and every note you've given).

## What's inside

- `skills/`: the instructions the AI follows (start, style, breakdown, edit, clips) with their references and templates.
- `scripts/`: small Python tools the AI runs (Python 3.8+, ffmpeg, faster-whisper; numpy comes with it):
  - `analyze.py` every cut, contact sheets (the hook frame by frame, every shot, the whole video), transcript, pacing, pause tightness, loudness
  - `fetch.py` downloads videos from links with yt-dlp (optional), with views and dates
  - `transcribe.py`, `silences.py`, `tighten.py` (cuts every pause on the audio without clipping a word), `checkcuts.py` (proves it)
  - `render.py` turns an edit plan into the video (captions, titles, punch-ins, zooms, overlays, b-roll, color and LUTs, sound effects, music, loudness, HDR conversion, .srt)
  - `compare.py` your edit next to your references; `frames.py`, `storyboard.py`, `join.py`, `sfx.py` (a starter pack of sound effects made from scratch), `check_setup.py`

## Needs

A computer (Mac or Windows) and Claude on a paid plan (the desktop app's Code tab, or Claude Code), or ChatGPT's Codex in the desktop app. Python 3.8+, ffmpeg with caption support (Mac: `brew install ffmpeg-full`; Windows: `winget install --id Gyan.FFmpeg -e`) and `faster-whisper`. The start command installs it all with you. Optional: yt-dlp (downloads from links) and Pillow (rounded text boxes).

## Privacy

Everything runs on your computer. Videos are only read, never uploaded, posted or sent anywhere. Downloads only happen from links you give it.
