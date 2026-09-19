---
name: cost-optimization
description: Reduce API costs through model tiering and session caching.
category: agent-operations
version: 1.0
author: Hermes
last_updated: 2026-09-18
---

# Cost Optimization

Strategies and tools to reduce monthly API spend while maintaining quality.

## Current Spend Baseline
| Service | Est. Monthly | Critical? |
|---------|-------------|-----------|
| OpenRouter kimi-k2.5 | $20-40 | Yes for complex reasoning |
| POYO (ElevenLabs TTS) | ~$22 | **YES — brand quality** |
| Ideogram images | $10-15 | Yes for OptiRFP branding |
| **Total** | ~$60-100 | |

**Note:** TTS quality is brand-critical. Do NOT edge-tts for Tales Untold.

## Strategy 1: Model Router Pattern

Use task-appropriate models instead of premium model for everything.

### Cost Savings Matrix
| Task Type | Premium (kimi-k2.5) | Cheap Alternative | Savings |
|-----------|-------------------|------------------|---------|
| Web search | $0.50/MTok | Deepseek-chat ($0.03/MTok) | ~90% |
| Summaries | $0.50/MTok | Deepseek-chat ($0.03/MTok) | ~90% |
| Heartbeats | $0.50/MTok | Deepseek-chat ($0.03/MTok) | ~90% |
| Coding | $0.50/MTok | MiniMax-Text-01 ($0.10/MTok) | ~70% |

### Implementation
`~/.hermes/scripts/model_router.py` — task-based model selection.

```python
from model_router import get_model_for_task

model = get_model_for_task("web_search", complexity="simple")
# Returns: "deepseek/deepseek-chat"

# Complex tasks always get premium
model = get_model_for_task("strategy", complexity="complex")
# Returns: "moonshotai/kimi-k2.5"
```

## Strategy 2: Session Compression

Lower the compression threshold to trigger earlier.

**Config:**
```yaml
compression:
  threshold: 0.3   # was 0.5 — compress sooner
  target_ratio: 0.2
  protect_last_n: 20
```

**Hermes CLI:**
```bash
hermes config set compression.threshold 0.3
```

## Strategy 3: Session Summaries (Obsidian Cache)

**Problem:** Every new session reloads full conversation history (10,000+ tokens).
**Solution:** Write compact summaries to Obsidian, load summaries only.

### Tool
`~/.hermes/scripts/session_summarizer.py`

### Usage
```python
# After task completion
from session_summarizer import write_summary

write_summary(
    session_id="20260918_0815",
    summary_text="Fixed Facebook posting for OptiRFP. Updated buffer_dual_account.py to include Facebook channel ID and post-facebook CLI command."
)
# Writes to: Agent-Hermes/summaries/2026-09-18-session-20260918_0815.md
```

### New Session Flow
1. Load `Agent-Hermes/working-context.md`
2. Load **latest summary** from `Agent-Hermes/summaries/`
3. Only search full history if specific detail needed

**Token reduction:** 10,000 → 500 tokens (20x).

## Config Files

### Cost Optimization Config
`~/.hermes/cost_optimization.yaml`
```yaml
model_router:
  default: moonshotai/kimi-k2.5
  routing:
    coding: minimax/miniMax-Text-01
    web_search: deepseek/deepseek-chat
    summarize: deepseek/deepseek-chat
    heartbeat: deepseek/deepseek-chat
    simple_qa: deepseek/deepseek-chat
    formatting: deepseek/deepseek-chat

budget:
  daily_warning_usd: 3.75
  monthly_max_usd: 200.0
  monthly_warning_usd: 150.0

summaries:
  enabled: true
  trigger_turns: 10
  max_tokens: 800
```

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Monthly spend | ~$60-100 | ~$30-60 |
| Avg tokens/turn | ~5,000-10,000 | <2,000 |
| Context reloads | Full history | Summary-only |

## Action Items

1. [ ] Route web search to Deepseek
2. [ ] Route heartbeats to Deepseek
3. [ ] Auto-summarize after semi/complex modes
4. [ ] Next session: load latest summary first

## Related

- [[project-state]] — active projects
- [[mistakes]] — cost-related issues
- `/memory/` — built-in memory notes
- `/summaries/` — session summaries
