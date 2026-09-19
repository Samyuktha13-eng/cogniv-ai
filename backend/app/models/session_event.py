from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class SessionEvent(BaseModel):
    event_id: str
    session_id: str
    patient_id: str
    story_id: str
    beat_id: str
    sequence: int
    question: str
    question_language: str = "en"
    spoken: bool                        # True = patient spoke; False = skipped
    audio_path: str | None = None       # relative path inside session folder
    transcript: str | None = None       # raw ASR output, never modified
    transcript_language: str | None = None
    asr_confidence: float | None = None
    started_at: datetime
    completed_at: datetime | None = None
