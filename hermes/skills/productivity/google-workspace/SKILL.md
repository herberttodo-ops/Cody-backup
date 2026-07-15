---
name: google-workspace
description: Gmail, Calendar, Drive, Contacts, Sheets, and Docs integration via Python. Uses OAuth2 with automatic token refresh. No external binaries needed — runs entirely with Google's Python client libraries in the Hermes venv.
version: 1.0.0
author: Nous Research
license: MIT
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials (downloaded from Google Cloud Console)
metadata:
  hermes:
    tags: [Google, Gmail, Calendar, Drive, Sheets, Docs, Contacts, Email, OAuth]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [himalaya]
---

# Google Workspace

Gmail, Calendar, Drive, Contacts, Sheets, and Docs — all through Python scripts in this skill. No external binaries to install.

## References

- `references/gmail-search-syntax.md` — Gmail search operators (is:unread, from:, newer_than:, etc.)

## Scripts

- `scripts/setup.py` — OAuth2 setup (run once to authorize)
- `scripts/google_api.py` — API wrapper CLI (agent uses this for all operations)

## First-Time Setup

**Quick start with pre-configured environment:**

```bash
# Set up shorthand commands
export GAPI="/home/herby/.hermes/skills/productivity/google-workspace/scripts/gw"
export GSETUP="/home/herby/.hermes/skills/productivity/google-workspace/scripts/gw-setup"

# Check auth status
$GSETUP --check
```

The setup is fully non-interactive — you drive it step by step so it works
on CLI, Telegram, Discord, or any platform.

**Note:** The skill now uses `/home/herby/.hermes/google_venv` (pre-installed with Google API dependencies) instead of the Hermes venv. Use the `gw` and `gw-setup` wrapper scripts which handle the Python path automatically.

### Step 0: Check if already set up

```bash
$GSETUP --check
```

If it prints `AUTHENTICATED`, skip to Usage — setup is already done.

### Step 1: Triage — ask the user what they need

Before starting OAuth setup, ask the user TWO questions:

**Question 1: "What Google services do you need? Just email, or also
Calendar/Drive/Sheets/Docs?"**

- **Email only** → They don't need this skill at all. Use the `himalaya` skill
  instead — it works with a Gmail App Password (Settings → Security → App
  Passwords) and takes 2 minutes to set up. No Google Cloud project needed.
  Load the himalaya skill and follow its setup instructions.

- **Calendar, Drive, Sheets, Docs (or email + these)** → Continue with this
  skill's OAuth setup below.

**Question 2: "Does your Google account use Advanced Protection (hardware
security keys required to sign in)? If you're not sure, you probably don't
— it's something you would have explicitly enrolled in."**

- **No / Not sure** → Normal setup. Continue below.
- **Yes** → Their Workspace admin must add the OAuth client ID to the org's
  allowed apps list before Step 4 will work. Let them know upfront.

### Step 2: Create OAuth credentials (one-time, ~5 minutes)

Tell the user:

> You need a Google Cloud OAuth client. This is a one-time setup:
>
> 1. Go to https://console.cloud.google.com/apis/credentials
> 2. Create a project (or use an existing one)
> 3. Click "Enable APIs" and enable: Gmail API, Google Calendar API,
>    Google Drive API, Google Sheets API, Google Docs API, People API
> 4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
> 5. Application type: "Desktop app" → Create
> 6. Click "Download JSON" and tell me the file path

Once they provide the path:

```bash
$GSETUP --client-secret /path/to/client_secret.json
```

### Step 3: Get authorization URL

```bash
$GSETUP --auth-url
```

This prints a URL. **Send the URL to the user** and tell them:

> Open this link in your browser, sign in with your Google account, and
> authorize access. After authorizing, you'll be redirected to a page that
> may show an error — that's expected. Copy the ENTIRE URL from your
> browser's address bar and paste it back to me.

### Step 4: Exchange the code

The user will paste back either a URL like `http://localhost:1/?code=4/0A...&scope=...`
or just the code string. Either works. The `--auth-url` step stores a temporary
pending OAuth session locally so `--auth-code` can complete the PKCE exchange
later, even on headless systems:

```bash
$GSETUP --auth-code "THE_URL_OR_CODE_THE_USER_PASTED"
```

### Step 5: Verify

```bash
$GSETUP --check
```

Should print `AUTHENTICATED`. Setup is complete — token refreshes automatically from now on.

### Notes

