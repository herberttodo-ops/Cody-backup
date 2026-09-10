# Visibility Fix: Contrast vs Size

## The Misunderstanding

User said: "The page is difficult to read. Please work on making it more visible"

**My initial wrong interpretation:**
- Made everything larger (font sizes increased)
- Elements became oversized
- User had to clarify: "I did not mean make everything larger. there was white text on white backgrounds"

**The actual problem:**
- Poor color contrast (white text on white backgrounds)
- Not a size issue at all

## The Correction Process

1. **User's first correction:** "Reverting to last version and create dark mode instead"
2. **User's second clarification:** "For visibility I did not mean make everything larger"

**Lesson learned:** When user says "visibility", clarify whether they mean:
- **Contrast/legibility** (color issues, light/dark mode)
- **Size** (zoom level, responsive breakpoints)
- **Layout** (information hierarchy, spacing)

## Diagnostic Questions to Ask

Before making changes:
1. "Is this a dark mode issue, or do you need larger text?"
2. "Can you describe what specifically is hard to read?"
3. "Is it the color contrast or the text size?"

## Prevention Pattern

```
User: "X is difficult to read/see"

Agent should NOT assume:
- Make text larger
- Add more contrast globally
- Change entire design

Agent should ASK:
- "What specifically is hard to see?"
- "Is it contrast (color), size, or something else?"
- Look for existing theme systems first
```
