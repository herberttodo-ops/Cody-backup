# Google Sheets Content Management for Social Media

Pattern discovered during LotSignal content creation (Sept 2026).

## Why Google Sheets?

When managing multi-channel social media for multiple brands, Google Sheets provides:
- **Single source of truth** for all posts, graphics, and scheduling
- **Easy editing** without redeploying code
- **Team sharing** without complex auth
- **Status tracking** with simple dropdowns
- **Graphics linking** via file paths or URLs

## Sheet Structure

### 1. Content Calendar (Tab)
Weekly scheduling with execution tracking.

| Column | Purpose | Example |
|--------|---------|---------|
| Date | ISO 8601 date | 2025-09-08 |
| Day | Day of week | Monday |
| Channel | Which account | LotSignal Business |
| Content Type | Format | Text Post |
| Content Pillar | Theme | Aged Inventory Insights |
| Post Title | Short name | Aged Inventory Daily Cost |
| Post Copy | Full text | Every aged unit costs... |
| Hashtags | Space-separated | #CarDealership #AgedInventory |
| Visual Concept | Graphic description | Counter graphic showing $100/day |
| Status | Ready/Scheduled/Posted | Ready |
| Scheduled Time | Time with timezone | 8:00 AM EST |
| Posted? | Yes/No | No |
| Notes | Any context | Week 1 - Day 1 |

### 2. Content Bank (Tab)
Reusable posts inventory.

| Column | Purpose |
|--------|---------|
| ID | Unique code (ls-b001, ls-p001) |
| Channel | LotSignal Business / Andrew Personal |
| Content Pillar | Theme/category |
| Post Title | Short descriptive name |
| Post Copy | Full post text with line breaks |
| Hashtags | Space-separated tags |
| Optimal Day | Best day to post this |
| Optimal Time | Best time to post |
| Status | Ready/Used/Archived |
| Posted Count | How many times used |
| Last Posted | Date last published |
| Performance | Impressions/engagements |

### 3. Graphics Library (Tab)
Track generated visuals.

| Column | Purpose |
|--------|---------|
| Post ID | Links to Content Bank |
| Post Title | Descriptive name |
| Graphic File | Filename |
| Local Path | Absolute path on disk |
| Status | Ready/Needs Update |

### 4. Performance Tracker (Tab)
Log metrics after posting.

| Column | Purpose |
|--------|---------|
| Date | Posted date |
| Post ID | Content Bank reference |
| Channel | Where posted |
| Impressions | Views |
| Engagements | Likes + comments + shares |
| Clicks | Link clicks |
| CTR % | Click-through rate |

### 5. Hashtag Library (Tab)
Organized hashtag sets.

| Column | Purpose |
|--------|---------|
| Category | Core Brand / Dealership / Marketing |
| Hashtags | Space-separated |
| Usage Count | Times used |
| Last Used | Date |
| Performance | Average engagement |

## Automation Patterns

### Batch Create Posts
```python
# Generate graphics for all posts in Content Bank
for post in content_bank:
    if post['status'] == 'Ready' and not post.get('graphic'):
        generate_graphic(post['title'], post['visual_concept'])
        update_sheet(post['id'], graphic_path)
```

### Schedule Week Content
```python
# Copy Content Bank rows to Content Calendar for next week
for post in week_posts:
    append_to_calendar(post)
    update_status(post['id'], 'Scheduled')
```

### Track Performance
```python
# After posts publish, update Performance Tracker
published = list_published_posts()
for post in published:
    metrics = get_post_metrics(post['id'])
    append_to_performance_tracker(metrics)
```

## Graphics Integration

Store graphic file paths in the sheet so they can be:
- Referenced when scheduling in Buffer
- Batch-generated when content is approved
- Easily found for re-use or updates

Format:
```
Local Path: /home/herby/.hermes/generated_images/or_image____ID___.png
```

## Content Tiers

**Business Posts (Professional Authority):**
- Industry insights, tips, case studies
- Product features and updates
- Third-party validation (reviews, awards)

**Personal Posts (Building in Public):**
- Founder journey and learnings
- Behind-the-scenes process
- Honest reflections on mistakes
- Early-stage vulnerability ("I don't know yet")

**Ratio Rule:** 
- Early-stage brands: 60% personal / 40% business
- Established brands: 30% personal / 70% business
