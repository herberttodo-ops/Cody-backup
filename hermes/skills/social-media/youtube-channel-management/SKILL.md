---
name: youtube-channel-management
description: Remove duplicate YouTube videos via Data API.
---

# YouTube Channel Management

Manage YouTube channel content at scale: detect duplicates, compare performance, remove underperformers, and verify cleanup. Designed for automated pipelines that produce many videos (e.g. Tales Untold) and need periodic hygiene runs.

## When to Use
- User reports duplicate videos were uploaded
- Need to clean up a channel after a pipeline bug (e.g. Buffer fallback bug)
- Want to audit upload history for duplicates, broken titles, or other content issues
- Need bulk metadata fixes or bulk deletions

## Prerequisites
- YouTube Data API OAuth credentials at `~/.config/youtube_credentials.json`
- `google-api-python-client`, `google-auth` Python packages
- Full `https://www.googleapis.com/auth/youtube` scope (delete operations need this)

## Step 1: Detect Duplicates

Fetch all uploads and group by title. Identical titles usually mean the same video uploaded twice.

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json, os

creds_path = os.path.expanduser('~/.config/youtube_credentials.json')
with open(creds_path) as f:
    d = json.load(f)

creds = Credentials(
    token=d['token'],
    refresh_token=d.get('refresh_token'),
    token_uri=d.get('token_uri', 'https://oauth2.googleapis.com/token'),
    client_id=d.get('client_id', os.environ.get('YOUTUBE_CLIENT_ID', '')),
    client_secret=d.get('client_secret', os.environ.get('YOUTUBE_CLIENT_SECRET', '')),
    scopes=d.get('scopes', ['https://www.googleapis.com/auth/youtube'])
)

youtube = build('youtube', 'v3', credentials=creds)

# Get upload playlist
channels = youtube.channels().list(part='contentDetails', mine=True).execute()
uploads_id = channels['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# Fetch ALL uploads (paginated)
videos = []
page_token = None
while True:
    params = {'part': 'snippet', 'playlistId': uploads_id, 'maxResults': 50}
    if page_token:
        params['pageToken'] = page_token
    pl = youtube.playlistItems().list(**params).execute()
    videos.extend(pl['items'])
    page_token = pl.get('nextPageToken')
    if not page_token:
        break

# Group by title
title_map = {}
for v in videos:
    title = v['snippet']['title']
    vid = v['snippet']['resourceId']['videoId']
    title_map.setdefault(title, []).append(vid)

duplicates = {k: v for k, v in title_map.items() if len(v) > 1}
print(f"Total videos: {len(videos)}, Duplicate titles: {len(duplicates)}")
```

**Edge case:** Some legitimate reuploads share titles (remasters). Always verify by checking upload timestamps - duplicates from a bug will be within minutes/seconds of each other.

## Step 2: Fetch Detailed Statistics

Get views, likes, comments for all duplicate candidates. Note: max 50 video IDs per API call.

```python
all_ids = [vid for group in duplicates.values() for vid in group]
stats = {}
for i in range(0, len(all_ids), 50):
    batch = all_ids[i:i+50]
    response = youtube.videos().list(
        part='statistics,snippet,status',
        id=','.join(batch)
    ).execute()
    for item in response.get('items', []):
        vid = item['id']
        stats[vid] = {
            'title': item['snippet']['title'],
            'views': int(item['statistics'].get('viewCount', 0)),
            'likes': int(item['statistics'].get('likeCount', 0)),
            'comments': int(item['statistics'].get('commentCount', 0)),
            'privacy': item['status'].get('privacyStatus', 'unknown'),
            'published': item['snippet']['publishedAt'],
        }
```

## Step 3: Choose Which to Delete (Scoring)

For each duplicate group, score each copy and keep the best:

```python
def score_video(v):
    # Weighted composite: views + likes*10 + comments*20
    return v['views'] + v['likes'] * 10 + v['comments'] * 20

for title, ids in duplicates.items():
    entries = [dict(stats[vid], id=vid) for vid in ids]
    entries.sort(key=score_video, reverse=True)
    
    best = entries[0]
    to_delete = entries[1:]
    
    print(f"\n'{title}':")
    print(f"  ★ KEEP  {best['id']} - {best['views']} views, {best['likes']} likes")
    for w in to_delete:
        print(f"  ✗ DELETE {w['id']} - {w['views']} views, {w['likes']} likes")
```

**Rationale:** Views weight 1 (discovery), likes 10x (engagement), comments 20x (strongest signal). Adjust for niche.

## Step 4: Execute Deletions

Delete the worse-performing copies:

```python
for item in removal_plan:
    vid = item['worse_id']
    try:
        youtube.videos().delete(id=vid).execute()
        print(f"✓ Deleted {vid}")
    except Exception as e:
        print(f"✗ Failed {vid}: {e}")
```

**Safety checks:** Print before deleting. Save plan JSON for audit. 404 errors mean already deleted - log and continue.

## Step 5: Verify Cleanup

Re-scan the channel to confirm zero duplicates remain:

```python
remaining = {k: v for k, v in title_map.items() if len(v) > 1}
if not remaining:
    print("\n✓ No duplicates remaining. Channel is clean.")
else:
    print(f"\n⚠ {len(remaining)} duplicate groups still present")
```

## API Error Handling

| Error | Cause | Fix |
|---|---|---|
| 403 Forbidden | Quota exceeded | Quota resets at midnight project timezone; retry tomorrow |
| 404 Not Found | Already deleted or stale ID | Log and continue |
| OAuth expired | Refresh failed | Re-run device auth: `python ~/.hermes/scripts/youtube_oauth_device.py` |

## Post-Bug Cleanup Protocol

After fixing duplicate root cause, always:

1. **Scan the channel immediately** - within 24h of fix
2. **Delete duplicates** - before they gain more views/impressions
3. **Exclude contaminated data** - mark duplicate period as excluded in AB test logs
4. **Add a post-upload dedupe gate** - check channel for matching titles before every upload

## Related
- `video-pipeline-operations` - Buffer/YouTube upload pipeline that can produce duplicates
- `references/buffer-upload-dedupe-bug-2026-11-22.md` - Root cause example (in video-pipeline-operations skill)