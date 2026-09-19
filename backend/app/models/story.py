from pydantic import BaseModel, Field

from .beat import StoryBeat


class Story(BaseModel):
    id: str
    title: str
    description: str

    available_languages: list[str] = Field(default_factory=lambda: ["en", "hi", "te", "ta"])

    beats: list[StoryBeat] = Field(default_factory=list)
