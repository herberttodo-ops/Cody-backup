Andrew (name: Herby): visually meticulous, spots brand/graphics artifacts immediately. "Fix the issue" is a directive — act, don't deliberate. Templates/checklists, avoid em dashes, no emojis.
§
OBSIDIAN: Vault at ~/Documents/Obsidian Vault (Index, OptiRFP, TLC Rescue, Rival Productions, Brand Guidelines, daily notes). Use obsidian skill.
§
Skills USER-OWNED, need `hermes curator adopt`. Buffer caps scheduled posts at 10 total account-wide; refill crons must check remaining budget. Andrew wants zero-manual-step autonomy but prefers waiting for natural resolution (posts publishing, credits refreshing) over upgrading plans/bumping existing posts when blocked.
§
Andrew expects verification before assumptions — video caption completeness via actual rendered output (not just code logic), posting time verification against niche data, and general skepticism toward claimed-but-unverified outputs.
§
LotSignal social pipeline: Target = single-point franchise dealers (Owner/GM). Optimal schedule (Option A): LinkedIn 10am, Instagram 12:30pm, Facebook 2pm ET. Day rotation: Mon=stat, Tue=insight, Wed=tip, Thu=stat, Fri=insight, Sat=tip, Sun=rest.
§
LotSignal Composio: SDK = `composio` v0.24+ session-based (Composio().create(user_id=...)), NOT deprecated composio_core/ComposioToolSet (HTTP 410). Andrew signed up at dashboard.composio.dev: real Project API key, LinkedIn/FB/IG connected. Publishing held: LinkedIn managed auth only grants w_member_social (personal) — company-page org scopes need custom LinkedIn Developer App approval (days). No LotSignal FB Page exists so IG posting has no attach point; YouTube OAuth left INITIATED. Andrew rejects Buffer for LotSignal — firm preference.
§
Tales Untold pipeline (Oct 6 fixed): Single Hermes cron 7bb4ab80b2c2 produces 3x/day at 8am/12pm/4pm ET for 6/7/8pm Buffer slots. Watchdog d9cbff5d6e8a runs every 2h, alerts on missed slots. Native crontab removed; tales_v3_producer.sh bash bug ${CATEGORY.title()} fixed. 200+ cryptid database. Cedric voice only. Alert-only mode.