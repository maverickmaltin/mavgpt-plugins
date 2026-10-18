---
name: style
description: Create, update or show the user's personal video editing style for the Video Editor plugin. Use when they say "add that to my style", "change my caption style", "update my editing style", "edit like this video", run /video-editor:style, or want their style learned from a reference video. Saves it as their own skill, my-video-style.
---

# Video Editor: your editing style

Their style lives in their own personal skill at `~/.claude/skills/my-video-style/SKILL.md` (Windows: `%USERPROFILE%\.claude\skills\my-video-style\SKILL.md`). Every edit reads it. It belongs to them, so keep it in their words and their choices, with real numbers.

## If it doesn't exist yet

Run the interview in `${CLAUDE_PLUGIN_ROOT}/skills/start/SKILL.md` Step 3, then write the file from `${CLAUDE_PLUGIN_ROOT}/skills/style/template.md`.

## Show it

Summarize it in six plain bullets (platform and shape, vibe and pacing, captions, titles, zooms and effects, brand and audio). Don't paste the whole file unless they ask.

## Update it

- "Add that to my style" after a change: work out exactly what they liked (for example "captions one size bigger" becomes `size` 84 to 96), update the right line, and confirm in one sentence.
- A bigger change: ask one or two questions, then edit.
- Keep a short "Changes" list at the bottom with the date and what changed, newest first. Keep the file under about 120 lines.
- Never put anything private in it (no passwords, addresses or account details).

## Learn from a reference video

When they give you a video whose editing they love (a file in `assets/`, downloaded by them):

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/frames.py assets/REFERENCE --every 1 --out work/reference` and look at the frames: caption font weight, size, color, highlight, position, words per caption; title style; how often the framing changes (cuts, zooms); overlays, b-roll, progress bars; colors.
2. Measure pacing: `ffmpeg -i assets/REFERENCE -vf "select='gt(scene,0.3)',showinfo" -f null -` and count scene changes per 10 seconds. Transcribe it with `transcribe.py` to see words per caption and talking speed.
3. Write what you found as specific rules ("a cut or zoom every 2.5 seconds", "3 words per caption, all caps, yellow active word"), show them, and ask what to keep. Then update their style.
4. Never copy its footage, music, logos or text. Learn the style only.
