# SocialMediaPlanner Crew

This project is now a faceless app-launch content workflow for TikTok and Instagram.
It supports two modes:

- `mock`: no paid API calls, deterministic outputs for workflow testing
- `live`: real CrewAI agents using your configured LLM provider

The current default in `.env.example` is `mock` mode so you can refine the system
before spending money.

## Current Scope

The system can currently:

1. read a manual app launch research packet
2. generate a research brief
3. generate launch-focused social content ideas
4. generate faceless social drafts
5. generate a weekly app launch content plan
6. generate candidate learnings for human review

The system does not yet:

- scrape social platforms automatically
- score ideas using real performance data
- post automatically
- update durable knowledge by itself without review

## Files You Will Edit

- `knowledge/app_launch_research_packet.md`
- `knowledge/learned_patterns.md`
- `knowledge/experiment_log.md`
- `src/social_media_planner/config/agents.yaml`
- `src/social_media_planner/config/tasks.yaml`
- `src/social_media_planner/main.py`

## Modes

### Mock Mode

Mock mode writes these files without calling any paid model:

- `output/research_brief.md`
- `output/content_ideas.md`
- `output/content_drafts.md`
- `output/weekly_app_launch_plan.md`
- `output/candidate_learnings.md`
- `output/mock_run_summary.md`

Use this mode to validate structure, prompts, content flow, and file outputs.

### Live Mode

Live mode runs the real 4-agent CrewAI workflow and writes:

- `output/weekly_app_launch_plan.md`

It requires a valid API key and provider quota.

## Setup

Your local `.env` should look like this:

```bash
RUN_MODE=mock
OPENAI_API_KEY=sk-...
SOCIAL_MEDIA_RESEARCH_PACKET=knowledge/app_launch_research_packet.md
```

Recommended workflow:

1. keep `RUN_MODE=mock` while refining the system
2. update the research packet
3. run the workflow
4. review `candidate_learnings.md`
5. copy only reviewed lessons into `knowledge/learned_patterns.md`
6. switch to `RUN_MODE=live` when you want real model output

## Running

From the project root:

```bash
python -m social_media_planner.main
```

## Local Test

```bash
python -m unittest discover -s tests
```
