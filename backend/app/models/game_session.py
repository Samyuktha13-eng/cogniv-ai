from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    READY = "ready"
    PLAYING = "playing"
    WAITING_FOR_SPEECH = "waiting_for_speech"   # video played, question shown, awaiting speak/skip
    WAITING_FOR_RECOGNITION = "waiting_for_recognition"  # kept for backward compat
    COMPLETED = "completed"


class GameSession(BaseModel):
    session_id: str
    patient_id: str
    story_id: str
    status: SessionStatus = SessionStatus.READY
    current_beat_id: str | None = None
    current_beat_sequence: int = 0
    completed_beat_ids: list[str] = Field(default_factory=list)
    event_ids: list[str] = Field(default_factory=list)   # SessionEvent ids in order
    video_status: str = "not_requested"
    video_url: str | None = None
    video_request_id: str | None = None
    video_error: str | None = None
    narration_language: str = "en"
    narration_text: str | None = None
    current_question: str | None = None
    last_transcript: str | None = None
    last_recognition_outcome: str | None = None
    care_reminder: str | None = None
    care_reminder_id: str | None = None
    presented_care_reminder_ids: list[str] = Field(default_factory=list)
    acknowledged_care_reminder_ids: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
