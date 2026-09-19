from __future__ import annotations

from pydantic import BaseModel, Field


class CaregiverIntent(BaseModel):
    raw_prompt: str
    topic: str = ""
    life_period: str = ""
    entities: list[str] = Field(default_factory=list)
    story_id: str | None = None


class ScenePlan(BaseModel):
    story_id: str
    beat_id: str
    chapter_id: str | None = None
    scene_id: str | None = None
    facts: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    interaction_plan: dict = Field(default_factory=dict)
    action: str
    motion_sequence: list[str]
    constraints: list[str]
    reference_images: list[str]          # relative paths under patient image folder
    grounding_source: str                # e.g. "story:jasmine_morning/beat:jasmine_04"
    video_prompt: str = ""


class GroundingResult(BaseModel):
    match: bool
    reason: str = ""
    intent: CaregiverIntent | None = None
    scene_plan: ScenePlan | None = None
