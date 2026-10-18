---
name: add-workspace
description: Add a new workspace (a new area of life, job, business, client or project) to the user's AI file system. Use when they say "add a workspace for...", "I started a new project", "set up a folder for my new client", or run /ai-file-system:add-workspace.
---

# AI File System: add a workspace

1. Read AGENTS.md and FOLDER-MAP.md so you know the existing workspaces. If the new area really belongs inside an existing one, say so and offer that instead.
2. Ask two or three quick questions: what the area is, what's active in it right now, any repeated task in it, and whether it must stay separate from another area.
3. Pick a short lowercase folder name (for example `workspaces/client-acme/`). Create `guide.md` and `CURRENT.md` from the workspace templates in `${CLAUDE_PLUGIN_ROOT}/skills/setup/templates/workspace/` (in Codex, the setup skill's `templates/workspace` folder), plus empty `outputs/` and `resources/` folders.
4. Add a row to FOLDER-MAP.md, add the name to the workspace list in AGENTS.md, and add a line to the table in CURRENT.md.
5. If it must stay separate from another area, add that to the "Never mix" line in AGENTS.md.
6. Confirm in two lines what you created.
