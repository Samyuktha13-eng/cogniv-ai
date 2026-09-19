import os
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from backend.magic_hour_video import RenderPreflightError, generate_video_from_bytes
from backend.story_video_service import generate_story_videos, get_story_definition

router = APIRouter(prefix="/video", tags=["video"])

TEMPLE_EXIT_SCENE_ID = "memory_04_temple_exit"
TEMPLE_EXIT_PROMPT = """Use the supplied exterior temple image as the actual visual reference.
Create a warm realistic nostalgic childhood memory of Lakshmi and her young daughter Anu coming out of the temple after seeing Krishna.
Preserve Lakshmi's established identity and keep Anu as the same young girl, never the adult woman from any other reference. Do not age or de-age either character, replace characters, morph faces, or add prominent unrelated people.
Preserve the same stone temple architecture, gopuram, lush green trees, tropical plants, flowers, stone pathway, and peaceful garden shown in the supplied reference. Do not redesign the temple or environment.
Lakshmi and young Anu slowly walk out from the temple entrance together, side by side along the garden pathway. Lakshmi gently holds Anu's hand. Anu looks happily at the flowers and trees, briefly looks back toward the temple, and Lakshmi smiles warmly at her.
Use natural walking, hand, eye, facial, saree and hair movement only. Begin near the entrance and slowly follow them with a gentle backward tracking shot, keeping the gopuram visible. End on a wider peaceful garden view.
Warm natural afternoon sunlight, soft shadows, photorealistic Indian family memory, stable 16:9 landscape composition, 5-8 seconds. No shaky camera, sudden cuts, dramatic movement, extra limbs, fantasy environment, or modern buildings."""


class VideoGenerateRequest(BaseModel):
    action_name: str
    prompt: str
    reference_images: list[str] = []


@router.get("/health")
async def video_health():
    return {
        "status": "ok",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "magic_hour_configured": bool(os.getenv("MAGIC_HOUR_API_KEY")),
        "videos_dir": str((Path(__file__).resolve().parents[1] / "assets" / "animations").resolve()),
    }


@router.post("/generate")
async def generate_video(request: VideoGenerateRequest):
    try:
        from backend.video.veo_generator import VeoVideoGenerator

        generator = VeoVideoGenerator()
        target = generator.ensure_video(
            action_name=request.action_name,
            prompt=request.prompt,
            reference_images=request.reference_images,
        )
        return {
            "action_name": request.action_name,
            "file": f"/videos/{request.action_name}.mp4",
            "local_path": str(target),
            "generated": True,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/story/lakshmi-anu")
async def generate_lakshmi_anu_story(limit: int | None = Query(default=None, ge=1)):
    try:
        resolution = os.getenv("MAGIC_HOUR_DEFAULT_RESOLUTION", "480p")
        result = generate_story_videos(model="ltx-2.3", resolution=resolution, scene_limit=limit)
        return result
    except RenderPreflightError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": exc.code, "message": exc.message},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/story/temple-exit")
async def generate_temple_exit(reference_image: UploadFile = File(...)):
    """Generate only memory_04_temple_exit from the image uploaded in this request."""
    image_bytes = await reference_image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded temple reference image is empty")

    try:
        result = generate_video_from_bytes(
            image_bytes=image_bytes,
            prompt=TEMPLE_EXIT_PROMPT,
            output_dir="generated_videos",
            duration=6,
            model="ltx-2.3",
            resolution=os.getenv("MAGIC_HOUR_DEFAULT_RESOLUTION", "480p"),
            name=TEMPLE_EXIT_SCENE_ID,
        )
        return {
            "scene_id": TEMPLE_EXIT_SCENE_ID,
            "file": "/videos/memory_04_temple_exit.mp4",
            "generated": True,
            "provider_result": result,
        }
    except RenderPreflightError as exc:
        raise HTTPException(status_code=409, detail={"code": exc.code, "message": exc.message})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/story/lakshmi-anu")
async def get_lakshmi_anu_story(limit: int | None = Query(default=None, ge=1)):
    try:
        return get_story_definition(scene_limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/file/{action_name}")
async def get_video_file(action_name: str):
    video_path = Path(__file__).resolve().parents[1] / "assets" / "animations" / f"{action_name}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"Video not found for action {action_name}")
    return {"file": f"/videos/{action_name}.mp4", "exists": True}
