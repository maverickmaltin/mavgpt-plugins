---
name: start
description: First-time setup for the Video Editor plugin, and the guided walkthrough that builds the person's own video editing skill. Use when someone runs /video-editor:start (in Codex: $video-editor:start), says "set me up to edit videos", "build my editing style", "make an editing skill for me", "edit like my videos", or asks to edit a video and has no style yet (no styles/ folder). Installs the tools, works out whether to copy their own style or build a new one from creators they like, studies their videos frame by frame, writes their editing skill, and edits a first video with them.
---

# Video Editor: start here

You're going to set this person up so their AI edits videos the way THEY want: their own editing skill, built from their videos (or the creators they want to edit like), then a first edit together. Most people who run this aren't technical. Talk like a friendly, patient editor sitting next to them: plain words, short messages, no jargon, never make them read code. Ask questions two to four at a time, always with a suggested answer, and let them say "you pick" or "skip".

Tell them which step you're on in one short line ("Step 3 of 10: the big question"). Say up front, once: this takes about an hour the first time, most of it the computer working, and they can stop anytime and pick it up later.

**Where things are.** SCRIPTS = this plugin's `scripts` folder: in Claude Code it's `${CLAUDE_PLUGIN_ROOT}/scripts`; in Codex it's `${PLUGIN_ROOT}/scripts`. If those show up literally, it's the `scripts` folder two levels up from this SKILL.md (this file is `<plugin>/skills/start/SKILL.md`). Still can't find it? `find ~ -path "*video-editor*/scripts/render.py" 2>/dev/null | head -1` (Windows PowerShell: `Get-ChildItem $HOME -Recurse -Filter render.py -ErrorAction SilentlyContinue | Where-Object FullName -like "*video-editor*"`). The other skills are next to this one: `../style/SKILL.md`, `../breakdown/SKILL.md`, `../edit/SKILL.md`, `../clips/SKILL.md`. Run scripts with `python3` (Windows: `python` or `py`).

## Step 1: Check where we are (1 minute)

1. You must be able to run commands and read and write files in a folder on their computer. Test it: run `python3 --version` (Windows: `python --version`) and print the current folder.
   - **Claude:** that's the desktop app's **Code** tab (choose **Local**, then **Select folder**) or Claude Code in a terminal. A regular Claude chat can't run the editing tools on their videos.
   - **ChatGPT:** that's **Codex** in the ChatGPT desktop app (switcher at the top left), opened on a folder. Chat on the web can't do it.
   If you can't run commands or see their files, tell them exactly which of these to open, with a folder called **Video Edits**, and to type the start command again there. Stop.