- Token is stored at `google_token.json` under the active profile's `HERMES_HOME` and auto-refreshes.
- Pending OAuth session state/verifier are stored temporarily at `google_oauth_pending.json` under the active profile's `HERMES_HOME` until exchange completes.
- Hermes now refuses to overwrite a full Google Workspace token with a narrower re-auth token missing Gmail scopes, so one profile's partial consent cannot silently break email actions later.
- To revoke: `$GSETUP --revoke`

## Usage

All commands go through the `gw` wrapper script. Set `GAPI` as a shorthand:

```bash
GAPI="/home/herby/.hermes/skills/productivity/google-workspace/scripts/gw"
```

### Gmail

```bash
# Search (returns JSON array with id, from, subject, date, snippet)
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:boss@company.com newer_than:1d"
$GAPI gmail search "has:attachment filename:pdf newer_than:7d"

# Read full message (returns JSON with body text)
$GAPI gmail get MESSAGE_ID

# Send
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"
$GAPI gmail send --to user@example.com --subject "Report" --body "<h1>Q4</h1><p>Details...</p>" --html

# Reply (automatically threads and sets In-Reply-To)
$GAPI gmail reply MESSAGE_ID --body "Thanks, that works for me."

# Labels
$GAPI gmail labels
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
$GAPI gmail modify MESSAGE_ID --remove-labels UNREAD
```

### Calendar

```bash
# List events (defaults to next 7 days)
$GAPI calendar list
$GAPI calendar list --start 2026-03-01T00:00:00Z --end 2026-03-07T23:59:59Z

# Create event (ISO 8601 with timezone required)
$GAPI calendar create --summary "Team Standup" --start 2026-03-01T10:00:00-06:00 --end 2026-03-01T10:30:00-06:00
$GAPI calendar create --summary "Lunch" --start 2026-03-01T12:00:00Z --end 2026-03-01T13:00:00Z --location "Cafe"
$GAPI calendar create --summary "Review" --start 2026-03-01T14:00:00Z --end 2026-03-01T15:00:00Z --attendees "alice@co.com,bob@co.com"

# Delete event
$GAPI calendar delete EVENT_ID
```

### Drive

```bash
$GAPI drive search "quarterly report" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5
```

### Contacts

```bash
$GAPI contacts list --max 20
```

### Sheets

```bash
# Read
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"

# Write
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[["Name","Score"],["Alice","95"]]'

# Append rows
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[["new","row","data"]]'
```

### Docs

```bash
$GAPI docs get DOC_ID
```

## Output Format

All commands return JSON. Parse with `jq` or read directly. Key fields:

- **Gmail search**: `[{id, threadId, from, to, subject, date, snippet, labels}]`
- **Gmail get**: `{id, threadId, from, to, subject, date, labels, body}`
- **Gmail send/reply**: `{status: "sent", id, threadId}`
- **Calendar list**: `[{id, summary, start, end, location, description, htmlLink}]`
- **Calendar create**: `{status: "created", id, summary, htmlLink}`
- **Drive search**: `[{id, name, mimeType, modifiedTime, webViewLink}]`
- **Contacts list**: `[{name, emails: [...], phones: [...]}]`
- **Sheets get**: `[[cell, cell, ...], ...]`

## Rules

1. **Never send email or create/delete events without confirming with the user first.** Show the draft content and ask for approval.
2. **Check auth before first use** — run `setup.py --check`. If it fails, guide the user through setup.
3. **Use the Gmail search syntax reference** for complex queries — load it with `skill_view("google-workspace", file_path="references/gmail-search-syntax.md")`.
4. **Calendar times must include timezone** — always use ISO 8601 with offset (e.g., `2026-03-01T10:00:00-06:00`) or UTC (`Z`).
5. **Respect rate limits** — avoid rapid-fire sequential API calls. Batch reads when possible.

## Current Status

This profile (`/home/herby/.hermes`) has an active Google Workspace token with access to:
- ✓ Gmail (modify, send, read)
- ✓ Google Drive
- ✓ Google Calendar
- ✓ Google Sheets
- ✓ Google Docs
- ✓ Google Contacts

