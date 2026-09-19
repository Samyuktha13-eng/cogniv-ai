import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.magic_hour_video import generate_video_from_bytes


class TempleUploadPipelineTests(unittest.TestCase):
    def test_uploaded_bytes_use_temporary_path_and_cleanup(self):
        observed_path = None

        def fake_generate_video(**kwargs):
            nonlocal observed_path
            observed_path = Path(kwargs["image_path"])
            self.assertTrue(observed_path.exists())
            self.assertEqual(observed_path.read_bytes(), b"uploaded-temple-image")
            return {"id": "mock-temple-exit"}

        with patch("backend.magic_hour_video.generate_video", side_effect=fake_generate_video):
            result = generate_video_from_bytes(
                b"uploaded-temple-image",
                "Temple exit motion.",
                name="memory_04_temple_exit",
            )

        self.assertEqual(result, {"id": "mock-temple-exit"})
        self.assertIsNotNone(observed_path)
        self.assertFalse(observed_path.exists())

    def test_empty_upload_is_rejected_before_render(self):
        with patch("backend.magic_hour_video.generate_video") as generate_mock:
            with self.assertRaises(ValueError):
                generate_video_from_bytes(b"", "Temple exit motion.")
            generate_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()