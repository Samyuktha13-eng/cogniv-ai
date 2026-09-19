"""Validated LTX 2B 0.9.8 BF16 multiscale image-to-video provider.

This implementation freezes the working generation profile that has already been
validated in the project: the local 2B distilled BF16 checkpoint, the matching
spatial upscaler, and the official multi-scale generation flow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import imageio.v3 as iio
import PIL.Image

from media_generation.models import MediaGenerationRequest, VideoGenerationResult


@dataclass(frozen=True)
class LTXBF16MultiScaleConfig:
    model_path: str = r"models\LTX-Video\ltxv-2b-0.9.8-distilled.safetensors"
    upscaler_path: str = r"models\LTX-Video\ltxv-spatial-upscaler-0.9.8.safetensors"
    output_dir: str = "outputs"
    fps: int = 8
    num_frames: int = 17
    seed: int = 42
    width: int = 512
    height: int = 320
    low_width: int = 352
    low_height: int = 224
    image_cond_noise_scale: float = 0.025
    guidance_scale: float = 1.0
    negative_prompt: str = (
        "blurry, noisy, distorted face, extra people, scene change, camera shake, "
        "flicker, warped limbs, invented objects, text, watermark."
    )
    dtype: str = "bfloat16"
    generator_profiles: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "safe": {
                "profile": "safe",
                "num_frames": 17,
                "fps": 8,
                "guidance_scale": 1.0,
                "image_cond_noise_scale": 0.025,
            },
            "quality": {
                "profile": "quality",
                "num_frames": 17,
                "fps": 8,
                "guidance_scale": 1.0,
                "image_cond_noise_scale": 0.0,
            },
            "retry": {
                "profile": "retry",
                "num_frames": 17,
                "fps": 8,
                "guidance_scale": 1.0,
                "image_cond_noise_scale": 0.025,
            },
        }
    )


class VideoGenerationGate:
    """Pre-generation gating logic for the validated LTX BF16 multiscale pipeline."""

    def __init__(self, config: LTXBF16MultiScaleConfig | None = None) -> None:
        self.config = config or LTXBF16MultiScaleConfig()

    def select_profile(self, profile_name: str = "safe") -> dict[str, Any]:
        profile = self.config.generator_profiles.get(profile_name, self.config.generator_profiles["safe"]).copy()
        profile.setdefault("num_frames", self.config.num_frames)
        profile.setdefault("fps", self.config.fps)
        profile.setdefault("guidance_scale", self.config.guidance_scale)
        profile.setdefault("image_cond_noise_scale", self.config.image_cond_noise_scale)
        return profile

    def validate_reference(self, reference_asset: str | Path) -> Path:
        path = Path(reference_asset)
        if not path.is_absolute():
            root = Path(__file__).resolve().parents[2]
            candidates = [
                root / path,
                root / "Patient story image" / path,
                root / "outputs" / path,
            ]
            for candidate in candidates:
                if candidate.exists():
                    return candidate
        if not path.exists():
            raise FileNotFoundError(f"Reference image not found: {path}")
        return path


class LTXVideoValidator:
    """Post-generation validation for output MP4 integrity and basic quality sanity."""

    def validate(self, video_path: str | Path) -> dict[str, Any]:
        path = Path(video_path)
        if not path.exists():
            return {"status": "fail", "reason": f"missing_video_file: {path}"}
        if not path.is_file():
            return {"status": "fail", "reason": f"not_a_file: {path}"}
        if path.stat().st_size <= 0:
            return {"status": "fail", "reason": f"empty_video_file: {path}"}

        try:
            frames = iio.imiter(path, plugin="FFMPEG")
            frame_count = 0
            for _ in frames:
                frame_count += 1
            if frame_count <= 0:
                return {"status": "fail", "reason": f"no_frames_decoded: {path}"}
        except TypeError:
            try:
                frames = iio.imiter(str(path), plugin="FFMPEG")
                frame_count = 0
                for _ in frames:
                    frame_count += 1
                if frame_count <= 0:
                    return {"status": "fail", "reason": f"no_frames_decoded: {path}"}
            except Exception as exc:  # pragma: no cover - runtime validation path only
                return {"status": "fail", "reason": f"decode_failed: {exc}"}
        except Exception as exc:  # pragma: no cover - runtime validation path only
            return {"status": "fail", "reason": f"decode_failed: {exc}"}

        return {
            "status": "pass",
            "reason": "video_decoded_successfully",
            "frame_count": frame_count,
            "file_size_bytes": path.stat().st_size,
        }


class LTXBF16MultiScaleProvider:
    """Production-facing provider around the validated 2B BF16 multiscale pipeline."""

    def __init__(
        self,
        config: LTXBF16MultiScaleConfig | None = None,
        gate: VideoGenerationGate | None = None,
        validator: LTXVideoValidator | None = None,
    ) -> None:
        self.config = config or LTXBF16MultiScaleConfig()
        self.gate = gate or VideoGenerationGate(self.config)
        self.validator = validator or LTXVideoValidator()
        self._pipeline = None
        self._upsample_pipe = None

    @property
    def is_loaded(self) -> bool:
        return self._pipeline is not None and self._upsample_pipe is not None

    def prepare_reference_image(self, image: PIL.Image.Image) -> PIL.Image.Image:
        """Keep the conditioning image readable and consistent with the model's expected aspect ratio."""
        rgb_image = image.convert("RGB")
        width, height = rgb_image.size
        max_side = 1024
        min_side = 512

        if max(width, height) > max_side or min(width, height) < min_side:
            scale = min(max_side / max(width, height), max(1.0, min_side / min(width, height)))
            new_width = max(1, int(round(width * scale)))
            new_height = max(1, int(round(height * scale)))
            rgb_image = rgb_image.resize((new_width, new_height), PIL.Image.Resampling.LANCZOS)

        if width != rgb_image.size[0] or height != rgb_image.size[1]:
            width, height = rgb_image.size

        if width >= height:
            target_width = 512
            target_height = 320
        else:
            target_width = 320
            target_height = 512

        if rgb_image.size != (target_width, target_height):
            rgb_image = rgb_image.resize((target_width, target_height), PIL.Image.Resampling.LANCZOS)

        return rgb_image

    def generate(self, request: MediaGenerationRequest, profile_name: str = "safe") -> VideoGenerationResult:
        if not request.reference_asset:
            raise ValueError("LTX BF16 multiscale image-to-video requires request.reference_asset")

        reference_image = self.gate.validate_reference(request.reference_asset)
        profile = self.gate.select_profile(profile_name)
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{request.request_id}.mp4"
        image = self.prepare_reference_image(PIL.Image.open(reference_image))
        generator = self._make_generator()

        pipe, upsample_pipe = self._load_pipeline()

        base = pipe(
            image=image,
            prompt=request.video_prompt,
            negative_prompt=" ".join(request.negative_constraints) or self.config.negative_prompt,
            height=self.config.low_height,
            width=self.config.low_width,
            num_frames=profile["num_frames"],
            frame_rate=profile["fps"],
            num_inference_steps=8,
            guidance_scale=profile["guidance_scale"],
            image_cond_noise_scale=profile["image_cond_noise_scale"],
            generator=generator,
            output_type="latent",
        )

        upsampled = upsample_pipe(
            latents=base.frames,
            height=self.config.low_height * 2,
            width=self.config.low_width * 2,
            tone_map_compression_ratio=0.6,
            output_type="latent",
        ).frames

        refined = pipe(
            prompt=request.video_prompt,
            negative_prompt=" ".join(request.negative_constraints) or self.config.negative_prompt,
            height=self.config.height,
            width=self.config.width,
            num_frames=profile["num_frames"],
            frame_rate=profile["fps"],
            num_inference_steps=8,
            guidance_scale=profile["guidance_scale"],
            image_cond_noise_scale=0.0,
            generator=generator,
            latents=upsampled,
            output_type="pil",
        )

        frames = refined.frames[0]
        from diffusers.utils import export_to_video

        export_to_video(frames, str(output_path), fps=profile["fps"])

        validation = self.validator.validate(output_path)
        if validation["status"] == "fail":
            raise RuntimeError(f"Generated video failed validation: {validation['reason']}")

        width, height = image.size
        return VideoGenerationResult(
            request_id=request.request_id,
            provider="ltx_bf16_multiscale",
            model_id="Lightricks/LTX-Video:ltxv-2b-0.9.8-distilled",
            output_path=str(output_path),
            duration_seconds=profile["num_frames"] / profile["fps"],
            width=width,
            height=height,
            fps=profile["fps"],
            seed=self.config.seed,
            metadata={
                "profile": profile["profile"],
                "validation": validation,
                "reference_asset": str(reference_image),
                "model_family": "ltx_2b_distilled_0.9.8",
                "pipeline": "bf16_multiscale_latent_upscaler",
                "continuity_constraints": request.continuity_constraints,
                "negative_constraints": request.negative_constraints,
            },
        )

    def _make_generator(self):
        try:
            import torch
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Torch is required to generate LTX videos.") from exc
        return torch.Generator(device="cpu").manual_seed(self.config.seed)

    def _load_pipeline(self):
        if self.is_loaded:
            return self._pipeline, self._upsample_pipe

        try:
            import torch
            from diffusers import LTXConditionPipeline, LTXLatentUpsamplePipeline, LTXVideoTransformer3DModel
            from diffusers.pipelines.ltx.modeling_latent_upsampler import LTXLatentUpsamplerModel
            from safetensors.torch import load_file
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "LTX BF16 multiscale generation requires diffusers, torch, and safetensors dependencies."
            ) from exc

        model_path = self._resolve_local_path(self.config.model_path)
        upscaler_path = self._resolve_local_path(self.config.upscaler_path)

        transformer = LTXVideoTransformer3DModel.from_single_file(
            str(model_path),
            torch_dtype=getattr(torch, self.config.dtype),
        )

        pipe = LTXConditionPipeline.from_pretrained(
            "Lightricks/LTX-Video",
            transformer=transformer,
            torch_dtype=getattr(torch, self.config.dtype),
        )
        pipe.scheduler.config.use_dynamic_shifting = False

        upsampler = LTXLatentUpsamplerModel(
            in_channels=128,
            mid_channels=512,
            num_blocks_per_stage=4,
            dims=3,
        )
        upsampler.load_state_dict(load_file(str(upscaler_path)))
        upsampler = upsampler.to(dtype=getattr(torch, self.config.dtype))
        upsample_pipe = LTXLatentUpsamplePipeline(vae=pipe.vae, latent_upsampler=upsampler)

        pipe.enable_model_cpu_offload()
        upsample_pipe.enable_model_cpu_offload()

        self._pipeline = pipe
        self._upsample_pipe = upsample_pipe
        return pipe, upsample_pipe

    @staticmethod
    def _resolve_local_path(path_value: str | Path) -> Path:
        path = Path(path_value)
        if path.exists():
            return path
        root = Path(__file__).resolve().parents[2]
        for candidate in [root / path, root / "models" / path, root / "models" / "LTX-Video" / path.name]:
            if candidate.exists():
                return candidate
        raise FileNotFoundError(f"LTX model not found: {path_value}")
