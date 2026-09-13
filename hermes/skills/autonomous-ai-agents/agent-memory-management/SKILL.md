---
name: agent-memory-management
description: Persistent memory system for AI agents using Obsidian vaults. Prevents information loss between sessions, reduces token bloat, and enables multi-agent coordination.
version: 1.0.0
author: Hermes Agent
category: autonomous-ai-agents
metadata:
  hermes:
    tags: [memory, obsidian, persistence, agents, vault]
---

# Agent Memory Management

Persistent memory system for AI agents using Obsidian vaults. Prevents information loss between sessions, reduces token bloat, and enables multi-agent coordination.

## Motivation

Without persistent memory, agents lose context between sessions. The typical failure mode is that **session history accumulates until it exceeds the model's token budget** (often 300k+ tokens after days of use), causing every prompt to fail with:

```
LLM request failed. rawError=Provider returned an incomplete or malformed tool call
```

The root cause is context pressure — the model receives the full conversation history plus the current prompt, exceeding its budget. Persistent memory solves this by storing important state in files instead of relying on the model's context window.

## 4-Layer Memory Architecture

| Layer | Source | Purpose | How to Access |
|-------|--------|---------|---------------|
| 1 | Built-in memory (~2,200 chars) | Compact facts, auto-injected | Injected every prompt |
| 2 | AGENTS.md + SOUL.md | Operating instructions, personality | Injected every prompt |
| 3 | **Obsidian Vault** | Detailed state, cross-agent shared | Read via `read_file`, write via `write_file`/`patch` |
| 4 | Session Search | Past conversation archive | Query via `session_search` |

**Layer 3 (the vault) is the key.** It moves detailed state out of the model's context window and into persistent files.

## Vault Path

Resolve before using:

```bash
# Method 1: Environment variable
env | grep OBSIDIAN_VAULT_PATH
# Expected: /home/herby/Documents/Obsidian Vault

# Method 2: Default location
ls -d ~/Documents/Obsidian Vault 2>/dev/null || echo "Vault not at default location"
```

**Note:** Do NOT pass paths with spaces through shell variables to file tools. Use concrete absolute paths.

## Vault Folder Structure (Multi-Agent)

```
~/Documents/Obsidian Vault/
├── Index.md                           # Master index — start here
│
├── Agent-Shared/                      # ALL AGENTS read/write
│   ├── user-profile.md                # Who the user is, preferences, corrections
│   ├── project-state.md               # All projects, current status, blockers
│   └── decisions-log.md               # Decision history with dates + rationales
│
├── Agent-Hermes/                      # Hermes private — DO NOT TOUCH by other agents
│   ├── working-context.md             # What Hermes is actively doing RIGHT NOW
│   ├── mistakes.md                    # Honest log of errors + lessons
│   └── daily/
│       └── YYYY-MM-DD.md              # One file per day
│
├── Agent-OpenClaw/                    # Herby private — DO NOT TOUCH by other agents
│   ├── working-context.md             # What Herby is doing NOW
│   ├── mistakes.md                    # Herby's errors + lessons
│   └── daily/
│       └── YYYY-MM-DD.md
│
└── Templates/                         # Reusable note templates
    ├── Daily Note Template.md
    └── Project Template.md
```

## The Shared Files (Agent-Shared/)

These are the CONTRACT between agents. Every agent MUST read these at session start.

### user-profile.md
**What it is:** The user's identity, preferences, communication style, technical setup.
**Who writes it:** Any agent that learns something new about the user.
**When to read:** EVERY session start.
**When to write:** When the user corrects you, expresses a preference, or when you discover something worth remembering.

