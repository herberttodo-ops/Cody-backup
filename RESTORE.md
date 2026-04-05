# Herby Agent Restore Guide

This backup contains sanitized configuration needed to restore your Herby agent.

## ⚠️ IMPORTANT: Secrets NOT Included

This backup intentionally excludes all secrets:
- API keys (OpenAI, OpenRouter, etc.)
- Tokens (Telegram bot token, GitHub PAT)
- Authentication credentials
- Sensitive environment variables

You must re-enter these manually after restore.

## What's Backed Up

| Directory | Contents |
|-----------|----------|
| `hermes/` | Core config (SOUL.md, memories, config.yaml) |
| `hermes/skills/` | All skill definitions |
| `hermes/cron/` | Cron job summaries (not full job definitions) |
| `openclaw/` | OpenClaw workspace and sanitized config |
| `user-memory/` | Your personal memory files |

## Restoration Steps

### 1. Install Hermes Agent
Follow the installation guide for your platform.

### 2. Restore Configuration Files
```bash
cp -r hermes/* ~/.hermes/
cp -r openclaw/* ~/.openclaw/
cp -r user-memory/* ~/memory/
```

### 3. Recreate Environment File
Create `~/.hermes/.env` with your actual secrets:
```bash
TELEGRAM_BOT_TOKEN=your_actual_token_here
OPENAI_API_KEY=your_actual_key_here
OPENROUTER_API_KEY=your_actual_key_here
HERMES_GATEWAY_TOKEN=your_actual_token_here
GITHUB_BACKUP_TOKEN=your_github_pat_here
```

### 4. Recreate Cron Jobs
The backup includes summaries but not the full job definitions (they contain secrets).

Recreate the daily backup job:
```bash
hermes cronjob create \
  --name "herby-daily-backup" \
  --schedule "30 4 * * *" \
  --prompt "Run the daily backup script" \
  --deliver "telegram:YOUR_CHAT_ID"
```

### 5. Verify Setup
```bash
hermes cronjob list
```

## Notes

- All long strings and IDs have been replaced with placeholders like `___TOKEN___`
- File structure and non-sensitive configuration is preserved
- You must re-authenticate with all services after restore
