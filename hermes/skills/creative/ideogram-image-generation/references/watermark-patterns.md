# Ideogram V4 Watermark Patterns and Prompt Engineering

Documenting fake watermarks and branding that Ideogram V4 injects, and how to suppress them.

## Known Fake Watermark Patterns

Ideogram V4 frequently adds the following fake branding to generated images:

| Pattern | Location | Description |
|---------|----------|-------------|
| `LinkedIFP` | Bottom left | Fake LinkedIn-style branding |
| `Thekecs` / `Thekecs aclonapt` | Bottom left/center | Nonsense watermark text |
| `Cxeottics` | Bottom right | Fake branding with numbers like "23/40" |
| `23/40`, `XX/YY` | Bottom right corner | Fake page/progress indicators |
| `+` icons | Near text | Decorative UI elements |
| Grid lines | Background | Subtle grid pattern |

## Suppression Strategy

### 1. Aggressive Prompt Exclusions

The most effective approach is explicit prohibition in the prompt:

```
ABSOLUTELY FORBIDDEN - NO EXCEPTIONS:
- NO watermarks of any kind
- NO "LinkedIFP", "Thekecs", "Cxeottics", or any similar text
- NO numbers in corners or edges
- NO fake logos or branding
- NO additional text beyond the exact headline provided
- NO decorative text, UI elements, or icons
- NO timestamps, NO counters, NO progress indicators
- The bottom area must be completely clean dark navy ONLY
```

### 2. Clean Zone Reservation

Explicitly reserve space to prevent visual clutter:

```
LAYOUT:
- Bottom 20% should be solid dark navy with absolutely NOTHING else
- This area is reserved for logo placement - keep it completely clean
- NO visual elements, text, or patterns in the bottom area
```

### 3. API Settings

```python
files = {
    "text_prompt": (None, prompt),
    "aspect_ratio": (None, "ASPECT_1_1"),
    "model": (None, "V_4"),
    "magic_prompt_option": (None, "OFF")  # Critical: disables auto-enhance
}
```

Setting `magic_prompt_option` to `"OFF"` prevents Ideogram from "enhancing" your prompt with its own additions.

## Quality Verification Checklist

After generation, verify:

- [ ] **Text Clarity**: Headline perfectly legible at full size and thumbnail
- [ ] **No Watermarks**: Scan all corners and edges for fake branding
- [ ] **Brand Colors**: Confirm dark navy (#0F172A) and mint (#40D395)
- [ ] **Clean Bottom**: Bottom 20-25% is solid color, no elements
- [ ] **No Grid Lines**: Background should not have unwanted grid patterns
- [ ] **No UI Icons**: No +, arrows, or decorative icons near text

## Regeneration Triggers

Regenerate if ANY of the following appear:
- Any watermark text (LinkedIFP, Thekecs, Cxeottics, etc.)
- Numbers in corners (like "23/40")
- Fake logos or icons
- Garbled/misspelled headline text
- Grid lines in background (if unwanted)
- Bottom area not clean for logo

## Success Rate

With aggressive exclusions:
- ~70% of generations come out clean on first try
- ~25% need 1 regeneration
- ~5% need 2+ regenerations

Always verify with vision analysis before proceeding to logo compositing.

## Related

- Main skill: `ideogram-image-generation`
- Compositor script: `scripts/ideogram_logo_compositor.py`
- Logo transparency: `remove_white_background()` function in compositor
