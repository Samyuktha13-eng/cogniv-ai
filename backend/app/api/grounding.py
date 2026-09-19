"""
Grounding API
=============
POST /api/grounding/resolve   — resolve a caregiver prompt to a ScenePlan (dry-run)
POST /api/grounding/generate  — resolve + create VideoJob + submit to Pixazo
"""
from __future__ import annotations

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models.grounding import GroundingResult
from ..services.grounding import GroundingAgent

router = APIRouter(prefix="/api/grounding", tags=["grounding"])


class GroundingRequest(BaseModel):
    patient_id: str
    prompt: str


class GenerateRequest(BaseModel):
    patient_id: str
    prompt: str


@router.post("/resolve", response_model=GroundingResult)
def resolve_prompt(request: GroundingRequest) -> GroundingResult:
    """
    Resolve a caregiver prompt to a grounded ScenePlan without generating anything.
    Returns match=False with a reason if no story beat can be found.
    """
    result = GroundingAgent().resolve(request.prompt)
    if not result.match:
        # Still 200 — the caller decides what to do with a no-match
        return result
    return result


@router.post("/generate")
def grounded_generate(request: GenerateRequest):
    """
    Full pipeline:
      1. Resolve prompt → ScenePlan
      2. Create a VideoJob for the matched beat
      3. Submit to Pixazo using the grounded video prompt
      4. Return the job + scene plan
    """
    from ..services.patient_library import create_video_job_for_beat, VIDEO_JOBS
    from ..services.assets import STORY_IMAGE_ROOT, StoryAssetService, AssetPublishError, UnsupportedAssetError
    from ..services.pixazo import PixazoVideoService
    from ..data.stories import get_story

    result = GroundingAgent().resolve(request.prompt)
    if not result.match:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "no_grounded_story_match",
                "reason": result.reason,
                "prompt": request.prompt,
                "message": (
                    "No patient story matches this prompt. "
                    "Please clarify the memory you want to show."
                ),
            },
        )

    plan = result.scene_plan
    story = get_story(plan.story_id)
    beat = next((b for b in story.beats if b.id == plan.beat_id), None)
    if beat is None:
        raise HTTPException(status_code=500, detail="Grounded beat not found in story registry")

    # Create a targeted VideoJob
    try:
        job = create_video_job_for_beat(
            request.patient_id,
            plan.story_id,
            plan.beat_id,
            plan.reference_images,
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    # Submit to Pixazo using the grounded prompt
    image_path = STORY_IMAGE_ROOT / beat.image_path
    try:
        image_path = image_path.resolve()
        image_path.relative_to(STORY_IMAGE_ROOT.resolve())
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Invalid source image path") from error

    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Source image file not found")

    try:
        asset_service = StoryAssetService()
        image_url = asset_service.publish_image(image_path)
        asset_service.validate_public_image_url(image_url)

        pixazo_job = PixazoVideoService().submit(
            beat_id=beat.id,
            image_url=image_url,
            prompt=plan.video_prompt,
            duration=6,
            image_strength=beat.image_strength,
            guidance_scale=beat.guidance_scale,
            enable_prompt_expansion=beat.enable_prompt_expansion,
            num_frames=beat.num_frames,
            frames_per_second=beat.frames_per_second,
        )
    except UnsupportedAssetError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except AssetPublishError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except requests.RequestException as error:
        detail = error.response.text if error.response is not None else str(error)
        raise HTTPException(status_code=502, detail=f"Pixazo submission failed: {detail}") from error

    # Update the VideoJob with the provider job id
    job.provider_job_id = pixazo_job.request_id
    from ..models.video_job import VideoJobStatus
    job.status = VideoJobStatus.PROCESSING
    VIDEO_JOBS[job.job_id] = job

    from ..services.patient_library import _save_index
    _save_index()

    return {
        "job_id": job.job_id,
        "provider_job_id": pixazo_job.request_id,
        "story_id": plan.story_id,
        "beat_id": plan.beat_id,
        "grounding_source": plan.grounding_source,
        "reference_images": plan.reference_images,
        "scene_plan": plan.model_dump(),
        "polling_url": f"https://gateway.pixazo.ai/v2/requests/status/{pixazo_job.request_id}",
    }
