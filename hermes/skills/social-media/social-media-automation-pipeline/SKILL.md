---
name: social-media-automation-pipeline
description: Social media automation with draft gen and approval gates.
version: 1.0.0
---

# Social Media Automation Pipeline

Build end-to-end pipelines: draft generation from content banks, compliance scoring, human approval via Telegram DM, and publish orchestration via Composio or Buffer. Auto-rotation, brand voice enforcement, bidirectional analytics.

## When to Use

- Automating daily/weekly posting across multiple platforms with human approval gates
- Replacing Buffer's 10-post cap with unlimited native API access
- Running multi-brand social operations (Tales Untold, OptiRFP, LotSignal)
- Need analytics feedback loop into content strategy

## Pipeline Stages

```
SIGNALS → DRAFT GEN → COMPLIANCE → APPROVAL → PUBLISH → ANALYTICS → FEEDBACK
```

### 1. Draft Generator
Builds text + image description from content banks with weekly rotation.

```python
STAT_BANK = [{"hook": "...", "body": "...", "cta": "...", "hashtags": "#A #B"}]
WEEKLY_ROTATION = {0: "stat", 1: "insight", 2: "tip", 3: "stat", 4: "insight", 5: "tip", 6: None}
```

### 2. Compliance Engine
Auto-scored before human sees it:
- Brand voice: sentence length, exclamation points, passive voice
- Legal guardrail: prohibited terms via regex
- Disclaimer injector: triggers on performance claims
- Platform validator: char limits, hashtag counts

**PITFALL — Dollar/Percentage Regex:** Do NOT use `r"\$\d+\b"` or `r"\b\d+%\b"`. Legitimate cost stats (`$500/month carrying cost`, `40% faster`) trigger these. Skip them for stat-heavy content; only flag financing terms (`APR`, `cash back`).

Scoring: base 100, -5 per long sentence, -10 per prohibited term, -10 per exclamation point. PASS >= 90, FAIL < 70.

### 3. Approval Queue (Human Gate)
Telegram DM format:
```
📋 LotSignal Draft — LinkedIn
Type: stat | Compliance: 95/100
[Text preview]
Scheduled: 6:00 PM ET
✅ APPROVE / ❌ REJECT / ✏️ EDIT
```
No auto-publish ever.

### 4. Publish Orchestrator
Cron at 6/7/8 PM ET:
- Read approved queue
- Upload media to CDN
- Publish via Composio MCP toolkit or Buffer/native APIs
- Log results, retry failed (max 3)

### 5. Analytics Harvester
Daily pull via same toolkit:
- LinkedIn: impressions, reactions, comments, shares
- Instagram: likes, comments, reach, saves
- Store in SQLite `performance.db`

### 6. Weekly Feedback Loop
Monday: extract winning/losing patterns, suggest prompt patches. Do NOT auto-apply.

## Directory Layout

```
~/.hermes/<brand>-social/
├── brand/brand_voice.json
├── signals/calendar.yaml, news_rss_cache.json
├── drafts/YYYY-MM/draft_ID_text.md, draft_ID_meta.json
├── compliance/guardrail_config.yaml, check_results/
├── publish/queue.json, published_log.csv
├── analytics/performance.db
└── scripts/
    ├── generate_draft.py --auto
    ├── run_compliance.py --all
    ├── notify_approval.py --latest
    ├── publish_queue.py [--dry-run]
    ├── fetch_analytics.py
    └── weekly_feedback.py
```

## Composio vs Buffer

| Factor | Buffer (10 cap) | Composio (unlimited) |
|--------|-----------------|---------------------|
| Direction | One-way post only | Bidirectional post+read |
| Analytics | None | Native metrics via MCP |
| Auth | Self-managed | Managed OAuth renewal |
| Cost | $6-12/mo | Free (100K calls) / $29 Scale |

## Pitfalls

1. Broad dollar/percentage regex false-positives on stat-heavy content
2. Telegram bot token expiration (401) — refresh via BotFather
3. Buffer `edit_post` silently ignores asset changes — attach at creation only
4. Daily refill beats Mon/Thu batch refill — prevents 2.5+ day gaps
5. Image generation failures — log desc, queue text-only with flag

## Related
- `buffer-api` — Buffer-specific MCP patterns and 10-post cap management
- `social-media-workflow` — Buffer-centric scheduling workflow
- `video-pipeline-operations` — Video scheduling, cost tracking, Buffer filling
- `automotive-dealership-marketing` — Strategy layer (pain points, personas)
