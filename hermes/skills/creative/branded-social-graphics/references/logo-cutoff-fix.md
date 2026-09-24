# Logo Cutoff Fix — Social Platform Cropping

**Issue Date:** 2026-09-23  
**Brand:** OptiRFP  
**File Affected:** `~/.hermes/scripts/ideogram_logo_compositor.py`

## Problem

Logo was being cut off at the bottom edge when posts appeared on LinkedIn and Facebook feeds.

## Root Cause

- Generated image size: 2560x1440 (16:9) — Ideogram V4 returns 16:9 even when requesting 4:3
- Logo positioned at: `img.height - logo.height - 50` (50px bottom margin)
- Logo bottom edge: only 50px from image bottom
- **LinkedIn/Facebook crop images for feed display**, cutting off bottom edges

## Solution

Increased bottom margin from 50px to **150px**:

```python
# BEFORE — logo gets cut off
position = ((img.width - logo.width) // 2, img.height - logo.height - 50)

# AFTER — safe from platform cropping
margin_bottom = 150
position = ((img.width - logo.width) // 2, img.height - logo.height - margin_bottom)
```

## Impact

| Metric | Before | After |
|--------|--------|-------|
| Logo Y position | 1290px | 1190px |
| Bottom margin | 50px | 150px |
| Safe zone | ❌ Too tight | ✅ Protected |

## Verification

Checked `~/.hermes/scripts/ideogram_logo_compositor.py` line 141-144:
- Changed: `position = ((img.width - logo.width) // 2, img.height - logo.height - 50)`
- To: `margin_bottom = 150` then `position = ((img.width - logo.width) // 2, img.height - logo.height - margin_bottom)`

## Prevention

**Always use 150px+ bottom margin for logos in social graphics.**

Social platforms (LinkedIn, Facebook, Twitter/X, Instagram) all crop images when displaying. The bottom edge is particularly vulnerable. Logo compositing code must account for this.

## Reference

- See main SKILL.md Pitfall #12 for full context
- Related: Buffer posting via `buffer_dual_account.py`
