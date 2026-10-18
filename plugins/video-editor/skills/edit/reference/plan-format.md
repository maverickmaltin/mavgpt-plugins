# plan.json format (render.py)

One file describes the whole edit. Paths are relative to the project folder (the folder that holds `work/`). Times are seconds.

- `keep` uses the ORIGINAL video's timeline (from `silences.py`, then edited for retakes).
- Everything else (`titles`, `zooms`, `overlays`, `broll`) uses the EDITED video's timeline. To place something on a word, find the word in `work/words.json`, then convert: edited time = (word time - start of its keep part) + total length of all earlier keep parts. Or render a preview and read the times off the frames.

```json
{
  "input": "raw/my-video.mp4",
  "output": "exports/my-video-final.mp4",
  "canvas": {"width": 1080, "height": 1920, "fps": 30, "fit": "cover", "focus": {"x": 0.5, "y": 0.4}},
  "keep": [[0.0, 3.21], [3.62, 9.8]],

  "captions": {
    "enabled": true,
    "words": "work/words.json",
    "words_per_caption": 3,
    "font": "Arial Black",
    "size": 84,
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
    {"file": "assets/screenshot.png", "start": 4.0, "end": 7.0, "x": 0.5, "y": 0.32, "width": 0.8, "fade": 0.2, "anim": "slide-up"}
  ],

  "broll": [
    {"file": "assets/broll-1.mp4", "start": 10.0, "end": 13.0, "from": 0.0, "mode": "full"}
  ],

  "music": {"file": "assets/music.mp3", "volume": 0.15, "duck": true},
  "audio": {"loudnorm": true, "target_lufs": -14, "denoise": false},
  "progress_bar": {"enabled": false, "color": "#FFD400", "position": "top"},
  "fonts_dir": "assets/fonts",
  "crf": 18
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
| `titles[].style` | `pop` (scales in), `slide` (rises in), `fade`. `box: true` puts it on a solid label. `position`: top, upper, center, lower, bottom, or a number 0 to 1. Use `\n` in `text` for two lines. |
| `zooms[]` | `scale` 1.1 to 1.3. `ease` 0 is an instant punch-in; 0.2 to 0.4 is a smooth push. `focus` is the point to zoom toward. |
| `overlays[]` | PNG/JPG/WebP images or videos (MOV/WebM with transparency work). `x`,`y` are the center as 0 to 1 of the frame, `width` is a fraction of the frame width. `anim`: `slide-up`, `slide-left`, `none`. |
| `broll[]` | Covers the picture with another clip while the voice keeps playing. `from` is where to start inside the b-roll clip. `mode`: `full` or `pip` (small, top right). |
| `music.duck` | Lowers the music automatically while someone is talking. |
| `audio.target_lufs` | Loudness. -14 suits Instagram, TikTok and YouTube. |
| `fonts_dir` | Folder with `.ttf`/`.otf` files so you can use their brand font by name. |

Avoid emoji in captions and titles; the caption engine draws them as empty boxes. Render with `--preview` while iterating; it's about 4x faster.
