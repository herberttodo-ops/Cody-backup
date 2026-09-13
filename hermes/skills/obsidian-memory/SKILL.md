---
name: obsidian-memory
description: Read and write to the Obsidian vault for persistent memory across sessions.
version: 1.0
author: Hermes
---

# Obsidian Memory

Persistent memory lives in the Obsidian vault at `~/Documents/Obsidian Vault`.

## 4-Layer System

| Layer | Location | Purpose | Who |
|-------|----------|---------|-----|
| 1 | Built-in memory (~2,200 chars) | Compact facts | Auto |
| 2 | AGENTS.md + SOUL.md | Operating instructions | Auto |
| 3 | Obsidian Vault | Detailed state | Read/Write |
| 4 | Session Search | Past conversations | Query |

## Vault Structure

```
~/Documents/Obsidian Vault/
├── Index.md                    # Master index
├── Agent-Shared/               # Hermes + Herby
│   ├── user-profile.md         # Who Andrew is
│   ├── project-state.md        # All projects status
│   └── decisions-log.md        # Decision history
├── Agent-Hermes/               # Hermes private
│   ├── working-context.md      # What I'm doing NOW
│   ├── mistakes.md             # Things I got wrong
│   └── daily/                  # One file per day
├── Agent-OpenClaw/             # Herby private (don't touch)
└── Templates/                  # Note templates
    ├── Daily Note Template.md
    └── Project Template.md
```

## Required Files to Read At Session Start

1. `Agent-Shared/user-profile.md`
2. `Agent-Shared/project-state.md`
3. `Agent-Hermes/working-context.md`
4. `Agent-Hermes/daily/YYYY-MM-DD.md` (today)
5. `Agent-Hermes/daily/YYYY-MM-DD.md` (yesterday)

## When to Write

| Trigger | File | Content |
|---------|------|---------|
| Task start | working-context.md | Update current focus |
| Every 3-5 tool calls | daily/YYYY-MM-DD.md | Checkpoint progress |
| Task completion | project-state.md, decisions-log.md | Status + decisions |
| Correction from user | mistakes.md | What went wrong |
| New preference | user-profile.md | Andrew's preferences |

## Quick Commands

```bash
# Today's note path
VAULT="/home/herby/Documents/Obsidian Vault"
TODAY=$(date +%Y-%m-%d)

# Read key files
read_file "$VAULT/Agent-Shared/user-profile.md"
read_file "$VAULT/Agent-Shared/project-state.md"
read_file "$VAULT/Agent-Hermes/working-context.md"

# Write checkpoint
patch "$VAULT/Agent-Hermes/daily/$TODAY.md" "## Checkpoint $(date +%H:%M)" "## Checkpoint $(date +%H:%M)\n- Updated..."
```
