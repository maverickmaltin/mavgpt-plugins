---
name: clips
description: Turn a long video (podcast, YouTube video, livestream, talk) into short vertical clips with the Video Editor plugin. Use when someone says "make shorts from this", "find the best moments", "turn this into reels", or runs /video-editor:clips.
---

# Video Editor: long video to shorts

SCRIPTS = `${CLAUDE_PLUGIN_ROOT}/scripts/`. Follow the same rules and style as `${CLAUDE_PLUGIN_ROOT}/skills/edit/SKILL.md`.

1. **Ask** how many clips [5], how long each [under 60 seconds], and the shape [9:16].
2. **Transcribe** the whole video: `python3 SCRIPTS/transcribe.py raw/VIDEO --out work/NAME-words.json` (for videos over an hour, `--model base` is much faster).
3. **Find the moments.** Read `work/NAME-transcript.txt` and pick the strongest standalone moments. Each needs a first line that hooks without context, one clear idea, and a clean ending. Prefer surprising claims, specific numbers, stories and strong opinions. Avoid moments that depend on something said earlier.
4. **Show a shortlist** (more than they asked for, about 1.5x): number, start and end time, the opening line, why it works, and a suggested hook title. Wait for them to pick.
5. **Edit each pick** as its own plan: `work/NAME-clip-01-plan.json` and so on, all using the same input and words file. For `keep`, run `silences.py` on the full video once and use the parts that fall inside each moment. If a moment has no talking (a reaction, a demo, action), its keep is simply `[[start, end]]`. For two people talking, use `"fit": "cover"` with `focus` on the person speaking, or `"blur"` to show both.
6. **Preview, check frames, fix,** exactly as in the edit skill. Show all the previews together and take changes.
7. **Export finals** to `exports/NAME-clip-01-final.mp4` and so on. List them with their hook titles. Never post them.
