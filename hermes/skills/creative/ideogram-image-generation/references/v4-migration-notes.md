# Ideogram V4 Migration - Key Learnings

## What Changed from V2A to V4

| Aspect | V2A | V4 |
|--------|-----|-----|
| Endpoint | `/generate` | `/v1/ideogram-v4/generate` |
| Content-Type | `application/json` | `multipart/form-data` |
| Request format | JSON payload | Form data with `files=` |
| Text quality | Good | Significantly better |
| Artifacts | Frequent (garbled text, watermarks) | Minimal |
| Speed | ~60-90s | ~60-90s |
| Cost | Same (~$0.04/image) | Same |

## Working V4 Request Pattern

```python
import requests

url = "https://api.ideogram.ai/v1/ideogram-v4/generate"
headers = {"Api-Key": IDEOGRAM_API_KEY}

# CRITICAL: Use multipart form data, not JSON
files = {
    "text_prompt": (None, prompt),
    "aspect_ratio": (None, "ASPECT_1_1"),
    "model": (None, "V_4"),
    "magic_prompt_option": (None, "OFF")  # Disable auto-enhance
}

response = requests.post(url, headers=headers, files=files, timeout=120)
data = response.json()
```

**Common mistake**: Using `json=payload` or `data=payload` instead of `files=files` results in 415 Unsupported Media Type error.

## Prompt Structure That Works

Key elements for clean, professional results:

1. **Headline text** - Explicitly quoted and described as "prominent"
2. **Visual description** - Topic-mapped visual elements
3. **Color specs** - Exact hex codes (#0F172A navy, #40D395 mint)
4. **Layout instructions** - "Bottom 25% clean for logo"
5. **Aggressive exclusions** - Multiple "NO text/watermarks/logos" statements

## Why Composite Logo Separately

Even with strict exclusions, Ideogram sometimes adds:
- Misspelled brand names ("OptirFP", "optirfin")
- Random text artifacts
- Watermark-like elements

**Solution**: Let Ideogram render text + background, then composite exact logo file using PIL.

## Cost Savings Summary

| Workflow | Per Image | Monthly (30) |
|----------|-----------|--------------|
| gpt-image-1 + composite | $0.08-0.12 | $2.40-3.60 |
| Ideogram V4 + logo | $0.04 | $1.20 |
| **Savings** | **50-67%** | **$1.20-2.40** |

## Batch Generation Script

See `scripts/regenerate_all_optirfp.py` for batch regenerating all social images.

Run with:
```bash
cd ~/.hermes/skills/creative/ideogram-image-generation
python3 scripts/regenerate_all_optirfp.py
```

Generates 24 images (~8 minutes) with summary output.
