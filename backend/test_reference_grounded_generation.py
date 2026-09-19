import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from backend.magic_hour_video import (
    DEFAULT_ASPECT_RATIO,
    DEFAULT_RESOLUTION,
    build_motion_prompt,
    build_reference_grounded_prompt,
    compose_reference_scene,
    compose_multi_reference_sheet,
)
from backend.story_video_service import build_scene_reference_image


class ReferenceGroundedGenerationTests(unittest.TestCase):
    def test_default_scene_config_is_landscape_16_9(self):
        self.assertEqual(DEFAULT_RESOLUTION, "720p")
        self.assertEqual(DEFAULT_ASPECT_RATIO, "16:9")

    def test_reference_grounded_prompt_keeps_visual_source_truth(self):
        prompt = build_reference_grounded_prompt(
            scene_id="memory_03_chapathi",
            original_prompt="Lakshmi and Anu make chapathi together in a warm kitchen.",
            references=["people/patient_lakshmi.png", "people/daughter_anu.png", "home/family_kitchen.jpg"],
        )

        lower_prompt = prompt.lower()
        self.assertIn("reference scene", lower_prompt)
        self.assertIn("do not redesign", lower_prompt)
        self.assertIn("visual source of truth", lower_prompt)
        self.assertIn("16:9", lower_prompt)
        self.assertIn("keep the camera fixed", lower_prompt)

    def test_compose_reference_scene_creates_fixed_16_9_reference(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            room = tmp / "room.png"
            left = tmp / "lakshmi.png"
            right = tmp / "anu.png"
            obj = tmp / "chapathi.png"

            Image.new("RGBA", (640, 360), (120, 100, 90, 255)).save(room)
            Image.new("RGBA", (200, 260), (50, 60, 70, 255)).save(left)
            Image.new("RGBA", (200, 260), (70, 80, 60, 255)).save(right)
            Image.new("RGBA", (120, 80), (200, 160, 110, 255)).save(obj)

            out_path = compose_reference_scene(
                scene_id="memory_03_chapathi",
                room_image=room,
                character_images=[left, right],
                object_images=[obj],
                output_dir=tmp / "reference_scenes",
                target_size=(960, 540),
            )

            self.assertTrue(Path(out_path).exists())
            self.assertTrue(Path(out_path).suffix.lower() == ".png")

            with Image.open(out_path) as composed:
                self.assertEqual(composed.size, (960, 540))

    def test_motion_prompt_only_describes_motion(self):
        prompt = build_motion_prompt(
            scene_id="present_03_reunion_hug",
            scene_story="Anu slowly walks toward Lakshmi and they embrace gently.",
        )

        text = prompt.lower()
        self.assertIn("animate the provided reference scene exactly as supplied", text)
        self.assertIn("do not redesign", text)
        self.assertIn("keep the same faces", text)
        self.assertIn("anu slowly walks toward lakshmi", text)

    def test_intro_prompt_preserves_house_only_establishing_shot(self):
        prompt = build_motion_prompt(
            scene_id="intro",
            scene_story="Lakshmi is seated on the sofa.",
        ).lower()

        self.assertIn("supplied house reference", prompt)
        self.assertIn("exact architecture", prompt)
        self.assertIn("keeping the entire house visible", prompt)
        self.assertIn("do not introduce lakshmi", prompt)
        self.assertIn("16:9 landscape composition", prompt)

    def test_living_room_prompt_preserves_lakshmi_identity(self):
        prompt = build_motion_prompt("memory_01_anu", "Lakshmi remembers her daughter Anu.").lower()

        self.assertIn("exact identity", prompt)
        self.assertIn("elderly age", prompt)
        self.assertIn("sitting naturally in the living room", prompt)
        self.assertIn("do not make her younger", prompt)
        self.assertIn("no additional people", prompt)
        self.assertIn("no cuts or transitions", prompt)

    def test_temple_prompt_preserves_young_anu_and_krishna_scene(self):
        prompt = build_motion_prompt("memory_03_temple", "Lakshmi remembers visiting the temple with Anu.").lower()

        self.assertIn("young anu", prompt)
        self.assertIn("never use adult anu", prompt)
        self.assertIn("temple interior image", prompt)
        self.assertIn("same temple", prompt)
        self.assertIn("krishna shrine", prompt)
        self.assertIn("morph faces", prompt)

    def test_multi_reference_sheet_is_fixed_landscape(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            first = tmp / "interior.png"
            second = tmp / "exterior.png"
            Image.new("RGB", (1024, 559), (20, 40, 60)).save(first)
            Image.new("RGB", (1024, 559), (60, 40, 20)).save(second)

            output = compose_multi_reference_sheet([first, second], tmp / "temple_references.png")

            with Image.open(output) as sheet:
                self.assertEqual(sheet.size, (960, 540))
                self.assertNotEqual(sheet.getpixel((100, 270)), sheet.getpixel((850, 270)))

    def test_intro_scene_can_be_house_only(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            house = tmp / "house.png"
            Image.new("RGBA", (640, 360), (100, 90, 80, 255)).save(house)

            scene = {
                "id": "intro",
                "image": str(house),
                "characters": [],
                "reference_bundle": [{"type": "environment", "path": str(house)}],
            }

            with patch("backend.story_video_service.resolve_image") as mock_resolve:
                mock_resolve.side_effect = lambda path: Path(path)
                output = build_scene_reference_image(scene, output_dir=tmp / "reference_scenes")

            self.assertIn("memory_01_home_reference.png", output)
            self.assertTrue(Path(output).exists())
            with Image.open(output) as composed:
                self.assertEqual(composed.size, (960, 540))

    def test_portrait_reference_is_transparent_outside_subject(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            room = tmp / "room.png"
            person = tmp / "person.png"
            Image.new("RGBA", (640, 360), (100, 90, 80, 255)).save(room)
            Image.new("RGBA", (200, 260), (50, 60, 70, 255)).save(person)

            output = compose_reference_scene(
                scene_id="masked_person",
                room_image=room,
                character_images=[person],
                output_dir=tmp / "generated_references",
            )

            with Image.open(output) as composed:
                self.assertEqual(composed.size, (960, 540))
                self.assertNotEqual(composed.getpixel((120, 180)), (50, 60, 70, 255))

    def test_intro_reference_occludes_portrait_edge_with_sofa(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            room = tmp / "living_room.png"
            person = tmp / "lakshmi.png"
            Image.new("RGBA", (960, 540), (80, 90, 100, 255)).save(room)
            Image.new("RGBA", (200, 260), (200, 30, 30, 255)).save(person)

            output = compose_reference_scene(
                scene_id="intro",
                room_image=room,
                character_images=[person],
                output_dir=tmp,
                output_name="memory_01_home_reference.png",
                sofa_occlusion=True,
            )

            self.assertEqual(Path(output).name, "memory_01_home_reference.png")
            with Image.open(output) as composed:
                self.assertEqual(composed.size, (960, 540))


if __name__ == "__main__":
    unittest.main()
