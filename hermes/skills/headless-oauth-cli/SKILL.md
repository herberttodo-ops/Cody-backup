---
name: headless-oauth-cli
description: "OAuth browser-to-terminal auth for headless CLI tools."
version: 1.0.0
---

# Headless OAuth CLI Authentication

Authenticate browser-based OAuth flows (Claude Code, GitHub CLI, AWS SSO, etc.) on remote/headless machines without SSH port-forwarding or browser-on-VM setup. Use **tmux** as the glue between the waiting CLI tool and the user copying codes between their local browser and Telegram.

## When to Use

- Remote VM with no local browser (the common case)
- OAuth provider requires browser approval but the tool runs on a server
- Auth code has <60s TTL, making manual round-trip too slow

## Prerequisites

- `tmux` installed (`sudo apt-get install -y tmux`)
- CLI tool already installed (e.g., `claude`, `gh`, `aws`)
- User has browser on separate device that can reach OAuth provider

## Core Pattern

### 1. Start tmux Session Wide

```python
subprocess.run(['tmux', 'new-session', '-d', '-s', 'oauth-auth', '-x', '200', '-y', '20'])
```

Use `-x 200`+ to prevent URL wrapping — the #1 auth failure source.

### 2. Launch Auth Command

```python
subprocess.run(['tmux', 'send-keys', '-t', 'oauth-auth', 'claude auth login --console', 'Enter'])
```

Wait 5-8 seconds.

### 3. Extract URL from Pane

```python
import subprocess, re
result = subprocess.run(['tmux', 'capture-pane', '-t', 'oauth-auth', '-p', '-S', '-15'],
                        capture_output=True, text=True)
text = ''.join(result.stdout.split('\n'))
start = text.find('https://platform.claude.com/oauth/authorize')
end = text.find('Paste code here', start)
url = re.sub(r'\s+', '', text[start:end].strip())
```

Use `references/url-extract.py` for reusable extraction.

### 4. User Opens URL, Pastes Code Back

### 5. Feed Full Code to tmux — Do NOT Split on #

```python
# CORRECT — send ENTIRE string with #state suffix
code = "abc123#state_xyz"
subprocess.run(['tmux', 'send-keys', '-t', 'oauth-auth', code, 'Enter'])

# WRONG — splitting on # fails every time
code = code.split('#')[0]  # NEVER DO THIS
```

The `#` is part of the OAuth state parameter, not a fragment separator.

## Supported Tools

| Tool | Command | Code Format |
|------|---------|-------------|
| Claude Code | `claude auth login --console` | `authcode#state` |
| Claude Code (Max) | `claude setup-token` | `authcode#state` |
| GitHub CLI | `gh auth login` | Device code |

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "Invalid code" | Missing #state suffix or expired | Send full string; user must paste within 60s |
| URL wraps lines | Terminal too narrow | Use `-x 200`+ or `references/url-extract.py` |

## References

- `references/url-extract.py` — Reusable Python script to extract wrapped OAuth URLs from tmux pane output
