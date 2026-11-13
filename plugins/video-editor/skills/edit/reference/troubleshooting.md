# Troubleshooting

Find the problem, apply the fix, explain it to them in one sentence. If the same step fails twice after a fix, say so plainly and offer the backup way.

## Installing and opening

| Problem | Fix |
| --- | --- |
| Claude: no Plugins tab in Customize | Plugins need a paid Claude plan (Pro or higher). Update the Claude desktop app and restart it. |
| Claude: adding the marketplace fails | Check the address is exactly `https://github.com/maverickmaltin/mavgpt-plugins` (or `maverickmaltin/mavgpt-plugins`), then try again in a minute. |
| Claude: the plugin is added but `/video-editor:start` does nothing in the Code tab | Start a new session (Code > Local > Select folder) so it loads. Still missing: click **+** next to the message box, open **Plugins** and turn Video Editor on, or restart the app. |
| Claude: a regular chat can't edit the video | Editing runs on their computer: use the **Code** tab (Local, with a folder). A regular chat can't run the tools on their files. |
| Claude: still on the old version | Customize > Plugins > the mavgpt marketplace > Check for updates (or turn on Sync automatically). Claude Code: `/plugin marketplace update mavgpt`, then `/reload-plugins`. |
| ChatGPT: can't find where to install | It's **Codex** in the ChatGPT desktop app (the ChatGPT / Codex switcher at the top left), then Plugins. On the web, Codex runs in the cloud without their files. |
| ChatGPT: the plugin doesn't show after adding the marketplace | Restart the ChatGPT desktop app, or start a new Codex session in the folder. Then look in Plugins under the mavgpt (Personal) source. |
| Codex keeps asking "allow this?" | That's normal: it asks before running commands. Say yes to commands for this folder and to downloads it explains (the speech model, yt-dlp, ffmpeg). Say no to anything about other folders. |
| Codex says it has no network | Installing tools and downloading links need the internet. Approve the network request, or switch the approval setting below the message box to one that allows it for this task. |
| Free ChatGPT plan runs out quickly | Codex on Free is limited. Analyze fewer videos (5 to 6) with `--detail light`, or come back after the limit resets. |

## Setting up the tools

| Problem | Fix |
| --- | --- |
| `check_setup.py` says ffmpeg NOT FOUND | Mac: `brew install ffmpeg-full` (install Homebrew from brew.sh first if `brew` is missing; they run that installer in Terminal because it asks for their password). Windows: `winget install --id Gyan.FFmpeg -e`, then restart the app. |
| Captions: NO (Mac) | Plain Homebrew `ffmpeg` can't burn in captions. `brew install ffmpeg-full`. It's kept out of the PATH on purpose; the scripts find it in `/opt/homebrew/opt/ffmpeg-full/bin` (or `/usr/local/opt/ffmpeg-full/bin` on Intel Macs). |
| A password prompt, or "Need sudo access" | Stop. They run that command in the Terminal app and type the password there. Never in the chat. |
| `pip install` says "externally managed environment" | `python3 -m pip install --user --break-system-packages faster-whisper`, or a virtual environment in the folder: `python3 -m venv .venv` then `.venv/bin/pip install faster-whisper` (Windows: `.venv\Scripts\pip`), and run the scripts with `.venv/bin/python`. |
| Windows: `python` opens the Microsoft Store | `winget install --id Python.Python.3.12 -e`, restart the app, then use `python` or `py`. |
| "This step needs numpy" | `python3 -m pip install --user numpy` (it normally comes with faster-whisper). |
| The first transcription is slow | Normal: it downloads a speech model once. After that a minute of video takes well under a minute on a recent computer. |
| A new Mac pops up "install command line developer tools" | Click Install, wait for it to finish, then continue. |

## Getting the videos

