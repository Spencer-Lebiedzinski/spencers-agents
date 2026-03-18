from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from collections import Counter
from pathlib import Path
from typing import Any

from social_media_planner.models import (
    CollectorConfig,
    QueryPack,
    ResearchCorpus,
    ResearchItem,
    ResearchReport,
)

USER_AGENT = "social-media-planner/0.1 (+https://local.repo)"
PAIN_KEYWORDS = (
    "pain",
    "problem",
    "struggle",
    "frustrat",
    "overwhelm",
    "confus",
    "stuck",
    "fail",
    "hard",
    "waste",
)
CAMPAIGN_KEYWORDS = (
    "viral",
    "trend",
    "campaign",
    "launch",
    "hook",
    "creator",
    "ugc",
    "share",
    "repost",
)


def _request_json(url: str, headers: dict[str, str] | None = None) -> Any:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _request_text(url: str, headers: dict[str, str] | None = None) -> str:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8")


def parse_csv_env(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def build_collector_config(inputs: dict[str, Any]) -> CollectorConfig:
    return CollectorConfig(
        seed_topics=list(inputs.get("seed_topics", [])),
        competitor_names=list(inputs.get("competitor_names", [])),
        competitor_domains=list(inputs.get("competitor_domains", [])),
        subreddits=list(inputs.get("subreddits", [])),
        x_keywords=list(inputs.get("x_keywords", [])),
        x_accounts=list(inputs.get("x_accounts", [])),
        time_window_days=int(inputs.get("time_window_days", 7)),
        max_items_per_source=int(inputs.get("max_items_per_source", 10)),
    )


def build_query_pack(inputs: dict[str, Any], config: CollectorConfig) -> QueryPack:
    app_name = str(inputs["app_name"])
    target_user = str(inputs["target_user"])
    user_problem = str(inputs["user_problem"])
    dream_outcome = str(inputs["dream_outcome"])
    topics = config.seed_topics or [app_name, user_problem, dream_outcome]
    pain_queries = [
        f"{topic} pain points {target_user}" for topic in topics[:3]
    ] + [
        f"{app_name} users frustrated with {user_problem}",
        f"{target_user} struggling with {user_problem}",
    ]
    competitor_queries = [
        f"{app_name} alternatives",
        f"best apps for {dream_outcome}",
    ] + [f"{name} reviews" for name in config.competitor_names[:5]]
    campaign_queries = [
        f"{app_name} launch campaign viral",
        f"{dream_outcome} viral marketing examples",
        f"{target_user} instagram reel campaign",
    ] + [f"{keyword} viral thread" for keyword in config.x_keywords[:3]]
    return QueryPack(
        pain_point_queries=_dedupe_preserve_order(pain_queries),
        competitor_queries=_dedupe_preserve_order(competitor_queries),
        campaign_queries=_dedupe_preserve_order(campaign_queries),
    )


def collect_research(inputs: dict[str, Any], output_dir: Path) -> ResearchCorpus:
    config = build_collector_config(inputs)
    query_pack = build_query_pack(inputs, config)
    raw_payload: dict[str, Any] = {
        "query_pack": query_pack.model_dump(),
        "collectors": {},
    }
    items: list[ResearchItem] = []

    news_items = _collect_news(query_pack, config)
    raw_payload["collectors"]["news"] = [item.model_dump() for item in news_items]
    items.extend(news_items)

    reddit_items = _collect_reddit(query_pack, config)
    raw_payload["collectors"]["reddit"] = [item.model_dump() for item in reddit_items]
    items.extend(reddit_items)

    x_items = _collect_x(query_pack, config)
    raw_payload["collectors"]["x"] = [item.model_dump() for item in x_items]
    items.extend(x_items)

    raw_payload["collectors"]["tiktok"] = {"status": "stubbed_for_future_phase"}
    raw_payload["collectors"]["instagram"] = {"status": "stubbed_for_future_phase"}

    corpus = ResearchCorpus(query_pack=query_pack, items=_dedupe_items(items))
    _write_json(output_dir / "raw_source_dump.json", raw_payload)
    _write_json(
        output_dir / "normalized_source_dataset.json",
        [item.model_dump() for item in corpus.items],
    )
    return corpus


def analyze_research(
    corpus: ResearchCorpus,
    inputs: dict[str, Any],
    output_dir: Path,
) -> ResearchReport:
    items = corpus.items
    top_items = sorted(items, key=_engagement_score, reverse=True)[:5]
    pain_counter = Counter()
    competitor_counter = Counter()
    campaign_counter = Counter()
    source_counter = Counter(item.source for item in items)

    for item in items:
        for pain in item.pain_points:
            pain_counter[pain] += 1
        for competitor in item.competitors:
            competitor_counter[competitor] += 1
        for campaign in item.campaign_patterns:
            campaign_counter[campaign] += 1

    fallback_pains = _fallback_pain_points(items)
    pain_clusters = [label for label, _ in pain_counter.most_common(8)] or fallback_pains
    competitor_watchlist = [label for label, _ in competitor_counter.most_common(8)]
    campaign_examples = [label for label, _ in campaign_counter.most_common(8)] or [
        _summarize_top_item(item) for item in top_items
    ]
    source_digest = [
        f"{source}: {count} collected items" for source, count in source_counter.most_common()
    ]
    summary = (
        f"Collected {len(items)} source items for {inputs['app_name']} across "
        f"{', '.join(sorted(source_counter)) or 'no live sources'}. "
        f"Top pain themes: {', '.join(pain_clusters[:3]) or 'not enough evidence yet'}. "
        f"Top competitor signals: {', '.join(competitor_watchlist[:3]) or 'not enough evidence yet'}."
    )
    report = ResearchReport(
        summary=summary,
        pain_point_clusters=pain_clusters,
        competitor_watchlist=competitor_watchlist,
        viral_campaign_examples=campaign_examples,
        source_digest=source_digest,
        top_items=top_items,
    )
    _write_json(output_dir / "research_report.json", report.model_dump())
    (output_dir / "research_pack.md").write_text(
        render_research_pack(report), encoding="utf-8"
    )
    return report


def load_research_report(research_dir: Path) -> ResearchReport:
    data = json.loads((research_dir / "research_report.json").read_text(encoding="utf-8"))
    return ResearchReport.model_validate(data)


def render_research_pack(report: ResearchReport) -> str:
    lines = [
        "# Research Pack",
        "",
        "## Summary",
        report.summary,
        "",
        "## Pain Point Clusters",
    ]
    lines.extend(f"- {item}" for item in report.pain_point_clusters or ["No clusters found"])
    lines.extend(["", "## Competitor Watchlist"])
    lines.extend(
        f"- {item}" for item in report.competitor_watchlist or ["No competitor signals found"]
    )
    lines.extend(["", "## Viral Campaign Examples"])
    lines.extend(
        f"- {item}" for item in report.viral_campaign_examples or ["No viral campaign examples found"]
    )
    lines.extend(["", "## Source Digest"])
    lines.extend(f"- {item}" for item in report.source_digest or ["No sources collected"])
    lines.extend(["", "## Top Source Items"])
    for item in report.top_items:
        lines.append(f"- [{item.source}] {item.title} ({item.url})")
    lines.append("")
    return "\n".join(lines)


def build_research_inputs(report: ResearchReport) -> dict[str, str]:
    return {
        "research_summary": report.summary,
        "pain_point_clusters": "\n".join(f"- {item}" for item in report.pain_point_clusters),
        "competitor_watchlist": "\n".join(
            f"- {item}" for item in report.competitor_watchlist
        ),
        "viral_campaign_examples": "\n".join(
            f"- {item}" for item in report.viral_campaign_examples
        ),
        "source_digest": "\n".join(f"- {item}" for item in report.source_digest),
    }


def _collect_news(query_pack: QueryPack, config: CollectorConfig) -> list[ResearchItem]:
    items: list[ResearchItem] = []
    queries = (
        query_pack.pain_point_queries
        + query_pack.competitor_queries
        + query_pack.campaign_queries
    )[: max(config.max_items_per_source, 1)]
    for query in queries:
        url = (
            "https://news.google.com/rss/search?q="
            + urllib.parse.quote(query)
            + "&hl=en-US&gl=US&ceid=US:en"
        )
        try:
            text = _request_text(url, headers={"User-Agent": USER_AGENT})
            root = ET.fromstring(text)
        except (urllib.error.URLError, ET.ParseError):
            continue
        for node in root.findall(".//item")[:3]:
            title = _node_text(node, "title")
            link = _node_text(node, "link")
            description = _strip_html(_node_text(node, "description"))
            items.append(
                _build_item(
                    source="news",
                    item_type="article",
                    url=link,
                    title=title,
                    author=_node_text(node, "source"),
                    published_at=_node_text(node, "pubDate"),
                    query=query,
                    text=f"{title}. {description}",
                    metadata={"description": description},
                )
            )
    return items[: config.max_items_per_source]


def _collect_reddit(query_pack: QueryPack, config: CollectorConfig) -> list[ResearchItem]:
    items: list[ResearchItem] = []
    queries = (
        query_pack.pain_point_queries
        + query_pack.competitor_queries
        + query_pack.campaign_queries
    )
    subreddits = config.subreddits or ["startups", "Entrepreneur", "marketing", "sideproject"]
    for subreddit in subreddits[:5]:
        for query in queries[:3]:
            url = (
                f"https://www.reddit.com/r/{urllib.parse.quote(subreddit)}/search.json"
                f"?q={urllib.parse.quote(query)}&restrict_sr=1&sort=top&t=week&limit=3"
            )
            try:
                payload = _request_json(url, headers={"User-Agent": USER_AGENT})
            except (urllib.error.URLError, json.JSONDecodeError):
                continue
            children = payload.get("data", {}).get("children", [])
            for child in children:
                data = child.get("data", {})
                excerpt = str(data.get("selftext", ""))[:500]
                item = _build_item(
                    source="reddit",
                    item_type="post",
                    url=f"https://www.reddit.com{data.get('permalink', '')}",
                    title=str(data.get("title", "")),
                    author=str(data.get("author", "")),
                    published_at=str(data.get("created_utc", "")),
                    query=query,
                    text=f"{data.get('title', '')}. {excerpt}",
                    metadata={
                        "subreddit": subreddit,
                        "score": int(data.get("score", 0)),
                        "num_comments": int(data.get("num_comments", 0)),
                    },
                )
                item.engagement_signals = {
                    "score": int(data.get("score", 0)),
                    "comments": int(data.get("num_comments", 0)),
                }
                items.append(item)
    return items[: config.max_items_per_source]


def _collect_x(query_pack: QueryPack, config: CollectorConfig) -> list[ResearchItem]:
    provider_url = os.getenv("SOCIAL_MEDIA_X_ENDPOINT")
    provider_key = os.getenv("SOCIAL_MEDIA_X_API_KEY")
    if not provider_url:
        return []

    payload = {
        "keywords": config.x_keywords or query_pack.campaign_queries[:3],
        "accounts": config.x_accounts,
        "limit": config.max_items_per_source,
        "time_window_days": config.time_window_days,
    }
    request = urllib.request.Request(
        provider_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {provider_key}" if provider_key else "",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError):
        return []

    items: list[ResearchItem] = []
    for row in data.get("items", [])[: config.max_items_per_source]:
        text = str(row.get("text", ""))
        item = _build_item(
            source="x",
            item_type=str(row.get("type", "post")),
            url=str(row.get("url", "")),
            title=(text[:80] + "...") if len(text) > 80 else text,
            author=str(row.get("author", "")),
            published_at=str(row.get("published_at", "")),
            query=str(row.get("query", "")),
            text=text,
            metadata={"account": row.get("account", "")},
        )
        item.engagement_signals = {
            "likes": int(row.get("likes", 0)),
            "reposts": int(row.get("reposts", 0)),
            "replies": int(row.get("replies", 0)),
            "views": int(row.get("views", 0)),
        }
        items.append(item)
    return items


def _build_item(
    *,
    source: str,
    item_type: str,
    url: str,
    title: str,
    author: str,
    published_at: str,
    query: str,
    text: str,
    metadata: dict[str, Any],
) -> ResearchItem:
    normalized = text.lower()
    return ResearchItem(
        source=source,
        item_type=item_type,
        url=url,
        title=title or query,
        author=author,
        published_at=published_at,
        query=query,
        theme=_infer_theme(query, normalized),
        pain_points=_extract_pain_points(text),
        competitors=_extract_competitors(text),
        campaign_patterns=_extract_campaign_patterns(text),
        raw_excerpt=text[:600],
        platform=source,
        metadata=metadata,
    )


def _infer_theme(query: str, normalized: str) -> str:
    if "viral" in query or any(keyword in normalized for keyword in CAMPAIGN_KEYWORDS):
        return "viral_campaign"
    if "alternative" in query or "review" in query:
        return "competitor"
    return "pain_point"


def _extract_pain_points(text: str) -> list[str]:
    segments = re.split(r"[.!?\n]+", text)
    findings: list[str] = []
    for segment in segments:
        lowered = segment.lower().strip()
        if len(lowered) < 20:
            continue
        if any(keyword in lowered for keyword in PAIN_KEYWORDS):
            findings.append(_trim_phrase(segment))
    return findings[:3]


def _extract_competitors(text: str) -> list[str]:
    tokens = re.findall(r"\b[A-Z][A-Za-z0-9+\-]{2,}\b", text)
    ignored = {"Reddit", "Google", "Instagram", "TikTok", "Monday", "Friday"}
    return [token for token in tokens if token not in ignored][:5]


def _extract_campaign_patterns(text: str) -> list[str]:
    segments = re.split(r"[.!?\n]+", text)
    findings: list[str] = []
    for segment in segments:
        lowered = segment.lower()
        if any(keyword in lowered for keyword in CAMPAIGN_KEYWORDS):
            findings.append(_trim_phrase(segment))
    return findings[:3]


def _trim_phrase(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" -")


def _fallback_pain_points(items: list[ResearchItem]) -> list[str]:
    snippets = [item.raw_excerpt for item in items if item.raw_excerpt][:3]
    return [_trim_phrase(snippet) for snippet in snippets if snippet]


def _engagement_score(item: ResearchItem) -> int:
    score = 0
    for value in item.engagement_signals.values():
        if isinstance(value, (int, float)):
            score += int(value)
    return score


def _summarize_top_item(item: ResearchItem) -> str:
    return f"{item.source}: {item.title}"


def _node_text(node: ET.Element, tag: str) -> str:
    child = node.find(tag)
    return child.text.strip() if child is not None and child.text else ""


def _strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _dedupe_items(items: list[ResearchItem]) -> list[ResearchItem]:
    seen: set[str] = set()
    result: list[ResearchItem] = []
    for item in items:
        key = f"{item.source}|{item.url}"
        if key not in seen and item.url:
            seen.add(key)
            result.append(item)
    return result


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
