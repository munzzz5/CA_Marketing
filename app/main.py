from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import get_connection, init_db
from .schemas import (
    CustomIdeaRequest,
    DigestOut,
    GenerateIdeasRequest,
    GeneratedIdeaOut,
    KeywordCreate,
    KeywordGroupCreate,
    KeywordGroupMembershipCreate,
    KeywordGroupOut,
    KeywordOut,
    KeywordUpdate,
    ScrapedContentOut,
)
from .services import (
    build_idea,
    fetch_digest_sections,
    infer_content_type,
    rows_to_dicts,
    seed_scraped_content_for_keyword,
)

app = FastAPI(title="Chaat Anna Marketing Intelligence", version="2.1.0")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "date": date.today().isoformat()}


@app.get("/keywords", response_model=list[KeywordOut])
def get_keywords(active_only: bool = Query(default=False)) -> list[dict]:
    query = "SELECT * FROM keywords"
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY priority DESC, id DESC"

    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
    return rows_to_dicts(rows)


@app.post("/keywords", response_model=KeywordOut, status_code=201)
def add_keyword(payload: KeywordCreate) -> dict:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO keywords (keyword, category, priority, is_active) VALUES (?, ?, ?, ?)",
            (payload.keyword, payload.category, payload.priority, int(payload.is_active)),
        )
        row = conn.execute("SELECT * FROM keywords WHERE id = last_insert_rowid()").fetchone()
    return dict(row)


@app.patch("/keywords/{keyword_id}", response_model=KeywordOut)
def patch_keyword(keyword_id: int, payload: KeywordUpdate) -> dict:
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields supplied")

    set_clauses = []
    values = []
    for field, value in updates.items():
        set_clauses.append(f"{field} = ?")
        values.append(int(bool(value)) if field == "is_active" else value)

    values.append(keyword_id)
    sql = f"UPDATE keywords SET {', '.join(set_clauses)} WHERE id = ?"

    with get_connection() as conn:
        cursor = conn.execute(sql, tuple(values))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Keyword not found")
        row = conn.execute("SELECT * FROM keywords WHERE id = ?", (keyword_id,)).fetchone()
    return dict(row)


@app.delete("/keywords/{keyword_id}", status_code=204, response_class=Response)
def delete_keyword(keyword_id: int) -> Response:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM keywords WHERE id = ?", (keyword_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Keyword not found")
    return Response(status_code=204)


@app.get("/keyword-groups", response_model=list[KeywordGroupOut])
def list_keyword_groups() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM keyword_groups ORDER BY id DESC").fetchall()
    return rows_to_dicts(rows)


@app.post("/keyword-groups", response_model=KeywordGroupOut, status_code=201)
def create_keyword_group(payload: KeywordGroupCreate) -> dict:
    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO keyword_groups (name, description) VALUES (?, ?)",
                (payload.name, payload.description),
            )
        except Exception as exc:
            raise HTTPException(status_code=409, detail="Group name already exists") from exc
        row = conn.execute("SELECT * FROM keyword_groups WHERE id = last_insert_rowid()").fetchone()
    return dict(row)


@app.post("/keyword-groups/{group_id}/keywords", status_code=201)
def add_keyword_to_group(group_id: int, payload: KeywordGroupMembershipCreate) -> dict:
    with get_connection() as conn:
        group = conn.execute("SELECT id FROM keyword_groups WHERE id = ?", (group_id,)).fetchone()
        keyword = conn.execute("SELECT id FROM keywords WHERE id = ?", (payload.keyword_id,)).fetchone()
        if not group or not keyword:
            raise HTTPException(status_code=404, detail="Group or keyword not found")

        try:
            conn.execute(
                "INSERT INTO keyword_group_members (group_id, keyword_id) VALUES (?, ?)",
                (group_id, payload.keyword_id),
            )
        except Exception as exc:
            raise HTTPException(status_code=409, detail="Keyword already in group") from exc

    return {"group_id": group_id, "keyword_id": payload.keyword_id}


@app.get("/keyword-groups/{group_id}/keywords", response_model=list[KeywordOut])
def list_group_keywords(group_id: int) -> list[dict]:
    sql = """
        SELECT k.*
        FROM keywords k
        JOIN keyword_group_members kgm ON kgm.keyword_id = k.id
        WHERE kgm.group_id = ?
        ORDER BY k.priority DESC, k.id DESC
    """
    with get_connection() as conn:
        rows = conn.execute(sql, (group_id,)).fetchall()
    return rows_to_dicts(rows)


