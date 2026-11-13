# Getting the videos to study

Everything goes in `style-lab/<style>/videos/`, numbered (`01-...`, `02-...`), and is listed in `style-lab/<style>/videos.md`: file, whose it is (theirs or a reference creator), format, views if known, and why it was chosen. SCRIPTS is the plugin's `scripts` folder.

## Which videos

- **Their own style (route A):** about 10 finished videos edited exactly the way they like. Their best performers are better than their latest, as long as they're in the current style. If they've changed style lately, only the recent ones count. One or two that flopped are useful as contrast: label them.
- **A new style (route B):** at least 5 from the creators they want to edit like, 8 to 12 is ideal, up to about 15. Two or three creators, same format as what they'll make. A creator's most-viewed videos show the style that works for them.
- **Both (route C):** 5 to 10 of theirs plus 3 to 5 references for the moves they want to borrow.
- Short-form is easy. For long videos (over about 4 minutes), the analysis looks at the first 3 minutes; that's where most of the editing style shows.

## The best way: the files themselves

Ask them to put the files in the folder (drag them into the chat or into `style-lab/<style>/videos/`).
- **Their own videos:** the finished file from their phone's Photos or camera roll (an app like CapCut, Edits or InShot saves the export there), their editor's exports (Drive, Dropbox, Frame.io), or their computer. These are sharper than anything downloaded from a platform.
- **iPhone to Mac:** AirDrop, or iCloud Photos, or plug in the phone. **To Windows:** the Phone Link app, a cable, or upload to Google Drive and download on the computer.
- **YouTube (their own):** YouTube Studio > Content > the three dots next to a video > Download.
- **TikTok:** open the video > Share > Save video (works for their own; for other people's, only when the creator allows it, and it adds a watermark).
- **Instagram:** the app shows a Download option in the share or ••• menu on some reels (their own, and public reels when the creator allows it; it adds a watermark). For everything at once, Instagram's "Download your information" (in Accounts Center) sends a file with all their posts; it can take a few hours to a day.

## Links

`SCRIPTS/fetch.py` downloads from links when yt-dlp is installed (ask first; Mac: `brew install yt-dlp` or `python3 -m pip install --user -U yt-dlp`; Windows: `winget install yt-dlp.yt-dlp`).
- Single videos: `python3 SCRIPTS/fetch.py LINK1 LINK2 ... --out style-lab/<style>/videos`
- A text file of links: `--list links.txt`
- A profile or channel: `python3 SCRIPTS/fetch.py PROFILE_LINK --latest 30 --top 10 --out style-lab/<style>/videos` takes the 10 most-viewed of the last 30 when the site shares view counts (YouTube and TikTok usually do), otherwise the latest 10.
- It saves views, likes and the date next to each video, so you can tell which ones performed.
- Works best for YouTube and TikTok. Instagram and some others often need a logged-in visitor. Then either they save those videos themselves (above), or, only if they say yes, add `--browser chrome` (or safari, firefox, edge) to use their own browser's login, on their computer. On a Mac this may ask them to allow access in a Keychain window.
- If a link fails, fetch.py says why and moves on. Don't retry the same blocked link over and over.

## "Just go look at my Instagram"

If you have a browser tool (Claude in Chrome, the ChatGPT browser), you can open their profile with them, find the videos that fit (the grid shows views on reels), and collect the links. The downloading still happens with fetch.py or by them; a browser can't save a video file for you. Never type their password: if a site wants them logged in, they log in themselves.

## The fallback that always works: screen recording

Play the video full screen on their phone and screen-record it.
- **iPhone:** Control Center > Screen Recording. **Android:** Quick Settings > Screen record, with media sound on.
- Trim the start and end, and tell you if app buttons or a watermark show (so you don't mistake them for the style).
- Then AirDrop or upload the recording into the folder.

## Performance data (optional, very useful)

Views tell you what worked; a retention graph tells you where people left. Ask for screenshots of their insights for the videos you're studying (Instagram Insights, TikTok Analytics, YouTube Studio > Analytics > audience retention). Note them in `videos.md` and look at what the edit did right before each drop.

## Rules

- Only download videos they're allowed to: their own, or other people's public videos to study privately. Never reuse anyone else's footage, music, logos or text in an edit; learn the style only.
- Never ask for or type their passwords.
- Keep the originals as they are. The analysis only reads them.
