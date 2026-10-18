# AI File System

One organized folder that Claude and Codex read before every task, so they already know who you are, what you're working on and how you like things done. A guided interview builds it for you.

Full guide: https://mavgpt.ai/resources/ai-file-system-setup-guide-2026

## Start

Open a new, empty folder (for example "Alex OS") in the Claude desktop app, Claude Code or Codex and say **"Set up my AI file system."** In Claude you can also type `/ai-file-system:setup`.

## Skills

| Skill | What it does |
| --- | --- |
| `setup` | Interviews you, optionally imports your ChatGPT or Claude history, builds and checks every file |
| `remember` | "Remember this": saves a fact or preference to its one right place |
| `add-workspace` | Adds a new area (job, client, project, part of life) |
| `tidy` | Monthly cleanup: stale notes, duplicates, broken links. Asks before deleting |
| `import-history` | Brings in a ChatGPT or Claude data export in safe, resumable batches |

## What it builds

`START-HERE.md`, `AGENTS.md` (the shared rulebook, read automatically by Codex), `CLAUDE.md` (points Claude at AGENTS.md), `CURRENT.md`, `MEMORY.md`, `FOLDER-MAP.md`, `context/` (about you, your work, preferences, voice) and `workspaces/<area>/` (guide, current status, outputs, resources).
