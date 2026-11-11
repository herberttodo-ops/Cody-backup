# Logo Positioning Pitfall: Logo Covering Main Graphic Elements

## Problem

Logo placed at **bottom-center** with **percentage-based bottom margin** visually crowds centered headline and graphic elements. Logo and main content compete for the same visual space.

## Why It Happens

1. **Horizontal position: center** — Logo sits directly under centered headline text
2. **Percentage bottom margin** — e.g. `3%` on 1440px image = only 43px, pushing logo into lower third where artwork exists

**Broken pattern:**
```python
x_center = (img.width - logo.width) // 2
y_bottom = img.height - logo.height - int(img.height * 0.03)
```

## Correct Pattern (OptiRFP Brand Spec)

**Position: bottom RIGHT**
**Margin: Fixed 150px from both right and bottom edges**
**Logo width: 30% of image width**

```python
MARGIN_RIGHT = 150
MARGIN_BOTTOM = 150
x_right = img.width - logo.width - MARGIN_RIGHT
y_bottom = img.height - logo.height - MARGIN_BOTTOM
img.paste(logo, (x_right, y_bottom), logo)
```

## Why Bottom-Right Works

- Keeps logo in corner, away from centered headline and graphics
- 150px fixed margin guarantees clearance above (for graphics) and below (for platform cropping)
- 30% width is visible but non-competing

## Verification Checklist

- [ ] Logo bounding box does not overlap headline area (top 40% of image)
- [ ] Logo is at bottom-right, not center
- [ ] Margins are fixed pixels (150px), not percentages
- [ ] Logo width is ~30% of total image width

## Files Fixed in This Incident

| File | Issues |
|------|--------|
| `~/.hermes/scripts/ideogram_logo_compositor.py` | center→right, 3%→150px, 25%→30%, icon default→logo.jpg |
| `~/.hermes/scripts/ideogram_logo_compositor_v2.py` | same |
| `~/.hermes/skills/ideogram-image-generation/scripts/ideogram_logo_compositor.py` | center→right, 40px→150px, fixed height→30% width |
| `~/.hermes/skills/creative/ideogram-image-generation/templates/optirfp_logo_compositor.py` | same |

## Migration Rule

When updating logo positioning:
1. Fix ALL compositor scripts (they proliferate across `scripts/`, `skills/*/scripts/`, `workspace/scripts/`)
2. Regenerate all pending scheduled posts with old positioning
3. Verify new images against checklist before scheduling
