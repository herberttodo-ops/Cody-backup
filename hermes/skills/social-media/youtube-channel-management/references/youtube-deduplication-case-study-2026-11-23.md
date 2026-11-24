# YouTube Deduplication Case Study - Tales Untold - 2026-11-23

## Context
Pipeline bug caused every video to be uploaded TWICE (Buffer + direct YouTube fallback) from Nov 15-22. Need to detect duplicates, score them, delete the worse performers, verify cleanup.

## Key Learning: The Credential Field Name
The `youtube_credentials.json` file uses field `"token"`, NOT `"access_token"`.

```python
# WRONG
token=creds_data['access_token']  # KeyError!

# CORRECT
token=creds_data['token']         # Works
```

This is a common trip hazard when building Credentials objects from JSON files.

## Complete Detection + Deletion Script

### Phase 1: Full Channel Scan (paginated)
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json, os

# Load credentials — note field name is 'token' not 'access_token'
creds_path = os.path.expanduser('~/.config/youtube_credentials.json')
with open(creds_path) as f:
    d = json.load(f)

creds = Credentials(
    token=d['token'],  # <-- Correct field name
    refresh_token=d.get('refresh_token'),
    token_uri=d.get('token_uri', 'https://oauth2.googleapis.com/token'),
    client_id=d.get('client_id', os.environ.get('YOUTUBE_CLIENT_ID', '')),
    client_secret=d.get('client_secret', os.environ.get('YOUTUBE_CLIENT_SECRET', '')),
    scopes=d.get('scopes', ['https://www.googleapis.com/auth/youtube'])
)

youtube = build('youtube', 'v3', credentials=creds)

# Get upload playlist ID
channels = youtube.channels().list(part='contentDetails', mine=True).execute()
uploads_id = channels['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# Fetch ALL uploads (paginated - essential for channels with >50 videos)
videos = []
page_token = None
while True:
    params = {
        'part': 'snippet',
        'playlistId': uploads_id,
        'maxResults': 50,
    }
    if page_token:
        params['pageToken'] = page_token
    pl = youtube.playlistItems().list(**params).execute()
    videos.extend(pl['items'])
    page_token = pl.get('nextPageToken')
    if not page_token:
        break
```

### Phase 2: Detect Duplicates by Title
```python
title_map = {}
for v in videos:
    title = v['snippet']['title']
    vid_id = v['snippet']['resourceId']['videoId']
    title_map.setdefault(title, []).append(vid_id)

duplicates = {k: v for k, v in title_map.items() if len(v) > 1}
print(f"Total videos: {len(videos)}, Duplicate titles: {len(duplicates)}")
```

**Edge case check:** Legitimate reuploads also share titles. Verify by checking upload timestamps: bug duplicates are within minutes-seconds of each other, while intentional reuploads are days/weeks apart.

### Phase 3: Fetch Statistics (50-ID batch limit)
```python
all_ids = [vid for group in duplicates.values() for vid in group]
stats = {}
for i in range(0, len(all_ids), 50):  # Must batch by 50s
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

### Phase 4: Score and Select for Deletion
```python
def score_video(v):
    # Composite score: views are discovery, likes/comments are engagement
    return v['views'] + v['likes'] * 10 + v['comments'] * 20

removal_plan = []
for title, ids in duplicates.items():
    entries = [dict(stats[vid], id=vid) for vid in ids]
    entries.sort(key=score_video, reverse=True)  # Best first
    
    best = entries[0]
    for w in entries[1:]:
        removal_plan.append({
            'title': title,
            'worse_id': w['id'],
            'worse_views': w['views'],
            'better_id': best['id'],
            'better_views': best['views'],
        })
```

### Phase 5: Delete and Verify
```python
for item in removal_plan:
    try:
        youtube.videos().delete(id=item['worse_id']).execute()
        print(f"✓ Deleted {item['title']} duplicate ({item['worse_id']})")
    except Exception as e:
        print(f"✗ Failed {item['worse_id']}: {e}")  # 404 = already gone
```

After deletion, **always re-scan** to confirm zero duplicates remain.

## Results from This Session

| Metric | Value |
|---|---|
| Channel videos before cleanup | 252 |
| Duplicate titles found | 14 |
| Duplicate videos removed | 15 |
| Channel videos after cleanup | 237 |
| Videos kept (best performer) | 14 |

**Pattern observed:** Duplicates published within seconds-to-minutes of each other. The 15 duplicate IDs removed ranged from 6 to 108 views each. The kept videos ranged from 22 to 265 views.

## Pitfall Notes

1. **Never assume `"access_token"` field name** — always inspect the actual JSON first with `cat ~/.config/youtube_credentials.json | python3 -m json.tool | head -20`
2. **Always paginate** — playlistItems.list returns max 50 per page; large channels need the while loop
3. **Save removal plan before executing** — write a JSON backup so you can audit later
4. **Re-verify after deletion** — run the detection loop again to confirm zeros

## Data Contamination Warning
All performance data from Nov 15-22 is contaminated because YouTube split impressions and engagement between duplicate pairs. When analyzing 4-arm test results, exclude this period entirely. Channel analytics for that window are unreliable.
