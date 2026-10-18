# plan.json format (render.py)

One file describes the whole edit. Paths are relative to the project folder (the folder that holds `work/`). Times are seconds.

- Every time in the plan uses the ORIGINAL video's timeline: the same seconds as in `work/NAME-words.json`. To put a zoom on a word, use that word's start and end from the transcript. If you later cut or restore parts in `keep`, everything stays attached to the right moment. Anything placed inside a part that was cut is skipped (render.py says so).
- To use edited-video times instead, add `"times": "edited"` at the top level.
- Use the video's own transcript: render.py stops if `captions.words` was made from a different video.

```json
{
  "input": "raw/my-video.mp4",
  "output": "exports/my-video-final.mp4",
  "times": "source",
  "canvas": {"width": 1080, "height": 1920, "fps": 30, "fit": "cover", "focus": {"x": 0.5, "y": 0.4}},
  "keep": [[0.0, 3.21], [3.62, 9.8]],

  "captions": {
    "enabled": true,
    "words": "work/my-video-words.json",
    "words_per_caption": 3,
    "font": "Arial Black",
    "size": 100,
    "color": "#FFFFFF",
    "highlight": "#FFD400",
    "outline": 6,
    "position": 0.7,
    "uppercase": false,
    "punctuation": false,
    "animation": "pop",
    "fix": {"clog code": "Claude Code"}
  },

  "title_style": {"font": "Arial Black", "size": 96, "color": "#FFFFFF", "box": "#000000CC"},
  "titles": [
    {"text": "Claude edits videos now", "start": 0.0, "end": 1.8, "position": "top", "style": "pop"},
    {"text": "Step 1", "start": 6.2, "end": 7.5, "position": "center", "style": "slide", "box": true}
  ],

  "zooms": [
    {"start": 2.1, "end": 3.0, "scale": 1.15},
    {"start": 8.0, "end": 10.0, "scale": 1.2, "ease": 0.3, "focus": {"x": 0.5, "y": 0.35}}
  ],

  "overlays": [
    {"file": "assets/screenshot.png", "start": 4.0, "end": 7.0, "x": 0.5, "y": 0.32, "width": 0.8, "fade": 0.2, "anim": "slide-up"},
    {"file": "assets/logo.png", "start": 0.0, "end": 30.0, "x": 0.88, "y": 0.07, "width": 0.14, "fade": 0.3, "anim": "none"}
  ],

  "broll": [
    {"file": "assets/broll-1.mp4", "start": 10.0, "end": 13.0, "from": 0.0, "mode": "full"}
  ],

  "music": {"file": "assets/music.mp3", "volume": 0.15, "duck": true},
  "audio": {"loudnorm": true, "target_lufs": -14, "denoise": false},
  "progress_bar": {"enabled": false, "color": "#FFD400", "position": "top"},
  "fonts_dir": "assets/fonts",
  "crf": 20
}
```

## Fields

| Field | What it does |
| --- | --- |
| `canvas.fit` | `cover` fills the frame and crops (use `focus` to keep the face in frame), `contain` letterboxes, `blur` fills the empty space with a blurred copy (best for horizontal footage in a vertical video). |
| `canvas` sizes | 9:16 = 1080x1920, 16:9 = 1920x1080, 1:1 = 1080x1080, 4:5 = 1080x1350. |
| `captions.position` | 0 is the top of the frame, 1 the bottom. 0.7 sits above TikTok and Reels buttons in 9:16. |
| `captions.highlight` | Colors the word being spoken. Set to `false` for plain captions. |
| `captions.fix` | Replaces misheard words (case-insensitive) before display. |
| `captions.punctuation` | `false` (default) drops trailing commas and periods but keeps ? and !. |
| `captions.size` | 100 to 110 reads as "big bold" in 9:16; 64 to 72 suits 16:9. |
| `titles[].style` | `pop` (scales in), `slide` (rises in), `fade`. `box: true` puts it on a solid label. `position`: top, upper, center, lower, bottom, or a number 0 to 1. Use `\n` in `text` for two lines. |
| `zooms[]` | `scale` 1.1 to 1.3. `ease` 0 is an instant punch-in; 0.2 to 0.4 is a smooth push. `focus` is the point to zoom toward. |
| `overlays[]` | PNG/JPG/WebP images or videos (MOV/WebM with transparency work). `x`,`y` are the center as 0 to 1 of the frame, `width` is a fraction of the frame's shorter side (so a logo keeps its size between 9:16 and 16:9). It's always kept inside the frame. `anim`: `slide-up`, `slide-left`, `none`. |
| `broll[]` | Covers the picture with another clip while the voice keeps playing. `from` is where to start inside the b-roll clip. `mode`: `full` or `pip` (small, top right). |
| `music.duck` | Lowers the music automatically while someone is talking. |
| `audio.target_lufs` | Loudness. -14 suits Instagram, TikTok and YouTube. |
| `fonts_dir` | Folder with `.ttf`/`.otf` files so you can use their brand font by name. A misspelled font name quietly falls back to a default font, so check the preview. |
| `crf` | Quality. 20 is a good default; 23 makes smaller files. |

Avoid emoji in captions and titles; the caption engine draws them as empty boxes. Render with `--preview` while iterating; it's about 4x faster.
