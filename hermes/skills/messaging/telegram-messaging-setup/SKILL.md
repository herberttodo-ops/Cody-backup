---
name: telegram-messaging-setup
title: Telegram Messaging Setup
description: Complete workflow for setting up Telegram as a messaging channel for Hermes agent
version: 1.0
---

# Telegram Messaging Setup

Sets up Telegram as the primary delivery target for messages from Hermes agent.

## Prerequisites

- User wants to switch to Telegram (not WhatsApp, not web chat)
- User has Telegram account and knows their username

## Workflow

### 1. Create Telegram Bot

1. User messages @BotFather in Telegram
2. Send `/newbot`
3. Follow prompts:
   - Name: e.g., "Herby Assistant"
   - Username: must end in "bot" (e.g., "herby_andrew_bot")
4. BotFather returns a **token** — save it

### 2. Get User Chat ID

1. User messages @userinfobot in Telegram
2. It replies with numeric user ID

### 3. Seed the Bot Chat

1. User finds their new bot in Telegram (by username)
2. Send any message (e.g., "hi")

### 4. Store Credentials

Bot token and chat ID are sensitive — store in `memory/telegram_config.md`:

```markdown
# Telegram Configuration
**Bot Token:** `TOKEN_HERE`
**Chat ID:** `CHAT_ID_HERE`
**Username:** @username
```

Add reference to main memory: `Telegram config: [memory/telegram_config.md]`

### 5. Update Agent Config

Credentials live in `~/.hermes/.env`:

```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

**CRITICAL:** These files are **protected**. User must edit manually:

```bash
nano ~/.hermes/.env
```

### 6. Restart Agent

After editing `.env`:
- systemd: `sudo systemctl restart hermes`
- Docker: `docker restart <container>`
- Process manager: restart that process

### 7. Verify

User sends test message to their bot. Agent should receive and reply.

## Memory Management Notes

- Main memory has 2,200 char limit
- Follow routing index pattern: link to detail files rather than inlining
- Remove old messaging channel references when switching

## Common Issues

| Issue | Fix |
|-------|-----|
| Agent can't write .env | Expected — user must edit manually |
| Memory full | Create separate file, link from main memory |
| Messages not received | Ensure user messaged bot first, then restart agent |