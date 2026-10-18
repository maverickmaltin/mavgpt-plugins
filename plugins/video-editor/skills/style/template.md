---
name: my-video-style
description: [NAME]'s personal video editing style. Use whenever editing a video for [NAME] with the Video Editor plugin, so captions, pacing, titles, zooms, colors and exports always match what they like.
---

# [NAME]'s editing style

Use these settings for every edit unless I ask for something different in the moment. They feed straight into plan.json (see the Video Editor plugin's plan format).

## Where my videos go
- Platforms: [REELS / TIKTOK / SHORTS / YOUTUBE]
- Canvas: [1080x1920, 30 fps, fit cover, focus x 0.5 y 0.4]
- Typical length: [30 to 60 seconds]

## Vibe and pacing
- Vibe: [FAST AND ENERGETIC]
- Silence cuts: silences.py --min-silence [0.2] --pad-before [0.05] --pad-after [0.1] [--remove-fillers]
- Retakes: keep my last full take of any repeated line.
- Something changes on screen about every [3] seconds. No more than [1] zoom or effect every [3] seconds.

## Captions
- On: [YES]
- words_per_caption [3], font "[Arial Black]", size [100], color "[#FFFFFF]", highlight "[#FFD400]", outline [6], position [0.7], uppercase [false], punctuation [false]
- Spelling: [NAMES AND BRANDS TO ALWAYS SPELL RIGHT]

## Titles
- Hook title in the first second: [YES], [2 TO 5] words, style [pop], position [top]
- Key-point titles: [STYLE AND HOW OFTEN]
- title_style: font "[Arial Black]", size [96], color "[#FFFFFF]", box "[#000000CC]"

## Zooms and effects
- Zooms: [PUNCH-IN 1.15 ON IMPORTANT WORDS, EVERY 5 TO 8 SECONDS]
- Overlays and b-roll: [SHOW SCREENSHOTS AND B-ROLL WHEN I MENTION THE THING]
- Progress bar: [NO]

## Brand
- Colors: [HEX CODES]
- Logo: [assets/logo.png as an overlay: x 0.88, y 0.07, width 0.14, anim none, the whole video] or [NONE]
- Fonts: [FONT NAMES, fonts_dir assets/fonts] or [SYSTEM FONTS]
- End card / call to action: [TEXT OR NONE]

## Audio
- Music: [NONE / FILE, volume 0.15, duck on]
- Loudness: target_lufs [-14]. Denoise: [NO]

## Exports
- Final: [exports/NAME-final.mp4], crf [20]
- Also make: [16:9 VERSION / NONE]

## Changes
- [DATE]: Created with /video-editor:start.
