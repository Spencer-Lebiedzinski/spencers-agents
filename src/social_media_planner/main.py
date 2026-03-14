#!/usr/bin/env python
import json
import os
import sys
import warnings

from datetime import datetime
from pathlib import Path

from social_media_planner.crew import SocialMediaPlanner
from social_media_planner.mock_pipeline import run_mock_pipeline

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESEARCH_PACKET = PROJECT_ROOT / "knowledge" / "app_launch_research_packet.md"


def get_run_mode() -> str:
    """Return the configured runtime mode."""
    return os.getenv("RUN_MODE", "live").strip().lower()


def load_research_packet() -> str:
    """Load the weekly research packet from disk for the research task."""
    packet_path = os.getenv("SOCIAL_MEDIA_RESEARCH_PACKET")
    path = Path(packet_path) if packet_path else DEFAULT_RESEARCH_PACKET
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.read_text(encoding="utf-8").strip()


def build_inputs() -> dict[str, str]:
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
        "current_year": str(datetime.now().year),
        "research_packet": load_research_packet(),
    }


def run():
    """Run the workflow in live or mock mode."""
    inputs = build_inputs()

    try:
        if get_run_mode() == "mock":
            run_mock_pipeline(inputs, output_dir=Path.cwd())
            return
        SocialMediaPlanner().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the workflow: {e}")


def train():
    """Train the live crew for a given number of iterations."""
    inputs = build_inputs()
    try:
        SocialMediaPlanner().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """Replay the live crew execution from a specific task."""
    try:
        SocialMediaPlanner().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """Test the live crew execution and return the results."""
    inputs = build_inputs()

    try:
        SocialMediaPlanner().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger():
    """Run the workflow with trigger payload."""
    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "app_name": "",
        "app_one_liner": "",
        "target_user": "",
        "user_problem": "",
        "dream_outcome": "",
        "launch_stage": "",
        "core_features": "",
        "proof_points": "",
        "platforms": "",
        "cta_target": "",
        "content_pillars": "",
        "brand_voice": "",
        "posts_per_week": "",
        "current_year": "",
        "research_packet": "",
    }

    try:
        if get_run_mode() == "mock":
            run_mock_pipeline(inputs, output_dir=Path.cwd())
            return None
        result = SocialMediaPlanner().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the workflow with trigger: {e}")


if __name__ == "__main__":
    run()
