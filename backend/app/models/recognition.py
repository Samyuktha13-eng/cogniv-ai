from pydantic import BaseModel, Field


class RecognitionResult(BaseModel):
    outcome: str
    transcript: str
    language: str
    confidence: float | None = None
    feedback: str
    next_beat_id: str | None = None
    recovery_required: bool = False


class SpeechTranscript(BaseModel):
    text: str
    language: str
    confidence: float | None = None
    engine: str = "adapter"


class RecognitionCheckpoint(BaseModel):
    beat_id: str
    question: str
    expected_concepts: list[str] = Field(min_length=1)
    acceptable_answers: list[str] = Field(min_length=1)
