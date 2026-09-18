# Tales Untold Shorts: Title & Metadata Strategy

Researched 2026-09-17 against live YouTube data (Mr Nightmare, CreepsMcPasta,
Let's Read, MrBallen) via yt-dlp. Small samples (5-15 shorts/channel) --
treat magnitude as directional, not statistically rigorous. Full writeup:
"Tales Untold Shorts Strategy Research 2026-09-17.md" in the Obsidian vault
(Agent-Shared/).

## The headline finding

Mr Nightmare's shorts view range (178K-1.34M sampled) beats CreepsMcPasta's
range (9.5K-26K sampled) by 7-19x at the floor. This is the single clearest
signal in the research: whatever else varies, Mr Nightmare's shorts strategy
categorically outperforms the other horror-specific channels in the niche.

## What's confirmed and now implemented

1. **Duration: 29-60s, not padded.** Mr Nightmare's shorts sampled: 29s, 35s,
   40s, 58s, 58s, 59s, 60s -- real variance, cut to what the story needs.
   Tales Untold's existing 48-61s range already matches this.

2. **Zero tags.** Every top performer sampled uses no tags at all on shorts
   (matches their long-form pattern too). Implemented: do not pass a `tags`
   field when posting.

3. **Minimal description, cross-promotion to long-form.** Pattern observed:
   one hook line (no hashtags) + "Subscribe for more stories in short & long
   form." Implemented as `build_short_description()` in
   `buffer_dual_account.py`: one hook line + "Subscribe for more Tales
   Untold, short and long form horror." No hashtag stuffing
   (previously: `#shorts #horror #creepypasta` in every description --
   removed).

## What's a hypothesis under active test, not yet confirmed

**Title structure.** The single highest performer in the research sample
("Her twin brothers were the original victims", 1.34M views) used a
third-person retrospective-reveal structure -- implies a larger mystery
rather than stating one jump-scare beat. Lower performers in the same sample
were more generic first-person "I saw X" statements. This is suggestive with
only 7 data points, not proven.

**Running A/B test (started 2026-09-17):**
- Variant A = direct first-person hook (our historical default)
- Variant B = third-person retrospective-reveal hook

Alternated automatically via `tales_ab_tracker.py next` in Phase 0 of
production. Logged via `tales_ab_tracker.py log <id> <A|B> <title>` after
each post. Pull results with `tales_ab_tracker.py report` -- wait for at
least 5 videos per variant (roughly 2 weeks at 3x/day mixed with long-form
weeks) before drawing a conclusion. The report script warns if the sample
is still too small.

## What was deliberately NOT changed

Production pipeline (voice, art style, story-writing formula, Whisper
alignment, HyperFrames rendering) -- none of that is a metadata/posting
concern and wasn't part of this research. Posting cadence (3x/day, 6-8pm ET)
was fixed separately; see the shorts-workflow-review note in the vault.
