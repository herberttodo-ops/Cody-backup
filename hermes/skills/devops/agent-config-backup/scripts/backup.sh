#!/usr/bin/env bash
# Agent Configuration Backup Script
# Usage: ./agent-config-backup.sh [BACKUP_REPO_URL]

set -euo pipefail

BACKUP_REPO="${1:-}"
BACKUP_DIR="${HOME}/.hermes/backup-staging"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
LOG_FILE="${HOME}/.hermes/logs/backup-${DATE}.log"

mkdir -p "${HOME}/.hermes/logs"
mkdir -p "${BACKUP_DIR}"

sanitize_content() {
    sed -E \
        -e 's/(ghp|github_pat)_[a-zA-Z0-9_]{30,}/___GITHUB_TOKEN___/gi' \
        -e 's/sk-[a-zA-Z0-9]{20,}/___OPENAI_KEY___/g' \
        -e 's/sk-proj-[a-zA-Z0-9_-]{20,}/___OPENAI_PROJ___/g' \
        -e 's/org-[a-zA-Z0-9]{20,}/___ORG_ID___/g' \
        -e 's/pk-[a-zA-Z0-9]{20,}/___API_KEY___/g' \
        -e 's/bearer[[:space:]]+[a-zA-Z0-9_-]{20,}/bearer ___TOKEN___/gi' \
        -e 's/"(access_token|refresh_token|token|botToken|api_key)":[[:space:]]*"[^"]+"/"\1": "___TOKEN___"/g' \
        -e 's/[a-zA-Z0-9_-]{40,}/___LONG_STRING___/g' \
        -e 's/[0-9]{10,}/___ID___/g'
}

safe_copy() {
    local src="$1" dst="$2"
    if [[ -f "$src" ]]; then
        mkdir -p "$(dirname "$dst")"
        cat "$src" | sanitize_content > "$dst" 2>/dev/null || cp "$src" "$dst"
    fi
}

rm -rf "${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"

# Clone repo
if [[ -n "${GITHUB_BACKUP_TOKEN:-}" ]]; then
    AUTH_REPO=$(echo "$BACKUP_REPO" | sed "s|https://|https://${GITHUB_BACKUP_TOKEN}@|")
else
    AUTH_REPO="$BACKUP_REPO"
fi

git clone "$AUTH_REPO" "$BACKUP_DIR" 2>&1
cd "$BACKUP_DIR"

# Backup files
safe_copy "${HOME}/.hermes/SOUL.md" "hermes/SOUL.md"
safe_copy "${HOME}/.hermes/memories/MEMORY.md" "hermes/memories/MEMORY.md"
safe_copy "${HOME}/.hermes/config.yaml" "hermes/config.yaml"

# Environment template
if [[ -f "${HOME}/.hermes/.env" ]]; then
    sed -e 's/=.*/=___REDACTED___/g' "${HOME}/.hermes/.env" > "hermes/.env.template"
fi

# Skills (sanitized)
mkdir -p "hermes/skills"
find "${HOME}/.hermes/skills" -type f 2>/dev/null | while read -r f; do
    rel="${f#${HOME}/.hermes/skills/}"
    safe_copy "$f" "hermes/skills/$rel"
done

# Commit and push
git add -A
git commit -m "Backup: ${DATE} ${TIME}" || exit 0
git push "$AUTH_REPO" HEAD:main --no-verify 2>&1 || \
    git push "$AUTH_REPO" HEAD:master --no-verify 2>&1

echo "Backup completed successfully"