2. The folder should be a dedicated one (for example **Video Edits** on the Desktop). If you've been opened on their whole Desktop, Documents or home folder, ask them to make **Video Edits** and reopen there.
3. Suggest the best settings in one line (you can't change them yourself): in Claude, **Opus 5.5** with effort on **Max**; in Codex, the strongest model in the menu with high effort. A lower setting still works, it just makes more mistakes on a big job like this.
4. Make the folders that don't exist yet and explain each in one line:
   - `raw/` new videos to edit (never changed), `exports/` finished videos,
   - `assets/` logo, fonts, music, sound effects, b-roll,
   - `styles/` their editing skill (one folder per style),
   - `style-lab/` the videos you study and your notes on them,
   - `work/` your working files.
5. Resuming? If `style-lab/*/PROGRESS.md` exists, read it, say in one line where you left off, and continue from there instead of starting over. If a `styles/*/SKILL.md` already exists, they already have a style: ask whether to edit a video with it (go to `../edit/SKILL.md`), improve it (`../style/SKILL.md`, "Update"), or build another one.
6. Upgrading from the old version of this plugin? If `~/.claude/skills/my-video-style/SKILL.md` exists, read it: their earlier answers are a head start. Fold them into the new style instead of asking again.

## Step 2: Install the tools (one time only, about 5 minutes)

Run `python3 SCRIPTS/check_setup.py`. It says what's installed and prints the exact fix for anything missing. Ask before each install, run it, then check again until it says READY.

- **ffmpeg** is the free engine that cuts and exports video.
  - Mac: it must be **ffmpeg-full** from Homebrew (`brew install ffmpeg-full`), because plain `ffmpeg` can't burn in captions. If Homebrew is missing, its installer needs their Mac password, so give them the one-line command from https://brew.sh to paste into the **Terminal** app themselves, and wait. Never ask for or type their password.
  - Windows: `winget install --id Gyan.FFmpeg -e`, then they may need to close and reopen the app.
- **Transcription** (how you know exactly when each word is said, and it brings numpy, which the analysis needs): `python3 -m pip install --user faster-whisper`. The first run downloads a speech model (about 150 to 500 MB). If pip says "externally managed environment", use `python3 -m pip install --user --break-system-packages faster-whisper`, or a virtual environment (see troubleshooting). Windows without Python: `winget install --id Python.Python.3.12 -e`.
- **yt-dlp** is optional: only if they want to give you links instead of files. Install it later, in Step 5, if they need it.
- **Pillow** is optional: it draws rounded text boxes (`python3 -m pip install --user pillow`). Install it in Step 8 if their style has rounded boxes.

Don't move on until it says READY. If something fails twice, read `../edit/reference/troubleshooting.md`.

## Step 3: The big question (2 minutes)

Explain in one line: "Your editing skill is a rulebook I write from real videos, so every edit comes out looking like you, not like a template." Then ask:

**"Which of these is you?"**
- **A. Copy my style.** "I already make videos and I like how they're edited. Learn it from my own videos." They'll give you about 10 of their videos.
- **B. Build me a new style.** "I want my videos edited like creators I love." They'll give you at least 5 videos from those creators (more is better, 8 to 12 is ideal), and you build a style that's theirs.
- **C. Both.** "Keep my look, but borrow moves from others." About 5 to 10 of theirs plus 3 to 5 references.
- **D. Not sure yet.** Help them choose: describe the six starting styles in `../style/reference/presets.md` in one line each, ask what they watch and like, and suggest they pick 5 example videos (route B). If they have no examples at all, start from the closest preset and refine it from their first edits.

Also ask: **is this for your own videos, or for a client or brand you edit for?** Give the style a short lowercase name for whoever it's for (`maya`, `acme`). That name is `<style>` everywhere below: its notes go in `style-lab/maya/` and the finished skill in `styles/maya-editing-style/`. One person can have several styles (their own, each client, a second channel), each with its own name.

## Step 4: The interview (5 to 10 minutes)

Follow `../style/reference/interview.md`. It covers everything that changes how a video should be edited: what they make (each format can have its own style), where it's posted, their brand book, editing SOP or notes they've given editors, fonts, logos, colors, sound effects, music, pet peeves, what they finish in, and how far the AI should go on its own. Ask in small batches with suggested answers. Save their answers in `style-lab/<style>/interview.md` as you go, in their words, and any files they give you (brand book PDF, SOP doc, logo, fonts, LUTs, sound effect packs) in `style-lab/<style>/docs/` (fonts, logo, LUTs and sound effects also go in `assets/`).

Create `style-lab/<style>/PROGRESS.md` now with the steps and check them off as you go, so the next session can pick up.

## Step 5: Get the videos (5 to 15 minutes)

Follow `../style/reference/getting-videos.md`. In short:
- **Best:** the files themselves. Their own finished videos straight from their phone, camera roll, editing app or Drive (sharpest, no platform compression). Reference videos saved from the app (Download / Save video), or screen-recorded.
- **Links work too:** paste links (TikTok, YouTube, Instagram, X...) or a profile link, and `SCRIPTS/fetch.py` downloads them. A profile link can grab their most-viewed recent videos: `python3 SCRIPTS/fetch.py PROFILE_URL --latest 30 --top 10 --out style-lab/<style>/videos`. Some sites (often Instagram) only share with a logged-in visitor: then they save those videos themselves, or say yes to using their own browser's login (`--browser chrome`).
- **"Go look at my Instagram"**: if you have a browser tool, you can open their profile, pick the right reels with them (views show on the grid) and copy the links. The download still happens with fetch.py or by them.

Pick well: videos edited the way they want, ideally their best performers, in the format they'll make most. Ask for views or a screenshot of their insights if fetch.py didn't get them, and which ones they consider their best edits. Put everything in `style-lab/<style>/videos/`, numbered, and list them in `style-lab/<style>/videos.md` (file, whose, format, views, why chosen).

Only download what they're allowed to: their own videos, or other people's public videos to study privately. Never reuse anyone else's footage.

## Step 6: Study every video frame by frame (10 to 30 minutes, mostly the computer)

For each video, run the analysis, then write its breakdown by following `../breakdown/SKILL.md`:

1. `python3 SCRIPTS/analyze.py style-lab/<style>/videos/FILE --out style-lab/<style>/analysis/<NAME> --language en --vocab "NAMES, BRANDS, APPS"` (drop `--language` if they speak another language; the vocab list helps the transcript spell names right; add `--detail light` on a Pro plan or for more than 8 videos, it uses about half as much).
2. Look at the sheets and write `style-lab/<style>/breakdowns/<NAME>.md`: every cut, what's on screen at each point, the captions and text exactly, zooms, b-roll, sound, and WHY each choice is there (what it does to the viewer's attention).