@app.delete(
    "/keyword-groups/{group_id}/keywords/{keyword_id}",
    status_code=204,
    response_class=Response,
)
def remove_keyword_from_group(group_id: int, keyword_id: int) -> Response:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM keyword_group_members WHERE group_id = ? AND keyword_id = ?",
            (group_id, keyword_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Membership not found")
    return Response(status_code=204)


@app.post("/scrape/run")
def run_scrape() -> dict:
    with get_connection() as conn:
        keywords = conn.execute(
            "SELECT * FROM keywords WHERE is_active = 1 ORDER BY priority DESC, id DESC"
        ).fetchall()

    created = [seed_scraped_content_for_keyword(dict(keyword)) for keyword in keywords]
    return {"processed_keywords": len(keywords), "stored_records": len(created)}


@app.post("/classify/run")
def run_classification() -> dict:
    with get_connection() as conn:
        rows = conn.execute("SELECT id, title FROM scraped_content").fetchall()
        for row in rows:
            inferred_type = infer_content_type(row["title"])
            conn.execute(
                "UPDATE scraped_content SET content_type = ? WHERE id = ?",
                (inferred_type, row["id"]),
            )
    return {"classified_records": len(rows)}


@app.get("/scrape/results", response_model=list[ScrapedContentOut])
def scrape_results(keyword_id: int | None = None, content_type: str | None = None) -> list[dict]:
    clauses = []
    values: list = []
    if keyword_id is not None:
        clauses.append("keyword_id = ?")
        values.append(keyword_id)
    if content_type:
        clauses.append("content_type = ?")
        values.append(content_type)

    sql = "SELECT * FROM scraped_content"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY published_date DESC, relevance_score DESC"

    with get_connection() as conn:
        rows = conn.execute(sql, tuple(values)).fetchall()
    return rows_to_dicts(rows)


@app.get("/content", response_model=list[ScrapedContentOut])
def get_content() -> list[dict]:
    return scrape_results()


@app.get("/content/{content_id}", response_model=ScrapedContentOut)
def get_content_item(content_id: int) -> dict:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM scraped_content WHERE id = ?", (content_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Content not found")
    return dict(row)


@app.post("/ideas/generate/{content_id}", response_model=list[GeneratedIdeaOut], status_code=201)
def generate_ideas(content_id: int, payload: GenerateIdeasRequest) -> list[dict]:
    with get_connection() as conn:
        content = conn.execute(
            "SELECT * FROM scraped_content WHERE id = ?", (content_id,)
        ).fetchone()
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        for _ in range(payload.max_ideas):
            title, description, notes, difficulty, impact = build_idea(dict(content), payload.idea_type.value)
            conn.execute(
                """
                INSERT INTO generated_ideas (content_id, idea_type, title, description, execution_notes, difficulty, expected_impact)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (content_id, payload.idea_type.value, title, description, notes, difficulty, impact),
            )

        rows = conn.execute(
            "SELECT * FROM generated_ideas WHERE content_id = ? ORDER BY id DESC LIMIT ?",
            (content_id, payload.max_ideas),
        ).fetchall()
    return rows_to_dicts(rows)


@app.post("/ideas/custom", response_model=list[GeneratedIdeaOut], status_code=201)
def generate_custom_ideas(payload: CustomIdeaRequest) -> list[dict]:
    clauses = []
    values: list = []

    if payload.keyword_ids:
        placeholders = ",".join("?" for _ in payload.keyword_ids)
        clauses.append(f"keyword_id IN ({placeholders})")
        values.extend(payload.keyword_ids)
    if payload.from_date:
        clauses.append("published_date >= ?")
        values.append(payload.from_date.isoformat())
    if payload.to_date:
        clauses.append("published_date <= ?")
        values.append(payload.to_date.isoformat())

    sql = "SELECT * FROM scraped_content"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY relevance_score DESC LIMIT 5"

    inserted_ids: list[int] = []
    with get_connection() as conn:
        content_rows = conn.execute(sql, tuple(values)).fetchall()
        if not content_rows:
            raise HTTPException(status_code=404, detail="No content matched filters")

        for content in content_rows:
            title, _, notes, difficulty, impact = build_idea(dict(content), payload.idea_type.value)
            description = f"Prompt: {payload.prompt}\n\nDerived action: {title}"
            conn.execute(
                """
                INSERT INTO generated_ideas (content_id, idea_type, title, description, execution_notes, difficulty, expected_impact)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    content["id"],
                    payload.idea_type.value,
                    f"Custom {title}",
                    description,
                    notes,
                    difficulty,
                    impact,
                ),
            )
            inserted_ids.append(conn.execute("SELECT last_insert_rowid()").fetchone()[0])

        placeholders = ",".join("?" for _ in inserted_ids)
        rows = conn.execute(
            f"SELECT * FROM generated_ideas WHERE id IN ({placeholders}) ORDER BY id DESC",
            tuple(inserted_ids),
        ).fetchall()

    return rows_to_dicts(rows)


@app.get("/ideas", response_model=list[GeneratedIdeaOut])
def list_ideas(idea_type: str | None = None) -> list[dict]:
    sql = "SELECT * FROM generated_ideas"
    values: tuple = ()
    if idea_type:
        sql += " WHERE idea_type = ?"
        values = (idea_type,)
    sql += " ORDER BY id DESC"
    with get_connection() as conn:
        rows = conn.execute(sql, values).fetchall()
    return rows_to_dicts(rows)


@app.get("/digest/preview", response_model=DigestOut)
def digest_preview() -> dict:
    sections = fetch_digest_sections()
    return {
        "generated_at": datetime.now(timezone.utc),
        **sections,
    }
