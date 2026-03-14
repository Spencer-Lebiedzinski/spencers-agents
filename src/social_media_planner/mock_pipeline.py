from pathlib import Path


def _write(output_dir: Path, filename: str, content: str) -> str:
    path = output_dir / filename
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return content.strip()


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
    return f"""
# Content Ideas

1. funnel_stage: awareness
title: Why Motivation Fails After 3 Days
platform: TikTok
hook: Most people do not have a motivation problem. They have a system problem.
angle: Explain why goals die when the daily workflow is too vague.
audience_takeaway: Clear systems beat vague ambition.
cta_target: {cta}
asset_type: b-roll + text

2. funnel_stage: awareness
title: Stop Using Bloated Productivity Tools
platform: Instagram
hook: Most productivity apps make simple things feel heavy.
angle: Contrast complexity with a simpler app promise.
audience_takeaway: Simplicity increases consistency.
cta_target: {cta}
asset_type: carousel

3. funnel_stage: proof
title: What {inputs["app_name"]} Actually Helps You Do
platform: TikTok
hook: This is how we are turning goals into daily actions.
angle: Introduce the app outcome instead of a feature dump.
audience_takeaway: The product is built around daily execution.
cta_target: {cta}
asset_type: faceless explainer

4. funnel_stage: consideration
title: Build In Public Update
platform: Instagram
hook: We are building the app we wish existed for consistency.
angle: Share progress and decisions behind the product.
audience_takeaway: The brand is thoughtful and credible.
cta_target: {cta}
asset_type: reel

5. funnel_stage: conversion
title: Join Before Launch
platform: TikTok
hook: If you want first access, now is the time.
angle: Push urgency around prelaunch access.
audience_takeaway: Early users get the earliest value.
cta_target: {cta}
asset_type: faceless CTA reel
"""


def build_mock_drafts(inputs: dict[str, str]) -> str:
    cta = inputs["cta_target"]
    return f"""
# Content Drafts

## Draft 1
platform: TikTok
hook: Most people do not have a motivation problem. They have a system problem.
short_script: You keep setting goals, getting inspired, and then falling off because your plan is too vague. We are building {inputs["app_name"]} to make daily action easier.
on_screen_text: Goals fail when the system is unclear
cta: {cta}

## Draft 2
platform: Instagram
caption: Most productivity apps ask you to manage too much. We think consistency should feel lighter, not heavier.
reel_or_carousel_angle: carousel showing bloated tools vs simple daily system
cta: {cta}

## Draft 3
platform: TikTok
hook: This is how we are turning goals into daily actions.
short_script: {inputs["app_name"]} is designed for people who want simple daily systems, not another overwhelming dashboard.
on_screen_text: daily actions > vague goals
cta: {cta}

## Draft 4
platform: Instagram
caption: Build update: we are keeping the product focused on one thing, helping people stay consistent.
reel_or_carousel_angle: reel with product mockups and value statements
cta: {cta}

## Draft 5
platform: TikTok
hook: If you want first access, now is the time.
short_script: We are getting closer to launch, and early users will shape what comes next. If the problem sounds familiar, join early.
on_screen_text: early access opens first
cta: {cta}
"""


def build_mock_plan(inputs: dict[str, str]) -> str:
    cta = inputs["cta_target"]
    return f"""
# Weekly App Launch Plan

| Day | Platform | Funnel Stage | Content Pillar | Post Concept | Asset Type | Production Note | Publish Note | CTA Target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Monday | TikTok | awareness | problem awareness | Why motivation fails after 3 days | b-roll + text | use high-contrast captions and short cuts | publish in morning search window | {cta} |
| Tuesday | Instagram | awareness | why current solutions fail | stop using bloated productivity tools | carousel | create 5 slides with one claim each | post as educational carousel | {cta} |
| Wednesday | TikTok | proof | feature reveal | what the app actually helps you do | faceless explainer | use mockup overlays and before/after framing | pin in profile if strong | {cta} |
| Thursday | Instagram | consideration | build in public | product update and design decision | reel | use screen recording and motion text | emphasize transparency | {cta} |
| Friday | TikTok | conversion | waitlist conversion | join before launch | faceless CTA reel | keep under 20 seconds and direct | use strongest CTA of the week | {cta} |
"""


def build_candidate_learnings(inputs: dict[str, str]) -> str:
    return f"""
# Candidate Learnings

- Problem-first hooks are stronger than feature-first hooks for {inputs["app_name"]}.
- Simple daily execution appears to be the clearest promise.
- The CTA should stay consistent across the week: {inputs["cta_target"]}.
- Build-in-public and proof content should appear before the hardest conversion push.
"""


def run_mock_pipeline(inputs: dict[str, str], output_dir: Path) -> None:
    research = _write(output_dir, "research_brief.md", build_mock_research(inputs))
    ideas = _write(output_dir, "content_ideas.md", build_mock_ideas(inputs))
    drafts = _write(output_dir, "content_drafts.md", build_mock_drafts(inputs))
    plan = _write(output_dir, "weekly_app_launch_plan.md", build_mock_plan(inputs))
    candidate_learnings = _write(
        output_dir,
        "candidate_learnings.md",
        build_candidate_learnings(inputs),
    )

    _write(
        output_dir,
        "mock_run_summary.md",
        f"""
# Mock Run Summary

- research_brief.md generated
- content_ideas.md generated
- content_drafts.md generated
- weekly_app_launch_plan.md generated
- candidate_learnings.md generated

## Notes
- Research length: {len(research)}
- Ideas length: {len(ideas)}
- Drafts length: {len(drafts)}
- Plan length: {len(plan)}
- Candidate learnings length: {len(candidate_learnings)}
""",
    )
