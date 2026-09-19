from pydantic import BaseModel


class SpeechJob(BaseModel):
    job_id: str
    session_id: str
    asset_id: str
    status: str = "queued"
    language: str | None = None
    transcript: str | None = None
    confidence: float | None = None
    error: str | None = None
