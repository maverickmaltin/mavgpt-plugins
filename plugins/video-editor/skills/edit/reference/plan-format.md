# plan.json format (render.py)

One file describes the whole edit. Paths are relative to the project folder (the folder that holds `raw/` or `exports/`). Times are seconds.

- Every time in the plan uses the ORIGINAL video's timeline: the same seconds as in `work/NAME-words.json`. To put a zoom on a word, use that word's start and end from the transcript. If you later cut or restore parts in `keep`, everything stays attached to the right moment. Anything placed inside a part that was cut is skipped (render.py says so).
- To use edited-video times instead, add `"times": "edited"` at the top level.
- Use the video's own transcript: render.py stops if `captions.words` was made from a different video.
- A style's `plan-defaults.json` "plan" block is the starting point: copy it in, then add this video's input, output, keep, words, titles, zooms, overlays, b-roll and sound effects.

```json
{
  "input": "raw/my-video.mp4",
  "output": "exports/my-video-final.mp4",
  "times": "source",
  "canvas": {"width": 1080, "height": 1920, "fps": "source", "fit": "cover", "focus": {"x": 0.5, "y": 0.4}},
  "keep": [[0.0, 3.21], [3.62, 9.8]],

  "captions": {
    "enabled": true,
    "words": "work/my-video-words.json",
    "words_per_caption": 3,
    "font": "Arial Black",
    "size": 100,
    "bold": true,
    "color": "#FFFFFF",
    "highlight": "#FFD400",
    "highlight_mode": "color",
    "highlight_text": "#000000",
    "outline": 6,
    "outline_color": "#000000",
    "shadow": 2,
    "box": false,
    "position": 0.7,
    "uppercase": false,
    "punctuation": false,
    "animation": "pop",
    "fix": {"clog code": "Claude Code"}
  },

  "title_style": {"font": "Arial Black", "size": 80, "color": "#FFFFFF", "box": "#000000CC"},
  "titles": [
    {"text": "Claude edits videos now", "start": 0.0, "end": 1.8, "position": "top", "style": "pop"},
    {"text": "Step 1", "start": 6.2, "end": 7.5, "position": 0.3, "style": "slide", "box": true, "color": "#000000", "box_color": "#FFFFFF"}
  ],

  "punch_ins": {"pattern": [1.0, 1.08], "focus": {"x": 0.5, "y": 0.38}},
  "zooms": [
    {"start": 2.1, "end": 3.0, "scale": 1.15},
    {"start": 8.0, "end": 10.0, "scale": 1.2, "ease": 0.3, "focus": {"x": 0.5, "y": 0.35}}
  ],

  "grade": {"contrast": 1.05, "saturation": 1.08, "brightness": 0.0, "gamma": 1.0, "temperature": 0.2, "vignette": 0.2, "grain": 0.0,
            "lut": "styles/maya-editing-style/assets/luts/warm.cube", "strength": 0.7},

  "overlays": [
    {"file": "assets/screenshot.png", "start": 4.0, "end": 7.0, "x": 0.5, "y": 0.32, "width": 0.8, "fade": 0.2, "anim": "slide-up"},
    {"file": "assets/logo.png", "start": 0.0, "end": 30.0, "x": 0.88, "y": 0.07, "width": 0.14, "fade": 0.3, "anim": "none"}
  ],

  "broll": [
    {"file": "assets/broll-1.mp4", "start": 10.0, "end": 13.0, "from": 0.0, "mode": "full"}
  ],

  "sfx_dir": "styles/maya-editing-style/assets/sfx",
  "sfx": [
    {"name": "riser", "at": 1.95},
    {"name": "click", "at": 4.0},
    {"name": "whoosh", "at": 10.0, "volume": 0.45},
    {"file": "assets/my-ding.wav", "at": 12.3, "volume": 0.4, "offset": -0.05}
  ],

  "music": {"file": "assets/music.mp3", "volume": 0.15, "duck": true},
  "audio": {"loudnorm": true, "target_lufs": -14, "denoise": false},
  "progress_bar": {"enabled": false, "color": "#FFD400", "position": "top"},
  "fonts_dir": "styles/maya-editing-style/assets/fonts",
  "hdr_to_sdr": true,
  "srt": true,
  "crf": 20
}
```

## Fields

