---
name: style
description: Build, update, show or share the person's own video editing skill (their editing style) for the Video Editor plugin. Use when they run /video-editor:style, say "add that to my style", "always do that", "never do that again", "learn my style from these videos", "build a style from these creators", "make another style for a client", "update my editing style", "show my style", "use my style in Claude or ChatGPT", or give you a brand book or editing SOP. Studies videos frame by frame (with the breakdown skill), finds what makes the style, and writes it as a skill folder in styles/.
---

# Video Editor: your editing skill

A person's editing skill lives in `styles/<name>-editing-style/` inside their video folder. It's theirs: plain files they can read, change, hand to a human editor or upload to another AI. Every edit reads it. SCRIPTS is this plugin's `scripts` folder (see `../start/SKILL.md` for how to find it). Templates are in `templates/` next to this file; the reference files are in `reference/`.

What's in a style folder:
- `SKILL.md`: the rules every edit follows, with real numbers (short; the editor reads it before every edit).
- `STYLE-GUIDE.md`: the full style written for a person, with the reasons and examples. It doubles as an SOP for a human editor.
- `plan-defaults.json`: the exact settings each edit plan starts from (captions, titles, zooms, color, sound, cuts, export).
- `formats/<format>.md`: the beat map for each kind of video they make, if their formats differ.
- `references/`: `breakdowns/` (every studied video, frame by frame), `sources.md` (which videos and why), `brand.md` (their brand book or SOP, if any).
- `revisions.md`: every note they give, dated, and the rule it became.
- `assets/`: style-wide files (fonts, logo, LUTs, their sound effects).

If there are several styles in `styles/`, ask which one (once per session) unless the request makes it obvious.

---

## Build a style

Normally `../start/SKILL.md` runs this as its Steps 3 to 9. When someone asks for another style ("make one for my client", "a second style for my podcast clips"), do the same steps here: the big question, the interview (`reference/interview.md`), the videos (`reference/getting-videos.md`), the frame-by-frame breakdowns (`../breakdown/SKILL.md`), then the two parts below. Keep `style-lab/<name>/PROGRESS.md` up to date so a later session can resume.

