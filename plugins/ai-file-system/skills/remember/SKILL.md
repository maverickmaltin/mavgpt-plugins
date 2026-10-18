---
name: remember
description: Save something to the right place in the user's AI file system. Use when they say "remember this", "save that", "note that I prefer...", "from now on...", run /ai-file-system:remember, or at the end of a task when something lasting was learned.
---

# AI File System: remember something

Put each thing in its one narrowest home. Read the target file first, update it in place, and never create a duplicate.

| What it is | Where it goes |
| --- | --- |
| A fact about them (background, people, tools) | context/about-me.md |
| A fact about their job or business | context/work.md |
| How they like you to work, or a new permission rule | context/preferences.md (a hard rule also goes in AGENTS.md "My rules") |
| A writing correction ("I'd never say that") | context/voice.md, with the before and after |
| Project status, a decision, a deadline, a next step | that workspace's CURRENT.md |
| How a repeated task should be done | that workspace's guide.md |
| A preference that applies everywhere | MEMORY.md, one dated line |
| What's most important right now | CURRENT.md at the top level |

Rules:
- Only save what they actually said or confirmed. Don't turn a one-off request into a permanent rule; if unsure, ask "Should I make that a standing rule or was it just for this?"
- Overwrite stale lines instead of appending. Remove anything the new fact makes wrong.
- No passwords, account numbers, ID numbers or API keys, ever.
- Confirm in one line: what you saved and where.
