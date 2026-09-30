# Composio YouTube Upload Pattern (Tales Untold)

Date: 2026-09-29
Created from session fixing Tales Untold pipeline Buffer -> Composio migration.

## Multi-Account YouTube Setup

When a user has multiple YouTube channels connected (e.g., Tales Untold + LotSignal):

### List connected accounts
```bash
composio connections list
```

### Target the correct account with --account
```bash
composio execute YOUTUBE_MULTIPART_UPLOAD_VIDEO \
  -d '{"title": "...", "description": "...", "categoryId": "24", "privacyStatus": "public"}' \
  --file /path/to/video.mp4 \
  --account youtube_trader-relink
```

Account aliases from connections list:
- `youtube_trader-relink` = Tales UnTold
- `youtube_chub-unshot` = LotSignal

## YOUTUBE_MULTIPART_UPLOAD_VIDEO Tool

### Schema (required fields)
- `title` — video title (max 100 chars)
- `description` — video description
- `categoryId` — numeric category (24 = Entertainment)
- `privacyStatus` — `public`, `private`, `unlisted`
- `videoFile` — FileUploadable with `name`, `mimetype`, `s3key`

### Upload via --file flag (CLI)
The CLI's `--file` flag injects a local file path into the single `file_uploadable` input, bypassing the need for an S3 staging step.

```bash
composio execute YOUTUBE_MULTIPART_UPLOAD_VIDEO \
  -d '{"title": "...", "categoryId": "24", "privacyStatus": "public", "tags": ["horror", "shorts"]}' \
  --file /path/to/FINAL_video.mp4 \
  --account youtube_trader-relink
```

### Return value
Response contains `data.videoId` on success:
```json
{"videoId": "dQw4w9WgXcQ"}
```

### Dry-run before real upload
Always add `--dry-run` first to validate:
```bash
composio execute YOUTUBE_MULTIPART_UPLOAD_VIDEO ... --dry-run
```

## LinkedIn Company Page Scope Issue

**Problem:** `LINKEDIN_CREATE_LINKED_IN_POST` with `author: urn:li:organization:<id>` fails with:
> "Organization Or Events permissions must be used when using organization as author"

**Root cause:** Composio's managed LinkedIn OAuth grants `w_member_social` (personal posting) but not `w_organization_social` (company page posting).

**Fix path:**
1. Disconnect LinkedIn in Composio dashboard
2. Reconnect and specifically approve "Post on behalf of an organization" / `w_organization_social`
3. This requires custom LinkedIn Developer App approval (takes days)

**Workaround for immediate posting:** Use Buffer MCP (`mcp__buffer__buffer_add_update`) for company page posts until Composio scope is fixed.

## Other Platform Quirks

### Facebook Pages
Tool: `FACEBOOK_LIST_MANAGED_PAGES` — returns pages the authenticated user manages. Verify LotSignal page is in this list.

### Instagram
Tool: `INSTAGRAM_GET_USER_INFO` — requires valid auth. Token errors (code 190) mean re-auth needed at instagram.com.

### Instagram Business Account
Requires an attached Facebook Page. Tool: `INSTAGRAM_POST_IG_USER_MEDIA` (create media container) + `INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH` (publish it).
