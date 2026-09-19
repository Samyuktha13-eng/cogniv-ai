"""Open-ended, supportive reminiscence language."""

from __future__ import annotations

from .conversation_state import ConversationState
from .memory_selector import MemoryCandidate


def opening_prompt(candidate: MemoryCandidate, time_of_day: str | None = None) -> str:
    if candidate.source == "story_scene":
        subject = _subject(candidate.title)
        return f"Does this {subject} remind you of anything?"
    return f"Does {candidate.title.lower()} bring any memories to mind?"


def follow_up_prompt(state: ConversationState, candidate: MemoryCandidate) -> str:
    concepts = (
        state.latest_concepts
        or state.recent_concepts
        or state.mentioned_people
        or state.mentioned_places
        or state.mentioned_objects
        or state.mentioned_activities
        or state.active_topics
    )
    if concepts:
        topic = concepts[0]
        return f"You remember {topic}. Would you like to tell me a little more about that?"
    return f"What do you remember about {candidate.title.lower()}?"


def supportive_response(meaning_result: dict) -> str:
    if meaning_result.get("needs_clarification"):
        return "That is okay. Take your time. Would another little memory cue help?"
    return "That sounds familiar. What happened next?"


def _subject(title: str) -> str:
    lowered = title.casefold()
    for prefix in ("the ", "a "):
        if lowered.startswith(prefix):
            return lowered[len(prefix):]
    return lowered
