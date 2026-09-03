---
name: openclaw-troubleshooting
description: "Troubleshoot and fix OpenClaw startup failures, migration issues, and database lock problems."
version: 1.0.0
author: Hermes Agent
platforms: [linux]
metadata:
  hermes:
    tags: [openclaw, troubleshooting, migration, nodejs, database, repair]
---

# OpenClaw Troubleshooting

Fix OpenClaw when it won't start, crashes on startup, or displays "Legacy session store requires migration" errors.

## Quick Fixes (try in order)

### 1. Legacy Session Store Migration

**Symptom:** Error message: `"Legacy session store requires migration: /home/herby/.openclaw/agents/main/sessions/sessions.json"`

**Fix:**
```bash
# First check Node.js version (must be >=22.22.3)
node --version

# Migrate: This runs the fix and migrates all legacy state
openclaw doctor --fix
```

**What gets migrated:**
- Session store (JSON → SQLite)
- Plugin catalogs (JSON → SQLite)
- TUI last-session pointers
- Config audit logs
- Crestodian audit logs
- Workspace attestations
- Model credentials

---

### 2. Node.js Version Too Old

**Symptom:** Error on startup: `"Node.js >=22.22.3 <23, >=24.15.0 <25, or >=25.9.0 is required"`

**Fix without sudo (local install):**
```bash
# Download and extract newer Node locally
cd /tmp
curl -fsSL "https://nodejs.org/dist/v22.23.2/node-v22.23.2-linux-x64.tar.xz" -o node.tar.xz
tar -xf node.tar.xz

# Use local Node instead of system Node
export PATH="/tmp/node-v22.23.2-linux-x64/bin:$PATH"

# Verify
node --version

# Now run OpenClaw
doctor --fix
openclaw
```

**Alternative with apt (requires sudo):**
```bash
sudo apt update
sudo apt upgrade -y nodejs
```

---

### 3. Database Locked / Another Gateway Running

**Symptom:** Error: `"another Gateway owns that state directory"` or database locked errors.

**Fix - Kill zombie processes:**
```bash
# Find what's holding the database
fuser ~/.openclaw/state/openclaw.sqlite

# Kill any OpenClaw/Node processes
pkill -9 -f "openclaw"
pkill -9 node

# Wait for processes to die
sleep 3

# Verify database is free
fuser ~/.openclaw/state/openclaw.sqlite
# Should return nothing ("No processes using file")

# Now retry migration
openclaw doctor --fix
```

---

### 4. Start After Migration

Once `doctor --fix` succeeds:

```bash
# Normal start
openclaw

# Or background/detached
openclaw > ~/.openclaw/logs/openclaw.log 2>&1 &

# Use local Node version if system Node is incompatible
export PATH="/tmp/node-v22.23.2-linux-x64/bin:$PATH"
openclaw
```

---

### 5. Telegram Bot Token Format Change (v2026.8.1+)

**Symptom:** Gateway starts but Telegram channel exits immediately with:
```
[telegram] [default] Telegram bot token unauthorized for account "default"
(getMe returned 404 from Telegram; source: config token)
```

**Root Cause:** OpenClaw v2026.8.1 changed the config format from:
- OLD: `channels.telegram.botToken`
- NEW: `channels.telegram.accounts.default.botToken`

The `doctor --fix` migration updates the structure but **cannot unmask tokens** that were saved as `***` in the config file. The old masked token fails validation in the new format.

**Fix:**

**Step 1: Find the real token**
```bash
# Check backup configs for unmasked token
python3 -c "
import json, glob
for backup in sorted(glob.glob('/home/herby/.openclaw/openclaw.json.bak*'), reverse=True):
    with open(backup) as f:
        config = json.load(f)
    token = config.get('channels', {}).get('telegram', {}).get('botToken', '')
    if token and not token.endswith('***'):
        print(f'Found token in: {backup}')
        print(f'Token: {token}')
        break
"
```

**Step 2: Update config with correct format**
```bash
openclaw config set channels.telegram.accounts.default.botToken "YOUR_REAL_TOKEN_HERE"
```

**Step 3: Restart gateway**
```bash
systemctl --user restart openclaw-gateway.service
```

**Verification:**
```bash
journalctl --user -u openclaw-gateway.service --since "1 minute ago" | grep telegram
# Should show: [telegram] [default] channel started
```

