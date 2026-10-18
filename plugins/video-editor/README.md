# Video Editor

Edit your videos in Claude. Give it a clip and it adds captions, cuts every silence and animates the key moments on screen, all on your own computer.

Full guide: https://mavgpt.ai/resources/make-videos-using-claude

## Commands

| Command | What it does |
| --- | --- |
| `/video-editor:start` | First time: installs ffmpeg and transcription, builds your editing style, edits your first video with you |
| `/video-editor:edit` | Edits a video in your style: transcript, storyboard for your OK, preview, self-check, changes, final MP4 |
| `/video-editor:style` | Shows or changes your style, or learns it from a video you love |
| `/video-editor:clips` | Turns a long video or podcast into short vertical clips |

Your style is saved as your own skill at `~/.claude/skills/my-video-style/SKILL.md`. Say "add that to my style" any time.

## What's inside

- `skills/`: the instructions Claude follows.
- `scripts/`: small Python tools Claude runs (standard library only, plus ffmpeg and faster-whisper): `check_setup.py`, `transcribe.py`, `silences.py`, `render.py` (turns an edit plan into the video), `frames.py`, `storyboard.py`.

## Needs

A paid Claude plan with the desktop app's Code tab (or Claude Code), Python 3.8+, ffmpeg with caption support (Mac: `brew install ffmpeg-full`; Windows: `winget install --id Gyan.FFmpeg -e`) and `faster-whisper`. The start command installs all of it for you.
