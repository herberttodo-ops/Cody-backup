# POYO Image Generation Reference

## Working Async Pattern

```python
from poyo_client import PoyoClient

async with PoyoClient() as client:
    # Submit image task
    task_id = await client.generate_image(
        prompt="your prompt here",
        model="gpt-image-2",  # Note: NOT gpt-image-2.5-flare
        size="1536x2732",      # Must be 2K/4K, both dims ÷16
        quality="high"
    )
    
    # Poll until complete
    result = await client.wait_for_result(task_id, timeout=300, poll_interval=3.0)
    
    # Download
    file_url = result["files"][0]["file_url"]
    await client.download_file(file_url, output_path)
```

## Size Validation

POYO requires **2K or 4K resolution** minimum. Custom sizes rejected otherwise.

**Constraints**:
- Total pixels: 655,360 to 8,294,400
- Both dimensions divisible by 16
- Max edge: 3840
- Aspect ratio: up to 3:1

**Finding valid 9:16 sizes**:
```python
def find_valid_size(target_w=1080, target_h=1920):
    """Find closest valid 9:16 size for POYO."""
    # 9:16 = 0.5625
    for w in range(1024, 3841, 16):
        h = int(w * 16 / 9)
        h = (h // 16) * 16  # Round to divisible by 16
        pixels = w * h
        if 655360 <= pixels <= 8294400 and h <= 3840:
            if h >= 1440:  # 2K minimum
                return f"{w}x{h}"
    return None

# Returns: "1216x2160" (2.6M pixels, valid 4K)
```

## Stephen Gammell Style Prompts

**Core elements**:
- "ink wash illustration"
- "Stephen Gammell style"
- "deep black shadows pooling like liquid ink"
- "textured aged book paper"
- "monochrome grayscale"
- "high contrast chiaroscuro"
- "Scary Stories to Tell in the Dark illustration style"

**Example**:
```
A person sleeping peacefully in bed, moonlight through window, 
ink wash illustration in the style of Stephen Gammell, deep black 
shadows pooling like liquid ink, textured aged book paper, surreal 
horror aesthetic, crosshatched shadows, monochrome grayscale, high 
contrast chiaroscuro, Scary Stories to Tell in the Dark illustration 
style
```

## Error Messages

| Error | Meaning | Fix |
|-------|---------|-----|
| "Custom size requires resolution 2K or 4K" | Size too small or not labeled 2K/4K | Use 1216x2160 or larger |
| "Invalid custom size" | Dims not ÷16 or out of pixel range | Both dims must be divisible by 16 |
| "Not Found" (404) | Wrong endpoint | Use `/api/generate/submit` |

## Model Availability

| Model | Status | Notes |
|-------|--------|-------|
| `gpt-image-2` | ✅ Available | Working image generation |
| `gpt-image-2.5-flare` | ❌ Invalid | Wrong model name |
| `gpt-4o-image` | ⚠️ Variable | May not be available on all accounts |

**When `gpt-image-2` fails**: Use Fal.ai `flux-pro/v1.1-ultra` as fallback.

## Credits

- Image generation: ~4 credits per image
- Voice generation: ~0.9-3 credits depending on length
- Account balance: Check via POYO dashboard
