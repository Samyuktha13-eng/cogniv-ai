from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class FolderAssetType(str, Enum):
    STORY_DOCUMENT = "story_document"
    IMAGE = "image"
    VOICE_STORY = "voice_story"
    TRANSCRIPT_DOCUMENT = "transcript_document"


class FolderAsset(BaseModel):
    asset_id: str
    patient_id: str
    type: FolderAssetType
    name: str
    path: str
    relative_path: str
    status: str = "ready"
    story_reference: str | None = None
    created_at: datetime


class PatientFolder(BaseModel):
    patient_id: str
    documents: list[FolderAsset] = Field(default_factory=list)
    image_assets: list[FolderAsset] = Field(default_factory=list)
    voice_story: FolderAsset | None = None
    voice_transcript: FolderAsset | None = None
    story_status: str = "not_built"
    generation_status: str = "not_started"
    game_status: str = "not_ready"
    build_id: str | None = None
    build_summary: dict[str, int] = Field(default_factory=dict)
    document_text: dict[str, str] = Field(default_factory=dict)
