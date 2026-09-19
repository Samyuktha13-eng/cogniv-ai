import hashlib
import json
import os
import shutil
from pathlib import Path

try:
    from backend.magic_hour_video import (
        build_motion_prompt,
        compose_reference_scene,
        generate_video,
        build_reference_grounded_prompt,
        compose_multi_reference_sheet,
        preflight_render,
    )
    from backend.lakshmi_story import build_lakshmi_memory_journey
except ModuleNotFoundError:
    from magic_hour_video import (
        build_motion_prompt,
        compose_reference_scene,
        generate_video,
        build_reference_grounded_prompt,
        compose_multi_reference_sheet,
        preflight_render,
    )
    from lakshmi_story import build_lakshmi_memory_journey

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PATIENT_DIR = PROJECT_ROOT / "Patient_001_Lakshmi"
VIDEO_DIR = Path(__file__).resolve().parent / "generated_videos"
CACHE_FILE = VIDEO_DIR / "video_cache.json"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_FILENAMES = {
    "intro": "memory_01_home.mp4",
    "memory_01_anu": "memory_02_anu.mp4",
    "memory_02_chapathi": "memory_03_chapathi.mp4",
    "memory_03_temple": "memory_04_temple.mp4",
    "memory_04_trip": "memory_05_trip.mp4",
    "memory_05_family": "memory_06_family_meal.mp4",
    "memory_06_garden": "memory_07_garden.mp4",
    "memory_07_radio": "memory_08_radio.mp4",
    "present_transition": "present_01_transition.mp4",
    "present_entry": "present_02_anu_enters.mp4",
    "reunion_hug": "present_03_reunion_hug.mp4",
}


def load_cache():
    if not CACHE_FILE.exists():
        return {}
    try:
        with CACHE_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def save_cache(cache):
    with CACHE_FILE.open("w", encoding="utf-8") as file:
        json.dump(cache, file, indent=2)


def make_cache_key(scene, image_path, model):
    content = scene["id"] + scene["prompt"] + str(image_path) + model
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def resolve_image(relative_path):
    image_path = PATIENT_DIR / relative_path
    if not image_path.exists():
        raise FileNotFoundError(f"Memory image not found: {image_path}")
    return image_path


def find_latest_video():
    videos = list(VIDEO_DIR.glob("*.mp4"))
    if not videos:
        return None
    return max(videos, key=lambda item: item.stat().st_mtime)


def normalize_scene_video(scene_file):
    if scene_file is None:
        return None

    path = Path(scene_file)
    if path.is_absolute():
        return f"/videos/{path.name}"
    return str(path)


def build_scene_payload(scene, video_path, cached=False):
    scene_payload = dict(scene)
    scene_id = scene.get("id") or scene.get("scene_id")
    scene_payload["id"] = scene_id
    scene_payload["scene_id"] = scene_id
    scene_payload["cached"] = cached
    scene_payload["video"] = normalize_scene_video(video_path)
    scene_payload["video_file"] = str(Path(video_path).resolve()) if video_path else None
    scene_payload["video_filename"] = VIDEO_FILENAMES.get(scene_id)
    return scene_payload


def get_story_definition(scene_limit=None):
    story = build_lakshmi_memory_journey()
    scenes = story["scenes"]
    if scene_limit is not None:
        scenes = scenes[:scene_limit]

    cache = load_cache()
    payload_scenes = []
    for scene in scenes:
        image_path = resolve_scene_image(scene)
        cache_key = make_cache_key(scene, image_path, "ltx-2.3")
        cached_file = Path(cache[cache_key]["file"]) if cache_key in cache else None
        known_video = VIDEO_DIR / VIDEO_FILENAMES.get(scene.get("id"), f"{scene.get('id')}.mp4")

        if cached_file and cached_file.exists():
            payload_scenes.append(build_scene_payload(scene, cached_file, cached=True))
        elif known_video.exists():
            payload_scenes.append(build_scene_payload(scene, known_video, cached=False))
        else:
            payload_scenes.append(build_scene_payload(scene, None, cached=False))

    return {
        "story_id": story["story_id"],
        "title": story["title"],
        "patient": story.get("patient"),
        "main_character": story.get("main_character"),
        "scenes": payload_scenes,
    }


def resolve_scene_image(scene):
    image_value = scene.get("image")
    if image_value:
        return resolve_image(image_value)

    refs = scene.get("reference_bundle", [])
    for ref in refs:
        path = ref.get("path")
        if path:
            return resolve_image(path)

    raise FileNotFoundError(f"No usable image found for scene {scene.get('id')}")


