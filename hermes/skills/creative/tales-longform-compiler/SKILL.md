---
name: tales-longform-compiler
description: Compile 500+ view folklore shorts into 10-12 minute videos.
triggers:
  - User wants to create long-form video from shorts
  - A short has exceeded 500 views and needs compilation
  - Need to expand successful short into 10-12 minute long-form
---

# Tales Untold Long-Form Compiler

**CRITICAL: Only produce long-form when a short exceeds 500+ views.**

## Performance Reality
| Format | Avg Views | Strategy |
|--------|-----------|----------|
| Folklore Shorts | **786** | Primary content |
| Long-Form (standalone) | **12** | **DO NOT PRODUCE** |
| Long-Form (compilation) | TBD | Only after 500+ view short |

## When to Compile
1. Check YouTube Analytics for shorts exceeding 500 views
2. Verify the short is Tier 1 folklore/cryptid content
3. Queue compilation only if both conditions met

## Compilation Format

### Target Specs
- **Duration:** 10-12 minutes (not 26+ minutes)
- **Structure:** 3 related shorts + expanded narration
- **Cost:** ~$3-5 vs $2-5 for failed 26-minute attempts

### Structure
1. **Cold Open (0:00-0:15)**
   - Most disturbing sentence from the entity encounter
   - No title card, no channel intro
   - Start on narration within 3 seconds

2. **Part 1: The Encounter (0:15-4:00)**
   - Original short #1 (unedited)
   - Or expanded 2-3 minute version

3. **Part 2: The Aftermath (4:00-7:00)**
   - Related short #2
   - Different angle on same entity

4. **Part 3: The Truth (7:00-10:00)**
   - Related short #3 or expanded climax

5. **Outro (10:00-11:00)**
   - CTA pointing to other compilations

### Title Format
"The Complete [Entity] Account | Tales Untold"
- No em dashes
- Entity name prominent
- Implies compilation, not standalone

### Visuals
- Use existing Gammell-style illustrations from shorts
- 40-50 unique images with Ken Burns variation
- No new image generation required

### Audio
- Music bed: existing Tales Untold tracks
- Duck to -22dB under narration
- Loop with 6-second crossfades

## Workflow

### Step 1: Verify Gate
```python
# Check if short exceeded 500 views
if short_views < 500:
    REJECT("Need 500+ views before compilation")
    return
```

### Step 2: Select Related Shorts
- Identify 2-3 shorts on same entity/topic
- Download from YouTube if needed
- Verify all have faststart flag

### Step 3: Build Compilation
- Concatenate shorts with chapter markers
- Add expanded narration between segments
- Apply music bed and captions

### Step 4: Upload
- Target: Weekend evenings or Thursday nights (6-8 PM ET)
- Playlist: Add to entity-specific playlist
- End screen: Point to next compilation

## Automation

### Cron (Conditional)
- Check: Any short >500 views in last 7 days?
- If YES: Queue compilation
- If NO: Skip

### Manual Trigger
Check YouTube Analytics weekly, queue compilation for top performer.

## References
- `spielberg` skill for shorts production
- `tales-music-bed` script for audio
- YouTube Analytics for view thresholds
