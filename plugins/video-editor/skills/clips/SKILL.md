---
name: clips
description: Turn a long video (podcast, YouTube video, livestream, talk, or a long talking-head take) into short vertical clips in the person's editing style with the Video Editor plugin. Use when someone runs /video-editor:clips, says "make shorts from this", "find the best moments", "cut this into five clips", "clips for trial reels", or "turn this into reels".
---

# Video Editor: long video to short clips

SCRIPTS is this plugin's `scripts` folder (see `../start/SKILL.md`). Every clip follows `../edit/SKILL.md` and `../edit/reference/editing-rules.md`, in their style from `styles/` (load it the same way the edit skill does).

1. **Ask** how many clips [5], how long each [under 60 seconds], and the shape [9:16]. Trial reels or tests? Then make the clips different from each other on purpose (different hooks, different moments) so the results teach them something.
2. **Transcribe** the whole video once: `python3 SCRIPTS/transcribe.py raw/VIDEO --out work/NAME-words.json --language en` (for videos over an hour, `--model base` is much faster).
3. **Find the moments.** Read `work/NAME-transcript.txt` and pick the strongest standalone moments. Each needs a first line that hooks without any context, one clear idea, and a clean ending. Prefer surprising claims, specific numbers, stories and strong opinions. Avoid moments that depend on something said earlier.
4. **Show a shortlist** (about 1.5 times as many as they asked for): number, start and end, the opening line, why it works, and a suggested hook title. Wait for them to pick.
5. **Cut each pick** as its own plan (`work/NAME-clip-01-plan.json` and so on), all using the same input and transcript: run `silences.py` once on the full video, keep the parts inside each moment, then `tighten.py` with their style's air on that clip's keep list, and `checkcuts.py` on its plan. A moment with no talking (a reaction, a demo) keeps `[[start, end]]`. Two people talking: `"fit": "cover"` with `focus` on whoever is speaking, or `"blur"` to show both.
6. **Preview, check frames, fix,** exactly as in the edit skill. Show all the previews together and take changes.
7. **Export the finals** to `exports/NAME-clip-01-final.mp4` and so on, each with its .srt. List them with their hook titles. Never post them.
