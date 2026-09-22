# Tales Untold Content Pivot: Folklore/Cryptid Focus

*Live data analysis, September 2026. Proven signal from 109 shorts on the Tales Untold channel.*

## The Finding: Named Entities Outperform Generic Horror by 3.2x

Scraped all 109 published shorts live via yt-dlp and categorized by content type.

| Category | Count | Avg Views | Top Example |
|----------|-------|-----------|------------|
| **Folklore / Cryptid / Mythology** | 13 | **786** | Skinwalkers Among Us (1,100) |
| Creature / Entity Horror | 37 | 244 | Whispering Woods (771) |
| Place-Based Horror | 16 | 240 | Voodoo Legends (689) |
| Non-Horror (contamination) | 9 | **5** | Education/AI slop |

Folklore/cryptid shorts averaged **786 views** vs **244 for generic creature horror** and **240 for place-based horror**.

**Top 10 performers (all named folklore):**
1. Skinwalkers Among Us — 1,100
2. Transylvania's Real-Life Dracula — 1,100
3. The Crypt Keeper — 1,100
4. The Bell Witch — 1,000
5. The Wendigo — 1,000
6. Phantom Hikers — 942
7. Curse of the Grave Robbers — 801
8. Beast of Gévaudan — 780
9. Ghostly Guardians of Ancient Cathedrals — 770
10. Shadow People — 714

## Content Tier System (Implemented)

**TIER 1 (70% of output): Named folklore/cryptids with cultural recognition**
Skinwalkers, Wendigos, Dracula, Bell Witch, Mothman, Chupacabra, Baba Yaga, Banshees, La Llorona, Jersey Devil, Beast of Gévaudan, Shadow People, Phantom Hikers, Michigan Dogman, Fouke Monster, Enfield Poltergeist, Kuchisake-onna, Kraken, Drop Bears, Yowie, Wendigo, etc.

**TIER 2 (25%): Original creature/entity with specificity**
Named places with named threats ("The Hollow Brook Watcher"), historical-document tie-ins ("The 1847 Expedition Log"), entity variants ("Not Skinwalkers. Something Older.")

**TIER 3 (5%): Place-based ONLY with attached entity**
Never produce: basement noises, wrong numbers, GPS glitches without a named entity.

## Channel Contamination
4/10 long-form videos and 9 shorts on the channel were NOT horror — AI-generated slop about "Smart Cities," "Retail Revolution," "Millionaire Mindset." Average views: 5. These likely damaged channel topical authority. They were identified live and flagged for removal.

## Title Formula That Performs

**Winning pattern: "[Entity]: [Specific Angle]"**

Examples from proven performers:
- "Skinwalkers Among Us"
- "Transylvania's Real-Life Dracula"
- "The Beast of Gévaudan"

**Formula variants to test:**
1. **"[Entity]: What [Authority] Refuses to Explain"** — "Wendigo: What Algonquian Elders Refuse to Explain"
2. **"[Entity]: [Untold Detail]"** — "The Wendigo: Why Starvation Isn't the Real Cause"
3. **"I [Encountered] [Entity]. [Consequence]"** — "I Tracked the Beast of Gévaudan. Twelve Claw Marks, One Trail"
4. **"[Location] Doesn't Talk About [Entity]"** — "Point Pleasant Doesn't Talk About the Mothman's Second Visitor"

**Rules:**
- Entity name in first 5 words
- No "| Tales Untold" suffix (burns title space at low sub counts)
- No em dashes
- No hashtags in description

## Anti-Patterns That Don't Work

| Bad Title | Why It Failed | Views |
|-----------|--------------|-------|
| "Wrong Number" | No entity, no specificity | 3 |
| "Mirror Bathroom" | Generic trope, no anchor | 1 |
| "GPS Road" | No entity, no folklore | 6 |
| "Basement Noise" | Place-based without named threat | 71 |
| "The Voice Incident" | Generic, no cultural anchor | 5 |

## Verification Method

To reproduce a comparable analysis on any YouTube channel:

```bash
# Scrape all shorts
yt-dlp -j --flat-playlist "https://www.youtube.com/channel/CHANNEL_ID/shorts"

# Scrape all regular videos
yt-dlp -j --flat-playlist "https://www.youtube.com/channel/CHANNEL_ID/videos"

# Extract JSON fields: id, title, view_count, duration
```

Then cluster by content type (folklore vs generic vs non-relevant) and compare averages. A 2.5x+ delta across >50 videos is actionable.

## Files Changed for This Pivot

- `~/.hermes/skills/creative/spielberg/references/folklore-cryptid-topics.csv` — topic database
- `~/.openclaw/workspace/tales-untold/prompts/shorts_system.txt` — rewritten with entity-first mandate
- `~/.hermes/scripts/buffer_dual_account.py` — auto-strips "| Tales Untold" suffix
- Cron job `7bb4ab80b2c2` — new prompt with folklore database reference

## Long-Form Gate

Do NOT produce standalone long-form until a short exceeds 500 views. At 211 subscribers, 23-minute videos average 12 views. Only compile long-form from 3+ related shorts that have proven traction.
