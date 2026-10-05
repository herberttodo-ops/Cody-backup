# Tales Untold Pipeline Session: October 5, 2026
**Session context:** 3-video production run, Buffer publish attempt, folklore database expansion, ComposIO diagnostic.

## 1. 200+ Entity Folklore Database
Created `data/folklore_cryptid_database.json` (205 unique entities) to replace the 14-entity hardcoded list in `tales_v3_producer.sh`.

**Structure:**
- `name`: Entity display name
- `region`: Cultural origin
- `category`: classification (cryptid, ghost, demon, shapeshifter, etc.)
- `tier`: 1 = proven performer

**Python module:** `folklore_db.py` provides:
- `load()` — returns all 205 entities
- `get(name)` — lookup by name
- `scenes(entity_name)` — auto-generates 4 Gammell-style scene prompts
- `pick_random(tier=1)` — random Tier 1 entity
- `remaining_producible()` — entities not yet in queue/queue_done
- `get_random_unproduced()` — random entity never produced

**Producer script updated:** `tales_v3_producer.sh` now:
1. Calls `folklore_db.get_random_unproduced()`
2. Auto-generates title: "The ENTITY_NAME: Region's Category"
3. Auto-generates 100-120 word story from template using name/region/category
4. Falls back to `pick_random()` if all 205 have been used

## 2. Buffer MCP Tool Discovery — Definitive List
Verified available tools via `tools/list`:

| Tool | Status |
|------|--------|
| `create_post` | WORKS |
| `list_posts` | WORKS |
| `delete_post` | WORKS |
| `publishPostNow` | NOT EXPOSED (-32602) |
| `publish_post_now` | NOT EXPOSED (-32602) |
| `update_post` | NOT EXPOSED (-32602) |
| `update_post_schedule` | NOT EXPOSED (-32602) |

**Implication:** Buffer posts CANNOT be published immediately via MCP. Only `create_post` with explicit `dueAt` or `create_post` with `schedulingType: "automatic"` (which auto-queues to next slot). For immediate publish, use Buffer web dashboard manual "Publish Now" button.

## 3. YouTube OAuth Direct Upload — Blocked
`~/.config/youtube_credentials.json` token expired Sept 18 → Oct 5. Refresh grant returned:
```
invalid_grant: Token has been expired or revoked.
```

Resolution: Buffer publishing is the working path. Direct YouTube upload via `youtube_upload.py` requires running `youtube_oauth_setup.py` to regenerate credentials (needs browser/device flow).

## 4. ComposIO YouTube Upload — Quota Blocked
ComposIO has `YOUTUBE_UPLOAD_VIDEO` and `YOUTUBE_MULTIPART_UPLOAD_VIDEO` tools but:
- YouTube Data API quota is **exhausted** (midnight PT reset)
- Every ComposIO YouTube call returns `quotaExceeded` 403
- Quota resets at **midnight Pacific Time** (3 AM ET)
- `YOUTUBE_UPLOAD_VIDEO` costs ~500 units vs ~1600 for multipart

**ComposIO connection status:**
- Alias "Tales UnTold" → ACTIVE (word_id: youtube_trader-relink)
- 2 other connections (1 EXPIRED, 1 ACTIVE for LotSignal)

## 5. Word Count Precision Refinement
Refined mapping after producing 3 videos:

| Words | Duration | Verdict |
|-------|----------|---------|
| 112 | 49s | Optimal |
| 111 | 50.60s | Optimal |
| 109 | 47-48s | Optimal |
| 120 | 52s | Upper limit (ok) |
| 129 | 64s | Too long |

**Updated target:** 100-115 words (not 100-120). 120 runs close to the 55s ceiling.

## 6. Pipeline Phase Timing (Oct 5 run)
| Phase | Duration |
|-------|----------|
| TTS (Cedric) | 30-40s |
| Whisper | 5-10s |
| Images (4× POYO) | 20-30s |
| HTML composition | <1s |
| HyperFrames render | 3-5 min |
| FFmpeg mix | 5-10s |
| Faststart re-encode | 30-60s |
| Drive upload | 10-30s |
| Buffer schedule | 2-5s |
| **Total end-to-end** | **~6-8 min per video** |

Parallel runs (2 videos simultaneously) took ~8-9 min each due to HyperFrames CPU contention.

## 7. Buffer Delete Works
Successfully deleted non-compliant "The Last Photograph" post using:
```python
buffer_call("delete_post", {"postId": "6ac2a533d467abe8cfc410d8"})
```
Queue went from 3→2 posts. Re-created with `create_post` + `schedulingType: "automatic"` which auto-assigned next available slots (~7:31 PM, 8:18 PM, 9:34 PM ET on Oct 5).

## 8. Gammell Scene Prompts — Auto-Generated
The `scenes()` function in `folklore_db.py` generates 4 prompts per entity:
1. "ominous ENTITY in REGION setting, establishing dread"
2. "terrifying ENTITY CATEGORY form close-up, disturbing"
3. "ENTITY emerging from darkness or shadows, reveal"
4. "aftermath of ENTITY presence, lingering horror"

All prefixed with: "Stephen Gammell ink wash illustration, deep black shadows, monochrome grayscale, high contrast"

This replaces the hand-written 14-entity STORY_SCENES dict in `pipeline_v3.py`.
