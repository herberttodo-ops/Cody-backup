# AI-Generated Fake Branding Marks Fix

**Issue Date:** 2026-09-30  
**Brand:** OptiRFP  
**Affected:** Ideogram V_4 with full-logo compositing

## Problem

LinkedIn post images showed "OptiRFP" text TWICE:
1. AI-generated fake marks at bottom (e.g., "OptiIFP", "IptiRFp" garbled variants)
2. Real logo composited on top

This happened 13+ hours before detection. First reported Sep 21, recurred Sep 30.

## Root Cause

Ideogram V_4 ignores prompt prohibitions on fake branding. Even with explicit "NO OptiIFP" etc. in prompt, the model generates wordmark-like text at the bottom.

When the compositor used the **full logo** (icon + "OptiRFP" wordmark), the result was:
- Base image: AI-generated garbled "OptiRFP" marks at bottom
- Logo overlay: Real icon + real "OptiRFP" wordmark centered at bottom
- Result: "OptiRFP" appears twice

## Solution (Two Layers)

### Layer 1: Post-Processing Erasure
Forcibly replace bottom 28% of image with solid brand color BEFORE compositing logo:

```python
def clean_bottom_region(image, clean_height_percent=28):
    """Erase any AI-generated fake branding."""
    clean_px = int(image.height * (clean_height_percent / 100))
    navy = (15, 23, 42, 255)  # OptiRFP #0F172A
    
    for y in range(image.height - clean_px, image.height):
        for x in range(image.width):
            image.putpixel((x, y), navy)
    
    return image
```

### Layer 2: Icon-Only Logo
Use the icon-only variant (no "OptiRFP" text) as the overlay asset:

```python
# BEFORE (double risk)
LOGO_PATH = "optirfp_logo.jpg"  # Icon + wordmark

# AFTER (single, controlled branding)
LOGO_PATH = "optirfp_icon_90px.png"  # Icon only, transparent background
```

**Why both layers matter:**
- Icon-only alone: If AI generates "OptiRFP", it still appears as fake text
- Erasure alone: If using full logo, real + fake still appear
- Both together: Guaranteed clean, single branding

## Implementation

```python
def composite_logo(image_data: bytes, logo_path: str) -> Image.Image:
    img = Image.open(io.BytesIO(image_data)).convert("RGBA")
    
    # Step 1: ERASE bottom 28% (destroys any AI-generated fake marks)
    clean_px = int(img.height * 0.28)
    navy = (15, 23, 42, 255)
    for y in range(img.height - clean_px, img.height):
        for x in range(img.width):
            img.putpixel((x, y), navy)
    
    # Step 2: Load icon-only logo
    logo = Image.open(logo_path).convert("RGBA")
    # Make white background transparent
    # ...
    
    # Step 3: Resize and center
    target_width = int(img.width * 0.25)
    logo = logo.resize((target_width, int(target_width / aspect)), Image.Resampling.LANCZOS)
    
    # Step 4: Place centered, 3% from bottom
    x = (img.width - logo.width) // 2
    y = img.height - logo.height - int(img.height * 0.03)
    img.paste(logo, (x, y), logo)
    
    return img
```

## Asset Requirements

Prepare TWO logo assets:
1. **Full lockup** (`optirfp_logo.jpg`) — For use cases where NO AI generation is involved
2. **Icon only** (`optirfp_icon_90px.png`) — For AI-generated backgrounds, transparent background

Generate icon-only from full lockup:
```python
from PIL import Image
logo = Image.open("optirfp_logo.jpg")
icon_only = logo.crop((0, 0, int(logo.width * 0.35), logo.height))
# Background removal, resize to 90px height, save as PNG with alpha
```

## Prevention

1. **Always use icon-only logo** when compositing onto AI-generated backgrounds
2. **Always post-process the bottom region** — erasure is more reliable than prompt instructions
3. **Monitor early posts** — check first 1-2 posts from any new pipeline for branding artifacts
4. **Log review** — inspect generated images before scheduling when possible

## Reference

- See main SKILL.md Pitfall #10 for text-edge-clipping issues
- See `references/logo-cutoff-fix.md` for margin requirements
