"""Deterministic selection across personal RAG memories and story cues."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from story.models import StoryScene
from story.scene_store import SceneStore


@dataclass(frozen=True)
class MemoryCandidate:
    memory_id: str
    title: str
    source: str
    scene_id: str | None = None
    topics: list[str] = field(default_factory=list)
    people: list[str] = field(default_factory=list)
    places: list[str] = field(default_factory=list)
    objects: list[str] = field(default_factory=list)
    activities: list[str] = field(default_factory=list)
    sensory_cues: list[str] = field(default_factory=list)
    story: str = ""
    image_filename: str | None = None
    video_filename: str | None = None

    @classmethod
    def from_memory(cls, memory: dict[str, Any]) -> "MemoryCandidate":
        return cls(
            memory_id=memory["memory_id"], title=memory["title"], source=memory.get("source", "personal_memory"),
            topics=memory.get("tags", []), people=memory.get("people", []), places=[memory["place"]] if memory.get("place") else [],
            objects=memory.get("objects", []), activities=[memory["activity"]] if memory.get("activity") else [], story=memory.get("story", ""),
        )

    @classmethod
    def from_scene(cls, scene: StoryScene) -> "MemoryCandidate":
        topics = [scene.title, scene.chapter_id, scene.story_reference]
        return cls(
            memory_id=scene.scene_id, title=scene.title, source="story_scene", scene_id=scene.scene_id,
            topics=topics, people=scene.characters, places=[scene.location], objects=scene.objects,
            activities=scene.memory_cues, sensory_cues=scene.sensory_cues, story=scene.story_section,
            image_filename=scene.image_asset.filename if scene.image_asset else None,
            video_filename=scene.video_asset.filename if scene.video_asset else None,
        )


class CandidateSource(Protocol):
    def candidates(self, patient_id: str) -> list[MemoryCandidate]: ...


class MemorySelector:
    def __init__(self, sources: list[CandidateSource] | None = None, scene_store: SceneStore | None = None) -> None:
        self.sources = list(sources or [])
        if scene_store is not None:
            self.sources.append(SceneCandidateSource(scene_store))

    def select(self, patient_id: str, signals: dict[str, Any] | None = None, exclude_ids: set[str] | None = None) -> MemoryCandidate | None:
        signals = signals or {}
        exclude_ids = exclude_ids or set()
        candidates = [candidate for source in self.sources for candidate in source.candidates(patient_id) if candidate.memory_id not in exclude_ids]
        if not candidates:
            return None
        wanted = _terms(signals)
        time_terms = _terms({"time_of_day": signals.get("time_of_day", "")})
        scored = []
        for index, candidate in enumerate(candidates):
            score = (
                3 * len(wanted & _terms({"topics": candidate.topics}))
                + 4 * len(wanted & _terms({"people": candidate.people}))
                + 3 * len(wanted & _terms({"places": candidate.places}))
                + 2 * len(wanted & _terms({"objects": candidate.objects}))
                + 2 * len(wanted & _terms({"activities": candidate.activities}))
                + len(time_terms & _terms({"sensory_cues": candidate.sensory_cues}))
            )
            scored.append((score, -index, candidate))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return scored[0][2]


class PersonalMemorySource:
    def __init__(self, store: Any) -> None:
        self.store = store

    def candidates(self, patient_id: str) -> list[MemoryCandidate]:
        return [MemoryCandidate.from_memory(memory) for memory in self.store.list_memories(patient_id)]


class SceneCandidateSource:
    def __init__(self, scene_store: SceneStore) -> None:
        self.scene_store = scene_store

    def candidates(self, patient_id: str) -> list[MemoryCandidate]:
        return [MemoryCandidate.from_scene(scene) for scene in self.scene_store.list_scenes() if scene.patient_id == patient_id]


def _terms(values: dict[str, Any]) -> set[str]:
    text = " ".join(_flatten(value) for value in values.values())
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def _flatten(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(_flatten(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_flatten(item) for item in value.values())
    return str(value or "")
