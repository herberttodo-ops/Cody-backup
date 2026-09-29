---
name: content-approval-pipelines
description: Build and debug automated content pipelines requiring human approval before publishing.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [content, social-media, automation, approval, notification]
    related_skills: [buffer-api, social-media-workflow]
---

# Content Approval Pipelines

Automated content pipelines that generate drafts and require human approval before publishing. Covers draft metadata, notification delivery, credential drift, and image path resolution.

## When to Use

- Building or debugging approval workflows for social media, blog, or marketing content
- Notification scripts fail silently or user never receives the approval message
- Image attachments are missing from approval notifications
- Need to auto-select logo variants based on background brightness

## Pitfalls

### Stale Telegram Bot Token in `~/.hermes/.telegram-token`

Scripts that call `urllib.request.urlopen("https://api.telegram.org/bot{token}/...")` bypass Hermes native delivery. If the token file is stale (e.g., points to a deprecated bot), the script returns `{"ok": True}` but the message goes to a dead bot and the user never sees it.

**Symptom:** Script exits 0, reports "Notification sent", but user confirms "I don't see it."

**Fix:** Verify the token with `getMe` before sending, or use Hermes' built-in delivery tools instead of raw urllib.

### Image Path Mismatch Between Compositor and Notifier

An image generator may save the image to `~/.hermes/generated_images/` and record that path in `meta["image_path"]`, while the notifier looks for `{draft_base}_image.png` adjacent to the meta file. The image is never attached and the user only gets plain text.

**Fix:** The notifier MUST read `meta["image_path"]` first, then fall back to a sibling `.png`.

### Telegram 20 MB Upload Cap

Telegram bots reject files over 20 MB server-side; they never land on disk. For large audio/video assets, use a side-channel upload script (not bot file transfer) or reference a hosted URL.

### Background-Aware Logo Variant Selection

When compositing a brand logo onto generated images, the logo color must contrast with the placement region.

**Approach:**
1. Define placement spec (fixed pixel margins, max width)
2. Sample dominant brightness/color of that region from the image
3. For each SVG variant (white, dark, brand-colored), calculate contrast ratio
4. Select highest-contrast variant; fall back to user-defined default if ambiguous
5. Alternatively: mutate a single adaptive SVG by injecting CSS variables before compositing

**Required from user:**
- SVG variants or one adaptive SVG template
- Placement spec (margins, max width)
- Fallback priority order

## Verification

- [ ] Script verifies Telegram token validity (getMe) before sending
- [ ] Notifier reads `image_path` from metadata before falling back to sidecar
- [ ] Notification received on correct bot/channel within 30 seconds
- [ ] Logo placement avoids feed crop zones (e.g., 150px bottom margin for LinkedIn)
