from enum import Enum

from pydantic import BaseModel, Field


class ReminderTrigger(str, Enum):
    AFTER_VIDEO = "after_video"


class ReminderQuestion(BaseModel):
    question_id: str
    type: str = "action_recall"
    language: str = "en"
    prompt: str
    expected_concepts: list[str] = Field(min_length=1)
    acceptable_answers: list[str] = Field(min_length=1)
    hint: str | None = None


class BeatReminder(BaseModel):
    beat_id: str
    enabled: bool = True
    trigger: ReminderTrigger = ReminderTrigger.AFTER_VIDEO
    question: ReminderQuestion
