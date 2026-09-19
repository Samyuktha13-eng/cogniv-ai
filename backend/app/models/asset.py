from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel


class AssetType(str, Enum):
    STORY_DOCUMENT = "story_document"
    IMAGE = "image"
    VOICE = "voice"


class PatientAsset(BaseModel):
    asset_id: str
    patient_id: str
    type: AssetType
    original_filename: str
    path: str
    story_reference: str | None = None
    created_at: datetime

    @classmethod
    def now(cls, **values):
        return cls(created_at=datetime.now(timezone.utc), **values)
