"""Typed models for story scenes and multimedia game content."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AnswerOutcome(str, Enum):
    """Internal answer state; presentation layers should choose their own wording."""

    REMEMBERED = "remembered"
    ALMOST_REMEMBERED = "almost_remembered"
    NEEDS_SUPPORT = "needs_support"


@dataclass(frozen=True)
class SceneAsset:
    asset_type: str
    filename: str
    description: str

    def __post_init__(self) -> None:
        if self.asset_type not in {"image", "video", "thumbnail"}:
            raise ValueError("asset_type must be image, video, or thumbnail")
        if not self.filename:
            raise ValueError("asset filename is required")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SceneAsset":
        return cls(
            asset_type=data["asset_type"],
            filename=data["filename"],
            description=data.get("description", ""),
        )


@dataclass(frozen=True)
class Question:
    question_id: str
    scene_id: str
    type: str
    prompt: str
    language: str
    expected_concepts: list[str] = field(default_factory=list)
    acceptable_answers: list[str] = field(default_factory=list)
    hint_scene_id: str | None = None
    difficulty: str = "gentle"
    allow_voice_answer: bool = True
    allow_touch_answer: bool = True

    def __post_init__(self) -> None:
        if not self.expected_concepts:
            raise ValueError(f"question {self.question_id} needs expected concepts")
        if not self.acceptable_answers:
            raise ValueError(f"question {self.question_id} needs acceptable answers")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Question":
        return cls(**data)


@dataclass(frozen=True)
class StoryScene:
    scene_id: str
    patient_id: str
    chapter_id: str
    sequence: int
    title: str
    story_section: str
    story_reference: str
    narrative_summary: str
    characters: list[str] = field(default_factory=list)
    location: str = ""
    objects: list[str] = field(default_factory=list)
    sensory_cues: list[str] = field(default_factory=list)
    image_asset: SceneAsset | None = None
    video_asset: SceneAsset | None = None
    memory_cues: list[str] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)
    hints: list[dict[str, str]] = field(default_factory=list)
    next_scene_id: str | None = None
    previous_scene_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StoryScene":
        values = dict(data)
        if values.get("image_asset"):
            values["image_asset"] = SceneAsset.from_dict(values["image_asset"])
        if values.get("video_asset"):
            values["video_asset"] = SceneAsset.from_dict(values["video_asset"])
        values["questions"] = [Question.from_dict(item) for item in values.get("questions", [])]
        return cls(**values)