How many videos: their own style, about 10 (5 is the minimum, say the style will be rougher). A new style from references, at least 5, 8 to 12 is ideal, up to about 15. More than 15 rarely adds anything and uses a lot of usage. Two to three creators are better than one (you learn the style, not one person's habits) and better than six (too many styles to blend). Same format as what they'll make.

Fewer than that? Go ahead with what they have (3 is the floor), say plainly that the style will copy those few videos more literally, mark the rules that rest on one or two videos as "from limited examples" in SKILL.md, and offer to add more videos later ("Learn from more videos"). Only one creator? Same thing: the style will carry that creator's personal habits, so ask which of them they actually want.

### Build: find the style

Read every breakdown in `style-lab/<name>/breakdowns/` and the numbers in each `analysis/*/analysis.json`. Then:

1. **Measure across videos.** Make a table (in `style-lab/<name>/synthesis.md`) of each trait per video and the median and range: length; cuts per 10 s; median and longest shot; first cut; cuts in the first 3 s; the hook (what's said, what's on screen, when the first visual change comes); captions (font look, weight, size as a share of the height, color, outline or shadow or box, words at a time, case, punctuation, position, animation, highlight); titles and text boxes; zooms and punch-ins (how often, how big, on what); b-roll and overlays (how often, full screen or over the face, what triggers them); transitions; color look; music (yes or no, energy, how loud); sound effects (which, on what events); loudness (LUFS); pause tightness (sentence gaps in ms); the ending and call to action; aspect, frame rate, safe margins.
2. **Sort what you found.**
   - **Always** (in about 70% or more of the videos): a rule, with the number.
   - **Often** (40 to 70%): a default, with when to use it.
   - **Sometimes** (under 40%): an option with its trigger ("a whoosh only when b-roll slides in").
   - **Depends on the format**: goes in that format's beat map.
3. **Find the why.** For each rule, the reason it works (from the "Why" columns of the breakdowns: holding attention, making a point land, proving a claim, making it readable on a phone). The why lets you apply the style to a video that's nothing like the references.
4. **Their own words win.** Their interview answers, their brand book or SOP, and their pet peeves override what you measured. If they conflict, ask.
5. **Loudness and placement.** Their own style (route A): match their measured loudness, so every video sounds the same in their feed. A new style from references (route B): use -14 LUFS (the usual level for Reels, TikTok and Shorts) unless they want the references' level. Caption and text positions: copy the references, even when captions sit low (up to about 0.82 of the height): that's part of the look. Only move things that the app's buttons would actually cover.
6. **References that disagree** (route B and C): list the choices in plain words ("Creator 1 uses one word of caption at a time, creator 2 uses three words with the current word in yellow. Which do you want?"). Suggest one.
7. **Can you do it?** Tag each element:
   - **Automatic**: the plugin does it from the plan (cuts, captions, titles, text boxes, zooms and punch-ins, overlays, b-roll, picture-in-picture, color and LUTs, music, sound effects, progress bar, any aspect ratio).
   - **Custom**: you can build it, slower (animated graphics, lower thirds with images, charts, a stylised end card), by rendering frames or a transparent .mov with Python, then placing it as an overlay.
   - **Not here**: complex motion graphics, 3D, tracking text to a moving object, rotoscoping, green screen replacement, AI effects you don't have tools for. Say so plainly and offer the closest thing you can do, or suggest they finish that part in their editing app.
8. **Show them** (Step 7 of start): the style in 8 to 12 plain lines, the choices to make, the "not here" items, and what you assumed. Change it until they say it's them.

### Build: write the skill

Make `styles/<name>-editing-style/` from the files in `templates/`:

1. `SKILL.md` from `templates/skill-template.md`. Frontmatter: only `name` (the folder name, lowercase with hyphens) and `description` (one or two sentences that say whose style it is and when to use it). No other frontmatter fields: some apps reject them on upload. Fill in real numbers, not adjectives ("a cut every 1.4 s on average, never a shot longer than 4 s", not "fast-paced"). Keep it under about 150 lines: details go in STYLE-GUIDE.md.
2. `STYLE-GUIDE.md` from `templates/STYLE-GUIDE.md`: the full style with the why, and examples from the breakdowns with timestamps ("Ref 3 at 0:02: the result pops up as a card over the face while she says 'look at this'").
3. `plan-defaults.json` from `templates/plan-defaults.json`: every number the edit plan needs (see `../edit/reference/plan-format.md` for each field). Measure, don't guess: caption size and position from the full-size frames (size: see plan-format's `captions.size` rule, then check it with compare.py on the first preview), pause tightness from the analysis (`--air` and checkcuts limits), loudness (see 5. above). Set `fonts_dir` and `sfx_dir` to the style's `assets/fonts` and `assets/sfx` only when the style has its own fonts or sounds; otherwise leave them `null`. Title boxes with rounded corners in the references: set `"rounded": true` on those titles (needs Pillow). A box that's already there on the first frame: `"style": "none"`.
4. `formats/<format>.md` from `templates/format.md` for each format with its own structure (a listicle, a talking-head tutorial, a vlog...). Skip if there's only one.
5. `references/breakdowns/`: copy the breakdown .md files (text only; the videos and sheets stay in `style-lab/`). `references/sources.md` from `templates/sources.md`. `references/brand.md` with the rules from their brand book or SOP (colors as hex, fonts, logo rules, words they always or never use on screen).
6. `revisions.md` from `templates/revisions.md`.
7. `assets/`: copy their fonts (`.ttf`/`.otf`) into `assets/fonts/`, logo into `assets/`, LUTs (`.cube`) into `assets/luts/`, sound effects into `assets/sfx/`. If they have no sound effects and the style uses them, make the starter pack: `python3 SCRIPTS/sfx.py --out styles/<name>-editing-style/assets/sfx` (simple sounds made from scratch, free to use), and suggest they swap in a pack they like later.
8. Check: the JSON files load (`python3 -c "import json;json.load(open('...'))"`), the frontmatter has only name and description, every font named in plan-defaults.json is in `assets/fonts/` or installed on the computer.
9. Read it back to them in five or six bullets, tell them where it is, and that saying "add that to my style" keeps improving it.

