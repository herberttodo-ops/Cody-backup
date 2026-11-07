# Tales Untold 4-arm script test: template integrity and voice analysis (Nov 6 2026)

Design source: `tales-untold/PIPELINE_UPDATE_PLAN_2026-10-17.md` section 12.
Arms: E = third-person explainer (Jan style), S = story opener (named person + concrete event, third person),
H = hook event then explainer, C = control (Oct style, first person). Measure stayed-to-watch, avg view %, median 7-day views.

## Trap: refill generators silently break the experiment
`arm_schedule_refill.py` (and the 9am cron copy `~/.hermes/scripts/tale_arm_schedule_refill.py`) chose
`random.choice(TEMPLATES)` regardless of arm. 3 of 5 templates were first person, so E/H videos went out first person
and the arms stopped meaning anything. Any time a generator touches queued stories, audit voice per arm, not just word count.

## Fix now in place
- `TEMPLATES_BY_ARM` (E/S/H, 3 each, third person, 100-130 words) plus old first-person `TEMPLATES` used only for C.
- `make_story(arm, ...)` validates 100-130 words and zero first-person words (I, I'm, my, me) for non-C arms.
- `arm_for(date_str, slot_i)` rotates arms across the 3 daily slots; both refill scripts import it.
- Entities with region "Internet/Global" or category creepypasta read badly in "In {region}" templates; check the rendered text.
- Backups: `arm_schedule_refill.py.bak_arms_20261106`, `queue_backup_arms_20261106/`.
- Existing already-queued days keep the fixed E 6pm / S 7pm / H 8pm pattern; no C was queued.

## Voice vs performance (analytics pulled Nov 6, small n, not conclusive)
Method (reusable):
1. `composio execute YOUTUBE_QUERY_ANALYTICS --account youtube_trader-relink -d '{"ids":"channel==MINE","startDate":"...","endDate":"...","metrics":"views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained","dimensions":"video","sort":"-views","maxResults":200}'`
2. Titles: `yt-dlp --flat-playlist --print "%(id)s|%(title)s|%(view_count)s" https://www.youtube.com/channel/UCr20g-L8cMMfBgSp7PA09ZQ/shorts` (the @handle URL has no shorts tab).
3. Join title to script in `queue_done/`, `queue/`, `stories/` by entity slug; classify first vs third person by opening sentences.
Result: only 40 of 150 videos matched a saved script. First person n=26 median 72 views / 45.4% watched; third person n=14 median 132 views / 43.6%. Oct-only: first 70 views (n=19) vs third 166 (n=4). Retention about equal; views lean third person. Pre-Oct first person had 71.8% watched (n=5). Arm n is 1 to 3 each, so no arm conclusion. Do not claim "first person is worse" from this.
Saved at `tales-untold/research/voice_analysis_nov6.json`.

## Fiction framing
S and C stories invent named people and claims. Keep them framed as stories, never as documented fact about the entity.