---

## Multiple Agents Migration Gotcha

**Problem:** `openclaw doctor --fix` only migrates the agent you run it from. If you have multiple agents (e.g., `main`, `claude-code`, `kimi`), each has its own `sessions.json` and each may need migration.

**Fix:** Check all agents for legacy sessions:
```bash
# Check which agents have legacy sessions
ls ~/.openclaw/agents/*/sessions/sessions.json

# Check stability logs for which agent is failing
grep -r "agents/" ~/.openclaw/logs/stability/*.json | grep "session store requires migration"

# The error message tells you WHICH agent:
# "Legacy session store requires migration: /home/herby/.openclaw/agents/CLAU..."
#                                                    ^^^^^^^^^^^
#                                                    This agent needs migration

# If doctor refuses to migrate because a gateway owns the state:
# 1. Stop the gateway
systemctl --user stop openclaw-gateway.service
# 2. Kill any remaining processes
pkill -9 -f "openclaw"
sleep 3
# 3. Run doctor
openclaw doctor --fix
# 4. Restart
systemctl --user start openclaw-gateway.service
```

---

## Orphan Session Files

**Symptom:** After migration, doctor reports "Found 2707 orphan transcript files" in `~/.openclaw/agents/main/sessions/`.

**Meaning:** These `.jsonl` files are no longer referenced by the new SQLite session store. They are dead weight.

**Fix (optional cleanup):**
```bash
# Archive orphans by renaming (reversible)
for f in ~/.openclaw/agents/main/sessions/*.jsonl; do
  mv "$f" "$f.orphan.$(date +%Y%m%d)"
done
```

Or leave them — they do not block startup.

---

## Gateway Runs But Control UI Shows "Did Not Start"

**Symptom:** `ps aux` shows the gateway process running. Port responds with HTML. But the page shows "Control UI did not start" and the JS bundle never loads.

**Causes & Fixes:**
1. **Browser cache** — Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
2. **Service worker stale** — Open DevTools → Application → Service Workers → Unregister, then reload
3. **Asset version mismatch** — The gateway may have restarted with a different version but the browser still references old hashed JS/CSS files. Clear site data for `localhost:18789`.
4. **Check for JS console errors** — Open DevTools Console for module loading errors.

**Quick recovery:**
```bash
# Force a fresh page load that bypasses cache
curl -s -H "Cache-Control: no-cache" http://localhost:18789/ > /dev/null
# Then reload browser with Ctrl+Shift+R
```

---

## Diagnostic Commands

### Check what processes are running:
```bash
ps aux | grep openclaw
ps aux | grep "node" | grep -v grep
```

### Check logs:
```bash
ls -la ~/.openclaw/logs/stability/
cat ~/.openclaw/logs/stability/openclaw-stability-*.json
```

### Check session files:
```bash
ls -la ~/.openclaw/agents/main/sessions/
```

### Check who holds the database lock:
```bash
fuser -v ~/.openclaw/state/openclaw.sqlite
```

---

## Session Recovery (if history was lost)

If you had to move `sessions.json` for migration, it's backed up to:
```bash
~/.openclaw/backup/sessions.json.bak.YYYYMMDD_HHMMSS
```

Session history is preserved during migration but the format changes from JSON to SQLite. The migration copies all data into the SQLite database.

---

## Common Error Patterns

| Error | Meaning | Fix |
|-------|---------|-----|
| `Legacy session store requires migration` | Old JSON format needs to become SQLite | `openclaw doctor --fix` |
| `Node.js >=22.22.3 required` | System Node too old | Use local Node binary (see #2) |
| `Another Gateway owns that state` | Zombie process holds database lock | Kill all node/openclaw processes |
| `Gateway startup failed` repeated | The failed process keeps crashing | Kill processes, check Node version, then migrate |

---

## Preconditions Checklist

Before troubleshooting, verify:
- [ ] Node.js version compatible (check with `node --version`)
- [ ] No zombie processes holding the database (check with `fuser`)
- [ ] Can access `~/.openclaw/state/openclaw.sqlite` (not locked)
- [ ] Can write to `~/.openclaw/` directory

---

## Support Files

- See `references/` directory for migration logs and session-specific details.
