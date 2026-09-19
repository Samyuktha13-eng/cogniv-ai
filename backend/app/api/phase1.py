from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..models.asset import AssetType
from ..models.care_plan import CarePlan
from ..models.patient_folder import FolderAssetType
from ..models.video_job import VideoJobStatus
from ..models.recognition import SpeechTranscript
from ..models.session_event import SessionEvent
from ..services.gameplay import GamePlayService
from ..services.story_playback import StoryAgent
from ..services.session_store import save_event, save_audio, finalise_session
from ..services.patient_library import (
    BUILDS,
    VIDEO_JOBS,
    build_story,
    create_video_jobs,
    get_folder,
    save_folder_asset,
    uploaded_story_supports_prompt,
)
from ..services.grounding import GroundingAgent
from ..services.phase1 import (
    ASSETS,
    CARE_PLANS,
    SPEECH_JOBS,
    SESSIONS,
    create_session,
    find_beat_for_prompt,
    patient_chapters,
    patient_profile,
    save_upload,
    story_catalog,
)
import uuid
from datetime import datetime, timezone
from ..models.speech_job import SpeechJob

router = APIRouter(prefix="/api", tags=["phase1"])


class SessionRequest(BaseModel):
    patient_id: str
    story_id: str | None = None
    prompt: str | None = None
    narration_language: str = "en"


class PromptRequest(BaseModel):
    patient_id: str
    story_id: str
    prompt: str


class TranscriptRequest(BaseModel):
    text: str
    language: str = "en"
    confidence: float | None = None


class SpeechCompletionRequest(BaseModel):
    text: str
    language: str = "en"
    confidence: float | None = None


class BuildRequest(BaseModel):
    force: bool = False


