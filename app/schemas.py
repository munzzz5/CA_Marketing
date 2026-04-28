from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class KeywordCategory(str, Enum):
    EVENTS = "Events"
    TRENDS = "Trends"
    FOOD = "Food"
    WEATHER = "Weather"
    B2B_LEADS = "B2B Leads"
    LOCAL = "Local"
    COMPETITOR = "Competitor"
    CUSTOM = "Custom"


class ContentType(str, Enum):
    EVENT = "Event"
    TREND = "Trend"
    NEWS = "News"
    MEME = "Meme"
    OPPORTUNITY = "Opportunity"


class IdeaType(str, Enum):
    PROMOTIONAL_OFFER = "PromotionalOffer"
    CAMPAIGN_IDEA = "CampaignIdea"
    SOCIAL_MEDIA_HOOK = "SocialMediaHook"
    B2B_SALES_IDEA = "B2BSalesIdea"


class KeywordCreate(BaseModel):
    keyword: str = Field(min_length=2, max_length=200)
    category: Optional[KeywordCategory] = None
    priority: int = Field(default=1, ge=1, le=5)
    is_active: bool = True


class KeywordUpdate(BaseModel):
    keyword: Optional[str] = Field(default=None, min_length=2, max_length=200)
    category: Optional[KeywordCategory] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    is_active: Optional[bool] = None


class KeywordOut(BaseModel):
    id: int
    keyword: str
    category: Optional[str]
    priority: int
    is_active: bool
    created_at: datetime


class KeywordGroupCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class KeywordGroupOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime


class KeywordGroupMembershipCreate(BaseModel):
    keyword_id: int


class ScrapedContentOut(BaseModel):
    id: int
    keyword_id: int
    title: str
    description: str
    source: str
    source_url: str
    content_type: str
    relevance_score: int
    published_date: date
    created_at: datetime


class GenerateIdeasRequest(BaseModel):
    idea_type: IdeaType
    max_ideas: int = Field(default=3, ge=1, le=20)


class CustomIdeaRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=1000)
    keyword_ids: list[int] = Field(default_factory=list)
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    idea_type: IdeaType


class GeneratedIdeaOut(BaseModel):
    id: int
    content_id: int
    idea_type: str
    title: str
    description: str
    execution_notes: Optional[str]
    difficulty: Optional[str]
    expected_impact: Optional[str]
    created_at: datetime


class DigestOut(BaseModel):
    generated_at: datetime
    upcoming_events: list[ScrapedContentOut]
    trending_topics: list[ScrapedContentOut]
    meme_opportunities: list[ScrapedContentOut]
    campaign_ideas: list[GeneratedIdeaOut]
    offer_suggestions: list[GeneratedIdeaOut]
    b2b_opportunities: list[ScrapedContentOut]
