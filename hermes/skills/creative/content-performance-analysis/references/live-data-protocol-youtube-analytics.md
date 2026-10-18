# Live-data protocol for YouTube channel reviews

Do this BEFORE any strategy claim. Never say "fixes are working / wait for the algorithm" from internal docs. A dead browser is not a reason to skip live data; yt-dlp and the Analytics API need no browser.

1. `yt-dlp --flat-playlist -J <channel>/shorts` returns titles and views only. For upload_date, duration, likes run `yt-dlp --skip-download -j https://www.youtube.com/shorts/ID` per id (6 threads, ~3 min for 190 videos). Run in background with notify_on_complete (foreground max 600s).
2. Cohort by upload month/week, compare medians, same age window (age >= 5 days). Do not only split before/after "the fix".
3. Retention via Composio works even when the Data API returns quotaExceeded (separate quota):
   `~/.composio/composio execute YOUTUBE_QUERY_ANALYTICS -d '{"ids":"channel==MINE","startDate":"..","endDate":"..","metrics":"views,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained","dimensions":"video","sort":"-views","maxResults":200}' --account <youtube account>`
   - Dimensions that worked: day, insightTrafficSourceType, country, ageGroup,gender, deviceType, creatorContentType.
   - Retention curve: metrics=audienceWatchRatio, dimensions=elapsedVideoTimeRatio, filters=video==ID (over 100% = replays).
   - Search terms: dimensions=insightTrafficSourceDetail, filters=insightTrafficSourceType==YT_SEARCH. A long date range gave HTTP 500; ~6 weeks worked.
   - Not available via API: impressions, CTR, viewed-vs-swiped (needs Studio export). Unsupported combos return 400 (subscribedStatus; video + traffic-source filter).
   - Use one wide pull over the full range when joining cohorts; separate pulls with different metric sets break joins.
4. The `day` dimension reveals bursts vs sustained growth (a batch upload can spike then go dormant for months).
5. Also check duplicate titles, uploads per day (bursts), and retention trend per cohort, not just views.
6. Competitors: use same-size or same-format channels. 7M+ channels are weak evidence. Guessed @handles often do not exist; check result size. flat-playlist gives no durations for competitors.

## Findings from Tales Untold review (Oct 2026), treat as hypotheses
- Named folklore beat generic horror ~3x at the median (87 vs 31). Viewers search entity names (la llorona, chupacabra...), so keep entity in titles.
- Best period (Jan 2026 batch): long descriptive "Entity: angle" titles (median 11 words), 46-55s, often hashtags. Sub-40s was the weakest duration bucket. An earlier version of this skill claimed short titles / zero hashtags win; not supported.
- Retention declined by cohort (median avg view %: Jan 63, Sep 53, Oct 39) at constant ~50s duration. Jan videos were rewatched (>100% retention); Oct videos lose half the audience by 25% of runtime.
- Jan spike (29k views) was a one-time batch; the channel was dormant Mar-Aug; 97% of recent views came from the newest videos.
- Mistake to avoid: recommending a 35s cap and declaring the pipeline "compliant, just wait" without checking cohort view/retention data.
