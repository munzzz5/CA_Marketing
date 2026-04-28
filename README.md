# Chaat Anna Promotion & Marketing Intelligence System (v2.1)

Production-ready starter for a **keyword-driven marketing intelligence engine** with:

- FastAPI backend
- Browser frontend
- Separate SQLite database (`data/marketing_intelligence.db`)
- Docker deployment support

## Added in this review pass

- Keyword groups (FR-34) via `keyword_groups` + membership table.
- Classification run endpoint (`POST /classify/run`).
- Digest preview endpoint (`GET /digest/preview`) with all digest sections.
- Hard duplicate prevention at DB layer using unique index on `(keyword_id, source_url)`.
- Dockerfile + docker-compose for one-command deployment.

## Core functionality

- Dynamic keyword CRUD
- Keyword grouping and group membership management
- Scrape run across active keywords
- Content storage, dedupe, relevance scoring
- Classification and content retrieval
- Idea generation (content based + custom prompt)
- Digest summary generation

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- UI: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`

## Docker run

```bash
docker compose up --build
```

- App URL: `http://127.0.0.1:8000/`
- Persistent DB volume: `./data:/app/data`

## API surface

### Keywords
- `GET /keywords`
- `POST /keywords`
- `PATCH /keywords/{id}`
- `DELETE /keywords/{id}`

### Keyword Groups
- `GET /keyword-groups`
- `POST /keyword-groups`
- `POST /keyword-groups/{group_id}/keywords`
- `GET /keyword-groups/{group_id}/keywords`
- `DELETE /keyword-groups/{group_id}/keywords/{keyword_id}`

### Scrape + Classification
- `POST /scrape/run`
- `POST /classify/run`
- `GET /scrape/results`

### Content
- `GET /content`
- `GET /content/{id}`

### Idea Generation
- `POST /ideas/generate/{content_id}`
- `POST /ideas/custom`
- `GET /ideas`

### Digest
- `GET /digest/preview`

## Strategic rule

Do not hardcode events/trends/hooks in code. Use:

**Keywords → Data → Classification/Ideas → Action**
