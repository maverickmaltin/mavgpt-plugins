# Starting styles (for people with no examples yet)

Use these for route D ("not sure yet"): describe them in one line each, ask which sounds closest to what they watch and like, and suggest finding 5 example videos in that style to build the real thing (route B). If they want to start right away, write their style from the closest preset (same files as a normal build, with "Built from the [preset] starting style" in SKILL.md), and let their notes on the first edits shape it.

Each preset lists its feel, the numbers, and the plan settings to start from.

## 1. Clean talking head (teaching, tips, explainers)

Feel: clear, calm, credible. The face and the words carry it; graphics only show what's being said.
- Cuts: no dead space (air 30 ms), retakes and ums removed. A visual change every 2 to 4 s.
- Hook: face + a white title box with black text in the top third for the first sentence. Show the result or proof by 4 s.
- Captions: 2 to 3 words, white, bold, soft shadow, no highlight, centred at about 72% of the height.
- Zooms: 8% punch-in on every other cut; a 15% push-in on numbers.
- Overlays: screenshots or results as a card over the face when named. No music. A click on each overlay.
- Plan: `"captions": {"words_per_caption": 3, "size": 86, "highlight": false, "outline": 0, "shadow": 3, "position": 0.72, "uppercase": false, "animation": "none"}`, `"punch_ins": {"pattern": [1.0, 1.08]}`, `"audio": {"target_lufs": -14}`; tighten `--air 30 --max-pause 0.15`.

## 2. Fast and punchy (entertainment, vlogs, hot takes)

Feel: high energy, constant motion, nothing still for long.
- Cuts: very tight (air 15 ms), a cut or zoom every 1 to 2 s, first cut within 1.5 s.
- Captions: 3 words, big, uppercase, the current word in yellow, quick pop.
- Zooms: punch-ins alternating 100%/112% on every cut, extra push-ins on emphasis.
- B-roll and memes when named; whoosh on transitions, pop on text; optional music bed about 20 dB under the voice, ducked.
- Plan: `"captions": {"words_per_caption": 3, "size": 100, "highlight": "#FFD400", "highlight_mode": "color", "outline": 6, "uppercase": true, "animation": "pop", "position": 0.7}`, `"punch_ins": {"pattern": [1.0, 1.12]}`; tighten `--air 15 --max-pause 0.1`.

## 3. Podcast and interview clips

Feel: the conversation is the star; easy to follow with the sound off.
- Cuts: natural (air 80 ms), keep the rhythm of the conversation, cut to whoever is speaking.
- Captions: big, 3 to 4 words, the current word on a colored box, centred.
- Hook: a title box with the topic or the boldest line for the first 3 to 4 s. Optional progress bar.
- No zooms except a slow push-in on the best line. No music, no sound effects.
- Plan: `"captions": {"words_per_caption": 4, "size": 92, "highlight": "#22C55E", "highlight_mode": "box", "highlight_text": "#000000", "uppercase": true, "position": 0.68}`, `"canvas": {"fit": "cover"}` with `focus` on the speaker; tighten `--air 80 --max-pause 0.35`.

## 4. Tutorial and screen recordings

Feel: "watch exactly what I do". Every step is visible and readable on a phone.
- The screen is the main shot, zoomed in on the part being talked about (about 2x), with the face for the hook, checkpoints and the call to action.
- Captions: 2 to 3 words, white with a dark shadow, kept clear of the screen content.
- A click sound on every click and every new screen; no music.
- Cuts: tight (air 30 ms); never more than about 30 s without the face.
- Plan: `"captions": {"words_per_caption": 3, "size": 80, "highlight": false, "shadow": 4, "outline": 0, "position": 0.8}` (move higher if it covers the screen), overlays for the screen recordings at `width` 0.92; tighten `--air 30 --max-pause 0.2`.

## 5. Faceless voiceover

Feel: a story told over pictures that change constantly.
- B-roll changes every 2 to 3 s, each clip matching the words exactly.
- Captions centred, 2 to 3 words, bold, the current word highlighted.
- Music bed under the voice (ducked), whooshes on bigger transitions.
- Plan: `"broll"` for every sentence, `"music": {"volume": 0.12, "duck": true}`, captions at `position` 0.5; tighten `--air 40`.

## 6. Cinematic and aesthetic (lifestyle, travel, food)

Feel: mood first; music drives the cuts.
- Cuts on the beat of the music, slow push-ins, a color look (a LUT or warm, contrasty grade, light grain).
- Few or no captions; a short title in an elegant font.
- Plan: `"grade": {"contrast": 1.08, "saturation": 1.05, "temperature": 0.25, "vignette": 0.25, "grain": 0.15}` or a `.cube` LUT, `"captions": {"enabled": false}`, `"music": {"volume": 0.9, "duck": false}`.
