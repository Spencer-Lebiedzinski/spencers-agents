import tempfile
import unittest
from pathlib import Path

from social_media_planner.main import build_inputs
from social_media_planner.mock_pipeline import run_mock_pipeline


class MockPipelineTest(unittest.TestCase):
    def test_run_mock_pipeline_writes_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            latest_dir = Path(tmp_dir) / "output" / "latest"
            archive_dir = Path(tmp_dir) / "output" / "archive" / "2026-03-16_12-00-00"
            run_mock_pipeline(build_inputs(), latest_dir, archive_dir)

            expected_files = {
                "research_brief.md",
                "content_backlog.md",
                "content_drafts.md",
                "weekly_app_launch_plan.md",
                "candidate_learnings.md",
                "mock_run_summary.md",
            }

            self.assertEqual(expected_files, {path.name for path in latest_dir.iterdir()})
            self.assertEqual(expected_files, {path.name for path in archive_dir.iterdir()})
