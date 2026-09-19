"""
Game API
========
POST /api/game/start          — caregiver text prompt → grounded GameSession
POST /api/game/{session_id}/next      — advance to next beat
POST /api/game/{session_id}/speak     — patient audio → ASR → recognition result
POST /api/game/{session_id}/replay    — replay current beat
POST /api/game/{session_id}/reminder/acknowledge

The caregiver prompt drives story/beat selection via the GroundingAgent.
The patient's voice is stored as a raw interaction for later story comparison.
"""
from __future__ import annotations

import uuid
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from ..models.game_session import GameSession, SessionStatus
from ..models.memory_graph import MemoryGraph, MemoryNode
from ..services.gameplay import GamePlayService, LibraryVideoProvider
from ..services.grounding import GroundingAgent
from ..services.recognition import RecognitionService
from ..services.session_store import SESSION_STORE
from ..services.story_playback import StoryAgent

router = APIRouter(prefix="/api/game", tags=["game"])

_recognition = RecognitionService()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class StartRequest(BaseModel):
    patient_id: str
    prompt: str                     # caregiver text prompt
    story_id: str | None = None     # override: skip grounding, use this story
    narration_language: str = "en"


class StartResponse(BaseModel):
    session_id: str
    patient_id: str
    story_id: str
    beat_id: str | None
    grounded: bool
    grounding_source: str
    reference_images: list[str]
    memory_graph_node: dict | None = None
    message: str = ""


# ---------------------------------------------------------------------------
# POST /api/game/start
# ---------------------------------------------------------------------------

@router.post("/start", response_model=StartResponse)
def start_game(request: StartRequest):
    """
    Caregiver text prompt → GroundingAgent → GameSession.

    If grounding fails (no story match), returns 422 with a clarification
    message instead of inventing a scene.
    """
    # 1. Resolve prompt unless story_id is explicitly provided
    if request.story_id:
        story_id = request.story_id
        grounding_source = f"caregiver_override:story:{story_id}"
        reference_images: list[str] = []
        beat_id_hint: str | None = None
    else:
        result = GroundingAgent().resolve(request.prompt)
        if not result.match:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "no_grounded_story_match",
                    "reason": result.reason,
                    "message": (
                        "No patient story matches this prompt. "
                        "Please describe the memory more specifically, "
                        "or choose one of the five available stories."
                    ),
                },
            )
        plan = result.scene_plan
        story_id = plan.story_id
        grounding_source = plan.grounding_source
        reference_images = plan.reference_images
        beat_id_hint = plan.beat_id

    # 2. Create GameSession
    session_id = str(uuid.uuid4())
    session = GameSession(
        session_id=session_id,
        patient_id=request.patient_id,
        story_id=story_id,
        narration_language=request.narration_language,
    )

    # 3. If grounding found a specific beat, pre-queue it
    if beat_id_hint:
        # Start from the grounded beat by marking earlier beats as skipped
        story_agent = StoryAgent(story_id)
        beats = story_agent.beats()
        for b in beats:
            if b.id == beat_id_hint:
                break
            session.completed_beat_ids.append(b.id)

    SESSION_STORE[session_id] = session

    # 4. Build a MemoryGraph node for this session
    memory_node = MemoryNode(
        beat_id=beat_id_hint or "",
        story_id=story_id,
        patient_id=request.patient_id,
        grounding_source=grounding_source,
        reference_images=reference_images,
    ) if beat_id_hint else None

    # 5. Play the first beat immediately
    story_agent = StoryAgent(story_id)
    service = GamePlayService(session, story_agent, video_provider=LibraryVideoProvider())
    first_beat = service.play_next()

    return StartResponse(
        session_id=session_id,
        patient_id=request.patient_id,
        story_id=story_id,
        beat_id=session.current_beat_id,
        grounded=bool(beat_id_hint),
        grounding_source=grounding_source,
        reference_images=reference_images,
        memory_graph_node=memory_node.model_dump(mode="json") if memory_node else None,
        message=f"Session started. {first_beat.get('narration', {}).get('text', '')}",
    )


# ---------------------------------------------------------------------------
# POST /api/game/{session_id}/next
# ---------------------------------------------------------------------------

@router.post("/{session_id}/next")
def next_beat(session_id: str):
    session = _get_session(session_id)
    story_agent = StoryAgent(session.story_id)
    service = GamePlayService(session, story_agent, video_provider=LibraryVideoProvider())
    result = service.play_next()
    SESSION_STORE[session_id] = session
    return result


# ---------------------------------------------------------------------------
# POST /api/game/{session_id}/speak  — patient audio → recognition
# ---------------------------------------------------------------------------

@router.post("/{session_id}/speak")
async def patient_speaks(
    session_id: str,
    audio: UploadFile = File(...),
    language: str = "en",
):
    """
        Receives patient audio, transcribes it, and returns the raw transcript.
        The transcript is not scored during playback; the session report performs
        the later comparison against canonical patient evidence.
    """
    session = _get_session(session_id)
    if session.status != SessionStatus.WAITING_FOR_SPEECH:
        raise HTTPException(
            status_code=409,
            detail=f"Session is in state '{session.status}', not waiting for speech.",
        )
    if not session.current_beat_id:
        raise HTTPException(status_code=409, detail="No current beat to evaluate.")

    # Transcribe
    transcript = await _transcribe(audio, session_id, language)

    session.last_transcript = transcript
    session.last_recognition_outcome = None
    session.status = SessionStatus.READY

    SESSION_STORE[session_id] = session

    return {
        "session_id": session_id,
        "beat_id": session.current_beat_id,
        "transcript": transcript,
        "language": language,
        "outcome": None,
        "feedback": None,
        "next_action": "play_next",
    }


# ---------------------------------------------------------------------------
# POST /api/game/{session_id}/replay
# ---------------------------------------------------------------------------

@router.post("/{session_id}/replay")
def replay_beat(session_id: str):
    session = _get_session(session_id)
    story_agent = StoryAgent(session.story_id)
    service = GamePlayService(session, story_agent, video_provider=LibraryVideoProvider())
    result = service.replay()
    SESSION_STORE[session_id] = session
    return result


# ---------------------------------------------------------------------------
# POST /api/game/{session_id}/reminder/acknowledge
# ---------------------------------------------------------------------------

@router.post("/{session_id}/reminder/acknowledge")
def acknowledge_reminder(session_id: str):
    session = _get_session(session_id)
    story_agent = StoryAgent(session.story_id)
    service = GamePlayService(session, story_agent, video_provider=LibraryVideoProvider())
    acknowledged = service.acknowledge_care_reminder()
    SESSION_STORE[session_id] = session
    return {"acknowledged": acknowledged, "session_id": session_id}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_session(session_id: str) -> GameSession:
    session = SESSION_STORE.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


async def _transcribe(audio: UploadFile, session_id: str, language: str) -> str:
    """
    Write upload to a temp file and run the Indic Conformer ASR.
    Falls back to an empty string if the model is unavailable.
    """
    suffix = Path(audio.filename or "audio.wav").suffix or ".wav"
    with NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        from ..services.asr_provider import IndicConformerASRProvider
        from pathlib import Path as _Path
        project_root = _Path(__file__).resolve().parents[3]
        provider = IndicConformerASRProvider(project_root)
        job = await provider.submit(tmp_path, session_id, language)
        result = await provider.get_result(job)
        return result.text
    except Exception:
        # ASR unavailable in this environment — return empty so caller can retry
        return ""
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass
