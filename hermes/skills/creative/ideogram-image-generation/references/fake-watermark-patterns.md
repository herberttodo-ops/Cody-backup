# Fake Watermark Patterns in Ideogram V4

## Known Fake Branding Patterns

Ideogram V4 frequently generates fake watermarks and branding that resemble the requested content. These must be aggressively excluded in prompts.

### Observed Fake Watermarks

| Pattern | Description | Location | Severity |
|---------|-------------|----------|----------|
| `LinkedIFP` | Fake LinkedIn-style branding | Bottom center | High |
| `Thekecs` | Nonsensical fake watermark | Corners | Medium |
| `Cxeottics` | Nonsensical fake watermark | Corners | Medium |
| `OptiIFP` | Corruption of "OptiRFP" | Bottom left | High |
| `IptiRFp` | Transposition of "OptiRFP" | Bottom center | High |
| `in` icon | Blue square LinkedIn-style "in" logo | Bottom center | High |
| `OptiRFP in` | Combined fake branding with "in" icon | Bottom center | High |
| Numbers | Random digits in corners | Any corner | Low |

### Working Exclusion Strategy

After testing, this exclusion block proved effective:

```
ABSOLUTELY FORBIDDEN - NO EXCEPTIONS:
- NO watermarks of any kind
- NO "LinkedIFP", "Thekecs", "Cxeottics", "OptiIFP", "IptiRFp" or similar fake branding
- NO LinkedIn icons, NO social media icons, NO "in" logos
- NO numbers in corners or edges
- NO fake logos or branding of any kind
- NO additional text beyond the exact headline provided
- NO small text in corners, NO bylines, NO attribution text
- NO decorative text, UI elements, or icons
- NO timestamps, NO counters, NO progress indicators
- Bottom 20% of image must be completely clean dark navy ONLY
```

### Key Settings

- `magic_prompt_option: "OFF"` - Critical. Disables Ideogram's auto-enhancement which often adds branding
- Explicit "NO" list with examples - Naming specific fake watermarks that appeared helps prevent them
- Clean zone specification - Reserving 20% at bottom prevents logo-area contamination

### Regeneration Strategy

Ideogram V4 is non-deterministic. If fake watermarks appear:

1. **Do not retry with same prompt** - V4 often generates similar artifacts
2. **Add specific exclusion** - Include the exact fake watermark text in exclusions
3. **Regenerate up to 3 times** - Usually resolves by third attempt
4. **Verify with vision** - Always check output before compositing logo

### Quality Threshold

- **9/10 or above**: Proceed to post
- **7-8/10**: Minor issues (e.g., small fake watermark like LinkedIn "in" icon), regenerate if time permits
- **Below 7/10**: Regenerate (e.g., prominent fake branding, unreadable text)

**Common quality downgrades:**
- Blue LinkedIn "in" icon at bottom: -2 points (7/10)
- Fake "LinkedIFP" or "OptiIFP" branding: -3 points (6/10 or below)
- Text readability issues
- Wrong color scheme
- AI artifacts in visual elements
