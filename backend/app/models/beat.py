from enum import Enum

from pydantic import BaseModel, Field


class BeatStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class StoryBeat(BaseModel):
    id: str
    story_id: str

    sequence: int = Field(ge=1)

    image_path: str
    end_image_path: str | None = None

    action: str
    motion: str
    camera: str

    motion_sequence: list[str] = Field(default_factory=list)
    motion_constraints: list[str] = Field(default_factory=list)
    camera_motion: str | None = None
    image_strength: float = Field(default=1.0, ge=0.0, le=1.0)
    guidance_scale: float = Field(default=1.0, ge=0.0, le=10.0)
    enable_prompt_expansion: bool = False
    num_frames: int = Field(default=121, gt=0)
    frames_per_second: int = Field(default=24, gt=0)

    duration: float = Field(default=5.0, gt=0)

    language: str = "en"

    narration: str | None = None
    narration_by_language: dict[str, str] = Field(default_factory=dict)

    voice_enabled: bool = True

    status: BeatStatus = BeatStatus.PENDING

    video_url: str | None = None
    audio_url: str | None = None
