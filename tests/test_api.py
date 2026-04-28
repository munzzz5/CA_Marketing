from fastapi.testclient import TestClient

from app.database import init_db, get_connection
from app.main import app


client = TestClient(app)


def reset_db() -> None:
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM keyword_group_members")
        conn.execute("DELETE FROM keyword_groups")
        conn.execute("DELETE FROM generated_ideas")
        conn.execute("DELETE FROM scraped_content")
        conn.execute("DELETE FROM keywords")


def test_keyword_to_idea_flow():
    reset_db()

    create = client.post(
        "/keywords",
        json={
            "keyword": "festival Chennai",
            "category": "Events",
            "priority": 2,
            "is_active": True,
        },
    )
    assert create.status_code == 201

    scrape = client.post("/scrape/run")
    assert scrape.status_code == 200

    classify = client.post("/classify/run")
    assert classify.status_code == 200
    assert classify.json()["classified_records"] >= 1

    content = client.get("/content")
    assert content.status_code == 200
    assert len(content.json()) >= 1
    content_id = content.json()[0]["id"]

    ideas = client.post(
        f"/ideas/generate/{content_id}",
        json={"idea_type": "CampaignIdea", "max_ideas": 2},
    )
    assert ideas.status_code == 201
    assert len(ideas.json()) == 2


def test_keyword_group_and_digest_preview():
    reset_db()

    kw = client.post(
        "/keywords",
        json={
            "keyword": "corporate office Chennai",
            "category": "B2B Leads",
            "priority": 3,
            "is_active": True,
        },
    )
    assert kw.status_code == 201
    keyword_id = kw.json()["id"]

    grp = client.post("/keyword-groups", json={"name": "B2B Group", "description": "Corporate leads"})
    assert grp.status_code == 201
    group_id = grp.json()["id"]

    link = client.post(f"/keyword-groups/{group_id}/keywords", json={"keyword_id": keyword_id})
    assert link.status_code == 201

    group_keywords = client.get(f"/keyword-groups/{group_id}/keywords")
    assert group_keywords.status_code == 200
    assert any(k["id"] == keyword_id for k in group_keywords.json())

    client.post("/scrape/run")
    digest = client.get("/digest/preview")
    assert digest.status_code == 200
    body = digest.json()
    assert "b2b_opportunities" in body
    assert "campaign_ideas" in body
