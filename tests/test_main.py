import unittest

from social_media_planner.main import build_inputs, get_run_mode


class MainInputsTest(unittest.TestCase):
    def test_build_inputs_matches_app_launch_defaults(self) -> None:
        inputs = build_inputs()

        self.assertEqual(inputs["app_name"], "SignalSprout")
        self.assertEqual(inputs["platforms"], "TikTok and Instagram")
        self.assertEqual(inputs["posts_per_week"], "5")
        self.assertIn("prelaunch", inputs["launch_stage"])
        self.assertIn("waitlist", inputs["cta_target"])
        self.assertIn("Weekly App Launch Research Packet", inputs["research_packet"])

    def test_get_run_mode_is_supported_value(self) -> None:
        mode = get_run_mode()
        self.assertIn(mode, {"mock", "live"})
