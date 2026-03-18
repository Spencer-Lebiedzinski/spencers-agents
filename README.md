# SocialMediaPlanner Crew

This project is now a multi-source social research and content-planning workflow for app launches.
It can collect signals, analyze them, turn them into content, and produce companion media briefs
plus static image assets.

It supports two runtime modes:

- `mock`: deterministic outputs for workflow and artifact testing
- `live`: runs the collection pipeline, CrewAI analysis/planning crew, and image generation

## Current Scope

The system can currently:

1. collect and normalize source signals from news, Reddit, and X
2. analyze pain points, competitor mentions, and viral campaign patterns
3. generate a research pack for content planning
4. generate a larger launch-focused content backlog plus draft pack
5. generate a weekly app launch content plan, media pack, and image manifest
6. write archival mock outputs and timestamped live runs

The system is prepared, but not yet automated, for:

- TikTok source collection
- Instagram source collection

## Important Files

- `src/social_media_planner/main.py`
- `src/social_media_planner/research_pipeline.py`
- `src/social_media_planner/media_pipeline.py`
- `src/social_media_planner/config/agents.yaml`
- `src/social_media_planner/config/tasks.yaml`
- `knowledge/app_launch_research_packet.md`

## Output Artifacts

Mock mode writes the latest copy to `output/latest/` and archives the same run to
`output/archive/<timestamp>/`.

Live mode writes to `output/runs/<timestamp>/`.

Primary artifacts:

- `research_pack.md`
- `research_brief.md`
- `raw_source_dump.json`
- `normalized_source_dataset.json`
- `research_report.json`
- `content_backlog.md`
- `content_ideas.md`
- `content_drafts.md`
- `content_pack.md`
- `weekly_app_launch_plan.md`
- `media_pack.md`
- `generated_image_manifest.json`
- `images/*.png`

Mock mode also writes:

- `candidate_learnings.md`
- `mock_run_summary.md`

## Environment

Minimum local config:

```bash
RUN_MODE=mock
PIPELINE_MODE=collect_and_plan
OPENAI_API_KEY=sk-...
SOCIAL_MEDIA_RESEARCH_PACKET=knowledge/app_launch_research_packet.md
BATCH_SIZE=25
DRAFT_BATCH_SIZE=12
```

Optional collector configuration:

```bash
SOCIAL_MEDIA_SEED_TOPICS=goal systems,habit consistency,productivity app frustration
SOCIAL_MEDIA_COMPETITOR_NAMES=Notion,Todoist,Habitica,Motion
SOCIAL_MEDIA_COMPETITOR_DOMAINS=notion.so,todoist.com,habitica.com,usemotion.com
SOCIAL_MEDIA_SUBREDDITS=productivity,selfimprovement,sideproject,Entrepreneur
SOCIAL_MEDIA_X_KEYWORDS=build in public,habit app,productivity system
SOCIAL_MEDIA_X_ACCOUNTS=
SOCIAL_MEDIA_TIME_WINDOW_DAYS=7
SOCIAL_MEDIA_MAX_ITEMS_PER_SOURCE=10
SOCIAL_MEDIA_X_ENDPOINT=
SOCIAL_MEDIA_X_API_KEY=
SOCIAL_MEDIA_EXISTING_RESEARCH_DIR=
```

`PIPELINE_MODE` supports:

- `collect_and_plan`
- `plan_from_existing_research`

## Running

From the project root:

```bash
python -m social_media_planner.main
```

Mock workflow for cheap iteration:

```bash
RUN_MODE=mock python -m social_media_planner.main
```

## Tests

```bash
python -m unittest discover -s tests
```
