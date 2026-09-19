from pydantic import BaseModel, Field


class NarrationAsset(BaseModel):
    beat_id: str
    language: str
    text: str
    audio_url: str | None = None
    status: str = "pending"


class NarrationCatalog(BaseModel):
    beat_id: str
    narration_by_language: dict[str, str] = Field(default_factory=dict)
    fallback_language: str = "en"
