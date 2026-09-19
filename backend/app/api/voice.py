"""
Voice API
=========
POST /api/voice/transcribe          — transcribe any audio (generic)
POST /api/voice/caregiver-prompt    — caregiver speaks → ASR → GroundingAgent resolve
                                      (same result as POST /api/grounding/resolve with text)
"""
from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..models.grounding import GroundingResult
from ..services.grounding import GroundingAgent

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/transcribe")
async def transcribe_voice(
    audio: UploadFile = File(...),
    language: str = Form(default="en"),
):
    """Generic transcription endpoint — returns raw transcript."""
    transcript = await _run_asr(audio, "generic", language)
    return {"transcript": transcript, "language": language}


@router.post("/caregiver-prompt", response_model=GroundingResult)
async def caregiver_voice_prompt(
    patient_id: str = Form(...),
    audio: UploadFile = File(...),
    language: str = Form(default="en"),
):
    """
    Caregiver speaks a memory request.
    Pipeline: audio → ASR → GroundingAgent.resolve → GroundingResult

    Identical contract to POST /api/grounding/resolve but accepts voice.
    Returns match=False (200) when no story matches — never invents.
    """
    transcript = await _run_asr(audio, patient_id, language)
    if not transcript:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "empty_transcript",
                "message": "Could not transcribe the audio. Please try again.",
            },
        )
    result = GroundingAgent().resolve(transcript)
    # Attach the transcript so the caller can display what was heard
    result_dict = result.model_dump()
    result_dict["transcript"] = transcript
    return result_dict


# ---------------------------------------------------------------------------
# Shared ASR helper
# ---------------------------------------------------------------------------

async def _run_asr(audio: UploadFile, session_id: str, language: str) -> str:
    suffix = Path(audio.filename or "audio.wav").suffix or ".wav"
    with NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        from ..services.asr_provider import IndicConformerASRProvider
        project_root = Path(__file__).resolve().parents[3]
        provider = IndicConformerASRProvider(project_root)
        job = await provider.submit(tmp_path, session_id, language)
        result = await provider.get_result(job)
        return result.text
    except Exception:
        return ""
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass
