import tempfile
import unittest
from json import loads
from pathlib import Path
from unittest.mock import patch

import social_media_planner.main as main_module
from social_media_planner.main import build_inputs, run_with_trigger
from social_media_planner.mock_pipeline import run_mock_pipeline


class MockPipelineTest(unittest.TestCase):
    def test_run_mock_pipeline_writes_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            latest_dir = Path(tmp_dir) / "output" / "latest"
            archive_dir = Path(tmp_dir) / "output" / "archive" / "2026-03-16_12-00-00"
            run_mock_pipeline(build_inputs(), latest_dir, archive_dir)

            expected_files = {
                "research_pack.md",
                "research_brief.md",
                "raw_source_dump.json",
                "normalized_source_dataset.json",
                "research_report.json",
                "content_backlog.md",
                "content_ideas.md",
                "content_drafts.md",
                "content_pack.md",
                "weekly_app_launch_plan.md",
                "media_pack.md",
                "generated_image_manifest.json",
                "candidate_learnings.md",
                "mock_run_summary.md",
                "images",
            }

            self.assertEqual(expected_files, {path.name for path in latest_dir.iterdir()})
            self.assertEqual(expected_files, {path.name for path in archive_dir.iterdir()})

    def test_run_with_trigger_in_mock_mode_writes_outputs_using_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict("os.environ", {"RUN_MODE": "mock"}, clear=False):
                with patch.object(
                    main_module.sys,
                    "argv",
                    ["run_with_trigger", '{"app_name": "TriggerSprout"}'],
                ):
                    with patch(
                        "social_media_planner.main.DEFAULT_OUTPUT_DIR",
                        Path(tmp_dir) / "output",
                    ):
                        result = run_with_trigger()

            self.assertIsNone(result)
            latest_dir = Path(tmp_dir) / "output" / "latest"
            archive_root = Path(tmp_dir) / "output" / "archive"
            archive_dirs = list(archive_root.iterdir())
            self.assertTrue(latest_dir.exists())
            self.assertEqual(1, len(archive_dirs))
            plan_path = latest_dir / "weekly_app_launch_plan.md"
            self.assertTrue(plan_path.exists())
            self.assertIn("join the waitlist", plan_path.read_text(encoding="utf-8"))

    def test_mock_pipeline_writes_image_manifest_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            latest_dir = Path(tmp_dir) / "output" / "latest"
            archive_dir = Path(tmp_dir) / "output" / "archive" / "2026-03-16_12-00-00"
            run_mock_pipeline(build_inputs(), latest_dir, archive_dir)

            manifest = loads(
                (latest_dir / "generated_image_manifest.json").read_text(encoding="utf-8")
            )
            self.assertTrue(manifest)
            self.assertEqual("mock_image", manifest[0]["status"])
