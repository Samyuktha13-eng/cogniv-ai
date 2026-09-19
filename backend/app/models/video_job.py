from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class VideoJobStatus(str, Enum):
    WAITING = "waiting"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoJob(BaseModel):
    job_id: str
    patient_id: str
    story_id: str
    scene_id: str
    provider: str = "pixazo"
    status: VideoJobStatus = VideoJobStatus.WAITING
    provider_job_id: str | None = None
    output_path: str | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
