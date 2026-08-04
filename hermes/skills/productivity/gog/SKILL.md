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
  - Note: `search` takes a simple name query. Do NOT try to add `mimeType=...` filters to it — combine search with `ls --query` or filter results client-side.
- Create folder: `gog drive mkdir "Folder Name" --parent <folderId> -j --results-only`
- Upload to folder: `gog drive upload <localPath> --parent <folderId> -j --results-only`
- Get file metadata: `gog drive get <fileId> -j --results-only`

### Contacts
- List: `gog contacts list --max 20`

### Sheets
- Get data: `gog sheets get <sheetId> "Tab!A1:D10" --json`
- Update single cell: `gog sheets update <sheetId> "E4" "value" -j --results-only`
  - If the sheet has only one tab (or the last-accessed tab), just pass the cell reference — gog auto-resolves the tab.
- Update range: `gog sheets update <sheetId> "Tab!A1:B2" --values-json '[["A","B"],["1","2"]]' --input USER_ENTERED`
- Append: `gog sheets append <sheetId> "Tab!A:C" --values-json '[["x","y","z"]]' --insert INSERT_ROWS`
- Clear: `gog sheets clear <sheetId> "Tab!A2:Z"`
- Metadata: `gog sheets metadata <sheetId> --json`
- Note: When reading, tab names with spaces appear single-quoted in responses (e.g., `'Content Calendar'!E4`). You don't need to include the quotes when writing.

#### Cleaning and Restructuring Messy Sheets

When a sheet has fragmented data, duplicates, or wrong structure, use this workflow:

**Step 1: Read and analyze the existing data**
```bash
# Get current state (may need multiple ranges)
gog sheets get <sheetId> "A1:E50" -j --results-only

# Check for empty cells, fragments, or data in wrong columns
```

**Step 2: Extract and clean data programmatically**
```python
import json

# Parse the messy data, extract valid rows, remove duplicates
# Ensure every row has exactly the expected number of columns
clean_rows = [
    ["2026-07-15", "Business post content...", "Personal copy...", "Comments...", "https://drive.google.com/..."],
    ["2026-07-16", "Another post...", "Personal...", "Engagement...", ""],
    # ... more rows
]

# CRITICAL: Validate all rows have same column count
expected_cols = 5
for i, row in enumerate(clean_rows):
    if len(row) != expected_cols:
        print(f"Row {i}: Expected {expected_cols} cols, got {len(row)}")
        # Trim or pad as needed
        clean_rows[i] = row[:expected_cols]  # trim excess

# Write to temp file to avoid shell escaping issues
with open('/tmp/clean_data.json', 'w') as f:
    json.dump(clean_rows, f)
```

**Step 3: Clear old data before writing**
```bash
# Clear the range where you'll write (prevents stale data)
gog sheets clear <sheetId> "A2:E50"
```

**Step 4: Bulk write with --values-json**
```bash
# Use --input=RAW to preserve formatting, newlines, etc.
gog sheets update <sheetId> "A2:E14" \
  --input="RAW" \
  --values-json="$(cat /tmp/clean_data.json)"
```

**Key pitfalls to avoid:**
- **Column count mismatch**: If any row has a different number of columns, the entire update fails with "tried writing to column [F]"
- **JSON escaping**: Large text blocks with quotes/newlines can break shell interpolation — write to file first
- **Tab names with spaces**: Don't quote them in the range (use `A2:E14` not `'Sheet 1'!A2:E14`)
- **Date/number formatting**: Use `--input=RAW` to prevent Google from auto-formatting dates/numbers

**Complete example workflow:**
```bash
# 1. Read existing
original=$(gog sheets get SHEET_ID "A1:E30" -j --results-only)

# 2. Process with Python to extract clean rows, save to /tmp/clean.json
# 3. Clear target range
gog sheets clear SHEET_ID "A2:E30"

# 4. Write clean data
gog sheets update SHEET_ID "A2:E15" --input="RAW" --values-json="$(cat /tmp/clean.json)"

# 5. Verify
gog sheets get SHEET_ID "A1:E15" -j --results-only
```

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