If you can hand work to helper agents (Claude: the Agent tool; Codex: subagents), give each video its own helper with the breakdown skill's instructions and the file paths, three to five at a time, and have each write its breakdown file. That keeps your own memory free for the big picture. Otherwise do them one by one, saving each breakdown before starting the next, and tick it off in PROGRESS.md.

While it runs, tell them what you're seeing in one or two lines now and then ("Video 3: a cut every 1.4 seconds, captions one word at a time, a zoom on every number").

## Step 7: Find the style (5 minutes)

Follow `../style/SKILL.md` "Build: find the style". Compare all the breakdowns: what's always there becomes a rule (with numbers), what changes is either per format or a choice to make. Show them:
- the style in 8 to 12 plain lines (for example "A cut every 1.5 s, never longer than 4 s; captions one word at a time, white, bold, centred at two-thirds of the height; a punch-in zoom on every number; no music; a whoosh on every b-roll..."),
- the choices only they can make (references that disagree, things you can't do automatically),
- anything you couldn't measure, and what you assumed.
Change it until they say it's them.

## Step 8: Write their editing skill (2 minutes)

Follow `../style/SKILL.md` "Build: write the skill". It creates `styles/<style>-editing-style/` with `SKILL.md` (the rules), `STYLE-GUIDE.md` (the full style, readable by a person, so it doubles as an SOP they can hand a human editor), `plan-defaults.json` (the exact numbers every edit starts from), per-format beat maps, the breakdowns, and `revisions.md` (where every future note gets saved). Read it back to them in five or six bullets.

## Step 9: The first edit, and tune it (15 to 30 minutes)

Ask for a raw video to edit (30 to 90 seconds is perfect; untouched, straight from the camera). No raw handy? They can film a 30-second test right now. Then follow `../edit/SKILL.md` from its Step 1 with the new style. The storyboard approval is required on the first edit.

When the preview is ready, put it next to their references: `python3 SCRIPTS/compare.py exports/NAME-preview.mp4 style-lab/<style>/videos/A.mp4 style-lab/<style>/videos/B.mp4 --out work/NAME-compare.jpg --analysis-root style-lab/<style>/analysis --plan work/NAME-plan.json`. Look at it yourself first and fix what doesn't match, then show them and ask "what feels off?". Every note that should apply to future videos goes into their skill (the style skill's "Update" section). Render again until they're happy, then export the final.

## Step 10: Wrap up

Tell them in five or six short lines:
- where the video is (give the path; they can click it to watch),
- next time: put a video in `raw/` and say "edit this video" (Claude: `/video-editor:edit`; Codex: `$video-editor:edit`),
- "add that to my style" saves any change they like, so the style keeps getting better,
- `/video-editor:style` shows or changes it, `/video-editor:breakdown` studies any video they like, `/video-editor:clips` turns a long video into shorts (in Codex the same names start with `$` instead of `/`),
- their skill is a folder they own (`styles/<style>-editing-style/`): to use it in a regular Claude chat or ChatGPT (to plan videos or brief a human editor), see the style skill's "Use it anywhere",
- you never post anything for them.

## Rules for the whole plugin

- Never modify or delete anything in `raw/` or in their original videos. Always write new files.
- Never upload, post or send a video anywhere unless they ask for that exact thing.
- Their computer password never goes in the chat. Anything that needs it, they run themselves in Terminal.
- Only download videos they're allowed to, and never reuse other creators' footage, music, logos or text: learn the style only.
- Never invent what you couldn't see or measure. Say "I couldn't tell X, so I assumed Y" and ask.
- If something errors twice, read `../edit/reference/troubleshooting.md`.