Token location: `/home/herby/.hermes/google_token.json`

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `NOT_AUTHENTICATED` | Run setup Steps 2-5 above |
| `REFRESH_FAILED` | Token revoked or expired — redo Steps 3-5 |
| `HttpError 403: Insufficient Permission` | Missing API scope — `$GSETUP --revoke` then redo Steps 3-5 |
| `HttpError 403: Access Not Configured` | API not enabled — user needs to enable it in Google Cloud Console |
| `ModuleNotFoundError` | Dependencies should be in `/home/herby/.hermes/google_venv`. Run: `uv pip install --python /home/herby/.hermes/google_venv/bin/python google-api-python-client google-auth-oauthlib google-auth-httplib2` |
| `No module named pip` (in Hermes venv) | Use the `gw` wrapper script instead — it uses `google_venv` |
| `ModuleNotFoundError: No module named 'hermes_constants'` | The wrapper scripts set PYTHONPATH automatically |
| Advanced Protection blocks auth | Workspace admin must allowlist the OAuth client ID |
| PKCE errors (`invalid_grant`, `Missing code verifier`) | The auth code expired (valid ~10 min) or PKCE verifier mismatch. Use the non-PKCE flow in Fallback Setup instead of `google_auth_oauthlib` flows. |

## Fallback Setup (When setup.py Fails)

If the standard `setup.py` fails because the Hermes venv lacks pip, the system Python is locked down (PEP 668), or `hermes_constants` is missing from the path, use this manual approach.

**Important:** PKCE-based flows (default in `google_auth_oauthlib`) often fail in headless environments because the code verifier generated with the auth URL must persist for the exchange. Use the direct HTTP method below instead.

### Step A: Check for Existing Venv

First check if a Google venv already exists from a previous attempt:

```bash
ls -la ~/.hermes/google_venv/bin/python
```

If it exists, skip to Step C. If not, create one:

```bash
# Option 1: Using uv (preferred)
uv venv ~/.hermes/google_venv
uv pip install --python ~/.hermes/google_venv/bin/python \
  google-api-python-client google-auth-oauthlib google-auth-httplib2 requests

# Option 2: Using system pip
/usr/bin/python3 -m venv ~/.hermes/google_venv
~/.hermes/google_venv/bin/pip install \
  google-api-python-client google-auth-oauthlib google-auth-httplib2 requests
```

### Step B: Save the Client Secret

Save the user's `client_secret.json` to `~/.hermes/google_client_secret.json`.

### Step C: Generate Auth URL (Non-PKCE)

Use `execute_code` to generate an auth URL without PKCE (avoids verifier persistence issues):

```python
import json
import urllib.parse

# Load client config
with open('/home/herby/.hermes/google_client_secret.json') as f:
    config = json.load(f)['installed']

# Build auth URL without PKCE
params = {
    'client_id': config['client_id'],
    'redirect_uri': 'http://localhost',
    'scope': ' '.join([
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/contacts',
    ]),
    'response_type': 'code',
    'access_type': 'offline',
    'prompt': 'consent',
    'include_granted_scopes': 'true'
}

auth_url = f"{config['auth_uri']}?{urllib.parse.urlencode(params)}"
print(auth_url)
```

Send this URL to the user and tell them:
> Open this link in your browser, sign in with your Google account, and authorize access. After authorizing, you'll be redirected to a page showing a localhost error — that's expected. **Copy the ENTIRE URL from your browser's address bar immediately** (codes expire in ~10 minutes) and paste it back to me.

### Step D: Exchange Code for Token

When the user pastes the redirected URL, extract and exchange the code:

```python
import json
import urllib.parse
import requests

# Load configs
with open('/home/herby/.hermes/google_client_secret.json') as f:
    config = json.load(f)['installed']

# Parse the redirected URL from user
redirected_url = "PASTE_USER_URL_HERE"
parsed = urllib.parse.urlparse(redirected_url)
query = urllib.parse.parse_qs(parsed.query)
auth_code = query.get('code', [None])[0]

# Exchange code for token
token_data = {
    'code': auth_code,
    'client_id': config['client_id'],
    'client_secret': config['client_secret'],
    'redirect_uri': 'http://localhost',
    'grant_type': 'authorization_code'
}

resp = requests.post(config['token_uri'], data=token_data)

if resp.status_code == 200:
    data = resp.json()
    
    # Save token in the format expected by google-workspace skill
    token = {
        'token': data['access_token'],
        'refresh_token': data.get('refresh_token'),
        'token_uri': config['token_uri'],
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'scopes': data.get('scope', '').split(),
        'expiry': None
    }
    
    with open('/home/herby/.hermes/google_token.json', 'w') as f:
        json.dump(token, f, indent=2)
    
    print("SUCCESS: Token saved to google_token.json")
    print(f"Scopes granted: {len(token['scopes'])}")
else:
    print(f"Error: {resp.json()}")
```

### Step E: Verify

```bash
python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check
```

Should print `AUTHENTICATED`.

## Revoking Access

```bash
$GSETUP --revoke
```
