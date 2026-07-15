---
name: gog
description: Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs.
homepage: https://gogcli.sh
metadata:
  clawdbot:
    emoji: "🎮"
    requires:
      bins:
        - gog
    install:
      - id: brew
        kind: brew
        formula: steipete/tap/gogcli
        bins:
          - gog
        label: Install gog (brew)
---

# gog

Use `gog` for Gmail/Calendar/Drive/Contacts/Sheets/Docs. Requires OAuth setup.

## Setup (once)

1. Install gog CLI:
   ```bash
   brew install steipete/tap/gogcli
   ```

2. Set up OAuth credentials:
   ```bash
   gog auth credentials /path/to/client_secret.json
   ```

3. Add your account:
   ```bash
   gog auth add you@gmail.com --services gmail,calendar,drive,contacts,sheets,docs
   ```

4. Verify setup:
   ```bash
   gog auth list
   ```

## Common Commands

### Gmail
- Search: `gog gmail search 'newer_than:7d' --max 10`
- Send: `gog gmail send --to a@b.com --subject "Hi" --body "Hello"`

### Calendar
- List events: `gog calendar events <calendarId> --from <iso> --to <iso>`

### Drive
- Search: `gog drive search "query" --max 10`

### Contacts
- List: `gog contacts list --max 20`

### Sheets
- Get data: `gog sheets get <sheetId> "Tab!A1:D10" --json`
- Update: `gog sheets update <sheetId> "Tab!A1:B2" --values-json '[["A","B"],["1","2"]]' --input USER_ENTERED`
- Append: `gog sheets append <sheetId> "Tab!A:C" --values-json '[["x","y","z"]]' --insert INSERT_ROWS`
- Clear: `gog sheets clear <sheetId> "Tab!A2:Z"`
- Metadata: `gog sheets metadata <sheetId> --json`

### Docs
- Export: `gog docs export <docId> --format txt --out /tmp/doc.txt`
- View: `gog docs cat <docId>`

## Notes

- Set `GOG_ACCOUNT=you@gmail.com` to avoid repeating `--account`
- For scripting, prefer `--json` plus `--no-input`
- Sheets values can be passed via `--values-json` (recommended) or as inline rows
- Docs supports export/cat/copy. In-place edits require a Docs API client (not in gog)
- Confirm before sending mail or creating events

## Prerequisites

- Google Cloud OAuth client credentials (client_secret.json)
- Enabled APIs: Gmail, Calendar, Drive, Contacts, Sheets, Docs

## Installing This Skill

If `hermes skills install @steipete/gog` doesn't work, you can install manually:

```bash
mkdir -p ~/.hermes/skills/productivity/gog
# Download SKILL.md from ClawHub or create manually
curl -s https://clawhub.ai/steipete/skills/gog | grep -oP 'readme:\"[^\"]+' | head -1
```

Or create the files directly — the skill is just documentation (no scripts).

## Troubleshooting OAuth / Access Issues

### Check Current Auth Status

```bash
gog auth list
```

Shows authorized accounts and which services are enabled (e.g., `gmail,tasks` vs `gmail,calendar,drive,contacts,sheets,docs`).

### Adding Missing Services

If some services work (e.g., Drive) but others fail (e.g., Sheets), you need to add the missing scopes:

```bash
gog auth add you@gmail.com --services gmail,calendar,drive,contacts,sheets,docs
```

This will output an authorization URL. **You must complete this in a browser.**

**Important:** The `gog` CLI's OAuth flow expects to receive the callback directly on localhost. In headless environments (SSH, containers, some AI agents), this doesn't work automatically. You have two options:

#### Option A: Use a Local Machine (Easiest)

1. Run the auth command on a machine with a browser
2. Complete the OAuth flow
3. Copy the token file (`~/.config/gog/tokens/` or keyring) to your headless environment

#### Option B: Manual Code Exchange (Headless)

1. Run `gog auth add` to get the authorization URL
2. Open the URL in your browser, sign in, grant permissions
3. The redirect will fail (localhost not accessible) — copy the **full redirected URL**
4. Use the `google-workspace` skill's Python OAuth to complete the exchange:
   ```python
   # See google-workspace skill for the full script
   flow.fetch_token(code=auth_code_from_url)
   ```

**Note:** The `gog auth exchange` command does not exist. The CLI expects automatic callback handling.

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Google API error (404 notFound)` | Sheet/Doc ID doesn't exist or you lack access | Verify the ID and check sharing permissions |
| `No events` / `No contacts` | Service authorized but no data | Normal — add events/contacts or check account |
| `Error: unauthorized_client` | OAuth client not configured correctly | Check client_secret.json and ensure APIs are enabled in Google Cloud Console |
| `Scope has changed` | Token was created with different scopes | Run `gog auth add` with all needed services |

### Verify Service Access

Test each service individually:

```bash
# Drive (usually works first)
gog drive search "test" --max 1

# Gmail
gog gmail search 'newer_than:1d' --max 1

# Sheets (replace with actual sheet ID)
gog sheets get <sheetId> "Sheet1!A1:A1" --json

# Calendar
gog calendar events primary --from 2026-01-01T00:00:00Z --to 2026-01-02T00:00:00Z

# Contacts
gog contacts list --max 1

# Docs
gog docs cat <docId>
```
