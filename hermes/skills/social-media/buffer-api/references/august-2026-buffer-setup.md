# OptiRFP Content Pipeline - Session Log

## Session: August 2026 - Buffer Queue Setup

### Key Learnings

**User Correction: Scheduling Preferences**
- User explicitly stated: "Option 2 but these should be going to LinkedIn and facebook"
- **Critical workflow**: Schedule all posts in Buffer queue to both platforms simultaneously
- Buffer limit: 10 scheduled posts (user-aware)
- Posting window: Aug 15-24 initial batch

**Platform Decision Tree**:
```
- Image generation: Ideogram V4 API (not Buffer)
- Copy generation: linkedin-content-system skill
- Business page only: No personal reposts
- Scheduling: Buffer MCP (customScheduled mode)
- Channel posting: Both LinkedIn + Facebook per day
```

### JSON Structure Pattern (Validated)

**Correct asset placement for Buffer MCP create_post**:
```json
{
  "assets": [
    {"image": {"url": "DRIVE_URL", "metadata": {"altText": "..."}}}
  ],
  "channelId": "ID",
  "dueAt": "2026-08-15T08:00:00-04:00",
  "metadata": {"facebook": {"type": "post"}},
  "mode": "customScheduled",
  "schedulingType": "automatic",
  "text": "BUSINESS COPY HERE"
}
```

**Common error prevented**: Never nest `channelId`, `dueAt`, or `text` INSIDE the assets array - they go at top level.

### 10-Post Schedule (Aug 15-24)

Successfully created:
| Day | Date | Platform(s) | Status |

**Remaining**: Days 12-24 (13 days) need to be added when Buffer capacity frees up.

### Tool References

**buffer-api skill**:
- Facebook requires explicit `metadata.facebook.type: "post"`
- LinkedIn uses `metadata.linkedin.type: "post"`
- Google Drive images: `https://drive.google.com/uc?export=view&id=FILE_ID`
- Timezone: EST (-04:00 offset)

### API Channel IDs (verified)
- **LinkedIn Page "OptiRFP"**: `6a7f74bcb2d9d577437af9a4`
- **Facebook Page "Optirfp"**: `6a7f7476b2d9d577437af67f`
- **Organization**: `6a7f74229bd9eca99cf9f777`

## Notes for Future Sessions

- **Vista Social**: User may prefer this over Buffer for final scheduling
- **Time**: 8 AM EST is the fixed posting time preference
- **Limit**: Always check current scheduled count before attempting to add more
- **Both platforms**: User consistently wants LinkedIn AND Facebook, not either/or

---

*Session outcome: 10 posts scheduled successfully. System ready for next batch when capacity frees.*
