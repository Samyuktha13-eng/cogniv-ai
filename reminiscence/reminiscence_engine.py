"""Conversation orchestration without ASR, matching, or long-term writes."""

from __future__ import annotations

from typing import Any

from .conversation_state import ConversationState
from .memory_selector import MemoryCandidate, MemorySelector
from .models import MediaRequest, ReminiscenceTurn
from .prompt_builder import follow_up_prompt, opening_prompt, supportive_response


class ReminiscenceEngine:
    def __init__(self, selector: MemorySelector) -> None:
        self.selector = selector

    def start(self, patient_id: str, signals: dict[str, Any] | None = None) -> tuple[ConversationState, ReminiscenceTurn]:
        candidate = self.selector.select(patient_id, signals)
        if candidate is None:
            raise LookupError("No supported memory cue is available")
        state = ConversationState(patient_id=patient_id)
        turn = self._turn(state, candidate, opening_prompt(candidate, (signals or {}).get("time_of_day")))
        state.current_memory_id = candidate.memory_id
        state.current_scene_id = candidate.scene_id
        state.recent_memory_ids.append(candidate.memory_id)
        state.active_topics.extend(candidate.topics[:3])
        return state, turn

    def handle_meaning_result(self, state: ConversationState, meaning_result: dict[str, Any], response_text: str | None = None) -> tuple[ConversationState, ReminiscenceTurn | None]:
        concepts = _concept_fields(meaning_result.get("entities", {}))
        state.remember_concepts(concepts, response_text)
        current = self.selector.select(state.patient_id, {"concepts": state.recent_concepts, "people": state.mentioned_people, "places": state.mentioned_places, "objects": state.mentioned_objects, "activities": state.mentioned_activities}, set(state.recent_memory_ids))
        if current is None:
            return state, None
        state.current_memory_id = current.memory_id
        state.current_scene_id = current.scene_id
        state.recent_memory_ids.append(current.memory_id)
        return state, self._turn(state, current, follow_up_prompt(state, current))

    def response_acknowledgement(self, meaning_result: dict[str, Any]) -> str:
        return supportive_response(meaning_result)

    @staticmethod
    def _turn(state: ConversationState, candidate: MemoryCandidate, prompt: str) -> ReminiscenceTurn:
        media_type = "video" if candidate.video_filename else "image"
        return ReminiscenceTurn(
            memory_id=candidate.memory_id, scene_id=candidate.scene_id, prompt=prompt,
            media=MediaRequest(candidate.memory_id, candidate.scene_id, media_type, filename=candidate.video_filename or candidate.image_filename),
            follow_up_topics=candidate.topics + candidate.people + candidate.places,
        )


def _concept_fields(entities: dict[str, Any]) -> dict[str, list[str]]:
    mapping = {"person": "mentioned_people", "place": "mentioned_places", "object": "mentioned_objects", "activity": "mentioned_activities"}
    concepts: dict[str, list[str]] = {field: [] for field in mapping.values()}
    for key, field_name in mapping.items():
        value = entities.get(key)
        if value:
            concepts[field_name] = value if isinstance(value, list) else [str(value)]
    extra = entities.get("concepts", [])
    concepts["active_topics"] = extra if isinstance(extra, list) else ([str(extra)] if extra else [])
    return concepts
