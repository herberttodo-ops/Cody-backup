---
name: openai-image-generation-tool
title: OpenAI Image Generation Tool Integration
description: Guide for adding OpenAI gpt-image-1 image generation to Hermes Agent, including base64 handling and local file storage.
version: 1.0.0
tags: [openai, image-generation, gpt-image-1, mlops, tools]
---

# OpenAI Image Generation Tool Integration

Guide for adding OpenAI image generation capabilities to Hermes Agent.

## Overview

OpenAI's image generation API (gpt-image-1) returns base64-encoded image data rather than URLs. This requires special handling to save files locally before returning a path.

## Integration Steps

### 1. Create Tool File

Create `tools/openai_image_generation_tool.py` with:
- Base64 decoding logic
- Local file storage in `~/.hermes/generated_images/`
- Proper error handling for rate limits
- Tool registry registration

Key implementation details:
```python
# Handle base64 response from OpenAI
if "b64_json" in image_data:
    import base64
    from pathlib import Path
    
    image_bytes = base64.b64decode(image_data["b64_json"])
    
    # Save to hermes home directory
    hermes_home = os.path.expanduser("~/.hermes")
    image_dir = Path(hermes_home) / "generated_images"
    image_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"openai_image_{int(time.time())}.png"
    filepath = image_dir / filename
    
    with open(filepath, "wb") as f:
        f.write(image_bytes)
    
    return {
        "url": f"file://{filepath}",
        "local_path": str(filepath),
        # ... other metadata
    }
```

### 2. Add to Tool Discovery

Update `model_tools.py` `_discover_tools()` list:
```python
_modules = [
    # ... other tools
    "tools.openai_image_generation_tool",
    # ...
]
```

### 3. Register in Toolsets

Update `toolsets.py`:
- Add to `_HERMES_CORE_TOOLS` list
- Add to `image_gen` toolset definition

### 4. Configuration

The tool requires `OPENAI_API_KEY` in `~/.hermes/.env`.

## API Behavior Notes

### Model Discovery
OpenAI's image generation models have changed over time:
- `gpt-image-2` - Not yet publicly available
- `dall-e-3` - Returns 400 error on current endpoint
- `gpt-image-1` - Current working model ✅

### Response Format
Unlike FAL.ai (which returns URLs), OpenAI returns:
```json
{
  "data": [{
    "b64_json": "base64_encoded_image_data...",
    "revised_prompt": "..."
  }]
}
```

### Supported Parameters
- **Model**: `gpt-image-1`
- **Quality**: `high` or `medium`
- **Sizes**: 
  - `1024x1024` (square)
  - `1792x1024` (landscape)
  - `1024x1792` (portrait)

## Testing

Verify the tool works:
```python
from tools.openai_image_generation_tool import openai_image_generate_tool

result = openai_image_generate_tool(
    prompt="A simple test image",
    aspect_ratio="square",
    quality="medium"
)

# Result contains local file path
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Model not found error | Use `gpt-image-1`, not `gpt-image-2` or `dall-e-3` |
| No URL in response | Normal - check for `b64_json` field instead |
| Files not saving | Ensure `~/.hermes/generated_images/` directory exists and is writable |
| Timeout errors | Image generation takes 10-20 seconds - use appropriate timeout |

## Related Skills
- `image-generation-flux` - For FAL.ai FLUX integration (returns URLs)
- `logo-compositor-branded-graphics` - For compositing exact logos onto AI backgrounds
- `tool-registry` - For registering new tools

## Advanced: Logo Compositing

For brand graphics that require your **exact logo** (not AI approximations), combine this tool with PIL compositing:

```python
# 1. Generate background with this tool (no logos)
# 2. Composite exact logo with PIL
# 3. Add text overlays

See skill: logo-compositor-branded-graphics
```

This approach ensures:
- Exact logo reproduction (every circuit line, precise proportions)
- Consistent brand colors (#40D395 vs AI's approximation)
- Professional typography (actual brand fonts)
- Scalable to multiple posts while maintaining brand consistency

## References
- OpenAI Images API: https://platform.openai.com/docs/guides/images
- Tool registry pattern: See `tools/registry.py`
