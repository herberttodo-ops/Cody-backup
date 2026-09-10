# Title Cleaning Bug: When "Trailer 2" Becomes "2"

## Session
August 31, 2026 - First Watch Society dashboard automation

## Bug Discovery

User reported: The scraper extracted "Minions & Monsters 2" instead of "Minions & Monsters".

## Root Cause

Original buggy code:
```python
clean_title = title.replace(' Trailer', '').strip()
# "Minions & Monsters Trailer 2" → "Minions & Monsters 2" ❌
```

The regex extracted "Minions & Monsters Trailer 2" (the full alt text including "Trailer 2"). When `replace("Trailer", "")` ran, it only removed "Trailer", leaving " 2" as part of the movie title.

## Fix

Replace more specific patterns before less specific:

```python
# CORRECT
clean_title = title.replace(' Trailer 2', '').replace(' trailer 2', '')
clean_title = clean_title.replace(' Trailer', '').replace(' trailer', '')
clean_title = clean_title.strip()
# "Minions & Monsters Trailer 2" → "Minions & Monsters" ✓
```

## General Rule

When cleaning scraped strings with numbered variants, always replace from most specific to least specific:

1. "Foobar 2026" / "Foobar 2025" (dated)
2. "Foobar Trailer 2" / "Foobar Trailer 3" (numbered trailer)
3. "Foobar Trailer" (unnumbered trailer)
4. "Foobar " (trailing space cleanup)

## Verification

After fix, scraper output changed:
- Before: `{"title": "Minions & Monsters 2"}`
- After:  `{"title": "Minions & Monsters"}`

## Related

The movie is actually "Minions & Monsters" (2026), starring Pierre Coffin, Trey Parker, Jesse Eisenberg. It was appearing as "Minions & Monsters Trailer 2" on TrailerAddict on August 31, 2026.
