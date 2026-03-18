import base64
import json

from pathlib import Path

from social_media_planner.media_pipeline import build_image_briefs
from social_media_planner.models import ResearchItem, ResearchReport

PLACEHOLDER_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
    "/x8AAusB9Y5fL3QAAAAASUVORK5CYII="
)


def _write(output_dir: Path, filename: str, content: str) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return content.strip()


def _write_json(output_dir: Path, filename: str, payload: object) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / filename).write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def _write_binary(output_dir: Path, filename: str, content: bytes) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / filename).write_bytes(content)


def _distribute_stages(batch_size: int) -> list[str]:
    stages = ["awareness", "awareness", "consideration", "proof", "conversion"]
    return [stages[index % len(stages)] for index in range(batch_size)]


def build_mock_research(inputs: dict[str, str]) -> str:
    return f"""
# Research Brief

## Source-Backed Audience Pains
- {inputs["target_user"]} want a system, not another motivational feed.
- The main problem is: {inputs["user_problem"]}.
- Users are likely skeptical of new apps unless the benefit feels immediate and concrete.

## Competitor Positioning Patterns
- Most apps in this space sell generic productivity instead of a narrow transformation.
- Faceless launch brands tend to perform best when they repeat one clear promise.
- Feature lists alone are weak; transformation and friction reduction are stronger angles.

## Viral Campaign Lessons
- Problem-first hooks travel better than feature-dump posts.
- Founder-led explainers and screenshot-led reveals create believable momentum.
- Short launch threads and reels with one promise outperform broad positioning.

## Objections
- "I already have notes and reminders, why do I need this?"
- "This sounds like another habit app."
- "Will it actually help me stay consistent?"

## Top 5 Launch Opportunities
1. Show the cost of inconsistent systems.
2. Frame the app as simple and focused.
3. Reveal product features through user outcomes.
4. Build trust with transparent build-in-public updates.
5. Convert warm viewers with direct waitlist CTAs.
"""


def build_mock_research_report(inputs: dict[str, str]) -> ResearchReport:
    top_items = [
        ResearchItem(
            source="news",
            item_type="article",
            url="https://example.com/news/pain-points",
            title="People want simpler planning systems",
            author="Example News",
            published_at="2026-03-17",
            query="productivity app pain points",
            theme="pain_point",
            pain_points=["people are overwhelmed by bloated planning apps"],
            competitors=["Notion", "Todoist"],
            campaign_patterns=["founder-led explainers outperform vague feature drops"],
            raw_excerpt="People are overwhelmed by bloated planning apps and want simpler systems.",
            platform="news",
        ),
        ResearchItem(
            source="reddit",
            item_type="post",
            url="https://reddit.com/example",
            title="How do you stay consistent without overplanning?",
            author="founder_demo",
            published_at="2026-03-16",
            query="habit tracking frustration",
            theme="pain_point",
            pain_points=["users struggle to stay consistent when tools feel heavy"],
            competitors=["Habitica"],
            campaign_patterns=["problem-first posts get more discussion than feature-first posts"],
            engagement_signals={"score": 214, "comments": 38},
            raw_excerpt="Users struggle to stay consistent when productivity tools feel heavy.",
            platform="reddit",
        ),
        ResearchItem(
            source="x",
            item_type="post",
            url="https://x.com/example/status/1",
            title="Launch thread on simplifying habits",
            author="launchbuilder",
            published_at="2026-03-15",
            query="viral launch thread",
            theme="viral_campaign",
            pain_points=["users lose momentum after a few days"],
            competitors=["Motion"],
            campaign_patterns=["concise launch threads with screenshots and one promise travel well"],
            engagement_signals={"likes": 540, "reposts": 92, "replies": 27},
            raw_excerpt="Concise launch threads with screenshots and one promise travel well.",
            platform="x",
        ),
    ]
    return ResearchReport(
        summary=(
            f"Collected deterministic mock signals for {inputs['app_name']} across news, Reddit, "
            "and X. Pain points cluster around heavy tools, inconsistency, and vague goal-setting."
        ),
        pain_point_clusters=[
            "productivity tools feel bloated",
            "people lose momentum after a few days",
            "users want simpler daily systems",
        ],
        competitor_watchlist=["Notion", "Todoist", "Habitica", "Motion"],
        viral_campaign_examples=[
            "founder-led explainers with screenshots outperform generic hype",
            "problem-first hooks drive stronger discussion than feature dumps",
            "short launch threads with one promise and proof travel well",
        ],
        source_digest=[
            "news: 1 collected item",
            "reddit: 1 collected item",
            "x: 1 collected item",
        ],
        top_items=top_items,
    )


