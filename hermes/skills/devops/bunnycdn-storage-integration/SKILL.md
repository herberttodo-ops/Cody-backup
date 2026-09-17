---
name: bunnycdn-storage-integration
description: "Upload files to BunnyCDN storage zones and public CDN."
triggers: ["bunnycdn", "cdn upload", "storage zone", "pull zone", "video hosting"]
---

## Overview

BunnyCDN requires TWO components for public file access:
1. **Storage Zone** - Private upload endpoint (uses Storage Password)
2. **Pull Zone** - Public CDN endpoint (requires correct Origin URL)

## Key Distinction: API Keys

| Key Type | Purpose | Location | Header |
|----------|---------|----------|--------|
| Account API Key | Manage zones/users | Dashboard → Account | `AccessKey` or `Authorization: Bearer` |
| Storage Password | Upload files | Storage → Zone → FTP & API | `AccessKey` |

**Critical lesson**: Storage upload requires Storage Password, NOT Account API Key.

## Upload Workflow

```bash
# 1. Upload to storage (private)
curl -T "file.mp4" \
  "https://storage.bunnycdn.com/{ZONE}/path/file.mp4" \
  -H "AccessKey: {STORAGE_PASSWORD}"

# 2. Access via pull zone (public)
https://{PULL_ZONE}.b-cdn.net/path/file.mp4
```

## Pull Zone Configuration

**Origin URL must be**: `https://storage.bunnycdn.com/{ZONE}/`

Common mistake: Including zone name again creates 401 errors.

## Environment Variables

```bash
BUNNY_STORAGE_API_KEY=<storage-password>
BUNNY_STORAGE_ZONE=<zone-name>
BUNNY_PULL_ZONE=<public-zone-name>
```

## Python Upload Helper

```python
import subprocess

def upload_to_bunny(file_path, zone, api_key, remote_path):
    cmd = [
        "curl", "-T", file_path,
        f"https://storage.bunnycdn.com/{zone}/{remote_path}",
        "-H", f"AccessKey: {api_key}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
```
