# Ideogram Layout Prompting Guide

Lessons learned from fixing layout issues in OptiRFP social media graphics.

## The Problem

Initial prompts produced:
- Text off-center or left-aligned
- Weird negative space in random areas
- Navy blue rectangular blocks at bottom
- Unbalanced composition

## The Solution: Zone-Based Layout

Explicitly define three zones with exact percentages:

```
Zone 1 (Top 0-40%): Headline text, centered, prominent
Zone 2 (Middle 40-75%): Visual elements supporting the message  
Zone 3 (Bottom 75-100%): Clean dark navy area with NO elements
```

## Critical Prompt Elements

### 1. Headline Positioning (Explicit)

```
HEADLINE TEXT - POSITIONING IS CRITICAL:
"Your headline here"
- Place headline text in the UPPER CENTER of the image (top 40% of frame)
- Text must be CENTERED horizontally, not left-aligned or right-aligned
- Text should occupy the visual center of attention
- Large, bold, highly readable text
- Generous spacing around the text on all sides
```

**Why this works:**
- Removes ambiguity about "centered or top-aligned" 
- Forces centered horizontal alignment
- Defines exact vertical zone (top 40%)

### 2. Smooth Transitions (Critical)

```
CRITICAL LAYOUT RULES:
- The bottom area should naturally fade to solid navy - NO hard edges, NO rectangular blocks
- NO navy-colored rectangles, blocks, or bars anywhere - smooth gradients only
- Smooth, gradual transitions - NO hard edges or solid color blocks
- NO hard edges between visual areas - everything should blend smoothly
```

**Why this works:**
- Prevents navy rectangles/blocks at bottom
- Ensures smooth gradient transitions
- Avoids "divided" look with hard boundaries

### 3. Prohibitions for Clean Bottom

```
ABSOLUTE PROHIBITIONS:
- NO navy-colored rectangles, bars, or blocks (smooth gradients only)
- NO hard edges between visual areas - everything should blend smoothly
- NO decorative text elements in the bottom area
```

## Before vs After

### Before (Problematic):
```
LAYOUT:
- Headline text should be the FOCAL POINT, large and centered or top-aligned
- Visual elements should SUPPORT, not compete with, the text
- Bottom 25% of image: MUST be completely clean, solid dark navy background
```
**Result:** Off-center text, navy blocks, uneven spacing

### After (Fixed):
```
LAYOUT ZONES - FOLLOW EXACTLY:
Zone 1 (Top 0-40%): Headline text, centered, prominent
Zone 2 (Middle 40-75%): Visual elements ({visual}), supporting the message
Zone 3 (Bottom 75-100%): Clean dark navy area with NO elements whatsoever

CRITICAL LAYOUT RULES:
- The headline text MUST be centered in the upper portion of the image
- Visual elements in the middle should frame and support the centered text
- The bottom area should naturally fade to solid navy - NO hard edges, NO rectangular blocks
- The overall composition should feel balanced with the text as the clear focal point
- NO navy-colored rectangles, blocks, or bars anywhere - smooth gradients only
```
**Result:** Centered text, smooth gradients, balanced composition

## Verification Checklist

After generating, check for:
- [ ] Headline is centered (not left/right aligned)
- [ ] Text is in upper portion (not middle or scattered)
- [ ] No navy rectangles/blocks at bottom
- [ ] Smooth gradient transitions throughout
- [ ] Balanced composition with clear focal point
- [ ] Bottom area is clean for logo placement

## Related

- See `scripts/ideogram_logo_compositor.py` for working implementation
- See SKILL.md for complete prompt template