def build_mock_ideas(inputs: dict[str, str]) -> str:
    cta = inputs["cta_target"]
    batch_size = int(inputs["batch_size"])
    stage_titles = {
        "awareness": "Why Your System Keeps Breaking",
        "consideration": "What A Better Tool Should Actually Do",
        "proof": f"What {inputs['app_name']} Actually Helps You Do",
        "conversion": "Join Before Launch",
    }
    stage_assets = {
        "awareness": "b-roll + text",
        "consideration": "carousel",
        "proof": "faceless explainer",
        "conversion": "faceless CTA reel",
    }
    stage_hooks = {
        "awareness": "Most people do not have a motivation problem. They have a system problem.",
        "consideration": "Most productivity tools make simple things feel heavy.",
        "proof": "This is how we are turning goals into daily actions.",
        "conversion": "If you want first access, now is the time.",
    }
    stage_angles = {
        "awareness": "Explain why vague daily workflows kill consistency.",
        "consideration": "Contrast bloated tools with a narrow app promise.",
        "proof": "Reveal the product through outcomes instead of a feature dump.",
        "conversion": "Push urgency around waitlist access and early use.",
    }
    stage_takeaways = {
        "awareness": "Clear systems beat vague ambition.",
        "consideration": "Simplicity is a competitive advantage.",
        "proof": "The product is designed around daily execution.",
        "conversion": "Early users get the earliest value.",
    }

    lines = ["# Content Backlog", ""]
    for index, stage in enumerate(_distribute_stages(batch_size), start=1):
        platform = "TikTok" if index % 2 else "Instagram"
        lines.extend(
            [
                f"{index}. funnel_stage: {stage}",
                f"title: {stage_titles[stage]} #{index}",
                f"platform: {platform}",
                f"hook: {stage_hooks[stage]}",
                f"angle: {stage_angles[stage]}",
                f"audience_takeaway: {stage_takeaways[stage]}",
                f"cta_target: {cta}",
                f"asset_type: {stage_assets[stage]}",
                "",
            ]
        )
    return "\n".join(lines)


def build_mock_drafts(inputs: dict[str, str]) -> str:
    cta = inputs["cta_target"]
    draft_batch_size = int(inputs["draft_batch_size"])
    lines = ["# Content Draft Pack", ""]

    for index, stage in enumerate(_distribute_stages(draft_batch_size), start=1):
        platform = "TikTok" if index % 2 else "Instagram"
        lines.append(f"## Draft {index}")
        lines.append(f"platform: {platform}")
        lines.append(f"funnel_stage: {stage}")
        if platform == "TikTok":
            lines.extend(
                [
                    "hook: Most people do not have a motivation problem. They have a system problem.",
                    (
                        f"short_script: {inputs['app_name']} is for people who want lighter daily systems "
                        "and more consistent action without bloated productivity overhead."
                    ),
                    "on_screen_text: clearer systems create better follow-through",
                    f"cta: {cta}",
                ]
            )
        else:
            lines.extend(
                [
                    (
                        "caption: Most productivity tools overwhelm people before they help them. "
                        "We are building a cleaner path to consistency."
                    ),
                    "reel_or_carousel_angle: simple before-and-after frame around the problem and outcome",
                    f"cta: {cta}",
                ]
            )
        lines.append("")

    return "\n".join(lines)


def build_mock_plan(inputs: dict[str, str]) -> str:
    cta = inputs["cta_target"]
    return f"""
# Weekly App Launch Plan

| Day | Platform | Funnel Stage | Content Pillar | Post Concept | Asset Type | Production Note | Publish Note | CTA Target | Why It Made The Cut |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Monday | TikTok | awareness | problem awareness | Why motivation fails after 3 days | b-roll + text | use high-contrast captions and short cuts | publish in morning search window | {cta} | strong problem-first opener |
| Tuesday | Instagram | awareness | why current solutions fail | stop using bloated productivity tools | carousel | create 5 slides with one claim each | post as educational carousel | {cta} | clear comparison angle |
| Wednesday | TikTok | proof | feature reveal | what the app actually helps you do | faceless explainer | use mockup overlays and before/after framing | pin in profile if strong | {cta} | strongest proof slot |
| Thursday | Instagram | consideration | build in public | product update and design decision | reel | use screen recording and motion text | emphasize transparency | {cta} | trust-building midweek piece |
| Friday | TikTok | conversion | waitlist conversion | join before launch | faceless CTA reel | keep under 20 seconds and direct | use strongest CTA of the week | {cta} | best end-of-week conversion push |
"""


