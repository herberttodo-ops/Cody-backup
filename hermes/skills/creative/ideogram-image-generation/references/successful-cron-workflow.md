# Successful Cron Job Workflow

Session Date: 2026-09-06  
Context: Scheduled cron job for OptiRFP LinkedIn post generation

## What Worked

This session produced a fully working end-to-end workflow for generating and posting Optimized RFP graphics in a cron environment.

## Workflow Summary

```
1. GENERATE image with Ideogram V4 + compositor
2. UPLOAD to catbox.moe for temporary public URL
3. VERIFY quality with vision_analyze (≥9/10)
4. POST to Buffer MCP (LinkedIn + Facebook)
5. CONFIRM scheduled with post IDs
```

## Step 1: Generate Image

Used the compositor script successfully with terminal execution:

```python
# Save script to temp file
cat > /tmp/generate_post.py << 'EOF'
import sys
import importlib.util

spec = importlib.util.spec_from_file_location("compositor", "/home/herby/.hermes/skills/ideogram-image-generation/scripts/ideogram_logo_compositor.py")
compositor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compositor)

result = compositor.generate_optirfp_post_with_logo(
    headline="Copy paste RFPs copy paste losses",
    topic="copy-paste",
    aspect_ratio="ASPECT_1_1"
)

print(f"PATH: {result['final_path']}")
EOF

# Execute (cron-safe)
python3 /tmp/generate_post.py
```

**Output:**
```
PATH: /home/herby/.hermes/generated_images/optirfp_ideogram____ID___.png
```

### Headline Selection Tips (Validated)

- **5-8 words maximum** - Longer text causes garbling
- **Avoid punctuation** - Commas and quotes confuse the AI
- **Simple language** - Complex phrases duplicate/repeat
- **Test topics**: copy-paste, specificity, workflow all work well

## Step 2: Upload for Buffer

**Working service:** catbox.moe with `time` parameter

```bash
curl -s -F "reqtype=fileupload" \
     -F "time=1h" \
     -F "fileToUpload=@/home/herby/.hermes/generated_images/optirfp_ideogram____ID___.png" \
     https://litterbox.catbox.moe/resources/internals/api.php
```

**Returns:** `https://litter.catbox.moe/8zhlj5.png`

**Key findings:**
- `time=1h` parameter is REQUIRED (1 hour retention is sufficient)
- 2MB PNG uploads successfully
- URL valid for Buffer ingestion immediately
- No authentication needed

## Step 3: Verify Quality

Used `vision_analyze` tool with strict criteria:

```python
vision_analyze(
    image_url="/home/herby/.hermes/generated_images/optirfp_ideogram____ID___.png",
    question="Rate 1-10. Check: 1) Is headline perfectly readable? 2) Any watermarks? 3) Navy/mint colors? 4) Logo at bottom? 5) Any artifacts?"
)
```

**Quality Score: 9/10**
- ✅ Text "Copy paste RFPs copy paste losses" perfectly readable
- ✅ No watermarks or fake branding
- ✅ Dark navy (#0F172A) background with mint (#40D395) accents
- ✅ OptiRFP logo cleanly composited at bottom
- ✅ No AI artifacts or garbling

### Iteration Pattern

First attempts may fail. Regenerate with:
1. Simpler headline (remove punctuation)
2. Different topic keyword
3. Same seed if partial success

This session took 3 attempts to get 9/10 quality.

## Step 4: Post to Buffer

```python
# LinkedIn
mcp__buffer__create_post(
    channelId="6a7f74bcb2d9d577437af9a4",  # OptiRFP LinkedIn
    assets=[{
        "image": {
            "url": "https://litter.catbox.moe/8zhlj5.png",
            "metadata": {"altText": "Copy paste RFPs copy paste losses - OptiRFP tip"}
        }
    }],
    text="Copy paste RFPs copy paste losses...",  # Post copy
    schedulingType="automatic",  # "automatic" or "notification"
    mode="addToQueue"
)
```

**Critical parameters:**
- `schedulingType`: Must be `"automatic"` or `"notification"` (NOT `"addToQueue"`)
- `mode`: `"addToQueue"`, `"shareNow"`, `"shareNext"`, or `"customScheduled"`
- Image URL must be publicly accessible HTTPS

**Successful Response:**
```json
{
  "id": "6a9d56a305c83fb1f61ea2c6",
  "status": "scheduled",
  "dueAt": "2026-09-07T02:49:00.000Z"
}
```

### Facebook Cross-Post

Same pattern, different channel ID:
```python
mcp__buffer__create_post(
    channelId="6a7f7476b2d9d577437af67f",  # Optirfp Facebook
    ...
)
```

## Complete Session Output

| Platform | Post ID | Status | Scheduled For |
|----------|---------|--------|---------------|
| LinkedIn | 6a9d56a305c83fb1f61ea2c6 | Scheduled | Sept 7, 2:49 AM ET |
| Facebook | 6a9d56ac6acbdfc9ed9d61be | Scheduled | Sept 6, 1:10 PM ET |

**Image file:** `/home/herby/.hermes/generated_images/optirfp_ideogram____ID___.png`

## Lessons Learned

### What Consistently Works

1. **catbox.moe** - Use `time=1h` parameter for reliable uploads
2. **5-8 word headlines** - Sweet spot for clean rendering
3. **No punctuation** - Avoids garbling
4. **copy-paste topic** - Visuals work well with this theme
5. **terminal + script file** - Cron-safe execution pattern

### What to Avoid

1. execute_code in cron - always blocked, use terminal instead
2. Long headlines with punctuation - causes text artifacts
3. Regenerating with same headline - try different topic instead
4. Local file:// URLs in Buffer - must use public HTTPS

## File Locations

- Generated images: `~/.hermes/generated_images/optirfp_ideogram_*.png`
- Compositor script: `~/.hermes/skills/creative/ideogram-image-generation/scripts/ideogram_logo_compositor.py`
- This reference: `~/.hermes/skills/creative/ideogram-image-generation/references/successful-cron-workflow.md`
