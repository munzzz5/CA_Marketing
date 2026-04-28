# Chaat Anna Promotion & Marketing Intelligence System (v2.0)

This repository defines the **v2.0 blueprint** for transforming Chaat Anna from a promotion-only assistant into a reusable **marketing intelligence engine**.

## Vision

Build a system that behaves like a hybrid of:

- Google Trends (detect what matters now)
- CRM opportunity radar (surface B2B leads)
- Promotion engine (generate actionable campaigns/offers)

Core design rule:

> **No hardcoded events, trends, or campaign triggers**. Everything flows from configured keywords.

## End-to-End Flow

1. Keywords Defined
2. Scraping Engine Runs
3. Content Stored
4. AI Classifies Content
5. AI Generates Ideas (Offers / Campaigns / Leads)
6. Ideas Stored
7. Email Digest Sent
8. Team Executes
9. Sales Data Captured
10. Impact Analysis

---

## Functional Requirements

### Keyword Management Module

- **FR-31**: Add keywords dynamically.
- **FR-32**: Each keyword captures:
  - keyword text
  - category
  - priority
  - active/inactive flag
- **FR-33**: Edit/delete keywords.
- **FR-34**: Group keywords.

Supported categories:

- Events
- Trends
- Food
- Weather
- B2B Leads
- Local
- Competitor
- Custom

### Keyword-Based Scraping Engine

- **FR-35**: Run scraping across all active keywords.
- **FR-36**: Store scraped results as structured data.
- **FR-37**: Every record includes title, description, source, date, and matched keyword.
- **FR-38**: Deduplicate entries.
- **FR-39**: Assign relevance score.

### Content Classification Module

- **FR-40**: Classify into Event / Trend / News / Meme / Opportunity.
- **FR-41**: Link classified content to keywords.
- **FR-42**: Prioritize high-impact items.

### Multi-Purpose Idea Generation

- **FR-43**: Generate promotional offers, campaign ideas, social hooks, and B2B sales ideas.
- **FR-44**: Make output type selectable.
- **FR-45**: Store generated ideas separately.

### Custom Prompt Engine

- **FR-46**: Accept user custom prompt.
- **FR-47**: Let user choose keywords, time range, and idea type.
- **FR-48**: Generate output accordingly.

---

## API Surface (v2)

### Keywords

- `GET /keywords`
- `POST /keywords`
- `PATCH /keywords/{id}`
- `DELETE /keywords/{id}`

### Scraping

- `POST /scrape/run`
- `GET /scrape/results`

### Content

- `GET /content`
- `GET /content/{id}`

### Idea Generation

- `POST /ideas/generate/{content_id}`
- `POST /ideas/custom`
- `GET /ideas`

See `openapi.yaml` for request/response structure.

---

## Scheduling

Run on **every alternate Sunday**:

1. Fetch active keywords
2. Execute scraping
3. Persist content
4. Run classification
5. Generate ideas
6. Send digest

---

## Email Digest Contents

1. Upcoming events
2. Trending topics
3. Meme opportunities
4. Campaign ideas
5. Offer suggestions
6. B2B opportunities

---

## Starter Seed Keywords

### Events
- festival Chennai
- Tamil Nadu holidays
- India food days

### Trends
- viral Tamil meme
- Instagram trending India
- Chennai trending topics

### Weather
- rain Chennai forecast
- Chennai temperature heatwave

### B2B Leads
- IT companies Chennai events
- corporate office Chennai
- employee engagement programs

---

## Repository Assets

- `schema.sql` — relational schema for keywords/content/ideas
- `openapi.yaml` — endpoint contracts for v2 APIs
- `scheduler.md` — alternate-Sunday workflow guidance
