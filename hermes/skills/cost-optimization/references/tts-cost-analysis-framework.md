# TTS Cost Analysis Framework

Framework for analyzing TTS (Text-to-Speech) API costs vs local/StS alternatives like VoiceStudio, Piper, Coqui, etc.

## When to Use

- Evaluating migration from cloud TTS (ElevenLabs, OpenAI, Google) to local alternatives
- Calculating break-even points for self-hosted voice infrastructure
- Comparing per-character pricing vs compute-time pricing models

## Quick Calculator

```python
def analyze_tts_costs(
    posts_per_day: int,
    avg_chars_per_post: int,
    cloud_cost_per_1k_chars: float = 0.04,  # ElevenLabs standard
    local_inference_secs_per_post: float = 3.0,
    serverless_cost_per_sec: float = 0.0004  # Modal GPU
):
    """Compare cloud TTS vs self-hosted alternatives."""
    
    daily_chars = posts_per_day * avg_chars_per_post
    monthly_chars = daily_chars * 30
    
    # Cloud TTS costs
    monthly_cloud = (monthly_chars / 1000) * cloud_cost_per_1k_chars
    
    # Self-hosted (serverless GPU)
    daily_compute_secs = posts_per_day * local_inference_secs_per_post
    monthly_compute_secs = daily_compute_secs * 30
    monthly_serverless = monthly_compute_secs * serverless_cost_per_sec * 1.2  # +20% overhead
    
    return {
        'monthly_cloud': monthly_cloud,
        'monthly_serverless': monthly_serverless,
        'annual_savings': (monthly_cloud - monthly_serverless) * 12,
        'break_even_posts_per_day': None  # Serverless always cheaper at low volume
    }
```

## Decision Matrix

| Cloud Monthly Spend | Recommendation |
|--------------------|----------------|
| <$5 (<50K chars/day) | Stay on cloud — migration ROI too low |
| $5-25 (50K-250K chars/day) | Evaluate local; test quality first |
| $25-100 (250K-1M chars/day) | Strong case for local GPU |
| >$100 (>1M chars/day) | Self-hosted required |

## VoiceStudio-Specific Analysis

### Hardware Requirements
- **Minimum**: 6GB VRAM (CUDA/ROCm) for OmniVoice default
- **Recommended**: RTX 4090 (24GB) for batch processing
- **CPU fallback**: Fully functional but 10-20x slower

### Cost Comparison (Real Example)

**Tales Untold scenario:**
- 3 posts/day, ~550 chars each
- ElevenLabs: $1.98/mo
- VoiceStudio + Modal: $0.13/mo
- Savings: $22/year

**At scale:**
- 50 posts/day, ~550 chars each
- ElevenLabs: $33/mo
- VoiceStudio + Modal: $2.16/mo
- Savings: $370/year

### Migration Checklist

1. **Quality test first** — Clone existing voice, A/B compare outputs
2. **Latency check** — Cloud TTS is instant; local needs warm GPU
3. **Fallback plan** — Keep cloud API as backup during transition
4. **Batch optimization** — Queue multiple generations to amortize GPU startup

## Common TTS Alternatives

| Solution | Cost Model | Best For |
|----------|-----------|----------
| ElevenLabs | $0.04/1K chars | Convenience, voice quality |
| VoiceStudio | Self-hosted | Scale, privacy, cost control |
| Piper TTS | Free (CPU) | Simple announcements, low quality OK |
| Coqui TTS | Free (self-host) | English, customizable |
| OpenAI TTS | $0.015/1K chars | Speed, reliability |
| Azure TTS | $15/mo flat | Enterprise, SLAs |

## Pitfalls

1. **Ignoring inference time** — Local GPU "free" but startup latency kills UX
2. **Underestimating storage** — Voice models are 2-5GB each
3. **Neglecting quality** — Always A/B test cloned voices before migration
4. **Missing license cost** — Some engines (e.g., AWS Polly neural) have separate licensing

## When Migration Makes Sense

✅ **Do migrate when:**
- Monthly cloud spend >$25
- Privacy requirements mandate on-premise
- Custom voice cloning is core differentiator
- Scale predictably exceeds cloud rate limits

❌ **Don't migrate when:**
- Monthly cloud spend <$5
- Voice quality is brand-critical and untested locally
- Team lacks GPU infrastructure expertise
- Burst traffic patterns (self-hosted cannot auto-scale cheaply)

## Template: Cost Analysis Report

```markdown
## TTS Cost Analysis: {Project}

### Current Usage
- Posts/day: {N}
- Characters/post: {N}
- Monthly characters: {N}

### Cost Comparison
| Platform | Monthly | Annual |
|----------|---------|--------|
| {Cloud Provider} | ${X} | ${X*12} |
| {Local Option} | ${X} | ${X*12} |
| Savings | ${X} | ${X*12} |

### Recommendation
{Stay/Evaluate/Migrate} based on {reasoning}.

### Next Steps
1. Quality comparison test
2. Infrastructure prototype
3. Gradual rollout plan
```

## Resources

- VoiceStudio: https://github.com/debpalash/VoiceStudio
- Piper: https://github.com/rhasspy/piper
- Coqui: https://github.com/coqui-ai/TTS
- Modal serverless GPU: https://modal.com/
