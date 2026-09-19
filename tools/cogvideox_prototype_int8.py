"""Run exactly one TorchAO INT8 CogVideoX School Morning I2V prototype."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

MODEL_DEFAULT = "THUDM/CogVideoX-5b-I2V"
MIN_VRAM_DEFAULT_GB = 5.5
SCHOOL_SCENE_ID = "chapter_04_scene_01"
SCHOOL_IMAGE = "04_school_morning/school_01_morning_route.jpg"
FRAMES = 49
STEPS = 50
GUIDANCE_SCALE = 6.0
FPS = 8
SEED_DEFAULT = 42

PROMPT = (
    "Lakshmi, age 12, walks to school with her childhood friend Radha on their "
    "familiar South Indian morning route. Preserve the appearance, clothing, "
    "school bags, environment, and composition of the reference image. Create "
    "only subtle natural walking motion, gentle movement of clothing and school "
    "bags, and slight environmental movement. Maintain stable identities and "
    "scene continuity throughout the video. The scene is calm, warm, realistic, "
    "and suitable as an autobiographical reminiscence cue."
)

NEGATIVE_PROMPT = (
    "railway station, train, young man, romance, adult spouse, husband, sister, "
    "modern vehicles, smartphones, modern buildings, text, captions, subtitles, "
    "dialogue, logos, watermarks, new characters, additional children, scene "
    "changes, dramatic camera movement, fast motion, face distortion, distorted "
    "faces, duplicated people, extra limbs, extra fingers, deformed hands, flicker, "
    "unstable identity, invented objects, invented events, surreal elements, "
    "cinematic romance, historical footage"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", default=os.getenv("COGVIDEOX_MODEL_ID", MODEL_DEFAULT))
    parser.add_argument("--seed", type=int, default=int(os.getenv("COGVIDEOX_SEED", str(SEED_DEFAULT))))
    parser.add_argument("--output-dir", default=os.getenv("COGVIDEOX_OUTPUT_DIR"))
    parser.add_argument("--min-vram-gb", type=float, default=float(os.getenv("COGVIDEOX_INT8_MIN_VRAM_GB", str(MIN_VRAM_DEFAULT_GB))))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    checkpoint = root / "models" / "CogVideoX-5b-I2V"
    reference = root / "Patient story image" / SCHOOL_IMAGE
    output_dir = Path(args.output_dir) if args.output_dir else root.parent / "cogniv_prototype_outputs" / "school_morning_radha_int8"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "prototype_int8.mp4"

    print("PROTOTYPE: INT8 #1 ONLY")
    print("model_id:", args.model_id)
    print("checkpoint:", checkpoint)
    print("reference_image:", reference)
    print("prompt:", PROMPT)
    print("negative_prompt:", NEGATIVE_PROMPT)
    print("seed:", args.seed)
    print("frames:", FRAMES)
    print("inference_steps:", STEPS)
    print("guidance_scale:", GUIDANCE_SCALE)
    print("fps:", FPS)
    print("num_videos_per_prompt: 1")
    print("compute_dtype: bfloat16")
    print("quantization: torchao.int8_weight_only")
    print("model_cpu_offload: True")
    print("vae_tiling: True")
    print("vae_slicing: True")

    try:
        import torch
        import torchvision
        import diffusers
        import transformers
        import accelerate
        import safetensors
        from PIL import Image
        from diffusers import CogVideoXImageToVideoPipeline
        from diffusers.utils import export_to_video
    except ImportError as error:
        print("PROTOTYPE STATUS: FAILED")
        print("missing_runtime_dependency:", error)
        return 1

    try:
        from torchao.quantization import int8_weight_only, quantize_
    except ImportError as error:
        print("PROTOTYPE STATUS: FAILED")
        print("torchao is required; refusing BF16 fallback:", error)
        return 1

    if not checkpoint.is_dir():
        print("PROTOTYPE STATUS: FAILED")
        print("checkpoint_missing:", checkpoint)
        return 1
    if not reference.is_file():
        print("PROTOTYPE STATUS: FAILED")
        print("reference_missing:", reference)
        return 1
    if not torch.cuda.is_available():
        print("PROTOTYPE STATUS: FAILED")
        print("CUDA unavailable")
        return 1
    properties = torch.cuda.get_device_properties(torch.cuda.current_device())
    total_vram_gb = properties.total_memory / (1024 ** 3)
    free_before, _ = torch.cuda.mem_get_info()
    print("gpu:", properties.name)
    print("total_vram_gb:", round(total_vram_gb, 2))
    print("free_vram_before_gb:", round(free_before / (1024 ** 3), 2))
    if total_vram_gb < args.min_vram_gb:
        print("PROTOTYPE STATUS: FAILED")
        print(f"GPU VRAM {total_vram_gb:.2f} GB is below configured minimum {args.min_vram_gb:.2f} GB")
        return 1

    print("quantization_runtime: torchao available")
    started = time.perf_counter()
    try:
        pipeline = CogVideoXImageToVideoPipeline.from_pretrained(
            str(checkpoint),
            torch_dtype=torch.bfloat16,
            local_files_only=True,
            low_cpu_mem_usage=True,
        )
        quantize_(pipeline.text_encoder, int8_weight_only())
        quantize_(pipeline.transformer, int8_weight_only())
        quantize_(pipeline.vae, int8_weight_only())
        pipeline.enable_sequential_cpu_offload(gpu_id=torch.cuda.current_device())
        if hasattr(pipeline.vae, "enable_tiling"):
            pipeline.vae.enable_tiling()
        if hasattr(pipeline.vae, "enable_slicing"):
            pipeline.vae.enable_slicing()

        image = Image.open(reference).convert("RGB")
        generator = torch.Generator(device="cuda").manual_seed(args.seed)
        with torch.inference_mode():
            result = pipeline(
                image=image,
                prompt=PROMPT,
                negative_prompt=NEGATIVE_PROMPT,
                num_frames=FRAMES,
                num_inference_steps=STEPS,
                guidance_scale=GUIDANCE_SCALE,
                num_videos_per_prompt=1,
                generator=generator,
                output_type="pil",
            )
        frames = result.frames[0] if isinstance(result.frames, list) and isinstance(result.frames[0], list) else result.frames
        export_to_video(frames, str(output), fps=FPS)
    except Exception as error:
        print("PROTOTYPE STATUS: FAILED")
        print("generation_error_type:", type(error).__name__)
        print("generation_error:", str(error))
        return 1

    elapsed = time.perf_counter() - started
    free_after, _ = torch.cuda.mem_get_info()
    if not output.is_file() or output.stat().st_size <= 0:
        print("PROTOTYPE STATUS: FAILED")
        print("output_missing_or_empty:", output)
        return 1
    metadata: dict[str, Any] = {
        "prototype_number": 1,
        "quantization": "torchao.int8_weight_only",
        "model_id": args.model_id,
        "seed": args.seed,
        "reference_image": str(reference),
        "prompt": PROMPT,
        "negative_prompt": NEGATIVE_PROMPT,
        "frames_requested": FRAMES,
        "frames_actual": len(frames),
        "inference_steps": STEPS,
        "guidance_scale": GUIDANCE_SCALE,
        "fps": FPS,
        "resolution": list(frames[0].size) if frames else None,
        "output_mp4": str(output),
        "file_size_bytes": output.stat().st_size,
        "generation_seconds": elapsed,
        "gpu": properties.name,
        "total_vram_gb": total_vram_gb,
        "approx_vram_used_gb": (free_before - free_after) / (1024 ** 3),
        "synthetic_memory_cue": True,
    }
    (output_dir / "generation_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("PROTOTYPE STATUS: PASS")
    print("output_mp4:", output)
    print("generation_seconds:", round(elapsed, 2))
    print("actual_frames:", len(frames))
    print("output_size_bytes:", output.stat().st_size)
    print("No additional videos generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
