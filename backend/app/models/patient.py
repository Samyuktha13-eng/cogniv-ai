from pydantic import BaseModel, Field


class PatientProfile(BaseModel):
    patient_id: str
    name: str
    age: int | None = None
    preferred_languages: list[str] = Field(default_factory=lambda: ["en", "hi", "te", "ta"])
    story_id: str
    voice_profile_id: str | None = None
