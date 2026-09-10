# Telegram Token Troubleshooting for OpenClaw

## Quick Diagnosis (run these in order)

### 1. Is the gateway actually running?
```bash
ps aux | grep openclaw | grep gateway
curl -s http://localhost:18789/health
```
- If health returns `{"ok":true}` → gateway is alive (but Telegram may still be broken)
- If nothing responds → gateway is down, fix that first

### 2. Is the bot token valid? (Test BEFORE updating config)
```bash
curl -s "https://api.telegram.org/botYOUR_TOKEN/getMe"
```
- **Good:** `{"ok":true,"result":{"id":...,"is_bot":true,...}}`
- **Bad:** `{"ok":false,"error_code":404,"description":"Not Found"}`
  - Token is invalid, bot was deleted, or BotFather revoked it

### 3. Check channel status with --probe (not just status)
```bash
# WITHOUT --probe: shows cached config state only
openclaw channels status
# May show "enabled, configured" even when token is bad

# WITH --probe: actually tests the connection
openclaw channels status --probe
# Shows real health: running/connected vs error/stopped
```

**Example output when broken:**
```
- Telegram default: enabled, configured, 
  error:Telegram bot token unauthorized for account "default" 
  (getMe returned 404 from Telegram), 
  stopped, mode:polling, health:terminal-disconnect, probe failed
```

**Example output when fixed:**
```
- Telegram default: enabled, configured, running, connected, 
  transport:just now, mode:polling, bot:@YourBotName, works
```

### 4. Fix: Update token and restart gateway
```bash
# Set the new token
openclaw config set channels.telegram.accounts.default.botToken "YOUR_TOKEN"

# MUST restart gateway for token changes to take effect
# Option A: Kill PID and restart
ps aux | grep openclaw | grep gateway  # get PID
kill <PID>
sleep 3
openclaw gateway

# Option B: If using systemd
systemctl --user restart openclaw-gateway.service

# Wait 5-10 seconds, then verify
sleep 8
openclaw channels status --probe
```

## Common Pitfalls

| Pitfall | Why It Happens | Prevention |
|---------|---------------|------------|
| Updating token but not restarting gateway | Token is cached in memory at startup | Always restart after token changes |
| Using `channels status` without `--probe` | Shows stale config, not live health | Always use `--probe` for real status |
| Trusting `/health` endpoint | Only checks gateway process, not channels | Use `channels status --probe` |
| Testing token after config update | Wastes time if token is already bad | Test with `curl` BEFORE updating config |

## One-Liner Token Test
```bash
# Before touching config, verify the token works:
curl -s "https://api.telegram.org/bot${TOKEN}/getMe" | grep -q '"ok":true' && echo "✅ Token valid" || echo "❌ Token invalid"
```
