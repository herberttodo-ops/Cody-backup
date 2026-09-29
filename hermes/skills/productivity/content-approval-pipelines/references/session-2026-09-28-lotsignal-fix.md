# Session Reference: LotSignal Approval Notification Bug — 2026-09-28

## Bug Summary

`notify_approval.py` reported "Notification sent" but user never received the message.

## Root Cause 1: Wrong Bot Token

- Script reads `~/.hermes/.telegram-token` for Telegram bot auth
- Token file contained stale token for old bot `@TheSean_bot` (name: "Cody")
- Script bypassed Hermes native delivery, using `urllib.request.urlopen()` directly
- `getMe` confirmed bot identity; message went to wrong bot entirely

## Root Cause 2: Image Path Not in Meta

- Image generator stored result at `~/.hermes/generated_images/lotsignal_social____ID___.png`
- Meta JSON recorded `"image_path": "/home/herby/.hermes/generated_images/lotsignal_social____ID___.png"`
- Notifier looked for `draft_20260928_142054_image.png` adjacent to meta file
- Image never attached; notification sent as plain text only

## Verified Fix

```python
# In notifier, read meta["image_path"] FIRST
meta_path = os.path.join(draft_dir, draft_base + "_meta.json")
with open(meta_path) as f:
    meta = json.load(f)

img_file = meta.get("image_path") or os.path.join(draft_dir, draft_base + "_image.png")
```

## Environment

- Hermes profile: default
- Bot identity at time of bug: ID ___ID___, username @TheSean_bot
- Draft location: `~/.hermes/lotsignal-social/drafts/2026-09/`
- Image storage: `~/.hermes/generated_images/`
