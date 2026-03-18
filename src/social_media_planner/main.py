#!/usr/bin/env python
import json
import os
import sys
import warnings

from datetime import datetime
from pathlib import Path
from typing import Any

from social_media_planner.crew import SocialMediaPlanner
from social_media_planner.media_pipeline import (
    build_image_briefs,
    generate_images,
    write_content_outputs,
)
from social_media_planner.models import ResearchReport
from social_media_planner.mock_pipeline import run_mock_pipeline
from social_media_planner.research_pipeline import (
    analyze_research,
    build_research_inputs,
    collect_research,
    load_research_report,
    parse_csv_env,
)

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESEARCH_PACKET = PROJECT_ROOT / "knowledge" / "app_launch_research_packet.md"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"
SUPPORTED_RUN_MODES = {"mock", "live"}
SUPPORTED_PIPELINE_MODES = {"collect_and_plan", "plan_from_existing_research"}
TRIGGER_INPUT_KEYS = {
    "app_name",
    "app_one_liner",
    "target_user",
    "user_problem",
    "dream_outcome",
    "launch_stage",
    "core_features",
    "proof_points",
    "platforms",
    "cta_target",
    "content_pillars",
    "brand_voice",
    "posts_per_week",
    "batch_size",
    "draft_batch_size",
    "current_year",
    "research_packet",
    "seed_topics",
    "competitor_names",
    "competitor_domains",
    "subreddits",
    "x_keywords",
    "x_accounts",
    "time_window_days",
    "max_items_per_source",
}


def get_run_mode() -> str:
    """Return the configured runtime mode."""
    mode = os.getenv("RUN_MODE", "live").strip().lower()
    if mode not in SUPPORTED_RUN_MODES:
        supported_modes = ", ".join(sorted(SUPPORTED_RUN_MODES))
        raise ValueError(
            f"Unsupported RUN_MODE '{mode}'. Expected one of: {supported_modes}."
        )
    return mode


def get_pipeline_mode() -> str:
    """Return the configured pipeline mode."""
    mode = os.getenv("PIPELINE_MODE", "collect_and_plan").strip().lower()
    if mode not in SUPPORTED_PIPELINE_MODES:
        supported_modes = ", ".join(sorted(SUPPORTED_PIPELINE_MODES))
        raise ValueError(
            f"Unsupported PIPELINE_MODE '{mode}'. Expected one of: {supported_modes}."
        )
    return mode


