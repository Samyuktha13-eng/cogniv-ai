import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any, Sequence, Tuple, List

from PIL import Image, ImageDraw, ImageFilter
from dotenv import load_dotenv
from magic_hour import Client

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")

API_KEY = os.getenv("MAGIC_HOUR_API_KEY")
DEFAULT_RESOLUTION = "720p"
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_DURATION = 5.0


class RenderPreflightError(RuntimeError):
    """Raised when a render must be rejected before provider submission."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class RenderPreflight:
    resolution: str
    estimated_credits: int
    available_credits: Optional[int]


def preflight_render(
    resolution: str,
    duration: float = DEFAULT_DURATION,
    model: str = "ltx-2.3",
    supported_resolutions: Optional[Sequence[str]] = None,
    available_credits: Optional[int] = None,
    estimated_credits: Optional[int] = None,
) -> RenderPreflight:
    """Validate provider constraints before creating a Magic Hour job."""
    if not API_KEY:
        raise RenderPreflightError(
            "missing_api_key",
            "Magic Hour is not configured. Add MAGIC_HOUR_API_KEY to backend/.env. No render was attempted.",
        )

    configured_resolutions = supported_resolutions
    if configured_resolutions is None:
        configured_resolutions = tuple(
            value.strip()
            for value in os.getenv("MAGIC_HOUR_SUPPORTED_RESOLUTIONS", "480p").split(",")
            if value.strip()
        )
    if configured_resolutions and resolution not in configured_resolutions:
        raise RenderPreflightError(
            "unsupported_resolution",
            f"{resolution} unavailable for the configured Magic Hour plan. No render was attempted.",
        )

    credit_cost = estimated_credits
    if credit_cost is None:
        configured_cost = os.getenv("MAGIC_HOUR_CREDIT_COST")
        credit_cost = int(configured_cost) if configured_cost else 0
    balance = available_credits
    if balance is None:
        configured_balance = os.getenv("MAGIC_HOUR_CREDITS")
        balance = int(configured_balance) if configured_balance else None
    if balance is not None and balance < credit_cost:
        raise RenderPreflightError(
            "insufficient_credits",
            f"Insufficient Magic Hour credits: render needs {credit_cost}, account has {balance}. No render was attempted.",
        )

    return RenderPreflight(resolution, credit_cost, balance)


def _load_image(path: str | Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    return image


def _fit_to_box(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    iw, ih = img.size
    scale = min(target_w / iw, target_h / ih)
    nw = max(1, int(iw * scale))
    nh = max(1, int(ih * scale))
    return img.resize((nw, nh), Image.Resampling.LANCZOS)


def _center_on_canvas(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    x = (target_w - img.width) // 2
    y = (target_h - img.height) // 2
    canvas.paste(img, (x, y), img)
    return canvas


def _extract_foreground(image: Image.Image) -> Image.Image:
    """Create a soft subject mask for the repository's portrait reference images."""
    if image.getchannel("A").getextrema() != (255, 255):
        return image

    try:
        from rembg import new_session, remove

        return remove(image, session=new_session("u2netp")).convert("RGBA")
    except Exception:
        pass

    width, height = image.size
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(
        [
            (int(width * 0.28), int(height * 0.36)),
            (int(width * 0.35), int(height * 0.25)),
            (int(width * 0.50), int(height * 0.20)),
            (int(width * 0.66), int(height * 0.27)),
            (int(width * 0.76), int(height * 0.40)),
            (int(width * 0.88), height),
            (int(width * 0.08), height),
            (int(width * 0.18), int(height * 0.62)),
        ],
        fill=255,
    )
    image.putalpha(mask.filter(ImageFilter.GaussianBlur(radius=2)))
    return image


def compose_reference_scene(
    scene_id: str,
    room_image: str | Path,
    character_images: List[str | Path],
    object_images: Optional[List[str | Path]] = None,
    output_dir: str | Path = BACKEND_DIR / "generated_references",
    target_size: Tuple[int, int] = (960, 540),
    output_name: Optional[str] = None,
    sofa_occlusion: bool = False,
    standing_layout: bool = False,
    counter_occlusion: bool = False,
) -> str:
    """Create a fixed 16:9 scene composite that acts as the visual source of truth."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    room = _load_image(room_image)
    room = _fit_to_box(room, target_size[0], target_size[1])
    background = Image.new("RGBA", target_size, (240, 220, 200, 255))
    background = _center_on_canvas(room, target_size[0], target_size[1])

    overlay = background.copy()
    if counter_occlusion:
        positions = [(100, 80), (430, 80), (420, 330)]
    elif standing_layout:
        positions = [(650, 80), (560, 160), (420, 330)]
    else:
        positions = [(120, 180), (560, 160), (420, 330)]

    for index, char_path in enumerate(character_images[:3]):
        character = _extract_foreground(_load_image(char_path))
        character = _fit_to_box(character, 220, 320)
        x, y = positions[index]
        x = max(20, min(x, target_size[0] - character.width - 20))
        y = max(20, min(y, target_size[1] - character.height - 20))
        overlay.paste(character, (x, y), character)

    if sofa_occlusion and character_images:
        # Restore the sofa's front edge over the portrait's incomplete lower body.
        sofa_top = int(target_size[1] * 0.61)
        sofa_layer = background.crop((0, sofa_top, target_size[0], target_size[1]))
        overlay.paste(sofa_layer, (0, sofa_top))

    if counter_occlusion and character_images:
        # Restore the kitchen counter over the incomplete lower portrait bodies.
        counter_top = int(target_size[1] * 0.64)
        counter_layer = background.crop((0, counter_top, target_size[0], target_size[1]))
        overlay.paste(counter_layer, (0, counter_top))

    if object_images:
        obj_y = target_size[1] - 130
        obj_x = 380
        for obj_path in object_images[:2]:
            obj = _load_image(obj_path)
            obj = _fit_to_box(obj, 140, 120)
            overlay.paste(obj, (obj_x, obj_y), obj)
            obj_x += 180

    vignette = Image.new("RGBA", target_size, (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for i in range(70, 0, -2):
        vdraw.rectangle(
            [(i, i), (target_size[0] - i, target_size[1] - i)],
            outline=(0, 0, 0, int(18 * (i / 70))),
            width=2,
        )
    overlay = Image.alpha_composite(overlay, vignette)

    ref_path = output_dir / (output_name or f"{scene_id}_reference.png")
    overlay.save(ref_path, format="PNG")
    return str(ref_path)


def compose_multi_reference_sheet(
    reference_images: Sequence[str | Path],
    output_path: str | Path,
    target_size: Tuple[int, int] = (960, 540),
) -> str:
    """Preserve multiple scene references in one deterministic provider input."""
    if not reference_images:
        raise ValueError("At least one reference image is required")

    sheet = Image.new("RGB", target_size, (24, 24, 24))
    panel_width = target_size[0] // len(reference_images)
    for index, image_path in enumerate(reference_images):
        image = _fit_to_box(_load_image(image_path).convert("RGB"), panel_width, target_size[1])
        x = index * panel_width + (panel_width - image.width) // 2
        y = (target_size[1] - image.height) // 2
        sheet.paste(image, (x, y))

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, format="PNG")
    return str(output_path)


def build_motion_prompt(
    scene_id: str,
    scene_story: str,
    allow_new_motion: bool = True,
) -> str:
    """Describe motion only. Do not redefine identity or environment."""
    if scene_id == "intro":
        return (
            "Animate the supplied house reference as a gentle cinematic establishing shot. "
            "Preserve the exact architecture, roof, walls, windows, doors, plants, and surrounding environment from the reference image. "
            "Slowly move the camera toward the house as if approaching Lakshmi's home while keeping the entire house visible. "
            "Do not redesign, replace, crop, duplicate, or add buildings. "
            "Do not introduce Lakshmi or any other character, person, vehicle, furniture, object, text, caption, logo, or watermark. "
            "Keep the exterior environment stable and maintain a consistent 16:9 landscape composition throughout the shot."
        )
    if scene_id == "memory_01_anu":
        return (
            "Animate the supplied living-room reference image as a realistic cinematic scene. "
            "The elderly woman shown in the supplied Lakshmi reference is Lakshmi. Preserve her exact identity, elderly age, face, skin tone, hairstyle, saree, jewelry, and overall appearance. "
            "Lakshmi is sitting naturally in the living room near the family photographs. "
            "She quietly looks toward the photographs, slowly turns her head slightly toward them, blinks naturally, and breathes gently. "
            "Preserve the exact living-room environment from the supplied reference image, including furniture, walls, windows, doors, and family photographs. "
            "Do not replace Lakshmi with another woman. Do not make her younger. Do not change her clothing or appearance. "
            "No additional people. Use subtle realistic movement only. Stable cinematic camera. No cuts or transitions. "
            "Maintain a consistent 16:9 landscape composition throughout."
        )
    if scene_id == "memory_02_chapathi":
        return (
            "Use the supplied image as the primary visual reference for this memory scene. "
            "Create a realistic warm nostalgic childhood memory inside the exact same kitchen shown in the reference image. "
            "Preserve elderly Lakshmi and young daughter Anu as the same recognizable people shown in the supplied image. "
            "Keep Lakshmi on the left beside the gas stove and tawa, and Anu on the right beside the rolling board. "
            "Preserve the dish rack, utensils, tiled wall, window, stove, tawa, rolling board, and counter exactly. "
            "Only show body portions supported by the supplied image; the counter and stove must cover unsupported lower-body areas. Do not generate or hallucinate legs, feet, or clothing below the visible reference areas. "
            "Lakshmi gently cooks chapathi on the tawa with a spatula and looks toward Anu with a warm motherly smile. "
            "Anu gently rolls dough on the wooden rolling board and smiles naturally toward Lakshmi. "
            "Use subtle natural hand, arm, eye, facial, and breathing motion only. No exaggerated gestures, sudden movements, dancing, or theatrical acting. "
            "Keep the camera stable with a slight gentle push-in. Do not change the kitchen layout or location. "
            "No face morphing, age changes, character replacement, extra people, furniture, architecture, text, captions, logos, or watermarks. "
            "Maintain a consistent 16:9 landscape composition throughout a short 5-8 second clip."
        )
    if scene_id == "memory_03_temple":
        return (
            "Animate the supplied temple interior image as a warm, photorealistic nostalgic childhood memory. "
            "Lakshmi and young Anu must both remain clearly visible inside the same temple shown in the reference, standing together near the Krishna shrine. Keep the Krishna idol clearly visible in the background along with brass oil lamps, flower garlands, carved stone pillars, traditional decorations, and the devotional atmosphere. "
            "Lakshmi must remain exactly the same elderly person shown in the supplied reference. Young Anu must remain the same young girl shown in the supplied reference; never use adult Anu, age her, de-age Lakshmi, morph faces, or replace either character. Preserve their faces, skin tones, hairstyles, clothing, sarees, jewelry, and identities. "
            "Lakshmi gently holds young Anu's hand while they look peacefully toward Krishna. Anu looks at Krishna with happy fascination, then briefly looks around. Lakshmi smiles warmly at Anu and gently guides her through the temple. "
            "Start with a wider shot showing Lakshmi, young Anu, and Krishna together. Slowly move closer without cutting away. Keep all three visible throughout: Lakshmi, young Anu, and the Krishna shrine. "
            "Use only subtle natural hand, eye, facial, breathing, clothing, hair, and lamp-flicker motion. Keep the temple and composition stable. No extra people, duplicate people, extra limbs, new objects, redesigned shrine, cuts, transitions, shake, or dramatic movement. Maintain 16:9 landscape composition for 5-8 seconds."
        )

    scene_story = scene_story.strip().rstrip(".")
    return (
        "Animate the provided reference scene exactly as supplied. "
        "Do not redesign, replace, reinterpret, or invent the characters, environment, or objects. "
        "Keep the same faces, hairstyles, clothing, body proportions, relative positions, room layout, and object placement. "
        "Keep the camera fixed and preserve the original composition, framing, and geometry. "
        "Only animate natural motion: "
        f"{scene_story}. "
        "The video must remain in a 16:9 landscape format with a stable composition throughout. "
        "Do not add new people, furniture, props, text, captions, logos, subtitles, or extra scenes. "
        "Keep all characters visually consistent from first frame to last frame. "
        "This is a motion-only animation request based on the supplied reference scene."
    )


def resolve_output_dir(output_dir: Optional[str] = None) -> Path:
    if output_dir is None:
        base_dir = BACKEND_DIR / "generated_videos"
    else:
        base_dir = Path(output_dir)
        if not base_dir.is_absolute():
            base_dir = BACKEND_DIR / base_dir
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir.resolve()


def get_client() -> Client:
    if not API_KEY:
        raise RuntimeError(
            "MAGIC_HOUR_API_KEY is missing. Add it to backend/.env before generating videos."
        )
    return Client(token=API_KEY)


def build_reference_grounded_prompt(
    scene_id: str,
    original_prompt: str,
    references: Optional[Sequence[str]] = None,
    motion_notes: Optional[str] = None,
) -> str:
    refs = list(references or [])
    ref_summary = ", ".join(refs[:6]) if refs else "provided character and environment references"
    base_prompt = (original_prompt or "").strip()
    motion_text = motion_notes or (
        "Use only subtle natural motion, facial expression changes, walking, hand motion, and gentle interaction."
    )
    return (
        "Animate the provided reference scene, not a re-imagined scene. "
        "This image set is the visual source of truth: preserve the faces, hairstyles, clothing, "
        "body proportions, relative positions, environment, and object details from the supplied references. "
        "Do not redesign, replace, reinterpret, or invent the characters or setting. "
        "Keep the same composition, framing, and camera setup throughout the shot. "
        "Keep the camera fixed and preserve the original scene composition; only animate motion. "
        "Do not change the room, furniture, walls, doors, characters, props, or background. "
        "Do not add new people, objects, text, watermarks, logos, captions, or extra scenes. "
        "The final video must remain in a 16:9 landscape format and maintain consistent visual layout. "
        f"Scene ID: {scene_id}. "
        f"Original intent: {base_prompt}. "
        f"Reference set: {ref_summary}. "
        f"{motion_text} "
        "This is a reference-grounded animation request: preserve the visual identity and only animate the natural action."
    )


def generate_video(
    image_path: str,
    prompt: str,
    output_dir: str = "generated_videos",
    duration: float = DEFAULT_DURATION,
    model: str = "ltx-2.3",
    resolution: str = DEFAULT_RESOLUTION,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    name: str = "Cognitive Memory Scene",
    skip_preflight: bool = False,
    reference_images: Optional[Sequence[str | Path]] = None,
) -> Any:
    image_file = Path(image_path)
    end_image_file = None
    if reference_images:
        image_file = Path(reference_images[0])
        if len(reference_images) == 2:
            end_image_file = Path(reference_images[1])
    if not image_file.exists():
        raise FileNotFoundError(f"Source image does not exist: {image_file}")
    if end_image_file is not None and not end_image_file.exists():
        raise FileNotFoundError(f"End reference image does not exist: {end_image_file}")

    if not skip_preflight:
        preflight_render(resolution=resolution, duration=duration, model=model)
    target_dir = resolve_output_dir(output_dir)
    client = get_client()

    print("\n--------------------------------")
    print("Magic Hour video generation")
    print("--------------------------------")
    print(f"Image : {image_file}")
    print(f"Model : {model}")
    print(f"Resolution : {resolution}")
    print(f"Aspect ratio: {aspect_ratio}")
    print(f"Prompt: {prompt}")
    print(f"Output: {target_dir}")
    print("--------------------------------\n")

    generate_kwargs = {
        "assets": {"image_file_path": str(image_file.resolve())},
        "end_seconds": float(duration),
        "model": model,
        "resolution": resolution,
        "style": {"prompt": prompt},
        "name": name,
        "wait_for_completion": True,
        "download_outputs": True,
        "download_directory": str(target_dir),
    }
    if end_image_file is not None:
        generate_kwargs["assets"]["end_image_file_path"] = str(end_image_file.resolve())
    try:
        generate_kwargs["aspect_ratio"] = aspect_ratio
        result = client.v1.image_to_video.generate(**generate_kwargs)
    except TypeError:
        generate_kwargs.pop("aspect_ratio", None)
        result = client.v1.image_to_video.generate(**generate_kwargs)
    print(f"\nVideo generation complete at {resolution}.")
    return result


def generate_video_from_bytes(
    image_bytes: bytes,
    prompt: str,
    output_dir: str = "generated_videos",
    duration: float = DEFAULT_DURATION,
    model: str = "ltx-2.3",
    resolution: str = DEFAULT_RESOLUTION,
    name: str = "Cognitive Memory Scene",
) -> Any:
    """Render an uploaded reference and remove its temporary file afterwards."""
    if not image_bytes:
        raise ValueError("Uploaded reference image is empty")

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temporary_file:
            temporary_file.write(image_bytes)
            temporary_path = Path(temporary_file.name)
        return generate_video(
            image_path=str(temporary_path),
            prompt=prompt,
            output_dir=output_dir,
            duration=duration,
            model=model,
            resolution=resolution,
            name=name,
        )
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
