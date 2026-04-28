from __future__ import annotations

import sqlite3
from datetime import date
from typing import Any

from .database import get_connection


def rows_to_dicts(rows: list[Any]) -> list[dict[str, Any]]:
    return [dict(r) for r in rows]


def score_keyword(keyword: str) -> int:
    weights = {
        "festival": 82,
        "holiday": 78,
        "rain": 74,
        "meme": 80,
        "viral": 84,
        "corporate": 86,
        "office": 83,
        "it companies": 88,
    }
    keyword_lower = keyword.lower()
    base = 65
    for token, score in weights.items():
        if token in keyword_lower:
            base = max(base, score)
    return min(100, base)


def infer_content_type(keyword: str) -> str:
    val = keyword.lower()
    if any(k in val for k in ["festival", "holiday", "event", "college"]):
        return "Event"
    if any(k in val for k in ["meme", "viral", "trending"]):
        return "Meme"
    if any(k in val for k in ["trend", "instagram", "topic"]):
        return "Trend"
    if any(k in val for k in ["office", "corporate", "company", "employee"]):
        return "Opportunity"
    return "News"


def seed_scraped_content_for_keyword(keyword_row: dict[str, Any]) -> dict[str, Any]:
    keyword_text = keyword_row["keyword"]
    content_type = infer_content_type(keyword_text)
    score = score_keyword(keyword_text)
    source = "SignalStream"
    source_url = f"https://signals.example.com/search?q={keyword_text.replace(' ', '+')}"
    title = f"{keyword_text.title()} intelligence pulse"
    description = (
        f"Detected discussion momentum for '{keyword_text}' with marketing relevance in Chennai market segments."
    )

    with get_connection() as conn:
        try:
            conn.execute(
                """
                INSERT INTO scraped_content
                    (keyword_id, title, description, source, source_url, content_type, relevance_score, published_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    keyword_row["id"],
                    title,
                    description,
                    source,
                    source_url,
                    content_type,
                    score,
                    date.today().isoformat(),
                ),
            )
            row = conn.execute(
                "SELECT * FROM scraped_content WHERE id = last_insert_rowid()"
            ).fetchone()
            return dict(row)
        except sqlite3.IntegrityError:
            existing = conn.execute(
                "SELECT * FROM scraped_content WHERE keyword_id = ? AND source_url = ?",
                (keyword_row["id"], source_url),
            ).fetchone()
            return dict(existing)


def build_idea(content: dict[str, Any], idea_type: str) -> tuple[str, str, str, str, str]:
    title = f"{idea_type}: {content['title']}"
    description = (
        f"Use insight '{content['title']}' to create a targeted activation for Chennai audiences."
    )
    notes = (
        "Prepare creative in Tamil + English, set 48-hour launch SLA, and track coupon redemptions by source."
    )
    difficulty = "Medium"
    impact = "High" if content["relevance_score"] >= 80 else "Medium"
    return title, description, notes, difficulty, impact


def fetch_digest_sections() -> dict[str, list[dict[str, Any]]]:
    with get_connection() as conn:
        upcoming_events = rows_to_dicts(
            conn.execute(
                "SELECT * FROM scraped_content WHERE content_type = 'Event' ORDER BY relevance_score DESC LIMIT 5"
            ).fetchall()
        )
        trending_topics = rows_to_dicts(
            conn.execute(
                "SELECT * FROM scraped_content WHERE content_type IN ('Trend', 'News') ORDER BY relevance_score DESC LIMIT 5"
            ).fetchall()
        )
        meme_opportunities = rows_to_dicts(
            conn.execute(
                "SELECT * FROM scraped_content WHERE content_type = 'Meme' ORDER BY relevance_score DESC LIMIT 5"
            ).fetchall()
        )
        b2b_opportunities = rows_to_dicts(
            conn.execute(
                "SELECT * FROM scraped_content WHERE content_type = 'Opportunity' ORDER BY relevance_score DESC LIMIT 5"
            ).fetchall()
        )
        campaign_ideas = rows_to_dicts(
            conn.execute(
                "SELECT * FROM generated_ideas WHERE idea_type = 'CampaignIdea' ORDER BY id DESC LIMIT 5"
            ).fetchall()
        )
        offer_suggestions = rows_to_dicts(
            conn.execute(
                "SELECT * FROM generated_ideas WHERE idea_type = 'PromotionalOffer' ORDER BY id DESC LIMIT 5"
            ).fetchall()
        )

    return {
        "upcoming_events": upcoming_events,
        "trending_topics": trending_topics,
        "meme_opportunities": meme_opportunities,
        "campaign_ideas": campaign_ideas,
        "offer_suggestions": offer_suggestions,
        "b2b_opportunities": b2b_opportunities,
    }
