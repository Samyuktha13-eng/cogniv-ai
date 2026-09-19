"""Serializable, non-evaluative conversation state."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ConversationState:
    patient_id: str
    current_memory_id: str | None = None
    current_scene_id: str | None = None
    active_topics: list[str] = field(default_factory=list)
    mentioned_people: list[str] = field(default_factory=list)
    mentioned_places: list[str] = field(default_factory=list)
    mentioned_objects: list[str] = field(default_factory=list)
    mentioned_activities: list[str] = field(default_factory=list)
    recent_memory_ids: list[str] = field(default_factory=list)
    recent_concepts: list[str] = field(default_factory=list)
    latest_concepts: list[str] = field(default_factory=list)
    last_patient_response: str | None = None
    conversation_depth: int = 0
    pending_reminder: dict[str, Any] | None = None
    paused_memory_session: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationState":
        fields = {field_name for field_name in cls.__dataclass_fields__}
        return cls(**{key: value for key, value in data.items() if key in fields})

    def remember_concepts(self, concepts: dict[str, list[str]], response: str | None = None) -> None:
        self.latest_concepts = []
        for field_name, values in concepts.items():
            target = getattr(self, field_name)
            for value in values:
                if value and value not in target:
                    target.append(value)
                if value and value not in self.latest_concepts:
                    self.latest_concepts.append(value)
                if field_name == "active_topics" and value and value not in self.recent_concepts:
                    self.recent_concepts.append(value)
        if response is not None:
            self.last_patient_response = response
        self.conversation_depth += 1
