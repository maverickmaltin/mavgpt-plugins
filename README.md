# MavGPT plugins

Free plugins from [Maverick Maltin](https://mavgpt.ai) that make Claude (and Codex) do the work for you.

| Plugin | What it does | Works in | Guide |
| --- | --- | --- | --- |
| **Video Editor** (`video-editor`) | Your own AI video editor: studies your videos (or creators you love) frame by frame, writes your personal editing skill, then edits every new video in that style. | Claude (desktop app Code tab, or Claude Code) and ChatGPT (Codex in the desktop app) | [ChatGPT and Claude Can Now Edit Your Videos](https://mavgpt.ai/resources/ai-can-now-edit-videos-for-you) |
| **AI File System** (`ai-file-system`) | Builds one organized folder that your AI reads before every task, through a short interview, then keeps it up to date. | Claude (desktop app or Claude Code) and Codex | [AI File System Setup](https://mavgpt.ai/resources/ai-file-system-setup-guide-2026) |

## Install in the Claude desktop app (easiest)

Needs a paid Claude plan (Pro, Max, Team or Enterprise).

1. Open **Customize** in the left sidebar and go to **Plugins**.
2. Click **+ Add**, then **Add marketplace**, then **Add from a repository**.
3. Paste `maverickmaltin/mavgpt-plugins` into **URL** and click **Sync**.
4. Find **Video Editor** or **AI File System** in the list and add it.

Plugins you add here are saved to your Claude account and also show up in the desktop app's **Code** tab and in Claude Code.

## Install in Claude Code (terminal)

```
/plugin install video-editor --marketplace maverickmaltin/mavgpt-plugins
/plugin install ai-file-system --marketplace maverickmaltin/mavgpt-plugins
```

Or add the marketplace once (`/plugin marketplace add maverickmaltin/mavgpt-plugins`) and install with `/plugin install video-editor@mavgpt`. To get updates automatically: `/plugin`, then **Marketplaces**, select **mavgpt**, then **Enable auto-update**.

## Install in ChatGPT (Codex)

In the ChatGPT desktop app, switch to **Codex** and ask it to run these (or run them in a terminal):

```
codex plugin marketplace add maverickmaltin/mavgpt-plugins
codex plugin add video-editor@mavgpt
codex plugin add ai-file-system@mavgpt
```

Then restart the ChatGPT desktop app (or start a new Codex session).

## Use them

- **Video Editor:** open the Claude desktop app's **Code** tab (or Codex in the ChatGPT desktop app) on a folder for your videos, pick the strongest model with high effort, and type `/video-editor:start` (Codex: `$video-editor:start`). It installs what it needs, asks whether to copy your style or build a new one, studies your videos frame by frame, writes your editing skill and edits your first video with you. After that: `/video-editor:edit`, `/video-editor:style`, `/video-editor:breakdown`, `/video-editor:clips`.
- **AI File System:** open a new, empty folder (for example "Alex OS") in Claude or Codex and say "Set up my AI file system" (in Claude you can also type `/ai-file-system:setup`). Afterwards: "remember this", `/ai-file-system:add-workspace`, `/ai-file-system:tidy`, `/ai-file-system:import-history`.

## Privacy

Everything runs on your own computer through your own Claude or Codex account. These plugins don't send your videos or files anywhere except to Claude or Codex as you work, and to services you choose to connect (like Higgsfield). They never post, send or delete anything without asking you first.

## License

MIT. Free to use, share and adapt.
