# Social Media Image Workflow - OptiRFP

## Spreadsheet Structure

When integrating generated images with content calendars, ensure proper column structure:

### Required Columns

| Column | Purpose | Example Content |
|--------|---------|-----------------|
| Week | Content week number | "1" |
| Date | Publication date | Excel serial date |
| Day | Day of week | "Monday" |
| Time (ET) | Publication time | Decimal (0.___ID___ = 7:00 AM) |
| Channel | Platform | "LinkedIn", "Twitter/X", "Instagram" |
| Pillar | Content category | "Origin Story", "Education" |
| Copy | Post text | Full post content |
| Hashtags | Tags | "#GovCon #RFP" |
| Image/Video Description | Text description of visual | "30-sec video showing..." |
| CTA | Call to action | "Try free (link in bio)" |
| Status | Draft/Scheduled/Posted | "Draft" |
| Notes | Internal notes | "Thread part 3" |
| Image Link | **Direct URL to image file** | Google Drive direct link |

### Common Issues

**Problem:** Image links mixed with Image Description column

**Symptom:** Column I (Image/Video Description) contains both text descriptions and URLs

**Fix:** Add dedicated "Image Link" column (Column N) for actual image URLs

### Google Drive Integration

1. **Create folder** for social media images
   - Example: "OptiRFP Social Media Post Images"
   - Make publicly viewable: `type: anyone, role: reader`

2. **Upload images** with descriptive filenames
   - Format: `optirfp_{topic}_{timestamp}.png`

3. **Get direct links** for embedding:
   - Format: `https://drive.google.com/uc?export=view&id={FILE_ID}`
   - This renders the image directly, not a preview page

4. **Update spreadsheet** with direct links in "Image Link" column

### Quality Checklist Before Posting

- [ ] Image renders at 1024x1024 (square) or correct aspect ratio
- [ ] Text is crisp and readable at thumbnail size
- [ ] No AI artifacts or fake watermarks
- [ ] Exact logo is properly composited at bottom
- [ ] Brand colors match (#0F172A navy, #40D395 mint)
- [ ] Image link in spreadsheet opens correct file
- [ ] File is publicly accessible (test in incognito)

### Batch Regeneration Workflow

When regenerating all images (e.g., for style refresh):

1. Generate new images with updated prompt/settings
2. Upload to Google Drive folder
3. Update spreadsheet "Image Link" column with new URLs
4. Archive old images (move to "archive" subfolder)
5. Test a few links to verify accessibility

## Cost Tracking

| Action | Cost | Notes |
|--------|------|-------|
| Ideogram V4 generation | ~$0.04/image | Text baked in |
| Logo compositing | Free | PIL local processing |
| Google Drive storage | Free | Until 15GB limit |
| **Total per post** | **~$0.04** | 50% cheaper than composite workflow |
