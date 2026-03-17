from pathlib import Path


def _write(output_dir: Path, filename: str, content: str) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return content.strip()


def _distribute_stages(batch_size: int) -> list[str]:
    stages = ["awareness", "awareness", "consideration", "proof", "conversion"]
    return [stages[index % len(stages)] for index in range(batch_size)]


def build_mock_research(inputs: dict[str, str]) -> str:
    return f"""
# Research Brief

## Audience Pains
- {inputs["target_user"]} want a system, not another motivational feed.
- The main problem is: {inputs["user_problem"]}.
- Users are likely skeptical of new apps unless the benefit feels immediate and concrete.

## Competitor Patterns
- Most apps in this space sell generic productivity instead of a narrow transformation.
- Faceless launch brands tend to perform best when they repeat one clear promise.
- Feature lists alone are weak; transformation and friction reduction are stronger angles.

## Hook Formulas
- "Why most productivity advice fails for people like you"
- "This is the habit system I wish existed earlier"
- "If your goals keep dying after 3 days, this is probably why"
- "We are building this app because current tools feel bloated"

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


def build_candidate_learnings(inputs: dict[str, str]) -> str:
    return f"""
# Candidate Learnings

- Problem-first hooks are stronger than feature-first hooks for {inputs["app_name"]}.
- Simple daily execution appears to be the clearest promise.
- The CTA should stay consistent across the week: {inputs["cta_target"]}.
- Build-in-public and proof content should appear before the hardest conversion push.
"""


def run_mock_pipeline(inputs: dict[str, str], latest_dir: Path, archive_dir: Path) -> None:
    research = build_mock_research(inputs)
    backlog = build_mock_ideas(inputs)
    drafts = build_mock_drafts(inputs)
    plan = build_mock_plan(inputs)
    candidate_learnings = build_candidate_learnings(inputs)
    summary = f"""
# Mock Run Summary

- research_brief.md generated
- content_backlog.md generated
- content_drafts.md generated
- weekly_app_launch_plan.md generated
- candidate_learnings.md generated

## Notes
- Research length: {len(research)}
- Backlog length: {len(backlog)}
- Drafts length: {len(drafts)}
- Plan length: {len(plan)}
- Candidate learnings length: {len(candidate_learnings)}
"""

    filenames_to_content = {
        "research_brief.md": research,
        "content_backlog.md": backlog,
        "content_drafts.md": drafts,
        "weekly_app_launch_plan.md": plan,
        "candidate_learnings.md": candidate_learnings,
        "mock_run_summary.md": summary,
    }

    for filename, content in filenames_to_content.items():
        _write(latest_dir, filename, content)
        _write(archive_dir, filename, content)
