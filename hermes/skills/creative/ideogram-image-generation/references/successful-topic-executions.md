# Successful Topic Executions

Reference log of topic/headline combinations that produced clean, high-quality results.

## page-one Topic

**Headline**: "Win the RFP before page two" (6 words)

**Result**: 10/10 quality score
- Clean text rendering, no watermarks
- Excellent visual: open book with mint spotlight effect
- Logo composited cleanly at bottom via `create_branded_social_graphic`
- Brand colors perfect: dark navy (#0F172A) + mint (#40D395)

**Key Success Factors**:
- Concise headline (6 words) rendered crisply
- "page-one" topic produced relevant book imagery
- No fake watermarks or "in" icons appeared
- Bottom area remained clean for logo placement

**Tool Path**: 
1. `create_branded_social_graphic(headline=..., topic="page-one", aspect_ratio="square")` 
2. Handles Ideogram generation + logo compositing automatically
3. No need to manually locate logo file - tool manages asset internally

**Note**: When logo file is not available in `~/.hermes/assets/`, use `create_branded_social_graphic` instead of the Python compositor script - it has built-in logo asset access.

---

*Last updated: 2026-09-09*
