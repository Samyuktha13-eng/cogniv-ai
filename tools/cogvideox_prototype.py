"""Run exactly one real CogVideoX School Morning I2V prototype.

This script is intentionally isolated from Cogniv orchestration and content
layers. It performs the runtime gate before any model download, then consumes
an existing Step 11 request and reference image through the existing provider.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

MODEL_DEFAULT = "THUDM/CogVideoX-5b-I2V"
MIN_VRAM_DEFAULT_GB = 16.0
SCHOOL_SCENE_ID = "chapter_04_scene_01"
SCHOOL_IMAGE = "04_school_morning/school_01_morning_route.jpg"
PROTOTYPE_FRAMES = 49
PROTOTYPE_STEPS = 50
PROTOTYPE_GUIDANCE_SCALE = 6.0
PROTOTYPE_FPS = 8

PROTOTYPE_VIDEO_PROMPT = (
    "Lakshmi, age 12, walks to school with her childhood friend Radha on their "
    "familiar South Indian morning route. Preserve the appearance, clothing, "
    "school bags, environment, and composition of the reference image. Create "
    "only subtle natural walking motion, gentle movement of clothing and school "
    "bags, and slight environmental movement. Maintain stable identities and "
    "scene continuity throughout the video. The scene is calm, warm, realistic, "
    "and suitable as an autobiographical reminiscence cue."
)

PROTOTYPE_NEGATIVE_PROMPT = (
    "railway station, train, young man, romance, adult spouse, husband, sister, "
    "modern vehicles, smartphones, modern buildings, text, captions, subtitles, "
    "dialogue, logos, watermarks, new characters, additional children, scene "
    "changes, dramatic camera movement, fast motion, face distortion, distorted "
    "faces, duplicated people, extra limbs, extra fingers, deformed hands, "
    "flicker, unstable identity, invented objects, invented events, surreal "
    "elements, cinematic romance, historical footage"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", default=os.getenv("COGVIDEOX_MODEL_ID", MODEL_DEFAULT))
    parser.add_argument("--cache-dir", default=os.getenv("COGVIDEOX_CACHE_DIR"))
    parser.add_argument("--min-vram-gb", type=float, default=float(os.getenv("COGVIDEOX_MIN_VRAM_GB", MIN_VRAM_DEFAULT_GB)))
    parser.add_argument("--seed", type=int, default=int(os.getenv("COGVIDEOX_SEED", "42")))
    parser.add_argument("--frames", type=int, default=PROTOTYPE_FRAMES)
    parser.add_argument("--steps", type=int, default=PROTOTYPE_STEPS)
    parser.add_argument("--guidance-scale", type=float, default=PROTOTYPE_GUIDANCE_SCALE)
    parser.add_argument("--fps", type=int, default=PROTOTYPE_FPS)
    parser.add_argument("--output-dir", default=os.getenv("COGVIDEOX_OUTPUT_DIR"))
    return parser.parse_args()


def fail(message: str) -> int:
    print(f"PROTOTYPE STATUS: FAILED\n{message}")
    return 1


def runtime_gate(min_vram_gb: float) -> dict[str, Any] | None:
    print("PHASE 1: FINAL RUNTIME GATE")
    print(f"python_executable: {sys.executable}")
    try:
        import torch
        import torchvision
        import diffusers
        import transformers
        import accelerate
        import safetensors
        import PIL
        import imageio
        import imageio_ffmpeg
    except ImportError as error:
        print(f"missing_runtime_dependency: {error}")
        return None

    print(f"torch: {torch.__version__}")
    print(f"torchvision: {torchvision.__version__}")
    print(f"diffusers: {diffusers.__version__}")
    print(f"transformers: {transformers.__version__}")
    print(f"accelerate: {accelerate.__version__}")
    print(f"safetensors: {safetensors.__version__}")
    print(f"Pillow: {PIL.__version__}")
    print(f"imageio: {imageio.__version__}")
    print(f"imageio_ffmpeg: {imageio_ffmpeg.__version__}")
    print(f"cuda_available: {torch.cuda.is_available()}")
    if not torch.cuda.is_available():
        print("CUDA is unavailable; stopping before model download.")
        return None

    device_index = torch.cuda.current_device()
    properties = torch.cuda.get_device_properties(device_index)
    total_vram_gb = properties.total_memory / (1024 ** 3)
    free_bytes, _ = torch.cuda.mem_get_info(device_index)
    free_vram_gb = free_bytes / (1024 ** 3)
    print(f"gpu_name: {properties.name}")
    print(f"total_vram_gb: {total_vram_gb:.2f}")
    print(f"free_vram_gb: {free_vram_gb:.2f}")
    if total_vram_gb < min_vram_gb:
        print(f"GPU VRAM {total_vram_gb:.2f} GB is below configured minimum {min_vram_gb:.2f} GB; stopping before model download.")
        return None

    left = torch.tensor([1.0, 2.0, 3.0], device="cuda")
    right = torch.tensor([4.0, 5.0, 6.0], device="cuda")
    cuda_result = (left * right).sum().item()
    print(f"cuda_tensor_test: PASS (result={cuda_result})")
    return {
        "torch": torch,
        "device": "cuda",
        "gpu_name": properties.name,
        "total_vram_gb": round(total_vram_gb, 2),
        "free_vram_gb": round(free_vram_gb, 2),
    }


def locate_image(root: Path) -> Path | None:
    candidates = [
        root / "Patient story image" / SCHOOL_IMAGE,
        root / "outputs" / "Patient story image" / SCHOOL_IMAGE,
        root / SCHOOL_IMAGE,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def build_request(root: Path, image_path: Path, args: argparse.Namespace):
    from media_generation.prompt_builder import MediaPromptBuilder
    from reminiscence.memory_selector import MemoryCandidate
    from story.scene_loader import load_scenes

    scene = next((item for item in load_scenes() if item.scene_id == SCHOOL_SCENE_ID), None)
    if scene is None:
        raise FileNotFoundError(f"Story scene {SCHOOL_SCENE_ID} was not found in data/lakshmi_story_scenes.json")
    candidate = MemoryCandidate.from_scene(scene)
    request = MediaPromptBuilder().build(candidate, "P001", life_stage="childhood")
    request = replace(
        request,
        video_prompt=PROTOTYPE_VIDEO_PROMPT,
        negative_constraints=list(dict.fromkeys([*request.negative_constraints, PROTOTYPE_NEGATIVE_PROMPT])),
        reference_asset=str(image_path),
        requested_media_type="video",
    )
    return request


def disk_space(path: Path) -> int:
    return shutil.disk_usage(path).free


def load_and_generate(request: Any, args: argparse.Namespace, root: Path, runtime: dict[str, Any]) -> tuple[Any, float, Path]:
    from media_generation.providers.cogvideox_provider import CogVideoXConfig, CogVideoXProvider

    output_dir = Path(args.output_dir) if args.output_dir else root.parent / "cogniv_prototype_outputs" / "school_morning_radha"
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_path = Path(args.cache_dir) if args.cache_dir else Path.home() / ".cache" / "huggingface" / "hub"
    cache_path.mkdir(parents=True, exist_ok=True)
    print("PHASE 2: MODEL CHECKPOINT")
    print(f"model_id: {args.model_id}")
    print(f"cache_directory: {cache_path}")
    print(f"available_disk_gb: {disk_space(cache_path) / (1024 ** 3):.2f}")
    print("PHASE 3: COMPONENT LOAD VERIFICATION")
    print("loading_pipeline: CogVideoXImageToVideoPipeline")
    config = CogVideoXConfig(
        model_id=args.model_id,
        device="cuda",
        dtype="bfloat16",
        num_frames=args.frames,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance_scale,
        fps=args.fps,
        seed=args.seed,
        enable_cpu_offload=True,
        enable_vae_tiling=True,
        enable_vae_slicing=True,
        output_dir=str(output_dir),
        asset_root=str(root / "Patient story image"),
    )
    provider = CogVideoXProvider(config=config)
    started = time.perf_counter()
    result = provider.generate(request)
    duration = time.perf_counter() - started
    pipeline = provider._pipeline
    components = {
        "pipeline": pipeline is not None,
        "transformer": getattr(pipeline, "transformer", None) is not None,
        "vae": getattr(pipeline, "vae", None) is not None,
        "text_encoder": getattr(pipeline, "text_encoder", None) is not None,
        "tokenizer": getattr(pipeline, "tokenizer", None) is not None,
        "scheduler": getattr(pipeline, "scheduler", None) is not None,
    }
    print("component_load_report:", json.dumps(components, sort_keys=True))
    if not all(components.values()):
        raise RuntimeError(f"Incomplete CogVideoX pipeline components: {components}")
    return result, duration, output_dir


def sanity_check(result: Any, args: argparse.Namespace) -> dict[str, Any]:
    import imageio.v3 as iio

    output_path = Path(result.output_path)
    if not output_path.is_file() or output_path.stat().st_size <= 0:
        raise RuntimeError(f"MP4 missing or empty: {output_path}")
    metadata = iio.immeta(output_path, plugin="pyav")
    frame_count = metadata.get("n_frames") or metadata.get("n_images")
    fps = metadata.get("fps") or metadata.get("duration", 0) and (frame_count / metadata["duration"] if frame_count else None)
    duration = metadata.get("duration")
    if frame_count is not None and frame_count < args.frames:
        raise RuntimeError(f"MP4 has {frame_count} frames; expected at least {args.frames}")
    return {"file_size_bytes": output_path.stat().st_size, "frame_count": frame_count, "fps": fps, "duration_seconds": duration}


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    runtime = runtime_gate(args.min_vram_gb)
    if runtime is None:
        return fail("Runtime gate failed. No model weights were downloaded and no video was generated.")
    image_path = locate_image(root)
    if image_path is None:
        return fail(f"School Morning reference image not found. Expected: {root / 'Patient story image' / SCHOOL_IMAGE}")
    print("PHASE 4: SCHOOL MORNING INPUT")
    print(f"input_image: {image_path}")
    request = build_request(root, image_path, args)
    print("factual_memory:", request.factual_memory)
    print("prototype_configuration:", json.dumps({
        "frames": args.frames,
        "inference_steps": args.steps,
        "guidance_scale": args.guidance_scale,
        "fps": args.fps,
        "seed": args.seed,
        "num_videos_per_prompt": 1,
        "dtype": "bfloat16",
        "vae_tiling": True,
        "vae_slicing": True,
    }, sort_keys=True))
    print("video_prompt:", request.video_prompt)
    print("negative_prompt:", " ".join(request.negative_constraints))
    try:
        result, generation_seconds, output_dir = load_and_generate(request, args, root, runtime)
        sanity = sanity_check(result, args)
    except Exception as error:
        print(f"generation_error_type: {type(error).__name__}")
        return fail(f"Generation stopped without batch continuation: {error}")

    metadata = {
        "model_id": args.model_id,
        "seed": args.seed,
        "input_image": str(image_path),
        "prompt": request.video_prompt,
        "negative_prompt": " ".join(request.negative_constraints),
        "frame_count": args.frames,
        "inference_steps": args.steps,
        "guidance_scale": args.guidance_scale,
        "resolution": [result.width, result.height],
        "fps": args.fps,
        "generation_seconds": generation_seconds,
        "gpu_name": runtime["gpu_name"],
        "total_vram_gb": runtime["total_vram_gb"],
        "free_vram_gb_at_gate": runtime["free_vram_gb"],
        "device": "cuda",
        "dtype": "bfloat16",
        "sanity_check": sanity,
        "synthetic_memory_cue": True,
        "visual_quality_requires_manual_review": True,
    }
    metadata_path = output_dir / "generation_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("PROTOTYPE STATUS: PASS")
    print("output_mp4:", result.output_path)
    print("metadata_json:", metadata_path)
    print("generation_seconds:", f"{generation_seconds:.2f}")
    print("Automated sanity checks passed; visual quality requires manual inspection and caregiver approval.")
    print("One School Morning/Radha prototype generated. No Cogniv backend/frontend architecture was modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
