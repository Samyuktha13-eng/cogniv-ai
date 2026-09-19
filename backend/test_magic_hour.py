from pathlib import Path

try:
    from backend.magic_hour_video import generate_video
except ModuleNotFoundError:
    from magic_hour_video import generate_video

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE = PROJECT_ROOT / "Patient_001_Lakshmi" / "home" / "family_kitchen.jpg"
PROMPT = """
Create a warm and realistic memory scene of an Indian mother and her adult daughter preparing chapathi together in a familiar family kitchen.
The daughter gently prepares the chapathi while the mother stands nearby and helps her.
Show subtle natural human movement, gentle hand motion, realistic interaction, and warm emotional tone.
Keep the people visually consistent with the source image.
The atmosphere should feel peaceful, familiar, warm and emotionally positive.
No text, no captions, no subtitles.
""".strip()

if __name__ == "__main__":
    generate_video(
        image_path=str(IMAGE),
        prompt=PROMPT,
        output_dir="generated_videos",
        duration=5,
        model="ltx-2.3",
        resolution="480p",
        name="lakshmi_story_test_scene",
    )
