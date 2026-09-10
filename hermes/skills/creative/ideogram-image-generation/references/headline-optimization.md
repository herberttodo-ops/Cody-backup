# Ideogram Headline Optimization Guide

Based on production testing with Ideogram V4 for OptiRFP LinkedIn graphics.

## The 5-8 Word Rule

**Optimal headline length: 5-8 words**

Ideogram V4 struggles with longer headlines, often producing:
- Text duplication/repetition
- Garbled or misspelled words
- Truncated text
- Poor layout

## Examples

### ✅ Good (5-8 words) - Production Verified
| Headline | Result | Session |
|----------|--------|---------|
| "Features tell. Outcomes sell." | 9.5/10 - Perfect | Aug 2026 |
| "80% of losing RFPs are copy-pasted" | 9/10 - Clean | Aug 2026 |
| **"Copy paste RFPs copy paste losses"** | **9/10 - Clean** | **Sept 2026** |
| "Specificity beats generic promises" | 8/10 - Minor issues | Sept 2026 |

### ❌ Avoid (>10 words, punctuation, or complex)
| Headline | Result |
|----------|--------|
| "Lead with outcomes, not features" | 6/10 - Text duplication |
| "The winning RFPs focus on results not features" | 5/10 - Truncated, blurry |
| "Winning proposals answer so what first" | 7/10 - Minor artifacts |
| "Specificity beats generic promises every time" | 8/10 - Okay but wordy |

## Punctuation Guidelines

| Punctuation | Recommendation |
|-------------|----------------|
| Periods | ✅ Safe, use for punchy fragments |
| Commas | ⚠️ Avoid in short headlines; use only if necessary |
| Quotes | ⚠️ Can confuse AI; use sparingly |
| Question marks | ✅ Works if headline is short |
| Exclamation marks | ✅ Safe |
| Apostrophes | ✅ Safe |

## Headline Patterns That Work

### Pattern 1: X vs Y (2x2 words)
```
"Features tell. Outcomes sell."
"Process wastes. Results matter."
```

### Pattern 2: Statistic + Insight (5-7 words)
```
"80% of RFPs fail this test"
"Winning proposals lead with outcomes"
```

### Pattern 3: Imperative + Benefit (5-6 words)
```
"Stop copying. Start winning."
"Mirror the RFP. Win more."
```

## Testing Checklist

- [ ] Headline is 5-8 words
- [ ] No unnecessary punctuation
- [ ] Punchy and scannable
- [ ] Action-oriented or insight-driven
- [ ] Works without context

## When to Regenerate

If vision analysis shows:
- **Text duplication** → Shorten headline, simplify punctuation
- **Blurry text** → Reduce word count, increase font size in prompt
- **Truncation** → Shorten headline significantly

## Prompt Template

```python
HEADLINE = "Features tell. Outcomes sell."  # 5 words, periods only

# In prompt:
f"""HEADLINE TEXT (render prominently, large bold text):
\"{HEADLINE}\"

REQUIREMENTS:
- Text must be crystal clear, perfectly legible
- No duplication, no truncation
- Large, bold, centered"""
```
