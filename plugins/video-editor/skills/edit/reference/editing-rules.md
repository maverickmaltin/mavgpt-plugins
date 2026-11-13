# The rules every edit follows

These hold whatever the style, unless the person's own style says otherwise (theirs wins). They come from a full-time creator's editing notes over hundreds of short-form videos: each one fixes a mistake AI editors (and new human editors) make again and again.

## Cutting

1. **Cut the dead space first, across the whole video, in one pass**, before boxes, screens or effects. Then plan on the cut timeline.
2. **Right when one sentence ends, the next one starts, but no word is ever clipped.** A word's last sound (an s, a t, a k), and the next word's first sound (an h, an s), stay. It's a fine line: tighten.py finds it on the audio, checkcuts.py proves it. Never trust the transcript's word times for a cut.
3. **Check every cut on its own.** Each one is different. A breath inside a sentence isn't dead space; the pauses between sentences and takes are.
4. **Keep the last full take** of any repeated line, and drop false starts.

## What goes on screen

5. **The first seconds matter most.** Keep the hook clean (nothing added over it unless the style does it), and get the result or proof on screen fast, by about 3 to 4 seconds.
6. **Show exactly what's being said, exactly when it's said.** Each sentence gets the literal thing it names. A picture they're about to talk about holds still until they name it. A switch lands on the word: a frame early beats a frame late. Screen changes ride the cuts in their speech.
7. **One thing at a time, big and centered, readable on a phone.** No walls of text, grids or split screens (unless their style uses them). Text at least about 40 px tall on a 1920-tall frame. Hold a picture about a second after it lands before the next move.
8. **Every shot moves or changes:** a push-in, a glide, a highlight, a new picture. Vary the looks: the same animation or background twice in a row reads as a template.
9. **Real beats fake.** Real screenshots, real footage, real results first. Anything recreated must look exactly like the real thing. Never invent buttons, badges or pop-ups that the real app doesn't have, and no fake-looking AI images posing as results. Tell them what you recreated.
10. **It has to look like their channel.** Before adding something new, check it against their style. If nothing like it exists there, it needs a strong reason.
11. **Simple beats clever.** No effect without a job.
12. **Never show them looking away or reading their script.** If their eyes drop to the script, cover that moment with a screen or b-roll (full screen, or over their eyes), starting on the first frame their eyes move.
13. **Bring the face back** in long screen-only stretches (about every 20 to 40 seconds) when they're looking at the lens.

## Text and captions

14. **Captions match the audio word for word.** Names and brands spelled right, numbers as digits. Never change their words without saying so.
15. **Everything stays inside the safe area:** a margin on all four sides, and clear of the app's own caption, username and buttons (the bottom fifth and the lower right of a vertical video, and a strip at the top). Captions just above that line (up to about 0.82 of the height) are fine when their style puts them there.
16. **Never cover text that's already in the video** (text boxes they added before sending it): screens butt exactly against them, frame for frame.

## Sound

17. **Same loudness every video:** their measured LUFS. Sound effects sit quietly under the voice and use the same small kit each time. Typing sounds only while text visibly types, at a natural pace. Never music they don't have the rights to.

## Export and revisions

18. **Export at the source's frame rate** (60 stays 60), full resolution, high quality.
19. **Change only what they named.** Everything else stays exactly as it was, length included. The newest note wins; a reversal is context, not a contradiction.
20. **General notes become rules** in their style (style skill, "Update"), so they never have to say it twice.

## Before they see it

- checkcuts.py says PASS (no dead space over their limits, no clipped word).
- You looked at every frame of the preview (one a second) and the hook frame by frame.
- Every step or thing they name is on screen when they name it; nothing on screen contradicts what they say.
- Captions spelled right, in the safe area, never over a face or other text.
- No one-frame glitches at cuts, no frozen or black frames, nothing cut off at the edges.
- Side by side with their references (compare.py): same caption size and place, same framing, similar rhythm, same loudness.
- The length is the raw minus the cuts; nothing clipped at the start or end.
- You're the first viewer; they're the last. Tell them to watch it once with sound, because you checked frames and numbers, not the moving video.