| Problem | Fix |
| --- | --- |
| "yt-dlp isn't installed" | Only needed for links. Mac: `brew install yt-dlp` or `python3 -m pip install --user -U yt-dlp`. Windows: `winget install yt-dlp.yt-dlp`. Or skip links and drop the files in. |
| A link says it needs a login (often Instagram) | Save that video yourself (the app's Download or Save option, or a screen recording), or, only if they say yes, run fetch.py again with `--browser chrome` to use their own browser's login on their computer. A Mac may ask them to allow Keychain access. |
| A link says 403, blocked, or "unsupported" | Update yt-dlp (`brew upgrade yt-dlp` or `pip install -U yt-dlp`), make sure the link opens the video itself (not a profile or a search), then save it manually if it still fails. |
| A private video | Only the owner can save it. Ask for another video. |
| The download has a watermark or the app's buttons | Fine for studying, but tell the breakdown so it isn't mistaken for the style. Originals from their phone or editor are better for their own videos. |
| The video is too big to drag into the chat | Don't drag it into the chat: put it in `style-lab/<style>/videos/` (or `raw/`) in the folder. |
| Videos from an iPhone show up as .MOV or HEVC | That's fine. Everything here reads them. |

## Studying the videos (analysis and breakdowns)

| Problem | Fix |
| --- | --- |
| It hits the usage limit halfway | Everything is saved as it goes. After the reset, run the start command again: it reads `style-lab/<style>/PROGRESS.md` and picks up where it stopped. Use `--detail light` and 6 to 8 videos to use less. |
| analyze.py is slow | Most of the time is the speech model. `--model base` (the default) is fast; a 4K video takes longer to read. For long videos it analyzes the first 3 minutes. |
| Wrong language in the transcript | Run it with `--language` and their language code (es, fr, pt, de...). |
| "No speech found" | Normal for music-only or action videos. The cut rhythm and visuals still get measured; there are just no pause or talking-speed numbers. |
| The sheets have no timestamps | This ffmpeg can't draw text. Tiles still run left to right, top to bottom, at the rate in the summary. Installing ffmpeg-full (Mac) or the Gyan build (Windows) adds the labels. |
| It can't tell if there's music | The audio only gives a hint. Ask them. Many creators add music in the app after editing, so the download has it but their edit shouldn't. |
| A "cut" is listed in the middle of a fast pan or a flash | Check those frames; the detector counts sudden picture changes. Leave it out of the breakdown if it isn't a cut. |

## Their style

| Problem | Fix |
| --- | --- |
| "It doesn't feel like me" | Ask for the one thing that feels most off, and a frame or video of theirs that has it right. Add 2 or 3 more of their best videos and redo "find the style". Every note they give becomes a rule. |
| The references disagree | That's normal with several creators. List the choices plainly and let them pick, or use the one closest to their audience. |
| Something in their style can't be done here | Say so in one line and offer the closest thing: a custom graphic you build (slower), or finishing that part in their editing app from a rough cut. |
| Two styles got mixed up | Each style is its own folder in `styles/`. Ask which one at the start of each session. |
| The style got messy after lots of notes | Rebuild "find the style" from the breakdowns plus `revisions.md`, show them the cleaned-up version, keep the history in revisions.md. |
| Their fonts aren't used | Put the `.ttf`/`.otf` files in the style's `assets/fonts/` and set `fonts_dir`. Use the font's exact name (the name inside the file, not the file name). |
| Text boxes come out square, not rounded | Rounded boxes need Pillow: `python3 -m pip install --user pillow`, then `"rounded": true` on the title. render.py says when it fell back to a square box. |
| checkcuts lists "MISSING?" words | Only words right at a cut are checked. Pass the same `--vocab` as for the transcript; if it still lists one, listen to that spot before changing anything: whisper often hears a name differently. |

## Editing

| Problem | Fix |
| --- | --- |
| Dead space left, or a word clipped | Run `checkcuts.py work/NAME-plan.json`. Dead space: tighten.py with a lower `--air` or `--max-pause`, or trim that part. Clipped: move that cut point 0.03 to 0.05 s outward, or a higher `--air`. Check again. |
| The cuts feel robotic or rushed | Raise `--air` (60 to 120 ms feels natural) and save the new number to their style if they like it. |
| Captions out of sync | `captions.words` must be the transcript of the same input (render.py stops if it isn't). Joined clips: transcribe the joined file. |
| Names or numbers wrong in captions | Add them to `captions.fix` (`{"misheard": "Right"}`) and to `--vocab` next time. |
| Captions cover the face or the app's buttons | Move `captions.position` to 0.62 to 0.75 on 9:16, fewer words per caption, or smaller `size`. |
| Emoji show as empty boxes | Remove emoji from captions and titles. |
| A sound effect wasn't found | Make the starter pack (`sfx.py --out assets/sfx`) or use the exact file name in their `sfx_dir`. |
| A sound effect was skipped "because that part was cut" | It was placed inside removed audio. Move its `at` to a kept moment (often the start of the next part). |
| It's too quiet or too loud next to their other videos | Set `audio.target_lufs` to their measured number (from their style), render again. |
| iPhone video looks grey and washed out | That's HDR. Keep `hdr_to_sdr` on, with ffmpeg-full (Mac) or the Gyan build (Windows). Or turn off HDR video in the camera settings for next time. |
| Video is sideways | Phones store a rotation flag that's applied automatically. If it's still wrong, rotate once with ffmpeg (`-vf transpose=1`) into a new file and edit that. |
| Horizontal footage in a vertical video looks too zoomed | `"fit": "blur"` (the whole frame on a blurred background) or `"contain"`. |
| Render error mentioning a filter | Run `check_setup.py`; this ffmpeg is missing something. Install the full build. |
| "Cannot select channel layout" | Update to the latest plugin version. |
| File too big to upload | Re-render with `"crf": 23`, or `"video_bitrate": "12M"`. |
| The edit went sideways after lots of changes | Say "write down everything I've asked for", start a fresh session in the same folder, and paste it in with the edit command. A clean brief beats ten more fixes. |

## Using the style somewhere else

| Problem | Fix |
| --- | --- |
| Claude says the skill ZIP is invalid | The ZIP must contain the style folder itself (`maya-editing-style/SKILL.md`), not loose files. Its SKILL.md frontmatter should only have `name` and `description`. Turn on code execution and file creation in Settings > Capabilities first. |
| The uploaded copy is out of date | The folder in `styles/` is the master. Make a new ZIP after big changes and upload it again. |
