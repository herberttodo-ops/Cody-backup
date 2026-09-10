# Token Quote Extraction Pitfall

## Problem

When `GITHUB_BACKUP_TOKEN` is stored in `~/.hermes/.env` with surrounding quotes:
```bash
GITHUB_BACKUP_TOKEN="github_pat_11CA...c6"
```

The naive extraction includes quotes in the value:
```bash
export GITHUB_BACKUP_TOKEN=$(grep GITHUB_BACKUP_TOKEN ~/.hermes/.env | cut -d= -f2)
# Results in: GITHUB_BACKUP_TOKEN="github_pat_11CA...c6" (with quotes!)
```

This causes git to URL-encode the quotes into the remote URL:
```
fatal: could not read Password for 'https://%22git...6%22@github.com': No such device or address
```

Note `%22` is the URL-encoded double quote.

## Solution

Strip quotes when extracting:
```bash
export GITHUB_BACKUP_TOKEN="$(grep GITHUB_BACKUP_TOKEN ~/.hermes/.env | cut -d= -f2- | tr -d '"')"
```

## Prevention

All scripts and documentation extracting tokens from `.env` should use `tr -d '"'` to handle both quoted and unquoted values safely.
