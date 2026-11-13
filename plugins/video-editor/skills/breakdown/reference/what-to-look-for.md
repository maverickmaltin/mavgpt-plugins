# What to look for in an edit, and why it works

## The anatomy of an edit (check every item)

**Shape and quality.** Aspect ratio, size, frame rate (60 fps reads smoother on phones), how much of the frame the face fills, where the eyes sit (usually the top third), how close the framing is.

**The hook (0 to 3 s).** What's on screen at frame 0 (face, result, text, movement?), the first words, the text on screen and how it relates to what's said (the same words, or something that adds to them), when the first visual change comes, and what the viewer has seen by second 3. Count the frames: a change at 0.4 s and one at 1.8 s are different styles.

**Cuts and pacing.** The median and longest shot (from the summary), jump cuts inside a sentence or only between sentences, whether the framing changes at a jump cut (a punch-in), how tight the pauses are (the summary's "silence between sentences": under 30 ms reads as no pause at all), retakes or ums left in, whether the face ever stays on screen long and why.

**Captions.** Read them in the full-size frames:
- Font look: heavy rounded sans (Montserrat ExtraBold/Black, Poppins Bold), condensed (Bebas Neue, Anton), geometric black (Archivo Black, Arial Black), app default (TikTok Sans, SF Pro), comic (Komika), serif. Say "looks like" when unsure.
- Size: measure the capital-letter height in pixels on a 1920-tall frame. The plan's caption `size` is about that height divided by 0.55 (0.52 for Arial Black); the first preview's compare.py check confirms it.
- Color, outline (how thick), shadow (soft or hard), a box behind them, case (UPPERCASE or Normal), punctuation kept or dropped, emojis.
- Words at a time (1, 2 to 3, a full line), how they appear (instant, pop, bounce, fade, typewriter), the current word highlighted (a color, a box behind it, bigger).
- Position: the vertical center of the caption as a share of the height (0.5 is the middle, 0.75 is three-quarters down), and whether it moves to stay clear of things.

**Text and graphics.** Title boxes (white box with black text, colored label, plain text with an outline; square or rounded corners; already there on the first frame or popping in), where they sit, how long they stay (the whole first sentence? 2 s?), whether they repeat the words or add to them. Numbered boxes in lists, stickers, emojis, arrows, circles and highlights on screenshots, lower thirds, progress bars, logos and watermarks (and whether that's the creator's own branding or a platform watermark from the download).

**Zooms and motion.** Punch-ins at cuts (how big: 5%, 10%, 20%), slow push-ins (on what words), zoom-outs, shakes, whip pans, speed ramps. A quick zoom-in as a screen appears.

**B-roll, screens and overlays.** What appears when something is named (a screenshot, an app recording, a product shot, stock footage, a meme, an AI clip), full screen or a card over the face, how big, how long, how it enters (cut, slide, pop), how often the face comes back.

**Transitions.** Hard cuts (most short-form) or effects (whips, zoom blurs, flashes, glitches). How often.

**Color.** As filmed, or graded: warmer or cooler, more contrast, more saturated, faded blacks, grain, vignette. Compare skin tones and whites across frames.

**Sound.** Music under the voice or not (the summary's "sound under the voice" is only a hint: ask the creator if you can't tell), its energy, whether it stops for emphasis. Sound effects: what kind and on which events (whoosh on transitions, pop on text, click on screens, a riser into a reveal, a ding on a number). Loudness (LUFS: -14 is standard for social; quieter means a softer feel). Voice: raw, cleaned up, compressed.

**The ending.** The call to action (what, said or written, how long), an end card, a loop (the last line leads back into the first), or a hard stop.

## The why (what each choice does to the viewer)

Use these as lenses and write the reason in plain words in each breakdown.

- **The first seconds decide everything.** Viewers decide to stay or swipe almost immediately. A face looking at the lens, a bold claim or question, and on-screen text that backs it up make people stop.
- **Proof early.** Showing the result before explaining it turns curiosity into belief, so the viewer wants to know how.
- **Something new every few seconds.** A cut, a zoom, a new picture or a new caption line resets attention right when it would drift. The rhythm varies so it doesn't feel mechanical.
- **One thing at a time.** On a phone, viewers read one thing. Busy frames, walls of text and split screens make them hunt, and hunting loses them. Big, centred, readable.
- **Show exactly what's said, when it's said.** Picture and words together land the point; a picture that's late or loosely related weakens it.
- **Emphasis.** A push-in, a highlight or a sound effect says "this matters": numbers, punchlines, results.
- **Captions for the sound-off crowd.** Many people watch muted: captions carry the message, and big captions near the face keep the eyes in one place.
- **Faces build trust.** Eye contact and a human voice keep people watching; cutting back to the face re-engages after a stretch of screens.
- **No dead air.** A pause is a chance to leave. Tight cuts make it feel fast even when the person talks slowly.
- **Re-hooks.** Mid-video teases ("but the third one is the best") or a sudden visual change pull wandering viewers back.
- **Credibility.** Real screens, real numbers, real results. Anything that looks fake costs more than it adds.
- **Consistency.** A recognizable look (the same captions, boxes and sounds every time) makes people feel at home and watch longer.
- **One clear ask.** A single call to action at the end, said and shown, beats several.
- **Loops and replays.** An ending that flows back into the start gets rewatched.
- **The platform's own buttons.** On vertical video, the app covers the bottom fifth (caption, username), the lower right (like, comment, share) and a strip at the top. Good edits keep text and results out of those areas.

## Common traps

- A platform watermark or the app's own buttons in a downloaded or screen-recorded video are not part of the style.
- A trending sound added in the app may be in the download: ask whether the creator adds music in the edit or in the app.
- A cut detected inside a fast pan or a flash may not be a cut: check the frames.
- Text burned in by the creator before editing (TikTok-style text boxes) is part of their look, but the editor works around it rather than making it.
