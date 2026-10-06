# Entity Selection Pipeline Anti-Pattern
**Date:** 2026-10-05
**Session:** Tales Untold 3-short production run
**Severity:** Content strategy violation — repeating proven entities when 200+ unique ones exist

## The Mistake

When asked "Produce 3 more Tales Untold shorts and publish them to YouTube tonight," the pipeline was initialized with:
1. **Mothman** — already in hardcoded STORY_SCENES, already produced before
2. **Skinwalker** — already in hardcoded STORY_SCENES, already produced before
3. **Loch Ness** — already in hardcoded STORY_SCENES, already produced before

All three were from the 14-entity hardcoded list in `pipeline_v3.py`, despite:
- A 205-entity folklore database existing at `data/folklore_cryptid_database.json`
- A `folklore_db.py` module with `remaining_producible()` tracking
- A `queue_done/` directory showing these specific entities had ALREADY been produced

User corrected: "No, use something from the 200+" (paraphrased: these are from the 14 hardcoded list, you have 200+ to choose from).

## The Fix

When producing Tales Untold shorts, ALWAYS query the folklore database first:

```python
import sys
sys.path.insert(0, '/home/herby/.openclaw/workspace/tales-untold')
from folklore_db import get_random_unproduced, remaining_producible

# This yields ACTUALLY unique entities never before produced
entity = get_random_unproduced()
print(entity['name'], entity['region'], entity['category'])
```

The session recovered by selecting:
- **El Silbon** (Venezuela, ghost)
- **Siguanaba** (El Salvador, shapeshifter)
- **Aqrabuamelu** (Mesopotamia, scorpion-man)

All three required adding new scene prompts to `pipeline_v3.py`'s `STORY_SCENES` dict.

## Database Checklist

Before selecting any entity, verify these conditions ALL hold:
1. [ ] `remaining_producible()` contains > 100 entities (not exhausted)
2. [ ] Selected entity NOT in `queue_done/` directory
3. [ ] Selected entity NOT in hardcoded STORY_SCENES (or add scenes if it is)
4. [ ] Entity has unique cultural region (avoid "generic" category)

## When to Use Hardcoded vs Database

| Situation | Source |
|-----------|--------|
| Normal production | `folklore_db.get_random_unproduced()` |
| User explicitly requests specific entity | STORY_SCENES if available, else generate prompts |
| Database exhausted (< 5 remaining) | Rotate back to beginning with new variant angles |

## Scene Prompt Generation Pattern

For entities NOT yet in STORY_SCENES, write 4 Gammell-style prompts and add them:

```python
STORY_SCENES["entity_name"] = [
    "[entity] in [natural setting], establishing dread",
    "[terrifying detail of entity] close-up, disturbing",
    "[entity] [action: emerging/revealing/transforming]",
    "aftermath of [entity] presence, lingering horror",
]
```

All prefixed by pipeline with: "Stephen Gammell ink wash illustration, deep black shadows, monochrome grayscale, high contrast"
