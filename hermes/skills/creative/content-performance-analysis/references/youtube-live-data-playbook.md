# Live YouTube channel data: what actually works (verified Oct 2026, Tales Untold)

## Rule
Never claim a fix is "working" or give channel strategy from internal docs alone. Pull live numbers first, and
cohort them by upload date (before/after a change). A session once told the user "fixes working, wait for the
algorithm" with zero view data; the post-fix cohort was actually worse than baseline.

## Public data via yt-dlp (no auth)
- `yt-dlp --flat-playlist -J https://www.youtube.com/@HANDLE/shorts` gives ids, titles, view_count, subscriber count,
  but NO upload_date or duration. Channels with no long-form return an error on /videos (not a bug).
- For upload_date/duration/likes/comments run `yt-dlp --skip-download -j https://www.youtube.com/shorts/ID` per
  video, 6 threads. ~190 videos takes several minutes: run it as a script with terminal(background=true,
  notify_on_complete=true); foreground max is 600s.
- Group results by week/cohort, duration bucket, title format; compare MEDIANS (means are skewed by 1-2 hits).
- Subtitle download (`--write-auto-subs --sub-format json3`) hits HTTP 429 after ~10 videos. Use local script
  files if the pipeline saves them, and say the text is unverified against what was spoken.
- Competitor search (`ytsearchN:query`) mostly returns short films/memes. Scrape named channels' /shorts tab instead
  and check subscriber scale before comparing (a 7M-sub channel is not a benchmark for a 250-sub channel).
  Guessed handles often don't exist.

## Owner analytics via Composio (works when the Data API is quotaExceeded)
`~/.composio/composio execute YOUTUBE_QUERY_ANALYTICS -d '{...}' --account <youtube account>`
- Required: ids ("channel==MINE"), startDate, endDate, metrics.
- Worked: dimensions video / day / insightTrafficSourceType / country / ageGroup,gender / deviceType /
  creatorContentType; filters `video==ID`; per-video retention curve with dimension elapsedVideoTimeRatio and
  metric audienceWatchRatio (values >1 = replays).
- Metrics that worked: views, estimatedMinutesWatched, averageViewDuration, averageViewPercentage, likes,
  comments, shares, subscribersGained/Lost, viewerPercentage.
- NOT available: impressions, CTR, viewed-vs-swiped (ask the user for a Studio mobile screenshot of
  "How viewers engaged"). Unsupported combos returned 400/500 (subscribedStatus, search-source filtered by video,
  insightTrafficSourceDetail over a long range; the shorter Sep-Oct range worked and gave search terms).
- Pull the same metric set for every query you intend to join; a different metric list per file broke a join.

## Analysis checks that paid off
1. Monthly views by day: reveals bursts vs sustained growth (batch of 61 videos = one month of views, then nothing).
2. Cohort retention (median avg view %, avg view duration, subs per 1k views) by upload period.
3. Views-by-cohort over the last 30 days: shows whether old videos still earn (they did not).
4. Search terms: tells you whether the entity/keyword in the title matters.
5. Duration buckets: check before recommending a length cap. Under-40s was the WORST bucket here.
6. Duplicate-title count and uploads-per-day (burst posting).

## Verify the rendered output, not the code
Extract frames (`ffmpeg -ss T -i video.mp4 -frames:v 1 -vf crop=iw:ih*0.35:0:ih*0.55,scale=300:-1`), tile them with
PIL, and look. This caught a bug no log showed: GSAP TextPlugin never loaded, so captions silently did not render
on recent videos while the pipeline reported success. Keep heredocs short; very large inline commands get blocked.
