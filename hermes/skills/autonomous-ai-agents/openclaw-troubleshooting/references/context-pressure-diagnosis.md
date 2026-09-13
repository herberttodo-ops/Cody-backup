# Context Pressure Diagnosis — "LLM Request Failed" with Token Budget Exceeded

## Symptom

OpenClaw gateway running, Telegram connected, but every message fails with:
```
error=LLM request failed. rawError=Provider returned an incomplete or malformed tool call
```

Log shows:
```
[context-pressure-diagnostic] admitted provider attempt for openrouter/moonshotai/kimi-k2.5
route=compact_only estimatedPromptTokens=348149 promptBudgetBeforeReserve=242144
```

**Key confusion:** The user's prompt was only 2 sentences. The error is NOT the prompt length.

## Root Cause: Accumulated Session History

Even a short user prompt triggers the entire conversation history to be sent to the model. When this history grows excessively, the model has no room to respond.

### How to Diagnose

**Check session accumulation:**
```bash
# Count session files
ls ~/.openclaw/agents/main/sessions/ | wc -l
# → 8648 total session files (538MB)

# Check size
du -sh ~/.openclaw/agents/main/sessions/
# → 538M
```

**Look for the specific log signature:**
```bash
journalctl --user -u openclaw-gateway --since "10 minutes ago" 2>/dev/null | grep "estimatedPromptTokens"
# Should show "estimatedPromptTokens=348149 promptBudgetBeforeReserve=242144"
```

### Why This Happens

- OpenClaw retains full conversation history across sessions
- Each message, tool call, and response adds tokens
- After days/weeks of use, context grows to 300k+ tokens
- Even a simple "Hello" triggers all 300k tokens to be sent
- The model has ~100k tokens left to respond, but tool schemas and system prompt consume most of it
- Model returns malformed response because it was truncated mid-generation

## Fix: Reduce Session Accumulation

### Option 1: Archive Old Sessions (Immediate Relief)
```bash
# Archive sessions older than 1 day
mkdir -p ~/.openclaw/agents/main/sessions-archive
find ~/.openclaw/agents/main/sessions -name "*.jsonl" -type f -mtime +1 \
  -exec mv {} ~/.openclaw/agents/main/sessions-archive/ \; 2>/dev/null

# Check remaining sessions
ls ~/.openclaw/agents/main/sessions/*.jsonl | wc -l
```

### Option 2: Start Fresh Session
Send `/new` in Telegram to start a new conversation thread with zero history.

### Option 3: Vacuum SQLite Database
```bash
sqlite3 ~/.openclaw/agents/main/agent/openclaw-agent.sqlite "VACUUM;"
```

### Option 4: Compact in Session (If Session Is Active)
When context pressure is detected but you want to keep the current session, compact/summarize:
```
The conversation context has grown very large. Please summarize the key decisions and context from this conversation into a brief paragraph, then continue from there.
```

## Prevention

- **Monitor session growth:** Check `~/.openclaw/agents/main/sessions/` size weekly
- **Archive regularly:** Cron job to archive sessions older than 7 days
- **Use `/new` command:** Start fresh Telegram threads periodically
- **Set context limits:** Consider configuring `agents.defaults.maxContextTokens` if available

## Distinguishing Token Pressure vs Model Bug

| Symptom | Token Pressure | Model Bug |
|---------|---------------|-----------|
| `estimatedPromptTokens` > budget | ✅ Yes | ❌ No |
| `compactions=0` in log | ✅ Yes | May be 0 |
| All prompts fail (even "hello") | ✅ Yes | ❌ No |
| Complex prompts fail, simple work | ❌ No | ✅ Yes |
| Error: "incomplete or malformed tool call" | ✅ Possible | ✅ Yes |
| Session age | Days/weeks old | Any age |
| Token count in log | 300k+ | Normal (~50k) |

**Always check `estimatedPromptTokens` first.** If it exceeds budget, archive sessions before switching models.
