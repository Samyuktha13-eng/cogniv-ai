"""Lazy CogVideoX image-to-video adapter.

This module deliberately does not import or load Diffusers, Torch, or model
weights at module import time. It is safe to use for configuration and tests
in environments without optional media dependencies.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ..models import MediaGenerationRequest, VideoGenerationResult


@dataclass(frozen=True)
class CogVideoXConfig:
    model_id: str = "THUDM/CogVideoX-5b-I2V"
    device: str = "auto"
    dtype: str = "float16"
    num_frames: int = 49
    num_inference_steps: int = 50
    guidance_scale: float = 6.0
    fps: int = 8
    seed: int | None = 42
    enable_cpu_offload: bool = True
    enable_vae_tiling: bool = True
    enable_vae_slicing: bool = True
    output_dir: str = "outputs/generated_videos"
    asset_root: str | None = None


class CogVideoXUnavailableError(RuntimeError):
    """Raised when generation is requested without optional runtime packages."""


class CogVideoXProvider:
    def __init__(self, config: CogVideoXConfig | None = None, pipeline: Any | None = None, image_loader: Callable[[Path], Any] | None = None, generator_factory: Callable[[int, str], Any] | None = None) -> None:
        self.config = config or CogVideoXConfig()
        self._pipeline = pipeline
        self._image_loader = image_loader
        self._generator_factory = generator_factory

    @property
    def is_loaded(self) -> bool:
        return self._pipeline is not None

    def generate(self, request: MediaGenerationRequest) -> VideoGenerationResult:
        if not request.reference_asset:
            raise ValueError("CogVideoX image-to-video requires request.reference_asset")
        image_path = self._resolve_asset(request.reference_asset)
        if not image_path.exists():
            raise FileNotFoundError(f"Reference image not found: {image_path}")
        pipeline = self._load_pipeline()
        image = self._load_image(image_path)
        generator = self._generator()
        kwargs: dict[str, Any] = {
            "image": image,
            "prompt": request.video_prompt,
            "num_frames": self.config.num_frames,
            "num_inference_steps": self.config.num_inference_steps,
            "guidance_scale": self.config.guidance_scale,
            "generator": generator,
        }
        parameters = inspect.signature(pipeline.__call__).parameters
        if "negative_prompt" in parameters:
            kwargs["negative_prompt"] = " ".join(request.negative_constraints)
        output = pipeline(**kwargs)
        frames = getattr(output, "frames", output)
        output_path = self._save_video(frames, request.request_id)
        width, height = _dimensions(image)
        return VideoGenerationResult(
            request_id=request.request_id,
            provider="cogvideox",
            model_id=self.config.model_id,
            output_path=str(output_path),
            duration_seconds=self.config.num_frames / self.config.fps,
            width=width,
            height=height,
            fps=self.config.fps,
            seed=self.config.seed,
            metadata={
                "synthetic_memory_cue": True,
                "continuity_constraints": request.continuity_constraints,
                "negative_constraints": request.negative_constraints,
            },
        )

    def _load_pipeline(self) -> Any:
        if self._pipeline is not None:
            return self._pipeline
        try:
            import torch
            from diffusers import CogVideoXImageToVideoPipeline
        except ImportError as exc:
            raise CogVideoXUnavailableError(
                "CogVideoX requires optional torch and diffusers packages; they were not installed."
            ) from exc
        kwargs = {"torch_dtype": getattr(torch, self.config.dtype)}
        self._pipeline = CogVideoXImageToVideoPipeline.from_pretrained(self.config.model_id, **kwargs)
        device = self.config.device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.config.enable_cpu_offload and device == "cuda" and hasattr(self._pipeline, "enable_model_cpu_offload"):
            self._pipeline.enable_model_cpu_offload()
        else:
            self._pipeline.to(device)
        if self.config.enable_vae_tiling and hasattr(self._pipeline, "vae") and hasattr(self._pipeline.vae, "enable_tiling"):
            self._pipeline.vae.enable_tiling()
        if self.config.enable_vae_slicing and hasattr(self._pipeline, "vae") and hasattr(self._pipeline.vae, "enable_slicing"):
            self._pipeline.vae.enable_slicing()
        return self._pipeline

    def _generator(self) -> Any:
        if self.config.seed is None:
            return None
        if self._generator_factory is not None:
            device = "cuda" if self.config.device == "cuda" else "cpu"
            return self._generator_factory(self.config.seed, device)
        try:
            import torch
        except ImportError as exc:
            raise CogVideoXUnavailableError("A configured seed requires optional torch at generation time.") from exc
        device = "cuda" if self.config.device in {"auto", "cuda"} and torch.cuda.is_available() else "cpu"
        return torch.Generator(device=device).manual_seed(self.config.seed)

    def _load_image(self, path: Path) -> Any:
        if self._image_loader is not None:
            return self._image_loader(path)
        try:
            from PIL import Image
        except ImportError as exc:
            raise CogVideoXUnavailableError("CogVideoX image loading requires optional Pillow; it was not installed.") from exc
        return Image.open(path).convert("RGB")

    def _resolve_asset(self, reference_asset: str) -> Path:
        path = Path(reference_asset)
        if path.is_absolute():
            return path
        root = Path(self.config.asset_root) if self.config.asset_root else Path(__file__).resolve().parents[2] / "Patient story image"
        return root / path

    def _save_video(self, frames: Any, request_id: str) -> Path:
        try:
            from diffusers.utils import export_to_video
        except ImportError as exc:
            raise CogVideoXUnavailableError("Video export requires optional diffusers; it was not installed.") from exc
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{request_id}.mp4"
        export_to_video(frames, str(output_path), fps=self.config.fps)
        return output_path


def _dimensions(image: Any) -> tuple[int | None, int | None]:
    size = getattr(image, "size", None)
    return (size[0], size[1]) if isinstance(size, tuple) and len(size) == 2 else (None, None)
