# Alternate Sunday Scheduler Runbook

## Cadence

- Frequency: Every alternate Sunday (bi-weekly)
- Recommended UTC trigger: `03:00 UTC` to align with low-traffic windows

## Scheduled Pipeline

1. Load active keywords (`is_active = true`) sorted by priority descending.
2. Trigger scraping jobs per keyword group.
3. Persist deduplicated content into `scraped_content`.
4. Classify each record as Event/Trend/News/Meme/Opportunity.
5. Generate ideas for high-relevance items.
6. Persist ideas into `generated_ideas`.
7. Build and send digest email with sectioned insights.

## Operational Guardrails

- Do not execute scraping for inactive keywords.
- Enforce duplicate detection on `(source_url, keyword_id)` or content hash.
- Relevance score must be normalized to `0-100`.
- High-impact threshold (recommended): `relevance_score >= 75`.

## Failure Handling

- If scrape stage fails partially, continue processing successful keywords and flag failures in digest metadata.
- If classification model fails, assign `content_type = News` as fallback and log for retry.
- If idea generation fails, retain content for manual review queue.

## Digest Sections

1. Upcoming events
2. Trending topics
3. Meme opportunities
4. Campaign ideas
5. Offer suggestions
6. B2B opportunities
