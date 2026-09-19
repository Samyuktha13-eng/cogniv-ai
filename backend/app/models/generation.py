from enum import Enum

from pydantic import BaseModel


class GenerationStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationJob(BaseModel):
    id: str
    beat_id: str

    provider: str = "pixazo"
    model: str = "ltx-video"

    status: GenerationStatus = GenerationStatus.PENDING

    request_id: str | None = None

    source_image_url: str | None = None
    prompt: str

    output_url: str | None = None
    local_path: str | None = None

    error: str | None = None
