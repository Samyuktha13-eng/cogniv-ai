"""Deterministic memory-to-media prompt construction."""

from __future__ import annotations

import re

from reminiscence.memory_selector import MemoryCandidate

from .models import MediaGenerationRequest, MemorySceneSpecification


class MediaPromptBuilder:
    def build(
        self,
        candidate: MemoryCandidate,
        patient_id: str,
        life_stage: str = "unspecified",
        emotional_tone: str = "warm and gentle",
    ) -> MediaGenerationRequest:
        specification = MemorySceneSpecification(
            memory_id=candidate.memory_id,
            patient_id=patient_id,
            source_type=candidate.source,
            factual_memory=candidate.story,
            life_stage=life_stage,
            people=list(candidate.people),
            place=candidate.places[0] if candidate.places else None,
            objects=list(candidate.objects),
            sensory_cues=list(candidate.sensory_cues),
            emotional_tone=emotional_tone,
            visual_scene=_visual_scene(candidate),
        )
        request_id = _request_id(candidate.memory_id, candidate.scene_id)
        return MediaGenerationRequest(
            request_id=request_id,
            memory_id=specification.memory_id,
            patient_id=specification.patient_id,
            source_type=specification.source_type,
            factual_memory=specification.factual_memory,
            life_stage=specification.life_stage,
            people=specification.people,
            place=specification.place,
            objects=specification.objects,
            sensory_cues=specification.sensory_cues,
            emotional_tone=specification.emotional_tone,
            visual_scene=specification.visual_scene,
            image_prompt=_image_prompt(specification),
            video_prompt=_video_prompt(specification),
            continuity_constraints=_continuity_constraints(specification),
            negative_constraints=_negative_constraints(specification),
            reference_asset=candidate.image_filename or candidate.video_filename,
        )


def _visual_scene(candidate: MemoryCandidate) -> str:
    setting = candidate.places[0] if candidate.places else "the remembered setting"
    people = ", ".join(candidate.people) or "the people described in the memory"
    action = ", ".join(candidate.activities) or "a quiet moment connected to the memory"
    objects = ", ".join(candidate.objects)
    detail = f" with {objects}" if objects else ""
    return f"{people} in {setting}, {action}{detail}."


def _image_prompt(specification: MemorySceneSpecification) -> str:
    return (
        f"Create a respectful, gentle reminiscence image of {specification.visual_scene} "
        f"The image should reflect this factual memory: {specification.factual_memory} "
        f"Use {specification.emotional_tone} visual storytelling and preserve the stated people, place, objects, and sensory cues."
    )


def _video_prompt(specification: MemorySceneSpecification) -> str:
    return (
        f"Create a subtle memory-cue motion scene from this visual scene: {specification.visual_scene} "
        f"Use slow, natural movement and a {specification.emotional_tone} tone. "
        "Animate only the described people, objects, setting, or sensory details; do not add new events."
    )


def _continuity_constraints(specification: MemorySceneSpecification) -> list[str]:
    constraints = [
        "Keep the visual subject, setting, and action consistent with the factual memory.",
        "Treat the generated media as a reminiscence cue, not historical evidence.",
        "Preserve continuity across future frames and related media requests.",
    ]
    if specification.people:
        constraints.append(f"Keep the named people consistent: {', '.join(specification.people)}.")
    if specification.place:
        constraints.append(f"Keep the setting consistent: {specification.place}.")
    return constraints


def _negative_constraints(specification: MemorySceneSpecification) -> list[str]:
    return [
        "Do not invent autobiographical facts, dialogue, relationships, or events.",
        "Do not add identifiable people who are not in the memory metadata.",
        "Do not portray generated details as certain evidence of the patient's past.",
        "Avoid frightening, dramatic, humiliating, or distressing imagery.",
        "Avoid text overlays, quiz framing, scores, or evaluative language.",
    ]


def _request_id(memory_id: str, scene_id: str | None) -> str:
    suffix = scene_id or "memory"
    return "media_" + re.sub(r"[^a-zA-Z0-9_]+", "_", f"{memory_id}_{suffix}").strip("_")
