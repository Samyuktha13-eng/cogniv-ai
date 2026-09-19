import time
import torch
from diffusers import LTXConditionPipeline, LTXVideoTransformer3DModel

MODEL_FILE = r"models\LTX-Video\ltxv-2b-0.9.8-distilled.safetensors"

print("Loading non-FP8 LTX 2B checkpoint...")
t0 = time.time()

transformer = LTXVideoTransformer3DModel.from_single_file(
    MODEL_FILE,
    torch_dtype=torch.bfloat16,
)

print(f"Transformer loaded in {time.time() - t0:.1f}s")

print("Loading LTX pipeline...")
t1 = time.time()

pipe = LTXConditionPipeline.from_pretrained(
    "Lightricks/LTX-Video",
    transformer=transformer,
    torch_dtype=torch.bfloat16,
)

print(f"Pipeline loaded in {time.time() - t1:.1f}s")

print("Enabling CPU offload...")
pipe.enable_model_cpu_offload()

if torch.cuda.is_available():
    print(f"GPU allocated: {torch.cuda.memory_allocated()/1024**3:.2f} GB")
    print(f"GPU reserved:  {torch.cuda.memory_reserved()/1024**3:.2f} GB")

print()
print("BF16 LTX LOAD TEST SUCCESS")
print("No video generation was performed.")
