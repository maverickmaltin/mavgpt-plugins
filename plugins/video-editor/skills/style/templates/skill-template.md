---
name: [STYLE]-editing-style
description: [NAME]'s video editing style for [FORMATS] on [PLATFORMS]. Use it for every edit of [NAME]'s videos (with the Video Editor plugin, or to plan, brief or review an edit) so the cuts, captions, text, zooms, color and sound match how [NAME] wants them.
---

# [NAME]'s editing style

Built [DATE] from [N] videos: [WHOSE: "my own 10 best-performing reels" / "references from @A and @B"]. The full style, with the reasons and examples: `STYLE-GUIDE.md`. Exact settings for every edit: `plan-defaults.json`. When anything here disagrees with a newer note in `revisions.md`, the newer note wins.

## The style in 10 lines

1. [e.g. "Talking head, 9:16, 35 to 60 seconds, 60 fps."]
2. [e.g. "Zero dead space: the next sentence starts the instant the last one ends (air 20 ms)."]
3. [e.g. "The hook is the face plus a white title box with black text, top third, for the whole first sentence."]
4. [e.g. "The proof is on screen by 3.5 seconds: the result, big, as a card over the face."]
5. [e.g. "Captions: one word at a time, white, bold, uppercase, soft shadow, centred at 78% of the height."]
6. [e.g. "Something changes on screen about every 1.5 s; the face never stays longer than 4 s."]
7. [e.g. "Punch in 8% on every other cut; push in on every number as it's said."]
8. [e.g. "Screens and b-roll show exactly what's being said, the moment it's said."]
9. [e.g. "No music. A click on every screen entry, a soft whoosh on b-roll, a riser under the hook."]
10. [e.g. "Ends on the call to action box; loudness -16 LUFS; export 1080x1920, 60 fps."]

## Every edit

### Cuts and pacing
- [Dead space rule with numbers: tighten.py --air [X] --max-pause [Y]; checkcuts.py --max-sentence [A] --max-other [B] must pass.]
- [Cut rhythm: median shot [X] s, longest [Y] s, cuts in the first 3 s: [N].]
- [Retakes: keep the last full take. Fillers: remove / keep.]

### The hook (first 3 seconds)
- [What's on screen at frame 0, what's said, when the first visual change comes, what the viewer sees by second 3.]

### Captions
- [Font, weight, size as a share of the height, color, outline/shadow/box, words at a time, case, punctuation, position, animation, highlight. Names to always spell right.]

### Text on screen
- [Title or text boxes: look, position, when they appear and leave, wording rules (their exact words? max words? emojis?).]

### Zooms and motion
- [Punch-ins on cuts, push-ins on key words or numbers, how big, how fast. What never gets zoomed.]

### B-roll, screens and overlays
- [When something is named, what appears: full screen or over the face, how big, how long, how it enters. Where it comes from (their files, official images, recreated screens, AI clips). What must never be faked.]

### Color
- [None, a grade (contrast/saturation/warmth) or a LUT at what strength.]

### Sound
- [Music or not (how loud, ducked). Sound effects: which, on which events, how loud. Loudness target.]

### The ending
- [Call to action: words, box, timing, last frame.]

### Export
- [Size, frame rate, quality, file naming, versions (hooks, 16:9, 30-second cut), .srt captions file.]

## Formats

- [FORMAT]: `formats/[format].md` (delete this section if there's only one format)

## Never

- [Their pet peeves and anything the references never do: e.g. "no emojis in captions", "no music", "never cover the face for more than 6 s", "no fake-looking AI images".]

## Check before showing a draft

- `checkcuts.py work/NAME-plan.json --max-sentence [A] --max-other [B]` says PASS.
- The hook and first visual change land on time ([X] s); something changes about every [Y] s.
- Captions match the audio word for word; names spelled right.
- Text, logos and results sit inside the safe area (clear of the app's buttons and caption area).
- `compare.py` next to [two references]: same caption size and position, same framing, similar rhythm, same loudness.

## Learned from revisions

(Rules added from [NAME]'s notes, newest first. The dated history is in `revisions.md`.)

## Files

- `STYLE-GUIDE.md` the full style (also works as an SOP for a human editor)
- `plan-defaults.json` the settings each edit starts from
- `formats/` beat maps per format
- `references/breakdowns/` every studied video, frame by frame; `references/sources.md`; `references/brand.md`
- `revisions.md` every note, dated
- `assets/` fonts, logo, LUTs, sound effects
