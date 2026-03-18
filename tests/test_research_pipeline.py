import tempfile
import unittest
from pathlib import Path

from social_media_planner.models import CollectorConfig, QueryPack, ResearchCorpus, ResearchItem
from social_media_planner.research_pipeline import (
    analyze_research,
    build_collector_config,
    build_query_pack,
)


class ResearchPipelineTest(unittest.TestCase):
    def test_build_collector_config_uses_runtime_inputs(self) -> None:
        config = build_collector_config(
            {
                "seed_topics": ["habit systems"],
                "competitor_names": ["Notion"],
                "competitor_domains": ["notion.so"],
                "subreddits": ["productivity"],
                "x_keywords": ["build in public"],
                "x_accounts": ["@notionhq"],
                "time_window_days": 14,
                "max_items_per_source": 12,
            }
        )

        self.assertEqual(["habit systems"], config.seed_topics)
        self.assertEqual(["Notion"], config.competitor_names)
        self.assertEqual(14, config.time_window_days)
        self.assertEqual(12, config.max_items_per_source)

    def test_build_query_pack_includes_pain_competitor_and_campaign_queries(self) -> None:
        query_pack = build_query_pack(
            {
                "app_name": "SignalSprout",
                "target_user": "builders",
                "user_problem": "staying consistent",
                "dream_outcome": "daily progress",
            },
            CollectorConfig(
                seed_topics=["habit systems"],
                competitor_names=["Notion"],
                x_keywords=["build in public"],
            ),
        )

        self.assertTrue(query_pack.pain_point_queries)
        self.assertIn("SignalSprout alternatives", query_pack.competitor_queries)
        self.assertTrue(any("viral" in query for query in query_pack.campaign_queries))

    def test_analyze_research_writes_report_artifacts(self) -> None:
        corpus = ResearchCorpus(
            query_pack=QueryPack(
                pain_point_queries=["pain"],
                competitor_queries=["alternatives"],
                campaign_queries=["viral"],
            ),
            items=[
                ResearchItem(
                    source="reddit",
                    item_type="post",
                    url="https://reddit.com/example",
                    title="Too many steps to stay consistent",
                    author="poster",
                    published_at="2026-03-17",
                    query="pain",
                    theme="pain_point",
                    pain_points=["too many steps to stay consistent"],
                    competitors=["Notion"],
                    campaign_patterns=["problem-first hooks spark replies"],
                    engagement_signals={"score": 120, "comments": 19},
                    raw_excerpt="People are frustrated because staying consistent takes too many steps.",
                    platform="reddit",
                )
            ],
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            report = analyze_research(
                corpus,
                inputs={"app_name": "SignalSprout"},
                output_dir=Path(tmp_dir),
            )

            self.assertIn("too many steps", " ".join(report.pain_point_clusters))
            self.assertIn("Notion", report.competitor_watchlist)
            self.assertTrue((Path(tmp_dir) / "research_report.json").exists())
            self.assertTrue((Path(tmp_dir) / "research_pack.md").exists())
