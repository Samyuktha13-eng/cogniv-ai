from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    transcript_fragment: str
    matched_story_fact: str
    beat_id: str
    question: str = ""
    timestamp: datetime | None = None


class UnsupportedItem(BaseModel):
    transcript_fragment: str
    reason: str          # always "not found in available patient evidence"
    beat_id: str
    question: str = ""
    timestamp: datetime | None = None


class SessionReport(BaseModel):
    session_id: str
    patient_id: str
    patient_name: str
    stories_played: list[str]
    started_at: datetime
    ended_at: datetime
    total_beats: int
    spoken_responses: int
    skipped_responses: int
    events: list[dict] = Field(default_factory=list)   # serialised SessionEvent dicts
    supported_content: list[EvidenceItem] = Field(default_factory=list)
    unsupported_content: list[UnsupportedItem] = Field(default_factory=list)
    report_path: str | None = None      # absolute path to the .docx
