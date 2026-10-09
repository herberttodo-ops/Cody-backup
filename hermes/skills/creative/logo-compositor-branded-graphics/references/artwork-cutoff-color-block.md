# Pitfall: Artwork Cutoff via Color Block

## Incident

**Date:** 2026-10-08
**Brand:** OptiRFP
**Issue:** Artwork appeared cut off with a hard navy color block/bar at the bottom of social posts

## Root Cause

The `ideogram_logo_compositor.py` script contained a `clean_bottom_region()` function that manually painted a solid navy rectangle over the bottom 28% of every generated image. This was intended to hide AI-generated fake logos/text artifacts, but it created a hard visual cutoff that looked broken.

```python
# DEFUNCT CODE (caused the issue)
def clean_bottom_region(img):
    """Clean bottom region to ensure no text or artifacts."""
    width, height = img.size
    draw = ImageDraw.Draw(img)
    bottom_region_height = int(height * 0.28)  # Bottom 28%
    draw.rectangle(
        [0, height - bottom_region_height, width, height],
        fill=(15, 23, 42)  # Navy #0F172A
    )
    return img
```

## Detection

Pixel analysis reveals the color block:

```python
from PIL import Image
img = Image.open(image_path).convert("RGB")
width, height = img.size

# Sample bottom 150px
bottom_150 = img.crop((0, height-150, width, height))
pixels = list(bottom_150.getdata())

# Count navy pixels (approximate)
navy_pixels = sum(1 for r,g,b in pixels if (10<r<30 and 15<g<35 and 30<b<50))
if navy_pixels / len(pixels) > 0.9:
    print("ERROR: Hard color block detected - artwork is being erased")
```

In the broken images:
- Bottom 150px: **95-100% solid navy** (no variation)
- The visual elements simply stopped with a hard edge

## Fix Applied

1. **Removed the erasure function entirely** - Deleted `clean_bottom_region()` and all calls to it
2. **Updated Ideogram prompt** - Added explicit instruction to allow artwork to flow naturally:

```python
# Prompt addition
"""
CRITICAL: Let artwork and visual elements flow naturally to the bottom edge
with smooth fading/gradient effects. DO NOT create hard cutoff lines, 
color blocks, or solid bars at the bottom.
"""
```

3. **Shifted to vision-based validation** - Instead of pre-emptively erasing, the script now validates the generated image and rejects ones with AI artifacts

## Verification After Fix

```python
# Bottom 150px should show natural variation, not solid navy
bottom_150 = img.crop((0, height-150, width, height))
pixels = list(bottom_150.getdata())
navy_pixels = sum(1 for r,g,b in pixels if (10<r<30 and 15<g<35 and 30<b<50))
assert navy_pixels / len(pixels) < 0.5, "Color block still present"
```

In fixed images:
- Bottom 150px: **<10% navy** (artwork flows through naturally)
- Visual elements fade or continue to the edge

## Prevention

1. **Never pre-emptively erase** large regions of AI-generated images
2. **Prompt-level control** is better than post-processing erasure
3. **Use rejection + retry** for images with artifacts instead of painting over them
4. **Pixel-scan validation** should detect natural variation, not just check for logos

## Migration

When removing erasure logic:
1. Update the compositor script (source of truth)
2. Check for duplicate scripts in:
   - `~/.hermes/skills/*/scripts/`
   - `~/.openclaw/workspace/scripts/`
   - `~/.hermes/scripts/`
3. Regenerate any queued posts that used the broken compositor
4. Monitor first few generations to confirm smooth edges

## Related

- See also: `logo-icon-pitfall.md` (logo completeness detection)
- See also: `logo-compositor-branded-graphics/SKILL.md` Social Platform Cropping pitfall
