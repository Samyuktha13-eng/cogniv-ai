from pydantic import BaseModel, Field


class StoryDerivedActivity(BaseModel):
    activity_id: str
    label: str
    evidence: list[str] = Field(min_length=1)
    beat_ids: list[str] = Field(default_factory=list)
    source: str = "story"
