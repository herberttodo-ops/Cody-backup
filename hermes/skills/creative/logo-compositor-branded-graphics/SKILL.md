---
name: logo-compositor-branded-graphics
title: Logo Compositor for Branded Social Media Graphics
description: Create consistent branded graphics by compositing exact logo files onto AI-generated backgrounds. Solves the problem of AI generators being unable to faithfully reproduce specific brand assets.
version: 1.0.0
tags: [branding, image-generation, logo, social-media, PIL, compositing]
---

# Logo Compositor for Branded Social Media Graphics

## Problem

AI image generators (DALL-E, FLUX, gpt-image-1) cannot faithfully reproduce specific logos from text descriptions. They interpret and change the design, losing:
- Exact proportions and spacing
- Specific circuit/line details in logos
- Precise color matching (#40D395 vs AI's approximation)
- Typography accuracy

## Solution

Two-step process:
1. **AI generates background** - Visual elements, patterns, no logos/text
2. **Python composites exact logo** - PIL/Pillow overlays your actual logo file

## Implementation

### 1. Store Logo Asset

Save your exact logo to a standard location:
```bash
~/.hermes/assets/{brand_name}_logo.png  # or .jpg
```

### 2. Create Compositor Tool

Create `tools/logo_compositor_tool.py`:

```python
from PIL import Image, ImageDraw, ImageFont
from tools.openai_image_generation_tool import openai_image_generate_tool
import json
import os

def create_branded_graphic(
    headline: str,
    visual_concept: str,
    logo_path: str = None,
    aspect_ratio: str = "square",
    quality: str = "high"
) -> str:
    """
    Create branded graphic with exact logo composited on AI background.
    
    Args:
        headline: Main text (5-8 words recommended)
        visual_concept: Background description (no logos/text)
        logo_path: Path to logo file (auto-detected if None)
        aspect_ratio: square, landscape, or portrait
        quality: high or medium
    """
    # Generate background without logos
    background_prompt = f"""{visual_concept}
    
    IMPORTANT: Do NOT include any logos, brand names, or text.
    Clean background only with visual elements."""
    
    result = openai_image_generate_tool(
        prompt=background_prompt,
        aspect_ratio=aspect_ratio,
        quality=quality
    )
    
    result_data = json.loads(result)
    background_path = result_data.get("local_path") or \
                      result_data.get("image_url", "").replace("file://", "")
    
    # Open images with PIL
    background = Image.open(background_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")
    
    # Resize logo (max 25% of image width)
    max_logo_width = int(background.width * 0.25)
    logo_ratio = logo.height / logo.width
    new_width = min(max_logo_width, logo.width)
    new_height = int(new_width * logo_ratio)
    logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Position logo at bottom center
    logo_x = (background.width - new_width) // 2
    logo_y = background.height - new_height - int(background.height * 0.05)
    
    # Composite logo onto background
    background.paste(logo, (logo_x, logo_y), logo)
    
    # Add headline text with shadow
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("/path/to/bold/font.ttf", 
                              int(background.width * 0.08))
    
    # Calculate text position (centered, upper portion)
    bbox = draw.textbbox((0, 0), headline, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (background.width - text_width) // 2
    text_y = int(background.height * 0.15)
    
    # Draw shadow then text
    draw.text((text_x + 2, text_y + 2), headline, font=font, 
              fill=(0, 0, 0, 128))
    draw.text((text_x, text_y), headline, font=font, 
              fill=(255, 255, 255, 255))
    
    # Save final image
    output_path = f"~/.hermes/generated_images/branded_{int(time.time())}.png"
    final = Image.new("RGB", background.size, (15, 23, 42))  # Dark navy
    final.paste(background, mask=background.split()[3])
    final.save(output_path)
    
    return json.dumps({
        "success": True,
        "local_path": output_path,
        "headline": headline
    })
```

### 3. Register Tool

Add to `model_tools.py` `_discover_tools()`:
```python
_modules = [
    # ... other tools
    "tools.logo_compositor_tool",
]
```

Add to `toolsets.py`:
```python
"image_gen": {
    "tools": ["image_generate", "openai_image_generate", "create_branded_graphic"],
}
```

### 4. Auto-Logo Detection

```python
def _get_default_logo_path() -> str:
    """Auto-detect logo in standard locations."""
    paths = [
        Path.home() / ".hermes" / "assets" / "logo.png",
        Path.home() / ".hermes" / "assets" / "logo.jpg",
    ]
    for p in paths:
        if p.exists():
            return str(p)
    return None
```

## Usage

### Manual
```python
from tools.logo_compositor_tool import create_branded_graphic

result = create_branded_graphic(
    headline="80% of losing RFPs are copy-pasted",
    visual_concept="Document icons showing copy-paste repetition",
    aspect_ratio="square",
    quality="high"
)
```

### In Cron Jobs
Update daily content generation to use:
```
Use create_branded_graphic tool (not openai_image_generate directly).
This ensures the exact logo is used every time.
```

## Key Design Decisions

1. **Separate background generation from compositing**
   - AI handles creativity (backgrounds)
   - Python handles precision (logo placement)

2. **Explicit "no logos" instruction**
   - Prevents AI from hallucinating fake logos
   - Ensures clean background for compositing

3. **Text shadow for readability**
   - White text on varied backgrounds needs contrast
   - Subtle shadow improves legibility

4. **Auto-logo detection with fallback**
   - Convention over configuration
   - Custom path override available

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Logo looks blurry | Don't scale logo down too small (min 150px width) |
| Text hard to read | Add shadow, adjust font size based on image width |
| Logo has white box | Use PNG with transparency, not JPG |
| Background has logos/text | Strengthen "no logos" prompt, iterate |

## Brand Consistency Checklist

- [ ] Logo file saved to `~/.hermes/assets/`
- [ ] Logo is high-resolution PNG with transparency
- [ ] Brand colors documented in tool constants
- [ ] Font paths configured for system
- [ ] Output directory exists and is writable

## Related Skills

- `openai-image-generation-tool` - Base image generation
- `image-generation-flux` - Alternative AI generation backend
