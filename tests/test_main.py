import tempfile
import unittest
from datetime import datetime as real_datetime
from pathlib import Path
from unittest.mock import patch

import social_media_planner.main as main_module
from social_media_planner.main import (
    build_inputs,
    build_output_paths,
    build_run_output_dir,
    build_trigger_inputs,
    get_pipeline_mode,
    get_run_mode,
    load_research_packet,
    run_with_trigger,
)


class MainInputsTest(unittest.TestCase):
    def test_build_inputs_matches_app_launch_defaults(self) -> None:
        inputs = build_inputs()

        self.assertEqual(inputs["app_name"], "SignalSprout")
        self.assertEqual(inputs["platforms"], "TikTok and Instagram")
        self.assertEqual(inputs["posts_per_week"], "5")
        self.assertEqual(inputs["batch_size"], "25")
        self.assertEqual(inputs["draft_batch_size"], "12")
        self.assertIn("productivity", inputs["subreddits"])
        self.assertIn("Notion", inputs["competitor_names"])
        self.assertEqual(inputs["time_window_days"], 7)
        self.assertIn("prelaunch", inputs["launch_stage"])
        self.assertIn("waitlist", inputs["cta_target"])
        self.assertIn("Weekly App Launch Research Packet", inputs["research_packet"])

    def test_get_run_mode_is_supported_value(self) -> None:
        mode = get_run_mode()
        self.assertIn(mode, {"mock", "live"})

    def test_get_run_mode_rejects_invalid_values(self) -> None:
        with patch.dict("os.environ", {"RUN_MODE": "invalid"}, clear=False):
            with self.assertRaisesRegex(ValueError, "Unsupported RUN_MODE"):
                get_run_mode()

    def test_get_pipeline_mode_rejects_invalid_values(self) -> None:
        with patch.dict("os.environ", {"PIPELINE_MODE": "invalid"}, clear=False):
            with self.assertRaisesRegex(ValueError, "Unsupported PIPELINE_MODE"):
                get_pipeline_mode()

    def test_load_research_packet_raises_for_missing_file(self) -> None:
        with patch.dict(
            "os.environ",
            {"SOCIAL_MEDIA_RESEARCH_PACKET": "knowledge/does_not_exist.md"},
            clear=False,
        ):
            with self.assertRaisesRegex(FileNotFoundError, "Research packet not found"):
                load_research_packet()

    def test_build_trigger_inputs_keeps_defaults_for_missing_fields(self) -> None:
        inputs = build_trigger_inputs({"app_name": "TriggerSprout"})

        self.assertEqual(inputs["app_name"], "TriggerSprout")
        self.assertEqual(inputs["platforms"], "TikTok and Instagram")
        self.assertIn("sideproject", inputs["subreddits"])
        self.assertEqual(inputs["batch_size"], "25")
        self.assertIn("Weekly App Launch Research Packet", inputs["research_packet"])

    def test_run_with_trigger_rejects_non_object_json_payloads(self) -> None:
        with patch.object(
            main_module.sys,
            "argv",
            ["run_with_trigger", '["not-an-object"]'],
        ):
            with self.assertRaisesRegex(ValueError, "JSON object"):
                run_with_trigger()

    def test_build_output_paths_uses_latest_and_archive(self) -> None:
        class FrozenDateTime:
            @staticmethod
            def now():
                return real_datetime.strptime("2026-03-17_09-15-30", "%Y-%m-%d_%H-%M-%S")

        with patch.object(main_module, "datetime", FrozenDateTime):
            latest_dir, archive_dir = build_output_paths(Path("output"))

        self.assertEqual(Path("output") / "latest", latest_dir)
        self.assertEqual(Path("output") / "archive" / "2026-03-17_09-15-30", archive_dir)

    def test_build_run_output_dir_creates_timestamped_run_folder(self) -> None:
        class FrozenDateTime:
            @staticmethod
            def now():
                return real_datetime.strptime("20260317-091530", "%Y%m%d-%H%M%S")

        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.object(main_module, "datetime", FrozenDateTime):
                path = build_run_output_dir(Path(tmp_dir))

        self.assertEqual(Path(tmp_dir) / "runs" / "20260317-091530", path)