def build_mock_media_pack(inputs: dict[str, str]) -> str:
    return f"""
## Reel Support Assets

- title: System Problem Reel
  platform: TikTok
  asset_type: reel storyboard
  visual_goal: make the pain point feel immediate and relatable
  copy_text_overlay: Motivation is not the problem. The system is.
  production_notes: quick cuts of notes, calendar clutter, and simple app screens
  image_prompt: bold cover frame for a faceless consistency app reel

## Carousel and Static Post Design Briefs

- title: Bloated Tools vs Simple System
  platform: Instagram
  asset_type: carousel
  visual_goal: compare heavy workflows against a lighter product promise
  copy_text_overlay: stop managing your goals like a second job
  production_notes: five slides, one claim per slide, product mockup on final slide
  image_prompt: premium startup carousel cover showing complexity vs clarity

## Cover-Frame Concepts

- title: Why Goals Die After 3 Days
  platform: Instagram
  asset_type: reel cover
  visual_goal: create a strong stop-scroll hook
  copy_text_overlay: Why Goals Die After 3 Days
  production_notes: high contrast text, subtle product UI, clean focal point
  image_prompt: dramatic but clean reel cover for a productivity app launch
"""


def build_candidate_learnings(inputs: dict[str, str]) -> str:
    return f"""
# Candidate Learnings

- Problem-first hooks are stronger than feature-first hooks for {inputs["app_name"]}.
- Simple daily execution appears to be the clearest promise.
- The CTA should stay consistent across the week: {inputs["cta_target"]}.
- Build-in-public and proof content should appear before the hardest conversion push.
"""


def _write_artifacts(output_dir: Path, inputs: dict[str, str], report: ResearchReport) -> None:
    research = _write(output_dir, "research_pack.md", build_mock_research(inputs))
    _write(output_dir, "research_brief.md", research)
    backlog = _write(output_dir, "content_backlog.md", build_mock_ideas(inputs))
    _write(output_dir, "content_ideas.md", backlog)
    drafts = _write(output_dir, "content_drafts.md", build_mock_drafts(inputs))
    plan = _write(output_dir, "weekly_app_launch_plan.md", build_mock_plan(inputs))
    media_pack = _write(
        output_dir,
        "media_pack.md",
        "# Media Pack\n\n" + build_mock_media_pack(inputs),
    )
    candidate_learnings = _write(
        output_dir,
        "candidate_learnings.md",
        build_candidate_learnings(inputs),
    )
    _write_json(
        output_dir,
        "raw_source_dump.json",
        {
            "query_pack": {
                "pain_point_queries": ["productivity app pain points"],
                "competitor_queries": ["SignalSprout alternatives"],
                "campaign_queries": ["viral app launch campaign"],
            },
            "collectors": {
                "news": [item.model_dump() for item in report.top_items if item.source == "news"],
                "reddit": [item.model_dump() for item in report.top_items if item.source == "reddit"],
                "x": [item.model_dump() for item in report.top_items if item.source == "x"],
            },
        },
    )
    _write_json(
        output_dir,
        "normalized_source_dataset.json",
        [item.model_dump() for item in report.top_items],
    )
    _write_json(output_dir, "research_report.json", report.model_dump())
    content_pack = _write(
        output_dir,
        "content_pack.md",
        "\n".join(
            [
                "# Content Pack",
                "",
                "## Research Brief",
                research,
                "",
                "## Content Ideas",
                backlog,
                "",
                "## Drafts",
                drafts,
                "",
                "## Weekly Plan",
                plan,
            ]
        ),
    )

    briefs = build_image_briefs(inputs["app_name"], media_pack, inputs["platforms"])
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for brief in briefs:
        _write_binary(output_dir, brief.output_path, base64.b64decode(PLACEHOLDER_PNG))
        manifest.append(
            brief.model_copy(update={"status": "mock_image", "revised_prompt": brief.prompt}).model_dump()
        )
    _write_json(output_dir, "generated_image_manifest.json", manifest)

    _write(
        output_dir,
        "mock_run_summary.md",
        f"""
# Mock Run Summary

- research_pack.md generated
- research_brief.md generated
- raw_source_dump.json generated
- normalized_source_dataset.json generated
- research_report.json generated
- content_backlog.md generated
- content_ideas.md generated
- content_drafts.md generated
- content_pack.md generated
- weekly_app_launch_plan.md generated
- media_pack.md generated
- generated_image_manifest.json generated
- candidate_learnings.md generated

## Notes
- Research length: {len(research)}
- Backlog length: {len(backlog)}
- Drafts length: {len(drafts)}
- Plan length: {len(plan)}
- Content pack length: {len(content_pack)}
- Candidate learnings length: {len(candidate_learnings)}
""",
    )


def run_mock_pipeline(inputs: dict[str, str], latest_dir: Path, archive_dir: Path) -> None:
    report = build_mock_research_report(inputs)
    _write_artifacts(latest_dir, inputs, report)
    _write_artifacts(archive_dir, inputs, report)
