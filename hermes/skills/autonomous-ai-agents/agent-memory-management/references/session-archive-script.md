# Session Archive & Cleanup Script

When OpenClaw sessions accumulate, they cause context pressure — the model receives 300k+ tokens of history even for a 2-sentence prompt. Run this script regularly.

## Quick Diagnostic

```bash
# Check current risk level
echo "=== Session Files ==="
ls ~/.openclaw/agents/main/sessions/ | wc -l

echo ""
echo "=== Session Size ==="
du -sh ~/.openclaw/agents/main/sessions/

echo ""
echo "=== SQLite DB ==="
du -sh ~/.openclaw/agents/main/agent/openclaw-agent.sqlite
```

**Danger thresholds:**
- 1000+ files → Monitor
- 5000+ files → Archive immediately
- 538MB+ → Critical, will cause failures

## Archive Script (Safe — Reversible)

```bash
#!/bin/bash
# Save as ~/.openclaw/scripts/archive-sessions.sh

ARCHIVE_DIR="$HOME/.openclaw/agents/main/sessions-archive"
SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"

echo "Archiving old sessions..."

# Create archive dir if missing
mkdir -p "$ARCHIVE_DIR"

# Count before
BEFORE=$(ls "$SESSIONS_DIR" | wc -l)
echo "Before: $BEFORE files"

# Move sessions older than 1 day (preserves today's work)
find "$SESSIONS_DIR" -name "*.jsonl" -type f -mtime +1 \
  -exec mv {} "$ARCHIVE_DIR/" \; 2>/dev/null

# Count after
AFTER=$(ls "$SESSIONS_DIR" | wc -l)
ARCHIVED=$((BEFORE - AFTER))
echo "After: $AFTER files"
echo "Archived: $ARCHIVED files"

# Vacuum SQLite
echo ""
echo "Vacuuming SQLite DB..."
BEFORE_DB=$(du -b ~/.openclaw/agents/main/agent/openclaw-agent.sqlite | awk '{print $1}')

sqlite3 ~/.openclaw/agents/main/agent/openclaw-agent.sqlite "PRAGMA integrity_check;" 2>/dev/null
sqlite3 ~/.openclaw/agents/main/agent/openclaw-agent.sqlite "VACUUM;" 2>/dev/null

AFTER_DB=$(du -b ~/.openclaw/agents/main/agent/openclaw-agent.sqlite | awk '{print $1}')
SAVED=$((BEFORE_DB - AFTER_DB))
echo "SQLite DB reduced by $SAVED bytes"

echo ""
echo "Done. Archived to: $ARCHIVE_DIR"
```

## Aggressive Cleanup (Use When Already Broken)

If you're already at 348k tokens and getting LLM failures:

```bash
# Move ALL old sessions (not just +1 day)
mkdir -p ~/.openclaw/agents/main/sessions-archive-all
find ~/.openclaw/agents/main/sessions -name "*.jsonl" -type f \
  -exec mv {} ~/.openclaw/agents/main/sessions-archive-all/ \;

# Vacuum
sqlite3 ~/.openclaw/agents/main/agent/openclaw-agent.sqlite "VACUUM;"

# Restart gateway
kill $(pgrep -f "openclaw gateway")
sleep 3
openclaw gateway &
```

## Cron Job (Weekly)

```bash
# Add to crontab
crontab -e

# Add this line (runs Sundays at 3 AM)
0 3 * * 0 /bin/bash /home/herby/.openclaw/scripts/archive-sessions.sh >> /home/herby/.openclaw/logs/session-archive.log 2>&1
```

## What NOT to Delete

Keep these in `sessions/`:
- Files from today (active session)
- `.jsonl.lock` files (session locks)
- `skills-prompts` directory (skill prompt cache)

**Safe to archive:**
- `*.jsonl` files older than 1 day
- `*.jsonl.reset.*` files (reset backups)
- `*.jsonl.deleted.*.zst` files (compressed deleted sessions)
- `*.trajectory.jsonl` files (full trajectory logs — largest files)

## Recovery

If you archived something you need:

```bash
# List archived files
ls ~/.openclaw/agents/main/sessions-archive/

# Move specific file back
mv ~/.openclaw/agents/main/sessions-archive/SESSION_ID.jsonl \
   ~/.openclaw/agents/main/sessions/
```
