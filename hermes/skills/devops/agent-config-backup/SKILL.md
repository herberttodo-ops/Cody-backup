---
name: agent-config-backup
description: Backup and restore agent configuration to GitHub with secret sanitization
tags: [backup, restore, github, cron, automation, devops]
prerequisites: [telegram-setup, github-auth]
---

# Agent Configuration Backup

Backup and restore all agent configuration files to a private GitHub repository with automatic secret sanitization.

## Overview

This skill provides a complete backup solution for Hermes/OpenClaw agent configurations, including:
- Core personality files (SOUL.md, MEMORY.md)
- Configuration files (config.yaml, gateway state)
- Scheduled cron jobs
- All skill definitions
- User memory files
- OpenClaw workspace

All secrets are automatically sanitized before backup.

## When to Use

- Setting up automated daily backups of agent state
- Migrating agent configuration to a new machine
- Creating disaster recovery snapshots
- Version-controlling agent configuration changes

## Prerequisites

- Private GitHub repository for storing backups
- GitHub Personal Access Token with `repo` scope
- Telegram configuration for notifications (optional)

## Quick Start

### 1. Setup Authentication

Generate a GitHub Personal Access Token:
1. Visit https://github.com/settings/tokens
2. Generate new token (classic) with `repo` scope
3. Add to `~/.hermes/.env`:
   ```
   GITHUB_BACKUP_TOKEN=ghp_your_token_here
   ```

### 2. Run Initial Backup

```bash
# IMPORTANT: Use tr -d '"' to strip quotes if token is stored with them in .env
export GITHUB_BACKUP_TOKEN="$(grep GITHUB_BACKUP_TOKEN ~/.hermes/.env | cut -d= -f2- | tr -d '"')"
~/.hermes/bin/daily-backup.sh
```

### 3. Enable Daily Automation

```bash
# Job already created at 4:30 AM daily
# Job ID: herby-daily-backup
hermes cronjob list
```

## What Gets Backed Up

| Directory | Contents | Sanitization |
|-----------|----------|--------------|
| `hermes/` | SOUL.md, MEMORY.md, config.yaml, gateway_state.json | Yes - tokens redacted |
| `hermes/cron/` | All cron job definitions | No secrets expected |
| `hermes/skills/` | All SKILL.md files and supporting assets | Yes - checked |
| `openclaw/` | Workspace files, openclaw.json | Yes - bot tokens removed |
| `user-memory/` | Files from `~/memory/` | Reviewed |

## Secret Sanitization

The following patterns are automatically detected and replaced:

```bash
# API Keys
sk-...                      → [OPENAI_API_KEY]
sk-proj-...                 → [OPENAI_PROJECT_KEY]
org-...                     → [OPENAI_ORG_ID]
pk-...                      → [API_KEY]

# Tokens & Auth
Bearer ...                  → bearer [API_TOKEN]
"access_token": "___TOKEN___"       → "access_token": "___TOKEN___"
"token": "___TOKEN___"              → "token": "___TOKEN___"
"botToken": "___BOT_TOKEN___"           → "botToken": "___BOT_TOKEN___"

# Environment Variables
TELEGRAM_BOT_TOKEN=...      → TELEGRAM_BOT_TOKEN=[TELEGRAM_BOT_TOKEN]
OPENAI_API_KEY=...          → OPENAI_API_KEY=[OPENAI_API_KEY]
HERMES_GATEWAY_TOKEN=...    → HERMES_GATEWAY_TOKEN=[GATEWAY_TOKEN]

# Generic
[a-f0-9]{32,}               → [HASH_OR_KEY]  (hex strings)
```

## Troubleshooting

### Push Fails with Authentication Error

**Symptom:** `could not read Username for 'https://github.com'`

**Solution:**
1. Verify token is set: `grep GITHUB_BACKUP_TOKEN ~/.hermes/.env`
2. Test manually: `export GITHUB_BACKUP_TOKEN=... && ~/.hermes/bin/daily-backup.sh`
3. Check token has `repo` scope on GitHub

### Push Fails with "No Such Device or Address"

**Symptom:** `fatal: could not read Password for 'https://%22git...%22@github.com'` — note the URL-encoded `%22` (quote characters) in the error.

**Root Cause:** The `GITHUB_BACKUP_TOKEN` in `~/.hermes/.env` is stored with surrounding quotes (e.g., `GITHUB_BACKUP_TOKEN="ghp_..."`), and the extraction command included the quotes in the token value. Git then URL-encodes them into the remote URL, causing authentication failure.

**Fix:** Strip quotes when sourcing from `.env`:
```bash
export GITHUB_BACKUP_TOKEN="$(grep GITHUB_BACKUP_TOKEN ~/.hermes/.env | cut -d= -f2- | tr -d '"')"
```

**Prevention:** When documenting or scripting token extraction from `.env`, always include `| tr -d '"'` to handle both quoted and unquoted values safely.

### Missing Files in Backup

Check the backup log:
```bash
cat ~/.hermes/logs/backup-$(date +%Y-%m-%d).log
```

### Restore from Backup

See `RESTORE.md` in your backup repository for complete restoration steps.

## Files

- **Backup Script:** `~/.hermes/bin/daily-backup.sh`
- **Logs:** `~/.hermes/logs/backup-YYYY-MM-DD.log`
- **Setup Guide:** `~/.hermes/SETUP_BACKUP_AUTH.md`
- **Staging Area:** `~/.hermes/backup-staging/`

## Security Notes

- ✅ All secrets are sanitized before backup
- ⚠️ Never commit the `.env` file directly
- ⚠️ Keep your GitHub token secure
- ✅ Use a private repository for backups
- ✅ The backup script creates templates for credential files

## References

- [`references/token-quote-extraction.md`](references/token-quote-extraction.md) — Pitfall: quoted tokens in `.env` causing git auth failures

## Customization

To add additional files/directories to backup, edit the `safe_copy` calls in `daily-backup.sh`:

```bash
# Add this in the backup section
safe_copy "$HOME/.custom-config/my-file.txt" "$BACKUP_DIR/custom/my-file.txt"
```

## Related

- `cronjob` tool - Manage scheduled backup jobs
- GitHub authentication - Configure long-term access
