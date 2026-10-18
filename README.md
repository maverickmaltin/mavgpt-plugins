# MavGPT plugins

Free plugins from [Maverick Maltin](https://mavgpt.ai) that make Claude (and Codex) do the work for you.

| Plugin | What it does | Works in | Guide |
| --- | --- | --- | --- |
| **Video Editor** (`video-editor`) | Edits your videos: captions, silence cuts, zooms, titles, b-roll and music. Plans every edit as a storyboard first, and saves your own editing style. | Claude (desktop app Code tab, or Claude Code) | [Claude Can Now Edit Videos For You](https://mavgpt.ai/resources/make-videos-using-claude) |
| **AI File System** (`ai-file-system`) | Builds one organized folder that your AI reads before every task, through a short interview, then keeps it up to date. | Claude (desktop app or Claude Code) and Codex | [AI File System Setup](https://mavgpt.ai/resources/ai-file-system-setup-guide-2026) |

## Install in the Claude desktop app (easiest)

Needs a paid Claude plan (Pro, Max, Team or Enterprise).

1. Open **Customize** in the left sidebar and go to **Plugins**.
2. Click **Add**, then **Add marketplace**, then **Add from a repository**.
3. Paste `https://github.com/maverickmaltin/mavgpt-plugins` and confirm.
4. Find **Video Editor** or **AI File System** in the list and add it.

Plugins you add here are saved to your Claude account and also show up in the desktop app's **Code** tab and in Claude Code.

## Install in Claude Code (terminal)

```
/plugin marketplace add https://github.com/maverickmaltin/mavgpt-plugins.git
/plugin install video-editor@mavgpt
/plugin install ai-file-system@mavgpt
```

To get updates automatically: `/plugin`, then **Marketplaces**, select **mavgpt**, then **Enable auto-update**.

## Install in Codex

```
codex plugin marketplace add maverickmaltin/mavgpt-plugins
codex plugin add ai-file-system@mavgpt
```

Then restart the ChatGPT desktop app (or start a new Codex session). You can also find it in the Plugins directory after adding the marketplace.

## Use them

- **Video Editor:** open the Claude desktop app's **Code** tab in a folder for your videos (Local > Select folder), pick Opus 5.5 with Max effort, and type `/video-editor:start`. It installs what it needs, builds your editing style, and edits your first video with you. After that: `/video-editor:edit`, `/video-editor:style`, `/video-editor:clips`.
- **AI File System:** open a new, empty folder (for example "Alex OS") in Claude or Codex and say "Set up my AI file system" (in Claude you can also type `/ai-file-system:setup`). Afterwards: "remember this", `/ai-file-system:add-workspace`, `/ai-file-system:tidy`, `/ai-file-system:import-history`.

## Privacy

Everything runs on your own computer through your own Claude or Codex account. These plugins don't send your videos or files anywhere except to Claude or Codex as you work, and to services you choose to connect (like Higgsfield). They never post, send or delete anything without asking you first.

## License

MIT. Free to use, share and adapt.