def load_research_packet() -> str:
    """Load the weekly research packet from disk for local fallback usage."""
    packet_path = os.getenv("SOCIAL_MEDIA_RESEARCH_PACKET")
    path = Path(packet_path) if packet_path else DEFAULT_RESEARCH_PACKET
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.exists():
        raise FileNotFoundError(f"Research packet not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def build_inputs() -> dict[str, Any]:
    """Build the default faceless app-launch inputs for local testing."""
    return {
        "app_name": "SignalSprout",
        "app_one_liner": (
            "A lightweight app that helps ambitious people turn goals into daily systems"
        ),
        "target_user": (
            "students, young professionals, and self-improvement-focused builders who "
            "want structure without using bloated productivity tools"
        ),
        "user_problem": (
            "they set goals and consume motivation content, but they struggle to turn "
            "good intentions into repeatable daily action"
        ),
        "dream_outcome": (
            "they feel in control of their habits, see progress daily, and stay consistent"
        ),
        "launch_stage": "prelaunch waitlist growth",
        "core_features": (
            "simple daily planning, streak-friendly habit systems, lightweight progress "
            "tracking, and prompts that turn goals into daily actions"
        ),
        "proof_points": (
            "clear positioning, practical use cases, and transparent build-in-public style updates"
        ),
        "platforms": "TikTok and Instagram",
        "cta_target": "join the waitlist and pre-download when available",
        "content_pillars": (
            "problem awareness, why current solutions fail, build in public, feature reveals, "
            "user outcomes, social proof, and waitlist conversion"
        ),
        "brand_voice": "clear, sharp, practical, slightly aspirational, and direct",
        "posts_per_week": "5",
        "batch_size": os.getenv("BATCH_SIZE", "25"),
        "draft_batch_size": os.getenv("DRAFT_BATCH_SIZE", "12"),
        "current_year": str(datetime.now().year),
        "research_packet": load_research_packet(),
        "seed_topics": parse_csv_env(os.getenv("SOCIAL_MEDIA_SEED_TOPICS"))
        or [
            "goal systems",
            "habit consistency",
            "productivity app frustration",
        ],
        "competitor_names": parse_csv_env(os.getenv("SOCIAL_MEDIA_COMPETITOR_NAMES"))
        or ["Notion", "Todoist", "Habitica", "Motion"],
        "competitor_domains": parse_csv_env(os.getenv("SOCIAL_MEDIA_COMPETITOR_DOMAINS"))
        or ["notion.so", "todoist.com", "habitica.com", "usemotion.com"],
        "subreddits": parse_csv_env(os.getenv("SOCIAL_MEDIA_SUBREDDITS"))
        or ["productivity", "selfimprovement", "sideproject", "Entrepreneur"],
        "x_keywords": parse_csv_env(os.getenv("SOCIAL_MEDIA_X_KEYWORDS"))
        or ["build in public", "habit app", "productivity system"],
        "x_accounts": parse_csv_env(os.getenv("SOCIAL_MEDIA_X_ACCOUNTS")),
        "time_window_days": int(os.getenv("SOCIAL_MEDIA_TIME_WINDOW_DAYS", "7")),
        "max_items_per_source": int(os.getenv("SOCIAL_MEDIA_MAX_ITEMS_PER_SOURCE", "10")),
    }


def build_output_paths(base_output_dir: Path) -> tuple[Path, Path]:
    """Return the latest and archive output paths for the current mock run."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    latest_dir = base_output_dir / "latest"
    archive_dir = base_output_dir / "archive" / timestamp
    return latest_dir, archive_dir


def _require_cli_args(command_name: str, expected_count: int) -> list[str]:
    """Return positional CLI args or raise a clear usage error."""
    provided_args = sys.argv[1:]
    if len(provided_args) < expected_count:
        raise ValueError(
            f"{command_name} requires {expected_count} argument(s); got {len(provided_args)}."
        )
    return provided_args


def _parse_trigger_payload() -> dict[str, Any]:
    """Parse the JSON trigger payload from the CLI."""
    raw_payload = _require_cli_args("run_with_trigger", 1)[0]
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON payload provided as argument.") from exc
    if not isinstance(payload, dict):
        raise ValueError("Trigger payload must decode to a JSON object.")
    return payload


def build_trigger_inputs(trigger_payload: dict[str, Any]) -> dict[str, Any]:
    """Merge trigger payload into the default inputs for partial overrides."""
    inputs: dict[str, Any] = build_inputs()
    inputs["crewai_trigger_payload"] = trigger_payload
    for key in TRIGGER_INPUT_KEYS:
        if key in trigger_payload:
            inputs[key] = trigger_payload[key]
    return inputs


def build_run_output_dir(base_output_dir: Path = DEFAULT_OUTPUT_DIR) -> Path:
    """Create a timestamped output directory for the current live batch run."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = base_output_dir / "runs" / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _build_live_inputs(inputs: dict[str, Any], report: ResearchReport) -> dict[str, Any]:
    merged = dict(inputs)
    merged.update(build_research_inputs(report))
    return merged


def _resolve_existing_research_dir(output_dir: Path) -> Path:
    configured = os.getenv("SOCIAL_MEDIA_EXISTING_RESEARCH_DIR")
    if configured:
        candidate = Path(configured)
        return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate
    return output_dir


def _run_collection_stage(inputs: dict[str, Any], output_dir: Path) -> ResearchReport:
    corpus = collect_research(inputs, output_dir=output_dir)
    return analyze_research(corpus, inputs=inputs, output_dir=output_dir)


def _load_or_collect_research(inputs: dict[str, Any], output_dir: Path) -> ResearchReport:
    if get_pipeline_mode() == "plan_from_existing_research":
        return load_research_report(_resolve_existing_research_dir(output_dir))

    try:
        return _run_collection_stage(inputs, output_dir=output_dir)
    except Exception:
        if not os.getenv("SOCIAL_MEDIA_EXISTING_RESEARCH_DIR"):
            raise
        return load_research_report(_resolve_existing_research_dir(output_dir))


def _extract_task_outputs(result: Any) -> dict[str, str]:
    outputs = list(getattr(result, "tasks_output", []))
    raw_values = [str(getattr(task_output, "raw", "")) for task_output in outputs]
    while len(raw_values) < 5:
        raw_values.append("")
    return {
        "research_brief": raw_values[0],
        "content_ideas": raw_values[1],
        "content_drafts": raw_values[2],
        "weekly_plan": raw_values[3],
        "media_pack": raw_values[4],
    }


def _write_run_summary(
    output_dir: Path,
    report: ResearchReport,
    generated_images: list[Any],
) -> None:
    summary = "\n".join(
        [
            "# Run Summary",
            "",
            f"- Pipeline mode: {get_pipeline_mode()}",
            f"- Generated at: {datetime.now().isoformat()}",
            f"- Research summary: {report.summary}",
            f"- Image assets generated: {len(generated_images)}",
            "",
        ]
    )
    (output_dir / "run_summary.md").write_text(summary, encoding="utf-8")


def _run_live_pipeline(inputs: dict[str, Any], output_dir: Path) -> Any:
    report = _load_or_collect_research(inputs, output_dir=output_dir)
    result = SocialMediaPlanner().crew().kickoff(inputs=_build_live_inputs(inputs, report))
    task_outputs = _extract_task_outputs(result)
    _, media_pack = write_content_outputs(
        output_dir=output_dir,
        research_brief=task_outputs["research_brief"],
        idea_output=task_outputs["content_ideas"],
        writing_output=task_outputs["content_drafts"],
        planning_output=task_outputs["weekly_plan"],
        media_output=task_outputs["media_pack"],
    )
    generated_images = generate_images(
        build_image_briefs(inputs["app_name"], media_pack, str(inputs["platforms"])),
        output_dir=output_dir,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    _write_run_summary(output_dir, report, generated_images)
    return result


def _build_training_report() -> ResearchReport:
    return ResearchReport(
        summary=load_research_packet(),
        pain_point_clusters=["manual research packet fallback"],
        competitor_watchlist=[],
        viral_campaign_examples=[],
        source_digest=["manual packet"],
    )


def run():
    """Run the workflow in live or mock mode."""
    inputs = build_inputs()

    try:
        if get_run_mode() == "mock":
            latest_dir, archive_dir = build_output_paths(DEFAULT_OUTPUT_DIR)
            run_mock_pipeline(inputs, latest_dir, archive_dir)
            return
        output_dir = build_run_output_dir(DEFAULT_OUTPUT_DIR)
        _run_live_pipeline(inputs, output_dir=output_dir)
    except Exception as exc:
        raise RuntimeError("An error occurred while running the workflow.") from exc


def train():
    """Train the live crew for a given number of iterations."""
    inputs = build_inputs()
    try:
        args = _require_cli_args("train", 2)
        SocialMediaPlanner().crew().train(
            n_iterations=int(args[0]),
            filename=args[1],
            inputs=_build_live_inputs(inputs, _build_training_report()),
        )
    except Exception as exc:
        raise RuntimeError("An error occurred while training the crew.") from exc


def replay():
    """Replay the live crew execution from a specific task."""
    try:
        task_id = _require_cli_args("replay", 1)[0]
        SocialMediaPlanner().crew().replay(task_id=task_id)
    except Exception as exc:
        raise RuntimeError("An error occurred while replaying the crew.") from exc


def test():
    """Test the live crew execution and return the results."""
    inputs = build_inputs()

    try:
        args = _require_cli_args("test", 2)
        SocialMediaPlanner().crew().test(
            n_iterations=int(args[0]),
            eval_llm=args[1],
            inputs=_build_live_inputs(inputs, _build_training_report()),
        )
    except Exception as exc:
        raise RuntimeError("An error occurred while testing the crew.") from exc


def run_with_trigger():
    """Run the workflow with trigger payload."""
    trigger_payload = _parse_trigger_payload()
    inputs = build_trigger_inputs(trigger_payload)

    try:
        if get_run_mode() == "mock":
            latest_dir, archive_dir = build_output_paths(DEFAULT_OUTPUT_DIR)
            run_mock_pipeline(inputs, latest_dir, archive_dir)
            return None
        output_dir = build_run_output_dir(DEFAULT_OUTPUT_DIR)
        result = _run_live_pipeline(inputs, output_dir=output_dir)
        return result
    except Exception as exc:
        raise RuntimeError("An error occurred while running the workflow with trigger.") from exc


if __name__ == "__main__":
    run()
