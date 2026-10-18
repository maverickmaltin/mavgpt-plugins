# Troubleshooting

| Problem | Fix |
| --- | --- |
| `check_setup.py` says ffmpeg NOT FOUND | Mac: `brew install ffmpeg-full` (install Homebrew from brew.sh first if `brew` is missing; the user runs that installer in Terminal because it asks for their password). Windows: `winget install --id Gyan.FFmpeg -e`, then restart the app or terminal. |
| Captions: NO (Mac) | Plain Homebrew `ffmpeg` has no caption support. `brew install ffmpeg-full`. It's keg-only; the scripts find it at `/opt/homebrew/opt/ffmpeg-full/bin` (Apple Silicon) or `/usr/local/opt/ffmpeg-full/bin` (Intel) on their own. |
| `brew` asks for a password, or "Need sudo access" | Stop. The user runs the command in the Terminal app and types the password there. Never ask for it in chat. |
| `pip install` fails with "externally managed environment" | Use `python3 -m pip install --user --break-system-packages faster-whisper`, or make a virtual environment in the project: `python3 -m venv .venv && .venv/bin/pip install faster-whisper`, then run the scripts with `.venv/bin/python`. |
| Transcription is slow | Normal on the first run (it downloads the model). Use `--language en` for English. For very long videos use `--model base`, then fix names with `captions.fix`. |
| Words misheard (names, brands) | Re-run with `--vocab "Name, Brand"`, and add `captions.fix`. |
| Captions out of sync | Make sure `captions.words` points at the transcript of the same input as `input` (render.py stops if they don't match). If clips were joined, transcribe the joined file, not the originals. |
| "The captions file ... was made from ..." | You're using another video's transcript. Transcribe this video to `work/NAME-words.json` and point `captions.words` at it. |
| Action or scenery got cut | silences.py keeps long non-talking stretches by default and lists them. If you used `--cut-long-gaps`, re-run without it, or add the moment back to `keep`. |
| "No speech found" | Normal for footage without talking. Skip captions and silence cuts; pick moments from frames and build `keep` by hand. |
| Captions cover the face or the app buttons | Lower `captions.position` (0.62 to 0.7 for 9:16), fewer `words_per_caption`, smaller `size`. |
| Cuts clip the ends of words | Raise `--pad-after` to 0.15 to 0.2 in `silences.py`, re-run, and update `keep`. |
| Cuts feel choppy | Raise `--min-silence` to 0.35 so only real pauses go. |
| Too much got cut | Compare `work/keep.json` with `work/NAME-transcript.txt`; add the missing range back to `keep`. |
| Video is sideways | Phone videos carry a rotation flag that ffmpeg applies automatically. If it still looks wrong, add `"canvas": {"fit": "blur"}` or rotate with ffmpeg first (`-vf transpose=1`). |
| Horizontal footage in a vertical video looks too zoomed | `"fit": "blur"` (shows the whole frame on a blurred background) or `"contain"`. |
| Render error mentioning a filter | Run `check_setup.py`; the ffmpeg build may be missing something. Install the full build. |
| "Cannot select channel layout" | Update to the latest plugin version (the render script converts audio to stereo). |
| Emoji show as boxes | Remove emoji from captions and titles. |
| File too big to upload | Re-render with `"crf": 23` (smaller) or compress: `ffmpeg -i in.mp4 -c:v libx264 -crf 24 -preset slow -c:a copy out.mp4`. |
| Usage limit reached | Lower effort for small changes, render previews instead of finals, and split long videos into chapters. |
| Higgsfield tools missing | Connect it: Settings > Connectors (or Customize > Connectors) > Add custom connector > Higgsfield, `https://mcp.higgsfield.ai/mcp`. Needs a paid Higgsfield plan. |
| Screen recording is black | macOS needs Screen Recording permission for the app doing the recording: System Settings > Privacy & Security > Screen & System Audio Recording. Restart the app after allowing it. |