| Field | What it does |
| --- | --- |
| `canvas.fps` | `"source"` (default) keeps the original frame rate (up to 60); or a number (30, 60). |
| `canvas.fit` | `cover` fills the frame and crops (use `focus` to keep the face in frame), `contain` letterboxes, `blur` fills the empty space with a blurred copy (best for horizontal footage in a vertical video). |
| `canvas` sizes | 9:16 = 1080x1920, 16:9 = 1920x1080, 1:1 = 1080x1080, 4:5 = 1080x1350. |
| `keep` | The parts of the original to keep, in order: from silences.py, then tighten.py. |
| `captions.words_per_caption` | 1 for one word at a time, 2 to 4 for short lines. Captions also break at sentence ends and pauses. |
| `captions.position` | The caption's vertical center: 0 is the top, 1 the bottom. 0.62 to 0.75 stays clear of the app's buttons on 9:16. |
| `captions.size` | Font size on the 1080-wide frame. To match a reference: measure the capital-letter height in px on a 1920-tall frame and divide by 0.55 (Arial Black capitals are 0.52 of the size, most bold sans fonts 0.55 to 0.6), then check the first preview against the reference with compare.py and adjust. 100 to 110 reads as "big bold" on 9:16; 64 to 72 suits 16:9. |
| `captions.highlight` | The current word's color, or `false` for plain captions. |
| `captions.highlight_mode` | `color` (the word changes color), `box` (a colored box behind the word; `highlight_text` sets the word's color on it), `scale` (the word gets bigger), `none`. |
| `captions.outline` / `shadow` / `box` | Outline thickness in px (0 for none), shadow distance in px (0 for none), or a box color behind every caption (for example `"#000000AA"`). |
| `captions.animation` | `pop` (scales in), `bounce`, `fade`, `slide`, or `none` (instant). Applies when a new caption starts. |
| `captions.fix` | Replaces misheard words before display (case doesn't matter). Keys can be several words (`"clog code": "Claude Code"`, `"slash visual notes": "/visualnotes"`) or start with punctuation. Quotes around words are dropped automatically. |
| `captions.punctuation` | `false` (default) drops trailing commas and periods but keeps ? and !. |
| `titles[].style` | `pop` (scales in), `slide` (rises in), `fade`, or `none` (there from its first frame, like a text box burned into the video). `box: true` puts it on a solid label (`box_color`, text `color`; colors can have opacity, `#RRGGBBAA`); add `rounded: true` for rounded corners with each line its own width, TikTok style (drawn with Pillow in the exact font; `radius`, `pad_x`, `pad_y` to tune). Without a box, dark text gets a light outline automatically (or set `outline_color`). `position`: top, upper, center, lower, bottom, or a number 0 to 1. `\n` in `text` for two lines. |
| `punch_ins` | Changes the framing at every cut, cycling through `pattern` (for example `[1.0, 1.08]` alternates normal and 8% closer), so jump cuts look intentional. |
| `zooms[]` | `scale` 1.1 to 1.3. `ease` 0 is an instant punch-in; 0.2 to 0.4 is a smooth push. `focus` is the point to zoom toward. |
| `grade` | A look for your own footage (not b-roll or overlays): `contrast`, `saturation`, `brightness` (-0.1 to 0.1), `gamma`, `temperature` (-1 cool to 1 warm), `vignette` (0 to 1), `grain` (0 to 1), and/or a `.cube` `lut` at a `strength` from 0 to 1. Leave it out to keep the footage as filmed. |
| `overlays[]` | PNG/JPG/WebP images or videos (MOV/WebM with transparency work). `x`,`y` are the center as 0 to 1 of the frame, `width` is a fraction of the frame's shorter side (so a logo keeps its size between 9:16 and 16:9). Always kept inside the frame. `anim`: `slide-up`, `slide-left`, `none`. |
| `broll[]` | Covers the picture with another clip while the voice keeps playing. `from` is where to start inside the b-roll clip. `mode`: `full` or `pip` (small, top right). |
| `sfx[]` | Sound effects. `name` finds a file with that name in `sfx_dir` (default `assets/sfx`; make a starter pack with `sfx.py --out assets/sfx`), or `file` gives any path. `at` is when it starts (original-video time); `offset` nudges it (seconds, can be negative, for example to end a riser exactly on a cut); `volume` 0 to 1 (default 0.6). |
| `music.duck` | Lowers the music automatically while someone is talking. |
| `audio.target_lufs` | Loudness. -14 suits Instagram, TikTok and YouTube; use the style's measured number to match their other videos. |
| `fonts_dir` | Folder with `.ttf`/`.otf` files so you can use their fonts by name. A misspelled font name quietly falls back to a default font, so check the preview. |
| `hdr_to_sdr` | `true` (default) converts iPhone HDR video so it doesn't look grey and washed out. Needs ffmpeg-full (Mac) or the Gyan build (Windows). |
| `srt` | `true` (default) writes a captions file (.srt) next to the final video. |
| `crf` / `video_bitrate` | Quality. `crf` 18 to 20 is high quality, 23 makes smaller files. Or a fixed `video_bitrate` like `"25M"`. |

Avoid emoji in captions and titles; the caption engine draws them as empty boxes. Render with `--preview` while iterating; it's about 4x faster.
