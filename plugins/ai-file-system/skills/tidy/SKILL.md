---
name: tidy
description: Clean up the user's AI file system so it stays small, current and easy for AI to use. Use when they say "tidy my file system", "clean up my folder", "my AI is getting confused", or run /ai-file-system:tidy. Good to run about once a month.
---

# AI File System: monthly tidy

Check first, then show a short list of proposed changes and wait for OK before moving or deleting anything. Fixing out-of-date lines inside these files is fine without asking.

1. **Current files:** shorten CURRENT.md and each workspace CURRENT.md. Move finished items to "Recently done" (keep the last few) and delete ones that are clearly done or replaced. If something is past its date but not clearly done, ask.
2. **One home per fact:** look for the same fact in several files. Keep it in its home (see the remember skill's table in `../remember/SKILL.md`) and replace the copies with a pointer. The one-line summaries in AGENTS.md ("Who I am", "How to work with me") are intentional; leave them.
3. **Conflicts:** find instructions that contradict each other. Ask which one is right, then fix both places.
4. **Size:** AGENTS.md under about 150 lines, MEMORY.md under about 30 lines. Move detail into context files or workspace guides.
5. **Links:** every path in AGENTS.md, FOLDER-MAP.md and the guides should exist. Fix or remove broken ones.
6. **Clutter:** duplicate files, old copies ("final-v2-copy"), empty folders (except each workspace's outputs/ and resources/) and loose files at the top level. Propose where each belongs. Ask before deleting anything.
7. **Privacy:** scan for passwords, account numbers, ID numbers or API keys and suggest removing them.
8. **Workspaces:** suggest archiving areas that have had nothing active for a long time (move to `workspaces/_archive/`), and adding ones they keep asking about.

Finish with a three-line summary of what changed and anything waiting on them.