@router.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    patient = patient_profile(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/patient/{patient_id}/story")
def get_patient_story(patient_id: str):
    patient = patient_profile(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"patient": patient, "chapters": patient_chapters(), "stories": story_catalog()}


@router.get("/patients/{patient_id}/folder")
def get_patient_folder(patient_id: str):
    try:
        return get_folder(patient_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/patients/{patient_id}/folder/story-document")
async def upload_story_document(patient_id: str, document: UploadFile = File(...), story_reference: str | None = None):
    try:
        return save_folder_asset(
            patient_id,
            FolderAssetType.STORY_DOCUMENT,
            document.filename or "story-document",
            await document.read(),
            story_reference=story_reference,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/patients/{patient_id}/folder/images")
async def upload_story_images(
    patient_id: str,
    images: list[UploadFile] = File(...),
    relative_paths: list[str] | None = Form(None),
):
    if relative_paths is not None and len(relative_paths) != len(images):
        raise HTTPException(
            status_code=400,
            detail=f"relative_paths count ({len(relative_paths)}) must match uploaded files count ({len(images)})",
        )
    assets = []
    try:
        for index, image in enumerate(images):
            relative_path = relative_paths[index] if relative_paths else image.filename
            assets.append(save_folder_asset(
                patient_id,
                FolderAssetType.IMAGE,
                image.filename or "image",
                await image.read(),
                relative_path=relative_path,
            ))
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return assets


@router.post("/patients/{patient_id}/folder/voice")
async def upload_story_voice(patient_id: str, audio: UploadFile = File(...)):
    try:
        asset = save_folder_asset(
            patient_id,
            FolderAssetType.VOICE_STORY,
            audio.filename or "story-recording.wav",
            await audio.read(),
        )
        return {"asset": asset, "transcript_status": "queued"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/patients/{patient_id}/story/build")
def build_patient_story(patient_id: str, request: BuildRequest | None = None):
    try:
        return build_story(patient_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/patients/{patient_id}/story/build-status")
def get_story_build_status(patient_id: str):
    try:
        folder = get_folder(patient_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    build = BUILDS.get(folder.build_id) if folder.build_id else None
    return build or {"status": "not_built", "patient_id": patient_id}


@router.post("/patients/{patient_id}/videos/generate")
def generate_patient_videos(patient_id: str):
    try:
        return create_video_jobs(patient_id)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/patients/{patient_id}/videos")
def list_patient_videos(patient_id: str):
    return [job for job in VIDEO_JOBS.values() if job.patient_id == patient_id]


@router.get("/patients/{patient_id}/videos/status")
def patient_video_status(patient_id: str):
    jobs = [job for job in VIDEO_JOBS.values() if job.patient_id == patient_id]
    counts = {status.value: 0 for status in VideoJobStatus}
    for job in jobs:
        counts[job.status.value] += 1
    return {
        "status": "completed" if jobs and counts.get("completed", 0) == len(jobs) else "processing" if jobs else "not_started",
        "total": len(jobs),
        "completed": counts.get("completed", 0),
        "processing": counts.get("processing", 0),
        "waiting": counts.get("waiting", 0) + counts.get("queued", 0),
        "failed": counts.get("failed", 0),
    }


@router.post("/assets/{patient_id}/image")
async def upload_image(patient_id: str, image: UploadFile = File(...), story_reference: str | None = None):
    try:
        return save_upload(patient_id, AssetType.IMAGE, image.filename or "image", await image.read(), story_reference)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/assets/{patient_id}/voice")
async def upload_voice(patient_id: str, audio: UploadFile = File(...)):
    try:
        asset = save_upload(patient_id, AssetType.VOICE, audio.filename or "voice", await audio.read())
        return {"asset": asset, "status": "received", "transcription_status": "pending"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/assets/{patient_id}")
def list_assets(patient_id: str):
    return [asset for asset in ASSETS.values() if asset.patient_id == patient_id]


@router.post("/story/resolve")
def resolve_prompt(request: PromptRequest):
    patient = patient_profile(request.patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    beat = find_beat_for_prompt(request.story_id, request.prompt)
    if beat is None:
        raise HTTPException(status_code=404, detail="No matching story beat found")
    return {
        "story_id": request.story_id,
        "beat_id": beat.id,
        "action": beat.action,
        "motion_sequence": beat.motion_sequence,
        "narration": beat.narration,
        "image_path": beat.image_path,
    }


@router.post("/game/sessions")
def start_session(request: SessionRequest):
    try:
        story_id = request.story_id
        if story_id is None and request.prompt:
            folder = get_folder(request.patient_id)
            if folder.story_status != "ready" or not folder.documents:
                raise HTTPException(
                    status_code=409,
                    detail="Upload patient story documents and build the story before starting from a prompt",
                )
            result = GroundingAgent().resolve(request.prompt)
            if not result.match or result.scene_plan is None:
                raise HTTPException(status_code=422, detail={
                    "error": "no_grounded_story_match",
                    "reason": result.reason,
                })
            if not uploaded_story_supports_prompt(folder, request.prompt, result.scene_plan.story_id):
                raise HTTPException(status_code=422, detail={
                    "error": "prompt_not_found_in_uploaded_patient_story",
                    "reason": "no_uploaded_story_evidence_match",
                })
            story_id = result.scene_plan.story_id
        if story_id is None:
            raise HTTPException(status_code=422, detail="Provide story_id or prompt")
        session = create_session(request.patient_id, story_id)
        session.narration_language = request.narration_language
        return session
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.put("/patients/{patient_id}/care-plan")
def set_care_plan(patient_id: str, care_plan: CarePlan):
    if patient_profile(patient_id) is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    if care_plan.patient_id != patient_id:
        raise HTTPException(status_code=400, detail="Care plan patient_id does not match route")
    CARE_PLANS[patient_id] = care_plan
    return care_plan


@router.get("/game/sessions/{session_id}")
def get_session(session_id: str):
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game session not found")
    return session


@router.post("/game/sessions/{session_id}/play")
def play_session_beat(session_id: str):
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game session not found")
    try:
        result = GamePlayService(
            session,
            StoryAgent(session.story_id),
            CARE_PLANS.get(session.patient_id),
        ).play_next()
    except (RuntimeError, ValueError) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return result


@router.post("/game/sessions/{session_id}/recognition")
def submit_recognition(session_id: str, request: TranscriptRequest):
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game session not found")
    try:
        return GamePlayService(
            session,
            StoryAgent(session.story_id),
            CARE_PLANS.get(session.patient_id),
        ).submit_transcript(SpeechTranscript(**request.model_dump()))
    except (RuntimeError, ValueError) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/game/sessions/{session_id}/recognition/audio")
async def submit_recognition_audio(session_id: str, audio: UploadFile = File(...)):
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game session not found")
    try:
        asset = save_upload(session.patient_id, AssetType.VOICE, audio.filename or "recognition.wav", await audio.read())
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    job = SpeechJob(job_id=str(uuid.uuid4()), session_id=session_id, asset_id=asset.asset_id)
    SPEECH_JOBS[job.job_id] = job
    return job


@router.get("/speech/jobs/{job_id}")
def get_speech_job(job_id: str):
    job = SPEECH_JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Speech job not found")
    return job


@router.post("/speech/jobs/{job_id}/complete")
def complete_speech_job(job_id: str, request: SpeechCompletionRequest):
    job = SPEECH_JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Speech job not found")
    job.status = "completed"
    job.transcript = request.text
    job.language = request.language
    job.confidence = request.confidence
    return job


@router.post("/game/sessions/{session_id}/replay")
def replay_session_beat(session_id: str):
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game session not found")
    try:
        return GamePlayService(
            session,
            StoryAgent(session.story_id),
            CARE_PLANS.get(session.patient_id),
        ).replay()
    except (RuntimeError, ValueError) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/game/sessions/{session_id}/care-reminder/acknowledge")
def acknowledge_care_reminder(session_id: str):
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game session not found")
    acknowledged = GamePlayService(
        session,
        StoryAgent(session.story_id),
        CARE_PLANS.get(session.patient_id),
    ).acknowledge_care_reminder()
    return {"acknowledged": acknowledged, "session_id": session_id}


# ---------------------------------------------------------------------------
# Interaction endpoints  (speak / skip / end session / report)
# ---------------------------------------------------------------------------

class InteractionRequest(BaseModel):
    beat_id: str
    beat_sequence: int
    question: str
    spoken: bool
    transcript: str | None = None
    transcript_language: str = "en"
    asr_confidence: float | None = None
    audio_path: str | None = None


@router.post("/game/sessions/{session_id}/interaction")
async def record_interaction(
    session_id: str,
    request: InteractionRequest,
):
    """Store one beat interaction (speak or skip). No right/wrong feedback."""
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game session not found")

    now = datetime.now(timezone.utc)

    event = SessionEvent(
        event_id=str(uuid.uuid4()),
        session_id=session_id,
        patient_id=session.patient_id,
        story_id=session.story_id,
        beat_id=request.beat_id,
        sequence=request.beat_sequence,
        question=request.question,
        question_language=request.transcript_language,
        spoken=request.spoken,
        audio_path=request.audio_path,
        transcript=request.transcript,
        transcript_language=request.transcript_language if request.spoken else None,
        asr_confidence=request.asr_confidence,
        started_at=now,
        completed_at=now,
    )
    save_event(event)
    session.event_ids.append(event.event_id)
    session.last_transcript = request.transcript

    return {"event_id": event.event_id, "stored": True}


# In-memory event store keyed by event_id (session events are also on disk)
_SESSION_EVENTS: dict[str, list[SessionEvent]] = {}


@router.post("/game/sessions/{session_id}/interaction/audio")
async def record_interaction_audio(
    session_id: str,
    beat_id: str = Form(...),
    beat_sequence: int = Form(...),
    question: str = Form(...),
    transcript: str | None = Form(default=None),
    transcript_language: str = Form(default="en"),
    asr_confidence: float | None = Form(default=None),
    audio: UploadFile = File(...),
):
    """Multipart form version: audio file + metadata in one request."""
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game session not found")

    now = datetime.now(timezone.utc)
    data = await audio.read()
    audio_path = save_audio(session.patient_id, session_id, beat_id, beat_sequence, data) if data else None

    event = SessionEvent(
        event_id=str(uuid.uuid4()),
        session_id=session_id,
        patient_id=session.patient_id,
        story_id=session.story_id,
        beat_id=beat_id,
        sequence=beat_sequence,
        question=question,
        question_language=transcript_language,
        spoken=True,
        audio_path=audio_path,
        transcript=transcript,
        transcript_language=transcript_language,
        asr_confidence=asr_confidence,
        started_at=now,
        completed_at=now,
    )
    save_event(event)
    session.event_ids.append(event.event_id)
    session.last_transcript = transcript
    return {"event_id": event.event_id, "stored": True}


@router.post("/game/sessions/{session_id}/end")
def end_session(session_id: str):
    """Finalise session: write session_transcript.json + story_difference_report.docx."""
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game session not found")

    from ..services.session_store import PATIENT_LIBRARY_ROOT
    import json
    from pathlib import Path

    # Reload events from disk for this session
    transcript_dir = (
        PATIENT_LIBRARY_ROOT / session.patient_id / "sessions" / session_id / "transcripts"
    )
    events: list[SessionEvent] = []
    if transcript_dir.is_dir():
        for f in sorted(transcript_dir.glob("*.json")):
            try:
                events.append(SessionEvent.model_validate(json.loads(f.read_text(encoding="utf-8"))))
            except Exception:
                pass

    patient = patient_profile(session.patient_id)
    patient_name = patient.name if patient else session.patient_id

    report = finalise_session(
        session_id=session_id,
        patient_id=session.patient_id,
        patient_name=patient_name,
        stories_played=[session.story_id],
        events=events,
        started_at=session.started_at,
    )

    from ..models.game_session import SessionStatus
    session.status = SessionStatus.COMPLETED

    return {
        "session_id": session_id,
        "status": "completed",
        "total_beats": report.total_beats,
        "spoken_responses": report.spoken_responses,
        "skipped_responses": report.skipped_responses,
        "supported_content": len(report.supported_content),
        "unsupported_content": len(report.unsupported_content),
        "report_path": report.report_path,
        "download_url": f"/api/game/sessions/{session_id}/report",
    }


@router.get("/game/sessions/{session_id}/report")
def download_report(session_id: str):
    """Download the story difference report (.docx or .txt fallback)."""
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game session not found")

    from ..services.session_store import PATIENT_LIBRARY_ROOT
    from pathlib import Path

    session_dir = PATIENT_LIBRARY_ROOT / session.patient_id / "sessions" / session_id
    for ext in (".docx", ".txt"):
        candidates = list(session_dir.glob(f"*Story_Differences{ext}"))
        candidates += list(session_dir.glob(f"story_difference_report{ext}"))
        if candidates:
            path = candidates[0]
            media = (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if ext == ".docx" else "text/plain"
            )
            return FileResponse(str(path), media_type=media, filename=path.name)

    raise HTTPException(status_code=404, detail="Report not yet generated. Call /end first.")
