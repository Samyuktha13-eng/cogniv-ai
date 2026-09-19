import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image

from backend.magic_hour_video import RenderPreflightError, generate_video, preflight_render


class MagicHourPreflightTests(unittest.TestCase):
    def test_unsupported_resolution_does_not_submit(self):
        with patch("backend.magic_hour_video.API_KEY", "test-key"), patch(
            "backend.magic_hour_video.Client"
        ) as client_class:
            with self.assertRaisesRegex(RenderPreflightError, "720p unavailable"):
                preflight_render("720p", supported_resolutions=["480p"], available_credits=500, estimated_credits=120)
            client_class.assert_not_called()

    def test_insufficient_credits_does_not_submit(self):
        with patch("backend.magic_hour_video.API_KEY", "test-key"):
            with self.assertRaisesRegex(RenderPreflightError, "Insufficient Magic Hour credits"):
                preflight_render("480p", supported_resolutions=["480p"], available_credits=40, estimated_credits=120)

    def test_missing_api_key_does_not_submit(self):
        with patch("backend.magic_hour_video.API_KEY", None):
            with self.assertRaisesRegex(RenderPreflightError, "not configured"):
                preflight_render("480p", supported_resolutions=["480p"], available_credits=500, estimated_credits=120)

    def test_missing_local_credit_balance_allows_provider_preflight(self):
        with patch("backend.magic_hour_video.API_KEY", "test-key"), patch.dict(
            os.environ, {}, clear=True
        ):
            result = preflight_render("480p", supported_resolutions=["480p"])
        self.assertEqual(result.resolution, "480p")
        self.assertIsNone(result.available_credits)

    def test_successful_preflight_allows_mocked_render(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "reference.png"
            Image.new("RGB", (960, 540), "white").save(image_path)
            client = Mock()
            client.v1.image_to_video.generate.return_value = {"id": "mock-render"}
            with patch("backend.magic_hour_video.API_KEY", "test-key"), patch(
                "backend.magic_hour_video.get_client", return_value=client
            ), patch.dict(os.environ, {"MAGIC_HOUR_CREDIT_COST": "120", "MAGIC_HOUR_CREDITS": "500"}):
                result = generate_video(str(image_path), "Animate only.", output_dir=temp_dir, resolution="480p")
            self.assertEqual(result, {"id": "mock-render"})
            client.v1.image_to_video.generate.assert_called_once()

    def test_two_reference_images_use_native_start_and_end_assets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "exterior.png"
            second = Path(temp_dir) / "interior.png"
            Image.new("RGB", (960, 540), "green").save(first)
            Image.new("RGB", (960, 540), "brown").save(second)
            client = Mock()
            client.v1.image_to_video.generate.return_value = {"id": "mock-transition"}
            with patch("backend.magic_hour_video.API_KEY", "test-key"), patch(
                "backend.magic_hour_video.get_client", return_value=client
            ):
                result = generate_video(
                    str(first),
                    "Transition between references.",
                    output_dir=temp_dir,
                    resolution="480p",
                    reference_images=[first, second],
                )

            self.assertEqual(result, {"id": "mock-transition"})
            assets = client.v1.image_to_video.generate.call_args.kwargs["assets"]
            self.assertEqual(assets["image_file_path"], str(first.resolve()))
            self.assertEqual(assets["end_image_file_path"], str(second.resolve()))

    def test_temple_uses_one_image_path_without_end_reference(self):
        from backend.lakshmi_story import build_lakshmi_memory_journey

        scene = next(item for item in build_lakshmi_memory_journey()["scenes"] if item["id"] == "memory_03_temple")
        self.assertTrue((Path(__file__).resolve().parents[1] / "Patient_001_Lakshmi" / scene["image"]).exists())
        self.assertTrue((Path(__file__).resolve().parents[1] / "Patient_001_Lakshmi" / scene["character_reference_images"][0]).exists())
        self.assertEqual(scene["image"], "memories/anu_lakshmi_temple.jpg")
        self.assertEqual(scene["character_reference_images"], ["memories/young_anu.jpeg"])

        interior = Path(__file__).resolve().parents[1] / "Patient_001_Lakshmi" / scene["image"]
        client = Mock()
        client.v1.image_to_video.generate.return_value = {"id": "mock-temple"}
        with patch("backend.magic_hour_video.API_KEY", "test-key"), patch(
            "backend.magic_hour_video.get_client", return_value=client
        ):
            generate_video(str(interior), "Temple interior motion.", output_dir=str(interior.parent), resolution="480p")

        assets = client.v1.image_to_video.generate.call_args.kwargs["assets"]
        self.assertEqual(assets["image_file_path"], str(interior.resolve()))
        self.assertNotIn("end_image_file_path", assets)


if __name__ == "__main__":
    unittest.main()