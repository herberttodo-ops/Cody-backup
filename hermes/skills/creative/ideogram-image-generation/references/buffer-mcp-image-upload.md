# Buffer MCP Image Upload Pattern

Reference for posting generated images to Buffer via MCP with working upload services.

## Working Pattern (Verified September 2026)

### Step 1: Generate Image

Use the compositor script to generate image with text + logo:

```bash
cd ~/.hermes/scripts && python3 ideogram_logo_compositor.py "Your headline" topic-name
```

Output saved to: `~/.hermes/generated_images/optirfp_social_*.png`

### Step 2: Upload to Temporary Hosting

**catbox.moe** (working as of September 2026):

```bash
curl -s -F "reqtype=fileupload" -F "time=1h" \
  -F "fileToUpload=@/path/to/image.png" \
  https://litterbox.catbox.moe/resources/internals/api.php
```

Returns: `https://litter.catbox.moe/xxxxx.png`

**Important:** Always include `-F "time=1h"` parameter. Without it, uploads may fail silently.

### Step 3: Post to Buffer MCP

```python
mcp__buffer__create_post(
    channelId="your_linkedin_channel_id",  # Get from list_channels
    assets=[{
        "image": {
            "url": "https://litter.catbox.moe/xxxxx.png",  # Public URL from catbox
            "metadata": {"altText": "Descriptive alt text"}
        }
    }],
    text="Your post text here\n\n#hashtags",
    schedulingType="automatic",  # "automatic" or "notification" (required field)
    mode="addToQueue"            # "addToQueue", "shareNow", "shareNext", "customScheduled"
)
```

**Critical Parameters:**
- `schedulingType`: Controls publishing method
  - `"automatic"` = auto-publish at scheduled time
  - `"notification"` = send for manual approval
- `mode`: Controls timing behavior
  - `"addToQueue"` = add to posting queue
  - `"shareNow"` = publish immediately
  - `"shareNext"` = next scheduled slot
  - `"customScheduled"` = requires `dueAt` parameter

**Common Mistake:** Using `"addToQueue"` as `schedulingType` fails validation. Use it for `mode` instead.

## End-to-End Example

```python
# 1. Generate image
cd ~/.hermes/scripts
python3 ideogram_logo_compositor.py "Winning proposals start on page one" page-one
# Returns: /home/herby/.hermes/generated_images/optirfp_social____ID___.png

# 2. Upload (terminal)
curl -s -F "reqtype=fileupload" -F "time=1h" \
  -F "fileToUpload=@/home/herby/.hermes/generated_images/optirfp_social____ID___.png" \
  https://litterbox.catbox.moe/resources/internals/api.php
# Returns: https://litter.catbox.moe/3nazny.png

# 3. Post via MCP
mcp__buffer__create_post(
    channelId="6a7f74bcb2d9d577437af9a4",
    assets=[{
        "image": {
            "url": "https://litter.catbox.moe/3nazny.png",
            "metadata": {"altText": "Winning proposals start on page one - OptiRFP graphic"}
        }
    }],
    text="Winning proposals start on page one.\n\nMost evaluators decide within the first 3 pages...",
    schedulingType="automatic",
    mode="addToQueue"
)
```

## Upload Service Status

| Service | Status | Notes |
|---------|--------|-------|
| catbox.moe | ✅ Working | Requires `time=1h` parameter |
| transfer.sh | ❌ Failing | Connection refused |
| 0x0.st | ❌ Disabled | Uploads disabled due to spam |
| imgur API | ❌ Unreliable | 503 errors, requires auth |
| file.io | ❌ Failing | 301 redirects, intermittent |

## Fallback: Manual Upload Package

If Buffer MCP fails, provide user with:

```markdown
## Image Location
`/home/herby/.hermes/generated_images/optirfp_social_TIMESTAMP.png`

## POST COPY
[Headline]

[Body text]

[CTA]

## HASHTAGS
#RFP #B2BSales #ProposalWriting #GovCon #OptiRFP

## Upload Instructions
1. Go to https://buffer.com → OptiRFP LinkedIn channel
2. Upload image from path above
3. Paste post copy
4. Add hashtags
5. Schedule or add to queue
```

## Quality Verification Before Posting

Use vision_analyze to check image quality:

```python
vision_analyze(
    image_url="/path/to/generated_image.png",
    question="Rate quality 1-10. Check: 1) Text readability, 2) Watermarks/fake branding, 3) Colors (#0F172A navy, #40D395 mint), 4) Logo placement"
)
```

**Quality Threshold:**
- **9-10/10**: Proceed with posting
- **7-8/10**: Regenerate if time permits
- **< 7/10**: Must regenerate
