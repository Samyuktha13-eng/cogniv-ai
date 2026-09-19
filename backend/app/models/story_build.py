from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class BuildStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class StoryBuild(BaseModel):
    build_id: str
    patient_id: str
    status: BuildStatus
    documents_found: int = 0
    images_found: int = 0
    voice_found: int = 0
    chapters_found: int = 0
    image_groups_matched: int = 0
    narration_prepared: int = 0
    error: str | None = None
    created_at: datetime
    updated_at: datetime
