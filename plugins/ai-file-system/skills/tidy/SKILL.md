---
name: tidy
description: Clean up the user's AI file system so it stays small, current and easy for AI to use. Use when they say "tidy my file system", "clean up my folder", "my AI is getting confused", or run /ai-file-system:tidy. Good to run about once a month.
---

# AI File System: monthly tidy

Check first, then show a short list of proposed changes and wait for OK before moving or deleting anything. Fixing out-of-date lines inside these files is fine without asking.

1. **Current files:** shorten CURRENT.md and each workspace CURRENT.md. Move finished items to "Recently done" (keep the last few) and delete stale ones.
2. **One home per fact:** look for the same fact in several files. Keep it in its home (see the remember skill's table) and replace the copies with a pointer.
3. **Conflicts:** find instructions that contradict each other. Ask which one is right, then fix both places.
4. **Size:** AGENTS.md under about 150 lines, MEMORY.md under about 30 lines. Move detail into context files or workspace guides.
5. **Links:** every path in AGENTS.md, FOLDER-MAP.md and the guides should exist. Fix or remove broken ones.
6. **Clutter:** duplicate files, old copies ("final-v2-copy"), empty folders and loose files at the top level. Propose where each belongs. Ask before deleting anything.
7. **Privacy:** scan for passwords, account numbers, ID numbers or API keys and suggest removing them.
8. **Workspaces:** suggest archiving areas that have had nothing active for a long time (move to `workspaces/_archive/`), and adding ones they keep asking about.

Finish with a three-line summary of what changed and anything waiting on them.
