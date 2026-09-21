# Trend Pivot Workflow

Switching content themes based on trending topics (e.g., "creatures in the woods").

## When to Pivot

- User identifies a trending content angle
- Current batch has a defined end date
- New theme aligns with channel positioning

## Preparation Checklist

### Shorts (60s vertical)
- [ ] Write 5-7 micro-stories (140-180 words each)
- [ ] Create Gammell-style prompts for each
- [ ] Build JSON batch file with all metadata
- [ ] Test one complete video end-to-end
- [ ] Update story selector with date-based switcher

### Long-Form (12-17 min horizontal)
- [ ] Expand 3 best shorts into full narratives
- [ ] Target 27 minutes, ~155 WPM measured
- [ ] Write to `longform/queue/` as .txt files
- [ ] Include scene breakdowns in story
- [ ] Prepare thumbnail prompts

## Date-Based Switcher Pattern

```python
# story_selector.py
PIVOT_DATE = datetime(2026, 9, 22)  # When to switch

def get_current_batch():
    if datetime.now() >= PIVOT_DATE:
        return load_new_batch(), "new_theme"
    return load_old_batch(), "current_theme"
```

## Key Insight

Always prepare **BOTH** formats:
- Shorts fill Buffer (3/day)
- Long-form hits YouTube (3/week)
- Both pivot simultaneously for brand consistency

## Example: Creatures in Woods

**Shorts batch:** 5 stories
1. Trail cam shows something standing behind me
2. Deer standing on two legs
3. GPS says 47 miles on 3-mile loop
4. Ranger says footprints aren't bear
5. Something mimics my voice

**Long-form queue:** 3 expanded stories
- Same hooks, deeper narratives
- ~27 min each
- Same Gammell style, same voice

## Verification

```bash
# Check both queues
ls ~/.openclaw/workspace/tales-untold/stories/*batch.json
ls ~/.openclaw/workspace/tales-untold/longform/queue/*.txt

# Verify switcher works
python3 story_selector.py --test
```

## Cron Behavior

- Daily cron checks current date
- Auto-switches batches at pivot date
- No manual intervention needed
- Buffer never goes empty
