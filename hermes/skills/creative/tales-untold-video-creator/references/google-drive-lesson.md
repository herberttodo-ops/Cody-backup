# Google Drive Upload Setup

## Token Location
- **File:** `~/.hermes/google_token.json`
- **NOT** in project directories (common mistake from Sept 15 2026 session)

## Token Validity Checks
1. File must exist at `~/.hermes/google_token.json`
2. Must contain `"refresh_token"` field (not just access_token)
3. Scopes should include `https://www.googleapis.com/auth/drive`
4. If token is missing or lacks refresh_token, re-authentication is required

## Upload Script Pattern
```python
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

token = json.loads(Path.home().joinpath(".hermes/google_token.json").read_text())
creds = Credentials.from_authorized_user_info(token)
service = build("drive", "v3", credentials=creds, cache_discovery=False)

media = MediaFileUpload(str(file_path), resumable=True)
file_metadata = {
    "name": file_path.name,
    "mimeType": "video/mp4",
    "parents": [folder_id]
}
file = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()
```

## Folder ID Discovery (Don't Hardcode)
Folder IDs from memory often rot. Query dynamically:
```python
results = service.files().list(
    q="mimeType='application/vnd.google-apps.folder' and trashed=false",
    fields="files(id, name)",
    pageSize=50
).execute()
# Filter for folder name containing "Tales Untold" or similar
```

## Common Errors
| Error | Meaning | Fix |
|-------|---------|-----|
| `HttpError 403` + `"parentNotAFolder"` | FOLDER_ID is wrong or not a folder | Query for correct folder ID dynamically |
| `FileNotFoundError` for token | Looking in wrong directory | Use `~/.hermes/google_token.json` |
| `invalid_grant` | Refresh token expired | Re-authenticate via Google OAuth |

## Session Reference
- Sept 15 2026: Upload succeeded when token path corrected from `~/.openclaw/...` to `~/.hermes/google_token.json`
- Sept 15 2026: Folder ID `1GKg3uuAmsFu6sRMEG9P0AR6TAhxf0u41` (broken) → `1wEI-wZ9rY-z0ciZsTWglVjLJTR_HoOcx` (working). Hardcoded IDs rot — always query.
