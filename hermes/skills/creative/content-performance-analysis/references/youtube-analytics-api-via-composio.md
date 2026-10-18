# Live YouTube data recipes (Tales Untold, Oct 2026)

Use these BEFORE making any claim about whether a channel strategy or pipeline fix is "working".

## 1. Public data via yt-dlp
- `yt-dlp --flat-playlist -J https://www.youtube.com/@HANDLE/shorts` gives id, title, view_count, channel_follower_count but NO upload_date or duration.
- For dates, duration, likes, comments run `yt-dlp --skip-download -j https://www.youtube.com/shorts/ID` per video. 187 videos with 6 threads takes several minutes: run it as a background process (foreground max is 600s) and write results to a JSON file.
- Segment by upload date (week/month cohort), duration bucket, and title format. Compare medians, not just means.
- `--write-auto-subs --sub-format json3` works for a handful of videos, then hits HTTP 429. Fall back to the local script files the pipeline saved (queue_done/*.txt) and say so.
- Guessed competitor handles often do not exist; check the result size before analyzing. Search results for generic queries are mostly short films, not comparable channels.

## 2. Owner analytics via Composio (works with the channel's connected account)
`~/.composio/composio execute YOUTUBE_QUERY_ANALYTICS -d '<json>' --account youtube_trader-relink`
- Works even when the Data API tools (YOUTUBE_GET_CHANNEL_STATISTICS etc.) return 403 quotaExceeded.
- Required fields: ids ("channel==MINE"), startDate, endDate, metrics. Optional: dimensions, filters, sort, maxResults.
- Useful queries that worked:
  - per video: metrics views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained; dimensions video; sort -views; maxResults 200
  - traffic: dimensions insightTrafficSourceType
  - search terms: dimensions insightTrafficSourceDetail with filters insightTrafficSourceType==YT_SEARCH (worked for a 6-week window, 500 for longer)
  - daily trend: dimensions day (reveals dormant periods and burst effects)
  - content type: creatorContentType; country; ageGroup,gender; deviceType
  - retention curve for one video: metrics audienceWatchRatio, dimensions elapsedVideoTimeRatio, filters video==ID (values over 100% = replays)
- NOT available through the API: impressions, click-through rate, viewed-vs-swiped. Ask the user for a Studio screenshot (Analytics > Engagement > How viewers engaged).
- Unsupported combos return 400/500 (subscribedStatus dimension, video+traffic source filter). Do not retry; drop the query.
- Join the per-video table to yt-dlp upload dates to compare cohorts (retention, subs per 1k views).

## 3. What the analysis showed (use as priors, not rules)
- One burst of 61 videos produced 29k views in a month, then the channel was dormant; later output did not compound.
- Avg view % fell across cohorts while duration stayed constant, so duration alone was not the cause.
- Under-40s videos were the worst duration bucket in this channel's own data; do not assume shorter is better.
