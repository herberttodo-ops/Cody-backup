# Ideogram V4 vs. Composite Workflow - Cost Analysis

## Current Composite Workflow (gpt-image-1 + PIL)

| Component | Cost | Notes |
|-----------|------|-------|
| Background generation (gpt-image-1) | $0.08-0.12/image | OpenRouter or OpenAI direct |
| Text rendering (PIL) | $0 | Local processing |
| Logo compositing (PIL) | $0 | Local processing |
| **Total per image** | **$0.08-0.12** | — |
| **Monthly (30 posts)** | **$2.40-3.60** | — |

## New Ideogram V4 Workflow

| Component | Cost | Notes |
|-----------|------|-------|
| Image generation (Ideogram V4) | ~$0.04/image | Text baked in |
| Logo compositing (PIL) | $0 | Local processing |
| **Total per image** | **~$0.04** | — |
| **Monthly (30 posts)** | **~$1.20** | — |

## Summary

| Metric | Value |
|--------|-------|
| **Cost savings per image** | $0.04-0.08 (50-67%) |
| **Monthly savings** | $1.20-2.40 |
| **Annual savings** | ~$14-29 |
| **Speed improvement** | Single API call vs. two calls + processing |
| **Quality improvement** | V4 text rendering significantly better |

## Non-Cost Benefits

1. **Faster generation**: Single API call vs. 2 calls + compositing overhead
2. **Better text quality**: AI-rendered text is more integrated with visuals
3. **Fewer artifacts**: V4 produces cleaner images than V2A
4. **Simpler workflow**: One generation step instead of two-step process
5. **More consistent**: Less variation in text positioning and styling

## API Endpoint

```
POST https://api.ideogram.ai/v1/ideogram-v4/generate
Content-Type: multipart/form-data
Api-Key: <your_key>

Form fields:
- text_prompt: The prompt with headline text
- aspect_ratio: ASPECT_1_1, ASPECT_16_9, etc.
- model: V_4
- magic_prompt_option: OFF (for more control)
```

## Model Options

| Model | Use Case |
|-------|----------|
| V_4 | Latest, best text rendering, recommended |
| V_2A | Previous version, still available |
| V_2 | Older, not recommended |
| V_1 | Legacy, not recommended |
