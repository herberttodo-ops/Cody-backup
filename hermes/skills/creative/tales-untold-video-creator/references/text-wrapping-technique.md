# Text Wrapping Technique

## Problem
MoviePy's TextClip with method='caption' breaks words mid-word when wrapping, producing:
- "conversa-tion" (wrong)
- "whispe-red" (wrong)

## Solution: Manual Word Wrapping

```python
def manual_word_wrap(text, max_chars=28):
    """
    Wrap text at word boundaries only.
    Never break mid-word.
    """
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        # +1 for space
        if len(current_line) + len(word) + (1 if current_line else 0) <= max_chars:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return "\n".join(lines)

# Usage in TextClip
caption_text = manual_word_wrap("I've always been a heavy sleeper.")
txt = TextClip(
    text=caption_text,
    font='DejaVuSans-Bold',
    font_size=44,
    color="white",
    stroke_color="black",
    stroke_width=5,
    method='caption',  # Still needed for centering
    size=(900, None),  # Constrain width
)
```

## Result
- "I've always been a heavy sleeper." (correct, whole words)
- No hyphenation, no broken words