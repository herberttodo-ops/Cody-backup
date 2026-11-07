# Tales Untold: Buffer 429 and direct YouTube fallback (Nov 2026)

- Buffer MCP 429 with a rateLimit bucket at remaining 0 / resetSeconds ~719000 = ~8 day lockout. pipeline_v3 used to log COMPLETE anyway.
- Working fallback: `~/.hermes/scripts/youtube_upload_oauth.py <video> <title> <desc> --publish-at <ISO UTC>` (private + publishAt). Wired into pipeline_v3.py phase 9 (backup .bak_20261106) and accepted by tales_watchdog.py.
- OAuth invalid_grant: re-run youtube_oauth_device.py (Google now returns `verification_url`). Scope `youtube.upload` cannot read or change privacy; use `https://www.googleapis.com/auth/youtube` (edit SCOPES in both youtube_oauth_device.py and youtube_upload_oauth.py).
- Composio YOUTUBE_* has its own daily quota and 403s while direct OAuth uploads work. Read-back uses `parts` (not `part`).
- Refill templates must be >=100 words (pipeline gate: 100 words / 38s). tale_arm_schedule_refill.py now imports templates from tales-untold/arm_schedule_refill.py.
- Instruction fidelity: when Andrew says "publish to YouTube now", a private upload with future publishAt is NOT that. Flag the deviation before reporting success.
