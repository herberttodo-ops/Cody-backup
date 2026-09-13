# LLM Request Failed Errors — Diagnosis & Model Switching

## Symptom

OpenClaw gateway is running, Telegram is connected, but messages receive an error like:

```
error=LLM request failed. rawError=Provider returned an incomplete or malformed tool call
model=moonshotai/kimi-k2.6 provider=openrouter
```

**Key indicator:** The error comes from the LLM provider (OpenRouter/Anthropic/etc.) AFTER the message is received — not during gateway startup.

## Quick Diagnosis

### 1. Confirm the specific error in gateway logs
```bash
# View recent gateway logs via journalctl (if available)
journalctl --user -u openclaw-gateway --since "10 minutes ago" 2>/dev/null | grep -E "LLM|error|model"

# Or check all logs
grep -r "LLM request failed" ~/.openclaw/logs/ 2>/dev/null
```

### 2. Verify the model is the culprit
```bash
# Check which model is configured
openclaw agents list --json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['model'])"
```

Common failing models on OpenRouter:
- `moonshotai/kimi-k2.6` — known to return malformed tool calls with some tool schemas
- `openrouter/auto` — occasionally routes to unstable model variants

### 3. Test the model directly
```bash
# Test via OpenRouter API directly (bypass OpenClaw)
# You need the API key from: openclaw config schema → providers section
curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer YOUR_OPENROUTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "moonshotai/kimi-k2.6",
    "messages": [{"role":"user","content":"Say hello"}],
    "tools": [{"type":"function","function":{"name":"test","description":"test","parameters":{"type":"object","properties":{}}}}],
    "max_tokens": 10
  }' 2>&1 | python3 -m json.tool | head -20
# Malformed tool call = model-side bug, not OpenClaw
```

## Fix: Switch to a Working Model

### Step 1: Identify available fallbacks
```bash
openclaw config get agents.defaults.model 2>&1 | python3 -m json.tool
```

Your `fallbacks` array defines what OpenClaw tries when the primary model fails. Check that it contains working models.

### Step 2: Change the primary model
```bash
# The correct config path for the default agent's model
openclaw config set agents.defaults.model.primary "openrouter/moonshotai/kimi-k2.5"

# Verify change
openclaw config get agents.defaults.model.primary
```

**Note:** This change applies WITHOUT restarting the gateway — OpenClaw reads the config dynamically. You only need to restart if the gateway process itself is dead.

### Step 3: Verify the agent picked it up
```bash
openclaw agents list --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['model'])"
# Should show: openrouter/moonshotai/kimi-k2.5
```

### Step 4: Test by sending a message
Send a message to your bot (Telegram or other channel). If it responds, the model switch worked.

## Recommended Models (OpenRouter)

| Model | Status | Notes |
|-------|--------|-------|
| `openrouter/moonshotai/kimi-k2.5` | ✅ Reliable | Fast, good tool support |
| `anthropic/claude-sonnet-4-6` | ✅ Excellent | Best reasoning, slightly slower |
| `anthropic/claude-haiku-3-5` | ✅ Fast | Good for simple tasks, cheaper |
| `openrouter/auto` | ⚠️ Variable | Routes to "best" — sometimes picks unstable models |
| `moonshotai/kimi-k2.6` | ❌ Buggy | Malformed tool calls with some tool schemas |

## Config Reference

### Full model config path
```
agents.defaults.model.primary     → primary model
agents.defaults.model.fallbacks   → array of fallback models
agents.defaults.model.<model_ref> → per-model overrides (params, cacheRetention, etc.)
```

### Example full config
```
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/moonshotai/kimi-k2.5",
        "fallbacks": [
          "anthropic/claude-sonnet-4-6",
          "anthropic/claude-haiku-3-5"
        ],
        "openrouter/moonshotai/kimi-k2.5": {},
        "anthropic/claude-opus-4-6": {
          "params": {
            "cacheRetention": "short"
          }
        }
      }
    }
  }
}
```

## Prevention

1. **Set fallbacks** — always configure at least 2 fallback models so OpenClaw can route around failures
2. **Monitor gateway logs** — `LLM request failed` with tool call errors usually means model-side bug
3. **Test new models first** — before making a model primary, send a few test messages via the gateway to verify tool calling works
