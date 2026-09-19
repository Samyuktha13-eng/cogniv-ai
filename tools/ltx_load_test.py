import os
import time
import gc
import torch
from PIL import Image

from diffusers import LTXConditionPipeline, LTXVideoTransformer3DModel
from diffusers.pipelines.ltx.modeling_latent_upsampler import LTXLatentUpsamplerModel
from diffusers import LTXLatentUpsamplePipeline
from diffusers.utils import export_to_video

MODEL_FILE = r"models\LTX-Video\ltxv-2b-0.9.8-distilled-fp8.safetensors"
UPSCALER_FILE = r"models\LTX-Video\ltxv-spatial-upscaler-0.9.8.safetensors"
REFERENCE_IMAGE = r"Patient story image\04_school_morning\school_05_barefoot_walk.jpg"

print("=" * 60)
print("LTX-Video 2B FP8 LOAD TEST")
print("=" * 60)

print(f"CUDA available: {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise RuntimeError("CUDA is not available.")

print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
print(f"Model file exists: {os.path.exists(MODEL_FILE)}")

if not os.path.exists(MODEL_FILE):
    raise FileNotFoundError(MODEL_FILE)
if not os.path.exists(UPSCALER_FILE):
    raise FileNotFoundError(UPSCALER_FILE)

print("\nLoading FP8 transformer from local checkpoint...")
start = time.time()

transformer = LTXVideoTransformer3DModel.from_single_file(
    MODEL_FILE,
    torch_dtype=torch.float8_e4m3fn,
)
transformer = transformer.to(dtype=torch.bfloat16)

print(f"Transformer loaded in {time.time() - start:.1f}s")

print("\nLoading LTX pipeline components...")
start = time.time()

pipe = LTXConditionPipeline.from_pretrained(
    "Lightricks/LTX-Video",
    transformer=transformer,
    torch_dtype=torch.bfloat16,
)
pipe.scheduler.config.use_dynamic_shifting = False

print("\nLoading 0.9.8 spatial upscaler...")
from safetensors.torch import load_file

upsampler = LTXLatentUpsamplerModel(
    in_channels=128,
    mid_channels=512,
    num_blocks_per_stage=4,
    dims=3,
)
upsampler.load_state_dict(load_file(UPSCALER_FILE))
upsampler = upsampler.to(device="cuda", dtype=torch.bfloat16)
upsample_pipe = LTXLatentUpsamplePipeline(vae=pipe.vae, latent_upsampler=upsampler)

print(f"Pipeline loaded in {time.time() - start:.1f}s")

print("\nEnabling CPU offload...")
pipe.enable_model_cpu_offload()

gc.collect()
torch.cuda.empty_cache()

allocated = torch.cuda.memory_allocated() / 1024**3
reserved = torch.cuda.memory_reserved() / 1024**3

print("\n" + "=" * 60)
print("LOAD TEST SUCCESS")
print("=" * 60)
print(f"GPU allocated: {allocated:.2f} GB")
print(f"GPU reserved:  {reserved:.2f} GB")
print("LTX 2B FP8 pipeline loaded successfully.")
print("\nStarting official-style multi-scale image-to-video generation...")
generation_start = time.time()

reference_image = Image.open(REFERENCE_IMAGE).convert("RGB")
prompt = (
    "The two schoolgirls walk forward together along the village path toward school. They take natural walking "
    "steps with alternating legs, their school bags sway, and both girls remain together. The camera gently follows "
    "them while preserving their appearance and the original village environment."
)
negative_prompt = "standing still, frozen pose, blurry, distorted face, morphing, extra people, missing person, scene change, camera shake, flicker, noise"
low_height = 224
low_width = 352
base = pipe(
    image=reference_image,
    prompt=prompt,
    negative_prompt=negative_prompt,
    height=low_height,
    width=low_width,
    num_frames=25,
    frame_rate=8,
    timesteps=[1000, 993, 987, 981, 975, 909, 725, 0.03],
    guidance_scale=1.0,
    image_cond_noise_scale=0.025,
    decode_timestep=0.05,
    decode_noise_scale=0.025,
    generator=torch.Generator(device="cuda").manual_seed(42),
    output_type="latent",
)

upscaled = upsample_pipe(
    latents=base.frames,
    height=low_height * 2,
    width=low_width * 2,
    tone_map_compression_ratio=0.6,
    output_type="latent",
).frames

refined = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    height=low_height * 2,
    width=low_width * 2,
    num_frames=25,
    frame_rate=8,
    timesteps=[1000, 909, 725, 421, 0],
    denoise_strength=0.999,
    guidance_scale=1.0,
    image_cond_noise_scale=0.0,
    decode_timestep=0.05,
    decode_noise_scale=0.025,
    latents=upscaled,
    generator=torch.Generator(device="cuda").manual_seed(42),
    output_type="pil",
).frames[0]

video = [frame.resize((512, 320), Image.Resampling.LANCZOS) for frame in refined]
output_path = "outputs/ltx_i2v_school_multiscale_seed42.mp4"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
export_to_video(video, output_path, fps=8)

print(f"Generation completed in {time.time() - generation_start:.1f}s")
print(f"Video written to: {output_path}")
print("LTX 2B FP8 image-to-video generation test succeeded.")
print("=" * 60)
