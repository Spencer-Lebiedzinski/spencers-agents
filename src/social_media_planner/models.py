from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class CollectorConfig(BaseModel):
    seed_topics: list[str] = Field(default_factory=list)
    competitor_names: list[str] = Field(default_factory=list)
    competitor_domains: list[str] = Field(default_factory=list)
    subreddits: list[str] = Field(default_factory=list)
    x_keywords: list[str] = Field(default_factory=list)
    x_accounts: list[str] = Field(default_factory=list)
    time_window_days: int = 7
    max_items_per_source: int = 10


class QueryPack(BaseModel):
    pain_point_queries: list[str] = Field(default_factory=list)
    competitor_queries: list[str] = Field(default_factory=list)
    campaign_queries: list[str] = Field(default_factory=list)


class ResearchItem(BaseModel):
    source: str
    item_type: str
    url: str
    title: str
    author: str = ""
    published_at: str = ""
    query: str = ""
    theme: str = ""
    pain_points: list[str] = Field(default_factory=list)
    competitors: list[str] = Field(default_factory=list)
    campaign_patterns: list[str] = Field(default_factory=list)
    engagement_signals: dict[str, int | float | str] = Field(default_factory=dict)
    raw_excerpt: str = ""
    platform: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResearchCorpus(BaseModel):
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    query_pack: QueryPack
    items: list[ResearchItem] = Field(default_factory=list)


class ResearchReport(BaseModel):
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    summary: str
    pain_point_clusters: list[str] = Field(default_factory=list)
    competitor_watchlist: list[str] = Field(default_factory=list)
    viral_campaign_examples: list[str] = Field(default_factory=list)
    source_digest: list[str] = Field(default_factory=list)
    top_items: list[ResearchItem] = Field(default_factory=list)


class GeneratedImageAsset(BaseModel):
    asset_id: str
    title: str
    prompt: str
    platform: str
    asset_type: str
    output_path: str
    status: str
    revised_prompt: str = ""
    error: str = ""