### project-state.md
**What it is:** Dashboard of all active projects — status, last action, next action.
**Who writes it:** Any agent after completing a task that changes project status.
**When to read:** EVERY session start (know what's happening).
**When to write:** After task completion, status changes, or blockers encountered.

### decisions-log.md
**What it is:** Important decisions with date, reason, and impact.
**Who writes it:** Any agent that makes or witnesses a significant decision.
**When to read:** When investigating why something was done a certain way.
**When to write:** Immediately after a decision is made.

## Private Folders (per agent)

Each agent has its own private folder. Other agents **NEVER** modify files outside their own folder.

### working-context.md
**What it is:** Current session's focus, active tasks, what's being built/debugged.
**When to update:** At task start, every checkpoint, task completion.

### mistakes.md
**What it is:** Honest log of things you got wrong and how to avoid repeating them.
**When to write:** After the user corrects you, after a debugging path fails, when you misdiagnose.
**Why:** Future-you will read this and avoid the same mistake.

### daily/YYYY-MM-DD.md
**What it is:** Daily journal of tasks, decisions, errors, and next-session notes.
**When to create:** At the start of a new day (first task of the day).
**When to update:** Every 3-5 tool calls, at task completion.

## Session Startup Protocol

**Before doing anything else, read in this order:**

1. **AGENTS.md** (injected automatically — confirms startup checklist)
2. **SOUL.md** (injected automatically — personality + operating style)
3. **Agent-Shared/user-profile.md** — WHO am I helping?
4. **Agent-Shared/project-state.md** — WHAT'S happening?
5. **Agent-Hermes/working-context.md** (or Agent-OpenClaw equivalent) — What was I doing?
6. **Agent-Hermes/daily/*.md** — Today's and yesterday's daily notes

Then proceed with the user's request.

**In OpenClaw (Herby):** The same protocol applies, but with `Agent-OpenClaw/` files.

## Checkpoint Protocol

During long tasks, write state to the vault so that if context compacts or the session resets, work isn't lost.

| Trigger | Action | Target File |
|---------|--------|-------------|
| Task started | Update working-context.md with current focus | `working-context.md` |
| Every 3-5 tool calls | Add checkpoint to daily note | `daily/YYYY-MM-DD.md` |
| Task completed | Update project-state.md status | `project-state.md` |
| Decision made | Append to decisions-log.md | `decisions-log.md` |
| User corrected you | Log in mistakes.md | `mistakes.md` |
| User expressed preference | Update user-profile.md | `user-profile.md` |
| Context compacted | Re-read vault files | All key files |

## Cross-Agent Coordination Rules

1. **Read shared files, write shared files:** Both agents can read/write `Agent-Shared/` files. This is the coordination mechanism.
2. **Respect private folders:** Hermes never touches `Agent-OpenClaw/`. Herby never touches `Agent-Hermes/`.
3. **Update project-state when you finish:** If Hermes completes a LotSignal task, update `project-state.md` so Herby knows next time he starts.
4. **Don't duplicate decisions:** If a decision is already in `decisions-log.md`, don't add it again.

## Avoiding Context Pressure (Session History Overflow)

This is the #1 cause of agent failures in multi-day sessions. When sessions accumulate:

```bash
# Check if your agent is at risk
ls ~/.openclaw/agents/main/sessions/ | wc -l
# → 8648 files = DANGER

du -sh ~/.openclaw/agents/main/sessions/
# → 538MB = DANGEROUS
```

**Prevention:**
- Start fresh sessions with `/new` (Telegram) periodically
- Archive old sessions older than 1 day: `find sessions -mtime +1 -exec mv archive/ {} \;`
- Vacuum SQLite DB: `sqlite3 openclaw-agent.sqlite "VACUUM;"`
- Monitor weekly

**If already broken (348k tokens):**
```bash
# Archive old session files
mkdir -p ~/.openclaw/agents/main/sessions-archive
find ~/.openclaw/agents/main/sessions -name "*.jsonl" -type f -mtime +1 \
  -exec mv {} ~/.openclaw/agents/main/sessions-archive/ \;

# Start fresh
# Send /new in Telegram or open a new conversation
```

See `references/session-archive-script.md` for the full cleanup script.

## MEMORY.md as Routing Index

The old `MEMORY.md` (in the workspace, often `~/.openclaw/workspace/MEMORY.md`) is now a **routing index** — compact pointers that say "detailed info lives in these vault files." This keeps the lightweight memory compact (~2,200 chars) so it stays under the auto-injected budget.

## Key Principle

**Text > Brain.** If you want to remember something between sessions, WRITE IT TO A FILE. Mental notes don't survive session restarts. Files do.

## Support Files

- `references/session-archive-script.md` — Full session cleanup script with vacuum
- `references/multi-agent-setup-checklist.md` — Step-by-step setup for new agents
- `references/herby-obsidian-setup-prompt.md` — Ready-to-give prompt for Herby to set up his vault folder
