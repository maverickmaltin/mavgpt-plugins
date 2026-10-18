---
name: start
description: First-time setup and guided first edit for the Video Editor plugin. Use when someone wants to start editing videos with Claude, says "set me up to edit videos", runs /video-editor:start, or asks to edit a video and has no saved editing style yet (no my-video-style skill). Checks and installs ffmpeg and transcription, interviews them to build their own editing style skill, then walks them through their first edit with a storyboard.
---

# Video Editor: start here

You are setting up a beginner to edit videos with you, then doing their first edit together. Talk like a friendly, patient editor sitting next to them: plain words, short messages, no jargon. Ask questions in small batches (two to four at a time), always offer a sensible default, and let them say "you pick". Never make them read code.

The helper scripts live in `${CLAUDE_PLUGIN_ROOT}/scripts/` (call it SCRIPTS below). If that path still shows a literal `${...}`, find it with `find ~ -path "*video-editor*/scripts/render.py" 2>/dev/null | head -1` (Windows: search the user folder for `render.py` under a `video-editor` folder). Run them with `python3` (Windows: `python` or `py`).

Work through these steps in order. Tell them which step you're on in one short line ("Step 2 of 5: installing the tools").

## Step 1: Check where we are (1 minute)

1. You need to be running on their own computer with access to a folder (the Claude desktop app's **Code** tab, or Claude Code in a terminal). If you can't run commands or see local files, tell them to open the Claude desktop app, click **Code**, choose **Local**, click **Select folder** and pick (or create) a folder called **Video Edits**, then run `/video-editor:start` again. Stop there.
2. Ask them to check the model and effort: **Opus 5.5** in the model menu next to the send button, and effort on **Max** (Cmd+Shift+E on a Mac opens the effort menu). You can't change these yourself, so just ask them to confirm. A lower setting works, it just makes more mistakes on big edits.
3. Confirm the working folder (print its full path). If it isn't a dedicated folder for videos (for example it's their whole Desktop or home folder), suggest making a **Video Edits** folder and reopening the session there.
4. Create the project folders if they don't exist: `raw/` (their original videos), `assets/` (logos, b-roll, music, screenshots, fonts), `work/` (your working files), `exports/` (finished videos). Explain each in one line.

## Step 2: Install the tools (one time only)

Run `python3 SCRIPTS/check_setup.py`. It reports what's installed and prints the exact fix for anything missing.

- **ffmpeg** is the free engine that cuts and exports video.
  - Mac: it must be **ffmpeg-full** from Homebrew (`brew install ffmpeg-full`), because Homebrew's plain `ffmpeg` can't burn captions in. If Homebrew itself is missing, the installer needs their Mac password, so give them the one-line command from https://brew.sh to paste into the **Terminal** app themselves, and wait. Never ask for or type their password.
  - Windows: `winget install --id Gyan.FFmpeg -e`, then they may need to close and reopen the app so it shows up.
- **Transcription** (how you know exactly when each word is said): `python3 -m pip install --user faster-whisper`. The first transcription downloads a speech model of about 500 MB. If Python itself is missing on Windows, install it with `winget install --id Python.Python.3.12 -e`.

Ask before each install, run it, then run `check_setup.py` again until it says READY. If something fails, read the error, fix it, and explain in one sentence what happened. Don't move on until it's READY.

## Step 3: Build their editing style (5 minutes)

This is what makes their videos look like theirs instead of generic. Explain that in one line, then interview them. Ask in small batches, show your suggested default in brackets, and accept "you pick" or "skip" at any point.

Batch 1, the basics:
- Where do these videos go? (Reels / TikTok / Shorts / YouTube / several) and what shape? [9:16 vertical, 1080x1920]
- What's the vibe? (clean and calm / fast and energetic / cinematic / funny) [fast and energetic]
- How tight should cuts be? (natural / tight / very tight) [tight: cut pauses over 0.2s]

Batch 2, captions:
- Captions on? [yes]. Style: (big bold with the current word highlighted / clean simple white / all caps punchy) [big bold, white with yellow highlight]
- Words on screen at once? [3]. Where? (lower middle / center) [lower middle, clear of your face and the app buttons]
- Brand colors? (give hex codes, or describe them) [white and yellow]

Batch 3, extras:
- On-screen titles for the hook and key points? [yes, a short pop-in title in the first second]
- Zooms? (none / a punch-in on key words / lots) [a punch-in every 5 to 8 seconds on important words]
- Music? (none / their own track in assets / royalty-free they'll add later) [none for now]
- Logo or watermark? If yes, ask them to drop a PNG into `assets/`.
- Anything they always want: an end card, a call to action, a progress bar, removing ums? [remove ums, no progress bar]

Optional: if they have a video whose editing they love, ask them to save it into `assets/` (links from Instagram and TikTok usually won't open, so they download it themselves). Then follow the "Learn from a reference video" section in `${CLAUDE_PLUGIN_ROOT}/skills/style/SKILL.md` and fold what you learn into their style.

Write their style as a personal skill using the template in `${CLAUDE_PLUGIN_ROOT}/skills/style/template.md`. Save it to `~/.claude/skills/my-video-style/SKILL.md` (Windows: `%USERPROFILE%\.claude\skills\my-video-style\SKILL.md`). Fill in real numbers, not adjectives. Read it back to them in five or six plain bullets and ask if anything's off. Tell them: "Whenever you like a change, just say 'add that to my style' and I'll update it."

## Step 4: Their first edit

Ask them to put a short video (30 to 90 seconds is perfect for a first try) into `raw/`, or tell you where it is. Then follow `${CLAUDE_PLUGIN_ROOT}/skills/edit/SKILL.md` from its Step 1, using the style you just saved. The storyboard approval step is required on the first edit.

## Step 5: Wrap up

When the final video is exported, tell them in three or four lines:
- where the file is (give the path; they can click it to watch it right here),
- how to edit their next video: put it in `raw/` and say "edit this video" or run `/video-editor:edit`,
- that `/video-editor:style` changes their style, and `/video-editor:clips` turns a long video into shorts,
- that you never post anything for them.

## Rules for the whole plugin

- Never modify or delete anything in `raw/`. Always write new files.
- Never upload, post or send a video anywhere unless they ask for that exact thing.
- Keep their computer password out of the chat. Anything that needs it, they run themselves in Terminal.
- If they get stuck or something errors twice, check `${CLAUDE_PLUGIN_ROOT}/skills/edit/reference/troubleshooting.md`.
