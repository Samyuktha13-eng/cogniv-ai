import os
import time
import torch
from PIL import Image
from diffusers import LTXConditionPipeline, LTXVideoTransformer3DModel, LTXLatentUpsamplePipeline
from diffusers.pipelines.ltx.modeling_latent_upsampler import LTXLatentUpsamplerModel
from diffusers.utils import export_to_video
from safetensors.torch import load_file

MODEL_FILE = r"models\LTX-Video\ltxv-2b-0.9.8-distilled.safetensors"
UPSCALER_FILE = r"models\LTX-Video\ltxv-spatial-upscaler-0.9.8.safetensors"
IMAGE_FILE = r"Patient story image\04_school_morning\school_05_barefoot_walk.jpg"
OUTPUT_FILE = r"outputs\ltx_bf16_multiscale_i2v_school_walk_seed42.mp4"

SEED = 42
FRAMES = 17
FINAL_WIDTH = 512
FINAL_HEIGHT = 320
FPS = 8

prompt = (
    "Two Indian schoolgirls walk together along the same rural morning "
    "school route shown in the reference image. Both girls remain visible "
    "full body. They take several natural walking steps toward school, "
    "with gentle movement of their legs, feet, arms and school bags. "
    "Keep the same girls, clothing, bags, environment, road and morning "
    "lighting. Natural realistic motion. No new people, no vehicles, "
    "no text, no scene change, no camera jump, no invented objects."
)

negative_prompt = (
    "blurry, noisy, distorted face, extra people, scene change, camera shake, "
    "flicker, warped limbs, invented objects, text, watermark."
)

print("Loading BF16 LTX 2B + latent upscaler...")
t0 = time.time()

transformer = LTXVideoTransformer3DModel.from_single_file(
    MODEL_FILE,
    torch_dtype=torch.bfloat16,
)

pipe = LTXConditionPipeline.from_pretrained(
    "Lightricks/LTX-Video",
    transformer=transformer,
    torch_dtype=torch.bfloat16,
)

# Required for this diffusers build: the scheduler in this checkpoint expects
# the LTX 0.9.8 multi-scale pipeline flow and dynamic shifting is not compatible
# with the simplified calling pattern used in the earlier smoke test.
pipe.scheduler.config.use_dynamic_shifting = False

upsampler = LTXLatentUpsamplerModel(
    in_channels=128,
    mid_channels=512,
    num_blocks_per_stage=4,
    dims=3,
)
upsampler.load_state_dict(load_file(UPSCALER_FILE))
upsampler = upsampler.to(dtype=torch.bfloat16)
upsample_pipe = LTXLatentUpsamplePipeline(vae=pipe.vae, latent_upsampler=upsampler)

pipe.enable_model_cpu_offload()
upsample_pipe.enable_model_cpu_offload()

print(f"Pipeline ready in {time.time() - t0:.1f}s")

image = Image.open(IMAGE_FILE).convert("RGB")
generator = torch.Generator(device="cpu").manual_seed(SEED)

low_height = 224
low_width = 352

print("Running official-style multi-scale first pass...")
first_pass_t0 = time.time()

base = pipe(
    image=image,
    prompt=prompt,
    negative_prompt=negative_prompt,
    height=low_height,
    width=low_width,
    num_frames=FRAMES,
    frame_rate=FPS,
    num_inference_steps=8,
    guidance_scale=1.0,
    image_cond_noise_scale=0.025,
    generator=generator,
    output_type="latent",
)

print(f"First pass finished in {time.time() - first_pass_t0:.1f}s")
print(f"Latent frames: {len(base.frames)}")

print("Upsampling latent representation...")
upsampled = upsample_pipe(
    latents=base.frames,
    height=low_height * 2,
    width=low_width * 2,
    tone_map_compression_ratio=0.6,
    output_type="latent",
).frames

print(f"Upsampled latent frames: {len(upsampled)}")

print("Running official-style refinement pass...")
refine_t0 = time.time()

refined = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    height=FINAL_HEIGHT,
    width=FINAL_WIDTH,
    num_frames=FRAMES,
    frame_rate=FPS,
    num_inference_steps=8,
    guidance_scale=1.0,
    image_cond_noise_scale=0.0,
    generator=generator,
    latents=upsampled,
    output_type="pil",
)

frames = refined.frames[0]
print(f"Refinement finished in {time.time() - refine_t0:.1f}s")
print(f"Generated frames: {len(frames)}")

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
export_to_video(frames, OUTPUT_FILE, fps=FPS)

print()
print("OFFICIAL BF16 LTX MULTISCALE I2V TEST COMPLETE")
print(f"Output: {OUTPUT_FILE}")
