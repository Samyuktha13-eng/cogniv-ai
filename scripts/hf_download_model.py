import os
from dotenv import load_dotenv
from huggingface_hub import snapshot_download

load_dotenv()

MODEL_ID = "bodhan-ai/indic-transcribe-core"
OUTPUT_DIR = r"C:\Users\dmane\Downloads\Cogniv AI\models\indic-transcribe-core"

hf_token = os.getenv("HF_TOKEN")

if not hf_token:
    raise RuntimeError(
        "HF_TOKEN was not found in the .env file."
    )

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("HUGGING FACE MODEL DOWNLOAD")
print("=" * 60)
print("Model:", MODEL_ID)
print("Destination:", OUTPUT_DIR)
print("Workers: 8")
print()
print("Download starting...")
print("Progress will be shown below.")
print("=" * 60)

model_dir = snapshot_download(
    repo_id=MODEL_ID,
    token=hf_token,
    local_dir=OUTPUT_DIR,
    max_workers=8,
    force_download=False
)

print()
print("=" * 60)
print("DOWNLOAD COMPLETE")
print("=" * 60)
print("Model directory:")
print(model_dir)
print("=" * 60)