def build_scene_reference_image(scene, output_dir=None):
    if scene.get("reference_images"):
        return str(resolve_image(scene["reference_images"][0]))

    if scene.get("reference_image_direct"):
        source = resolve_scene_image(scene)
        target_dir = Path(output_dir) if output_dir else PROJECT_ROOT / "backend" / "generated_references"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{scene['id']}_reference.jpg"
        shutil.copy2(source, target)
        return str(target)

    refs = scene.get("reference_bundle", [])
    room_path = None
    character_paths = []
    object_paths = []

    for ref in refs:
        ref_type = (ref.get("type") or "").lower()
        ref_path = ref.get("path")
        if not ref_path:
            continue
        full_path = resolve_image(ref_path)
        if ref_type == "environment":
            room_path = full_path
        elif ref_type in {"character", "people", "person"}:
            character_paths.append(full_path)
        elif ref_type in {"food", "object", "prop"}:
            object_paths.append(full_path)

    for character_path in scene.get("characters", []) or []:
        if not character_paths:
            character_paths.append(resolve_image(character_path))
        else:
            normalized = str(character_path)
            if not any(str(p).endswith(normalized) for p in character_paths):
                character_paths.append(resolve_image(character_path))

    for object_path in scene.get("objects", []) or []:
        if not object_paths:
            object_paths.append(resolve_image(object_path))
        else:
            normalized = str(object_path)
            if not any(str(p).endswith(normalized) for p in object_paths):
                object_paths.append(resolve_image(object_path))

    image_value = scene.get("image")
    if image_value and not room_path:
        room_path = resolve_image(image_value)

    if not room_path:
        room_path = resolve_scene_image(scene)

    if not character_paths:
        for ref in refs:
            path = ref.get("path")
            if path and (ref.get("type") or "").lower() != "environment":
                character_paths.append(resolve_image(path))

    target_dir = Path(output_dir) if output_dir else VIDEO_DIR / "reference_scenes"
    target_dir.mkdir(parents=True, exist_ok=True)
    return compose_reference_scene(
        scene_id=scene["id"],
        room_image=room_path,
        character_images=character_paths,
        object_images=object_paths or None,
        output_dir=target_dir,
        target_size=(960, 540),
        output_name="memory_03_chapathi_reference.png" if scene["id"] == "memory_02_chapathi" else ("memory_01_home_reference.png" if scene["id"] == "intro" else None),
        sofa_occlusion=scene["id"] == "intro",
        counter_occlusion=scene["id"] == "memory_02_chapathi",
    )


def generate_story_videos(
    model="ltx-2.3",
    resolution="480p",
    scene_limit=None,
    force_refresh=False,
    scene_ids=None,
):
    story = build_lakshmi_memory_journey()
    cache = load_cache()
    generated_scenes = []
    scenes = story["scenes"]
    if scene_limit is not None:
        scenes = scenes[:scene_limit]
    if scene_ids is not None:
        requested_ids = set(scene_ids)
        scenes = [scene for scene in scenes if scene["id"] in requested_ids]

    for scene in scenes:
        image_path = resolve_scene_image(scene)
        cache_key = make_cache_key(scene, image_path, model)
        scene_video = VIDEO_DIR / VIDEO_FILENAMES.get(scene["id"], f"{scene['id']}.mp4")

        if not force_refresh and cache_key in cache:
            cached_file = Path(cache[cache_key]["file"])
            if cached_file.exists() and cached_file.resolve() == scene_video.resolve():
                print(f"Using cached video for {scene['id']}")
                generated_scenes.append(build_scene_payload(scene, scene_video, cached=True))
                continue

        reference_paths = []
        for ref in scene.get("reference_bundle", []):
            ref_path = ref.get("path")
            if ref_path:
                reference_paths.append(ref_path)
        if scene.get("image"):
            reference_paths.insert(0, scene["image"])

        composite_image = build_scene_reference_image(scene, output_dir=PROJECT_ROOT / "backend" / "generated_references")
        grounded_prompt = build_motion_prompt(
            scene_id=scene["id"],
            scene_story=scene.get("story") or scene["prompt"],
        )

        print(f"\nGenerating {scene['id']} from reference scene: {composite_image}")
        generate_video(
            image_path=str(composite_image),
            prompt=grounded_prompt,
            output_dir=str(VIDEO_DIR),
            duration=5,
            model=model,
            resolution=resolution,
            name=f"{story['title']}-{scene['id']}",
            skip_preflight=True,
            reference_images=scene.get("reference_images"),
        )

        latest_video = find_latest_video()
        if not latest_video:
            raise RuntimeError(f"Magic Hour returned no MP4 for {scene['id']}")

        if latest_video.resolve() != scene_video.resolve():
            shutil.copy2(latest_video, scene_video)

        cache[cache_key] = {
            "scene_id": scene["id"],
            "file": str(scene_video),
        }
        save_cache(cache)

        generated_scenes.append(build_scene_payload(scene, scene_video, cached=False))

    return {
        "story_id": story["story_id"],
        "title": story["title"],
        "patient": story.get("patient"),
        "main_character": story.get("main_character"),
        "scenes": generated_scenes,
    }
