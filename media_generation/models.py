"""Typed, serializable contracts for future media providers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class MemorySceneSpecification:
    memory_id: str
    patient_id: str
    source_type: str
    factual_memory: str
    life_stage: str
    people: list[str] = field(default_factory=list)
    place: str | None = None
    objects: list[str] = field(default_factory=list)
    sensory_cues: list[str] = field(default_factory=list)
    emotional_tone: str = "warm and gentle"
    visual_scene: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemorySceneSpecification":
        return cls(**data)


@dataclass(frozen=True)
class MediaGenerationRequest:
    request_id: str
    memory_id: str
    patient_id: str
    source_type: str
    factual_memory: str
    life_stage: str
    people: list[str]
    place: str | None
    objects: list[str]
    sensory_cues: list[str]
    emotional_tone: str
    visual_scene: str
    image_prompt: str
    video_prompt: str
    continuity_constraints: list[str]
    negative_constraints: list[str]
    reminiscence_purpose: str = "reminiscence_cue"
    reference_asset: str | None = None
    requested_media_type: str = "image_or_video"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MediaGenerationRequest":
        return cls(**data)


class MediaGenerator(Protocol):
    def generate(self, request: MediaGenerationRequest) -> Any: ...


@dataclass(frozen=True)
class VideoGenerationResult:
    request_id: str
    provider: str
    model_id: str
    output_path: str
    duration_seconds: float | None
    width: int | None
    height: int | None
    fps: int
    seed: int | None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
