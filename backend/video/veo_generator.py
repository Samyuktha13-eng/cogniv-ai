import os
import time
from pathlib import Path
from typing import Optional, List

from google import genai
from google.genai import types


class VeoVideoGenerator:
    """Generate and cache Veo animation videos from backend semantic actions."""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or Path(__file__).resolve().parents[1])
        self.assets_dir = self.project_root / "backend" / "assets" / "animations"
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your backend environment before generating Veo videos."
            )

        self.client = genai.Client(api_key=api_key)

    def _local_path_for(self, action_name: str) -> Path:
        return self.assets_dir / f"{action_name}.mp4"

    def has_video(self, action_name: str) -> bool:
        return self._local_path_for(action_name).exists()

    def ensure_video(self, action_name: str, prompt: str, reference_images: Optional[List[str]] = None, use_image_prompt: Optional[str] = None) -> Path:
        """Generate a video if it does not already exist, then return the cached local file path."""
        target = self._local_path_for(action_name)
        if target.exists():
            return target

        reference_image_objects = []
        if reference_images:
            for image_path in reference_images[:3]:
                full_path = Path(image_path)
                if not full_path.exists():
                    continue
                reference_image_objects.append(
                    types.VideoGenerationReferenceImage(
                        image=full_path,
                        reference_type="asset",
                    )
                )

        config = types.GenerateVideosConfig(
            aspect_ratio="16:9",
            duration_seconds=8,
            resolution="720p",
        )
        if reference_image_objects:
            config.reference_images = reference_image_objects

        operation = self.client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            image=use_image_prompt if use_image_prompt else None,
            config=config,
        )

        while not operation.done:
            time.sleep(10)
            operation = self.client.operations.get(operation)

        generated = operation.response.generated_videos[0]
        destination = str(target)
        self.client.files.download(file=generated.video, destination=destination)
        return target


# Convenience factory for the prototype flow.
def build_video_generator() -> VeoVideoGenerator:
    return VeoVideoGenerator()
