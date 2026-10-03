# Pitfall: Logo vs Icon File Detection

## Incident

**Date:** 2026-10-02
**Brand:** OptiRFP
**Issue:** Posts published with partial logo (feather + "O" icon only) instead of full logo (feather + "OptiRFP" wordmark)

## Root Cause

The compositor script at `~/.openclaw/workspace/scripts/ideogram_logo_compositor.py` defaulted to `optirfp_icon_150px.png` instead of `optirfp_logo.jpg`.

## Detection Method

Pixel count reveals logo completeness:

| File | Dark Pixels | Contains |
|------|-------------|----------|
| `optirfp_icon_90px.png` | 2,283 | Feather + "O" only |
| `optirfp_icon_150px.png` | 5,644 | Feather + "O" only |
| `optirfp_logo.jpg` | 100,383 | Full "OptiRFP" wordmark |

```python
from PIL import Image
img = Image.open(logo_path)
data = list(img.getdata())
dark_pixels = sum(1 for r,g,b,a in data if a > 100 and (r+g+b)/3 < 200)
if dark_pixels < 10000:
    print("WARNING: Logo may be icon-only, not full wordmark")
```

## Fix Applied

Changed LOGO_PATH default from icon to full logo:
```python
# Before (WRONG)
LOGO_PATH = os.getenv("OPTIRFP_LOGO", str(Path.home() / ".hermes" / "assets" / "optirfp_icon_150px.png"))

# After (CORRECT)
LOGO_PATH = os.getenv("OPTIRFP_LOGO", str(Path.home() / ".hermes" / "assets" / "optirfp_logo.jpg"))
```

## Prevention

1. **Naming:** `brand_logo.*` = full, `brand_icon.*` = icon only
2. **Default:** Always default to full logo, never icon
3. **Verification:** Check pixel count or inspect before scheduling

## Recovery

1. Delete queued posts with broken images
2. Regenerate with fixed compositor
3. Reschedule with correct logo
4. Audit other compositor scripts
