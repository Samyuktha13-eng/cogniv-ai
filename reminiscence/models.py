"""Small transport models for reminiscence orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class MediaRequest:
    memory_id: str
    scene_id: str | None
    media_type: str
    purpose: str = "reminiscence_cue"
    filename: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReminiscenceTurn:
    memory_id: str
    scene_id: str | None
    prompt: str
    media: MediaRequest
    follow_up_topics: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
