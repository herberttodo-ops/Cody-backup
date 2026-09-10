# OpenClaw Troubleshooting Transcript — Multiple Agent Migration

**Date:** 2026-09-01  
**Problem:** OpenClaw gateway crash-looping after Node.js / openclaw version upgrade. 20+ `gateway.startup_failed` events in 4 minutes.  
**Root cause:** `main` agent migrated successfully earlier, but `claude-code` agent still had legacy `sessions.json` blocking all gateway startups.

---

## Timeline of Fixes Applied

### 1. Initial Error — Legacy Session Store (main agent)

```json
{
  "reason": "gateway.startup_failed",
  "error": {
    "message": "Legacy session store requires migration: /home/herby/.openclaw/agents/main/sessions/sessions.json. Run \"openclaw doctor --fix\" ..."
  }
}
```

### 2. Blocked — Node.js Version Too Old

System Node: `v22.22.0`  
Required: `>=22.22.3`

**Fix:** Downloaded portable Node to `/tmp/node-v22.23.2-linux-x64/bin/node` and used it via `PATH` override.

### 3. Blocked — Another Gateway Owns State Directory

Error:
```
Another gateway (pid X) already owns this state directory;
refusing to run automatic startup migrations
```

**Fix:** Killed all zombie `node` / `openclaw` processes with `pkill -9`, verified database lock released via `fuser`.

### 4. First Migration Succeeded (main agent)

`openclaw doctor --fix` completed and migrated:
- 3 plugin catalogs (anthropic, ollama, openrouter)
- 1 model credential
- 9 config audit log rows
- 1 Crestodian audit log
- TUI pointers, workspace attestations

### 5. Gateway Still Crash-Looping After Migration

20+ new `gateway.startup_failed` events appeared.  
Investigated latest stability log:

```json
{
  "error": {
    "message": "Legacy session store requires migration: /home/herby/.openclaw/agents/claude-code/sessions/sessions.json"
  }
}
```

### 6. Discovery — Multiple Agents

Found three agent directories:
```
~/.openclaw/agents/claude-code/sessions/sessions.json   (2 bytes — empty)
~/.openclaw/agents/kimi/                                (no sessions.json)
~/.openclaw/agents/main/                                (already migrated)
```

### 7. Final Fix

Killed running gateway process again (PID holding the SQLite lock), then re-ran `openclaw doctor --fix`. The second pass migrated the `claude-code` agent. Gateway started successfully.

---

## Key Commands Used

```bash
# Check which Node version is active
node --version

# Check for multiple agents with legacy sessions
ls ~/.openclaw/agents/*/sessions/sessions.json

# Check who holds the database lock
fuser -v ~/.openclaw/state/openclaw.sqlite

# Kill all OpenClaw / node processes
pkill -9 -f "openclaw"
pkill -9 node
sleep 3

# Verify lock released
fuser ~/.openclaw/state/openclaw.sqlite
# Should return nothing

# Run migration with portable Node
export PATH="/tmp/node-v22.23.2-linux-x64/bin:$PATH"
openclaw doctor --fix

# Check latest stability failure reason
ls -lt ~/.openclaw/logs/stability/
cat ~/.openclaw/logs/stability/openclaw-stability-*.json
```

---

## Pitfalls Encountered

1. **Assuming one `doctor --fix` covers all agents** — It does not. Each agent directory with a legacy `sessions.json` must be migrated.
2. **Not checking all agent directories** — The `main` agent migration masked the `claude-code` agent issue.
3. **Not checking the *latest* stability log** — Earlier logs showed the `main` agent error; later logs (with newer timestamps) revealed the `claude-code` error.
4. **Gateway lock contention** — A running gateway process holds the SQLite lock, preventing `doctor` from mutating shared state. Must kill the process before re-running doctor.

---

## Verification After Fix

```bash
# Gateway process running
ps aux | grep openclaw
# → PID ... node .../openclaw/dist/index.js gateway --port 18789

# Health endpoint responds
curl -s --max-time 5 http://localhost:18789/__openclaw__/health
# → Returns HTML (Control UI page)

# No new stability failures
ls -lt ~/.openclaw/logs/stability/ | head -5
# → No new files in last minute
```
