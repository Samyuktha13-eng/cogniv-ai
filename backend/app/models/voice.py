from enum import Enum

from pydantic import BaseModel


class VoiceType(str, Enum):
    NARRATOR = "narrator"
    CHARACTER = "character"
    PLAYER = "player"


class VoiceAsset(BaseModel):
    id: str
    beat_id: str

    voice_type: VoiceType = VoiceType.NARRATOR

    speaker_id: str | None = None
    language: str = "en"

    text: str

    audio_url: str | None = None
    local_path: str | None = None

    duration: float | None = None

    status: str = "pending"
