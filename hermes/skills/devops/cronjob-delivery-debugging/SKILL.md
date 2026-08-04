---
name: cronjob-delivery-debugging
title: "Cron Job Delivery Debugging"
category: "devops"
tags: [cron, troubleshooting, telegram, gateway, logs]
description: "Debug cron jobs that report 'ok' but never deliver output to the user. Diagnose silent delivery failures in the gateway/platform layer."
---

# Cron Job Delivery Debugging

## When to Use

A cron job appears to run successfully (`last_status: ok`) but the user never receives the output on Telegram, email, or other channels. The job executes but delivery fails silently.

## Symptoms
- `cronjob list` shows `last_status: ok` and recent `last_run_at`
- User reports: "You didn't send me the daily update" / "The bot is unresponsive"
- No error visible in cronjob status itself

## Diagnostic Steps

### 1. Verify the job state
```
cronjob list --include_disabled
```
Check:
- `enabled: true`
- `state: scheduled` (not paused)
- `last_status: ok`
- `last_run_at` is recent

If any of these are off, fix the job state first (resume, enable, etc.).

### 2. Check delivery target
Look at the `deliver` field. Common targets:
- `telegram` — routes to default Telegram chat
- `telegram:CHAT_ID` — specific chat
- `email:address` — email delivery
- `origin` — web chat
- `local` — local delivery only

If `deliver` is wrong or the chat ID changed, update it:
```
cronjob update --job_id JOB_ID --deliver telegram:NEW_CHAT_ID
```

### 3. Read gateway error logs
This is where silent delivery failures hide:
```bash
# Search for Telegram-related errors in the past few days
grep -i "telegram\|delivery\|gateway" ~/.hermes/logs/errors.log | tail -30

# Search for the specific job run time
grep "YYYY-MM-DD HH:" ~/.hermes/logs/errors.log | head -20

# Check gateway binary log (may be binary, use strings or grep -a)
grep -a "YYYY-MM-DD" ~/.hermes/logs/gateway.log | head -20
```

Look for:
- `Failed to send Telegram message: Timed out`
- `cannot import name '...' from 'tools.tool_backend_helpers'`
- `httpx.RemoteProtocolError`
- `File not found` (missing media attachments)

### 4. Search session history for related failures
```
session_search --query "telegram cron undelivered" --role_filter user,assistant
```
This finds past instances of the same bug pattern.

### 5. Test delivery manually
Trigger the job immediately and monitor:
```
cronjob run --job_id JOB_ID
```
Then quickly tail the logs:
```
tail -f ~/.hermes/logs/errors.log
```

If the manual run also fails to deliver, the issue is reproducible and likely a platform bug.

### 6. Distinguish execution vs delivery failure

| What happened | `last_status` | Logs show | Fix |
|--------------|---------------|-----------|-----|
| Job code crashed | `error` or `failed` | Traceback in cron output | Fix the prompt or code |
| Job ran, delivery broke | `ok` | Gateway import/timeout error | Platform bug or network issue |
| Job never triggered | `ok` but `last_run_at` is old | Nothing | Check schedule/timezone |

## Common Root Causes

### Gateway Import Errors (Stale Python Module Cache)
A Python `ImportError` in the gateway logs (e.g. `cannot import name '...' from 'tools.tool_backend_helpers'`) is often a **stale `.pyc` cache in a long-running process**, not missing source code.

**Diagnose stale cache:**
1. Verify the name exists in source:
   ```bash
   grep -n "function_name" /path/to/source.py
   ```
2. Compare file mtime vs process start time:
   ```bash
   stat /path/to/source.py | grep Modify
   ps -o pid,lstart,comm -p $(pgrep -f "hermes")
   ```
   If source was modified after the process started, the process has stale bytecode.
3. Check `.pyc` cache timestamps:
   ```bash
   ls -lt /path/to/__pycache__/module.cpython-311.pyc
   ```
4. Prove it with a fresh process test:
   ```bash
   /path/to/venv/bin/python3 -c "
   import sys; sys.path.insert(0, '/path/to/agent')
   from module import function_name
   print('Import OK')
   "
   ```
   If fresh process works but gateway crashes, it is 100% stale cache.

**Fix:** Restart the Hermes process. Python does not auto-reload cached modules. Also check if the systemd gateway service is dead:
```bash
systemctl --user status hermes-gateway.service
```
If `inactive`, restart properly:
```bash
systemctl --user start hermes-gateway.service
systemctl --user enable hermes-gateway.service
```
Note: A foreground `hermes` process may still be alive while the systemd service is dead. The service is the canonical runner.

### Network Timeouts
Telegram API timeouts. Usually transient. If recurring, switch delivery target.

### Missing Media Files
Cron job references images/paths that don't exist. Delivery fails because the attachment is missing. Fix by ensuring files exist before the cron runs, or removing media from the delivery.

### Chat ID Mismatch
User changed Telegram handles, blocked the bot, or the chat ID rotated. Verify with:
```bash
cat ~/.hermes/telegram_config.md
grep -i "chat_id\|chat not found" ~/.hermes/logs/gateway.log
```

## Workarounds (When Platform Bug Blocks Fix)

If the gateway has a broken import or persistent timeout:

1. **Switch delivery target**
   ```
   cronjob update --job_id JOB_ID --deliver origin
   ```
   Then run the job and paste output to the user manually.

2. **Switch to email backup**
   ```
   cronjob update --job_id JOB_ID --deliver email:user@example.com
   ```

3. **Pause and run manually**
   ```
   cronjob pause --job_id JOB_ID --reason "Telegram gateway import bug"
   ```
   Then run on-demand and deliver via chat.

4. **Change schedule to reduce noise** while waiting for fix:
   ```
   cronjob update --job_id JOB_ID --schedule "0 8 * * MON"
   ```

## Prevention

After fixing or working around:
- Update the cron job's `reason` field to document the incident
- Set up a test cron (`schedule: "0 */6 * * *"`) that sends a heartbeat message to verify delivery health
- If the user manages multiple cron jobs, recommend a weekly delivery test