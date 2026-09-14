# Buffer Image URL Requirements

## Critical Rule

Buffer **requires** publicly accessible image URLs. Local filesystem paths will fail or produce broken posts.

## Working URL Formats

| Format | Status | Example |
|--------|--------|---------|
| Google Drive `uc?export=view` | Working | `https://drive.google.com/uc?export=view&id=FILE_ID` |
| Google Drive `usercontent/download` | Working | `https://drive.usercontent.google.com/download?id=FILE_ID&export=view` |
| Catbox.moe / Litter | BROKEN | URLs expire or get blocked by Buffer |
| Local file paths | BROKEN | `/home/.../image.png` fails silently |

## Auto-Upload Pipeline

### Quick Upload (CLI)
```bash
cd ~/.openclaw/workspace/scripts
python3 auto_upload_to_drive.py /path/to/image.png
```

### In-Code Upload
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".openclaw/workspace/scripts"))
from auto_upload_to_drive import upload_image

public_url = upload_image("/path/to/image.png")
# Returns: https://drive.google.com/uc?export=view&id=FILE_ID
```

### In Buffer Post
```python
mcp__buffer__create_post(
    channelId="YOUR_CHANNEL_ID",
    text="Your post text",
    assets=[{
        "image": {
            "url": public_url,  # Must be public URL
            "metadata": {"altText": "Description"}
        }
    }],
    schedulingType="automatic"
)
```

## Drive Folder
All uploaded images live in: `Hermes Generated Graphics` folder on Google Drive.

## Facebook Posts Require Metadata
Always include:
```python
metadata={"facebook": {"type": "post"}}
```
