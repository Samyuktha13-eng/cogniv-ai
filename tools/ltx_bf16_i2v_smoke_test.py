import time
import torch
from diffusers import LTXConditionPipeline, LTXVideoTransformer3DModel
from PIL import Image
from diffusers.utils import export_to_video

MODEL_FILE = r"models\LTX-Video\ltxv-2b-0.9.8-distilled.safetensors"
IMAGE_FILE = r"Patient story image\04_school_morning\school_05_barefoot_walk.jpg"
OUTPUT_FILE = r"outputs\ltx_bf16_i2v_school_walk_seed42.mp4"

SEED = 42
FRAMES = 17
WIDTH = 512
HEIGHT = 320
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

print("Loading non-FP8 BF16 LTX 2B...")
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

# This diffusers build enables dynamic timestep shifting by default, but the
# loaded scheduler requires an explicit `mu` value. Disabling it keeps the
# smoke test compatible with the current LTX pipeline release while validating
# the real BF16 I2V output path.
pipe.scheduler.config.use_dynamic_shifting = False

pipe.enable_model_cpu_offload()

print(f"Pipeline ready in {time.time() - t0:.1f}s")

image = Image.open(IMAGE_FILE).convert("RGB")

generator = torch.Generator(device="cpu").manual_seed(SEED)

print("Starting BF16 I2V generation...")
t1 = time.time()

result = pipe(
    image=image,
    prompt=prompt,
    width=WIDTH,
    height=HEIGHT,
    num_frames=FRAMES,
    num_inference_steps=8,
    guidance_scale=1.0,
    image_cond_noise_scale=0.025,
    generator=generator,
)

frames = result.frames[0]

print(f"Generation finished in {time.time() - t1:.1f}s")
print(f"Generated frames: {len(frames)}")

export_to_video(frames, OUTPUT_FILE, fps=FPS)

print()
print("BF16 I2V TEST COMPLETE")
print(f"Output: {OUTPUT_FILE}")