Then the first edit (start's Step 9).

---

## Update a style ("add that to my style")

This is how the style gets as good as a human editor who's worked with them for a year: every note becomes a rule.

- **A note about this video only** ("make the caption at 0:14 bigger"): change this video's plan only.
- **A note that should apply from now on** ("always", "never", "I hate when...", "add that to my style", or the same note twice): 
  1. Add a dated line to `revisions.md`: the date, their exact words, which video, and the rule it became.
  2. Change the rule where it lives in `SKILL.md` (the section it belongs to, right next to the rule it refines), as a small edit. Don't rewrite the skill around one note. Add one line under "Learned from revisions" pointing to it ("2026-11-12: captions bigger (Captions)").
  3. If it changes a number, change `plan-defaults.json` too. Update the matching line in `STYLE-GUIDE.md`, so the human version never goes stale.
  4. If it reverses an older rule, replace the old rule (the history stays in revisions.md). The newest note wins.
  5. Tell them in one line what you saved.
- Not sure if it's a one-off? Ask: "Just this video, or always?"
- When they explain why ("because my audience is older and needs it slower"), save the why too. It helps with videos the rule doesn't cover.

## Learn from more videos

When they want to add videos (a new favorite creator, their latest best performers, a new format): get them into `style-lab/<name>/videos/` (reference/getting-videos.md), analyze and break them down (`../breakdown/SKILL.md`), then redo "find the style" with all the breakdowns and show them only what changed ("New: a zoom on every number. Changed: cuts are a little faster, every 1.2 s instead of 1.5"). Update the files after they agree. A good habit: refresh it every month or two from their newest best-performing videos.

## Bring in a brand book or editing SOP

Read it (PDF, doc, slides, images). Pull out every rule that affects editing: colors (exact hex), fonts and where each is used, logo placement and size rules, intro and outro, lower thirds, caption rules, words to always or never show, music and sound rules, export specs, file naming, delivery. Put them in `references/brand.md`, then work each one into SKILL.md and plan-defaults.json. Where the document and the measured style disagree, ask which wins (usually the document for brand rules, the videos for pacing).

## Show the style

Six plain bullets: where it's posted and the shape; pacing and cuts; captions; text and titles; zooms, b-roll and color; sound. Then the path to `STYLE-GUIDE.md` for the full version. Don't paste the whole file unless they ask.

## Use it anywhere

The folder in `styles/` is the master copy: it's the one that gets updated. Copies are snapshots; make a fresh one after big changes.
- **Claude (regular chats, web or app):** zip the folder with the folder itself at the top (`cd styles && zip -r <name>-editing-style.zip <name>-editing-style`; Windows: `Compress-Archive -Path styles\<name>-editing-style -DestinationPath <name>-editing-style.zip`). They upload it in **Customize > Skills > + > Upload a skill** (code execution and file creation must be on in Settings > Capabilities). There it can plan edits, write briefs and review frames, but the actual editing runs here.
- **Claude Code in other folders:** copy the folder to `~/.claude/skills/`.
- **Codex:** copy the folder to `~/.agents/skills/` (personal skills), or keep working in this folder with the plugin.
- **ChatGPT chats:** attach `STYLE-GUIDE.md` to the chat or a project.
- **A human editor:** send `STYLE-GUIDE.md` and the `assets/` folder. It reads like an editing SOP.
