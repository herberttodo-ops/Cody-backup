# Multi-Agent Vault Setup Checklist

Use this when setting up Obsidian vault memory for the first time or adding a new agent.

## Step 1: Resolve Vault Path

```bash
echo "Vault: ${OBSIDIAN_VAULT_PATH:-/home/herby/Documents/Obsidian Vault}"
VAULT="${OBSIDIAN_VAULT_PATH:-/home/herby/Documents/Obsidian Vault}"
```

## Step 2: Verify Vault Exists

```bash
ls -la "$VAULT/" 2>/dev/null || mkdir -p "$VAULT"
```

## Step 3: Create Folder Structure

```bash
# Shared (all agents)
mkdir -p "$VAULT/Agent-Shared"

# Agent-specific (one per agent)
mkdir -p "$VAULT/Agent-Hermes/daily"
mkdir -p "$VAULT/Agent-OpenClaw/daily"  # add more as needed

# Templates
mkdir -p "$VAULT/Templates"
```

## Step 4: Create Shared Files

### user-profile.md
Capture: name, timezone, communication preferences, active projects, technical setup.
**When to update:** Any time the user corrects you or expresses a preference.

### project-state.md
Capture: all active projects with status, last action, next action.
**When to update:** After any task completion that changes project status.

### decisions-log.md
Capture: date, decision, reason, impact.
**When to update:** Immediately after a significant decision.

## Step 5: Create Agent-Specific Files

For EACH agent (Hermes, Herby, etc.):

### working-context.md
- Current focus
- Recent issues fixed
- Technical state (PIDs, ports, model)
- Active tools/files being monitored
- Notes for other agents

### mistakes.md
- Errors made and lessons learned
- User corrections
- Wrong debugging paths taken

### daily/YYYY-MM-DD.md
- Morning checklist
- Tasks with status
- Key events and decisions
- Next session notes

## Step 6: Create Index.md

Master index linking all files. Include the 4-layer memory architecture and read-order protocol.

## Step 7: Create Templates

### Daily Note Template
```markdown
# YYYY-MM-DD
## Morning Checklist
- [ ] Read [[working-context]]
- [ ] Read [[project-state]]
- [ ] Check gateway status
## Tasks
| Task | Status | Notes |
|------|--------|-------|
| | | |
## Key Events
## Decisions Made
## Errors / Lessons
## Next Session Notes
```

### Project Template
```markdown
# Project: {{name}}
## Status
- Current Phase:
- Health: green/yellow/red
## Key People
## Resources
## Notes
```

## Step 8: Update System Prompt Files

- **AGENTS.md** — Add Obsidian vault read requirement to session startup checklist
- **MEMORY.md** — Convert to routing index: "Detailed info lives in vault"
- **SOUL.md** — No changes needed

## Step 9: Test Read Order

Simulate a session start by reading in order:
1. user-profile.md
2. project-state.md
3. working-context.md (your agent)
4. daily/*.md (today + yesterday)

## Step 10: Set Checkpoint Habit

Agree on checkpoint frequency. Start with: **write checkpoint every 3 tool calls**.

## Cross-Agent Rules

| Rule | Violation |
|------|----------|
| Read Agent-Shared at every start | Forgot project status |
| Write project-state after tasks | Other agent doesn't know status |
| Never touch another agent's private folder | Data loss, confusion |
| Update decisions-log immediately | Repeated decisions, wasted time |
| Archive old sessions weekly | Context pressure failures |
