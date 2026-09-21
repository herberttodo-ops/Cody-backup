Andrew (name: Herby): strategic collaborator, templates/checklists, avoid em dashes, direct about uncertainty, no emojis.
§
OBSIDIAN: Vault at ~/Documents/Obsidian Vault (Index, OptiRFP, TLC Rescue, Rival Productions, Brand Guidelines, daily notes). Use obsidian skill.
§
Skills USER-OWNED, need `hermes curator adopt`. Buffer caps scheduled posts at 10 total account-wide; refill crons must check remaining budget. Andrew wants zero-manual-step autonomy but prefers waiting for natural resolution (posts publishing, credits refreshing) over upgrading plans/bumping existing posts when blocked.
§
OptiRFP LinkedIn graphics: 4:3 aspect ratio, text LEFT, visuals RIGHT, logo 70-100px. Tales Untold pivot to 'creatures in the woods' after Sep 22.
§
TALES_UNTOLD_BUFFER_TOKEN=___LONG_STRING___ (YouTube channel)
OPTIRFP_BUFFER_TOKEN=___LONG_STRING___ (LinkedIn/Facebook)
OPTIRFP_BUFFER_ORG_ID=6a7f74229bd9eca99cf9f777
§
Andrew expects verification before assumptions, not just for APIs but for output claims (e.g. caught 53% of video captions silently truncated by watching — verify things like caption completeness against actual rendered output, not just code logic). He verifies posting times against niche best practices and shifts quickly when suboptimal.
§
POYO takes raw ElevenLabs voice IDs and 12k+ chars/request without truncation, but does NOT error on a bad voice ID: verify a voice swap via MD5 + duration + band RMS.
§
Telegram caps bot downloads at 20MB; bigger files are rejected server-side and never hit disk, so don't hunt for them. Use ~/.hermes/scripts/tales_add_music.sh <path|direct URL> for large audio.
§
OptiRFP Buffer posting: Ensure cron script posts to both LinkedIn AND Facebook. The optirfp_daily_post.sh only called post-linkedin, missing post-facebook entirely. When adding new channels, update both buffer_dual_account.py (add channel ID and CLI command) AND the daily posting script (add the platform call). Images via Ideogram are working correctly.