"""Cogniv media service layer built around the validated LTX BF16 multiscale engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from media_generation.models import MediaGenerationRequest
from media_generation.providers.ltx_bf16_multiscale_provider import LTXBF16MultiScaleProvider
from story.scene_loader import load_scenes


class CognivVideoGenerationService:
    """Scene-aware generator that wraps the frozen BF16 multiscale LTX provider."""

    def __init__(self, provider: LTXBF16MultiScaleProvider | None = None) -> None:
        self.provider = provider or LTXBF16MultiScaleProvider()

    def build_request(self, scene_id: str, profile_name: str = "safe", prompt_override: str | None = None) -> MediaGenerationRequest:
        scene = self.get_scene(scene_id)
        image_path = self.resolve_scene_reference(scene)
        prompt = prompt_override or self.default_prompt(scene)
        negative = [
            "blurry, noisy, distorted face",
            "extra people",
            "scene change",
            "text, watermark",
            "invented objects",
        ]
        return MediaGenerationRequest(
            request_id=f"scene_{scene.scene_id}_{profile_name}",
            memory_id=scene.scene_id,
            patient_id=scene.patient_id,
            source_type="story_scene",
            factual_memory=scene.story_section,
            life_stage="childhood",
            people=scene.characters,
            place=scene.location,
            objects=scene.objects,
            sensory_cues=scene.sensory_cues,
            emotional_tone="warm and gentle",
            visual_scene=scene.narrative_summary,
            image_prompt=f"Refined figure-ground still for {scene.title}. {scene.narrative_summary}",
            video_prompt=prompt,
            continuity_constraints=[
                "Keep the scene consistent with the story memory.",
                "Maintain the same people, clothing, and location throughout the clip.",
                "Use gentle motion only; do not create new story events.",
            ],
            negative_constraints=negative,
            reminiscence_purpose="story_scene_video",
            reference_asset=str(image_path),
            requested_media_type="video",
        )

    def get_scene(self, scene_id: str):
        for scene in load_scenes():
            if scene.scene_id == scene_id:
                return scene
        raise ValueError(f"Scene not found: {scene_id}")

    def resolve_scene_reference(self, scene: Any) -> Path:
        root = Path(__file__).resolve().parents[1]
        asset_name = scene.image_asset.filename if scene.image_asset else None
        if asset_name is None:
            raise ValueError(f"Scene has no image asset: {scene.scene_id}")
        candidates = [
            root / "Patient story image" / asset_name,
            root / asset_name,
            root / "data" / asset_name,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        raise FileNotFoundError(f"Reference asset not found for {scene.scene_id}: {asset_name}")

    def default_prompt(self, scene: Any) -> str:
        people = ", ".join(scene.characters) if scene.characters else "the main character"
        location = scene.location or "the remembered setting"
        return (
            f"{people} in {location}. Keep the same people, clothing, setting, lighting, and mood from the reference image. "
            f"Use very slight natural movement only: tiny body shift, gentle walking, or soft head motion. "
            f"Maintain the same background, same objects, and same scene structure. "
            f"No new people, no invented objects, no scene change, no dramatic action, no text, and no stylization."
        )

    def generate_for_scene(self, scene_id: str, profile_name: str = "safe", prompt_override: str | None = None):
        request = self.build_request(scene_id, profile_name=profile_name, prompt_override=prompt_override)
        return self.provider.generate(request, profile_name=profile_name)
