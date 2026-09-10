# Gog Skill Card

**Google Workspace CLI Integration**

## Capabilities
- Gmail search and send
- Calendar event listing
- Drive file search
- Contacts management
- Sheets read/write/append/clear
- Docs export and view

## Requirements
- `gog` CLI installed via Homebrew
- Google OAuth client credentials
- Enabled Google APIs

## Setup Commands
```bash
brew install steipete/tap/gogcli
gog auth credentials /path/to/client_secret.json
gog auth add you@gmail.com --services gmail,calendar,drive,contacts,sheets,docs
```

## Quick Start
```bash
# List Gmail messages
nog gmail search 'newer_than:7d' --max 10

# Search Drive
gog drive search "project" --max 10

# Get Sheet data
gog sheets get <sheetId> "Sheet1!A1:D10" --json
```

## Environment Variables
- `GOG_ACCOUNT` - Default account email

## Tags
#gmail #calendar #drive #contacts #sheets #docs #google-workspace
