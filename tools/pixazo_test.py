import argparse
import base64
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=True)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

API_KEY = os.getenv("PIXAZO_API_KEY")
DEFAULT_IMAGE_PATH = PROJECT_ROOT / "Patient story image" / "01_jasmine_morning" / "jasmine_01_door.jpg"

if not API_KEY:
    raise RuntimeError("PIXAZO_API_KEY is not set")


def to_data_url(image_path: Path) -> str:
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    suffix = image_path.suffix.lower().lstrip(".")
    mime = "image/jpeg" if suffix in {"jpg", "jpeg"} else "image/png"
    return f"data:{mime};base64,{encoded}"


def build_rag_prompt() -> str:
    return (
        "A gentle cinematic morning moment. Lakshmi slowly opens the old wooden back door "
        "and begins stepping outside. Subtle natural body movement, realistic cloth movement, "
        "soft early-morning light, and a calm village atmosphere. Preserve Lakshmi's identity, "
        "clothing, face, environment, and composition from the reference image. Slow camera "
        "push-in, realistic motion, no sudden movements, and no new people or objects."
    )


def request_video(endpoint, payload):
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": API_KEY,
    }
    response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
    print("HTTP status:", response.status_code)
    print(response.text)
    return response


def poll_until_done(request_id):
    status_url = f"https://gateway.pixazo.ai/v2/requests/status/{request_id}"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}
    for _ in range(20):
        time.sleep(5)
        status_resp = requests.get(status_url, headers=headers, timeout=120)
        print("Status poll:", status_resp.status_code)
        print(status_resp.text)
        if not status_resp.ok:
            continue
        status_json = status_resp.json()
        status = status_json.get("status")
        output = status_json.get("output") or {}
        media_url = output.get("media_url")
        if status in {"COMPLETED", "ERROR", "FAILED"}:
            if media_url:
                print("media_url:", media_url)
            return status_json
    return None


def run_image_to_video(image_path: Path):
    endpoint = "https://gateway.pixazo.ai/ltx-video/v1/image-to-video"
    image_url = to_data_url(image_path)
    prompt = build_rag_prompt()
    payload = {
        "prompt": prompt,
        "image_url": image_url,
    }
    print("Using image:", image_path)
    print("Prompt:", prompt)
    response = request_video(endpoint, payload)
    if response.status_code not in (200, 201, 202):
        return
    request_id = response.json().get("request_id")
    print("request_id:", request_id)
    poll_until_done(request_id)


def main():
    parser = argparse.ArgumentParser(description="Validate Pixazo free image-to-video using a project reference image and RAG prompt flow.")
    parser.add_argument("--image-path", type=Path, default=DEFAULT_IMAGE_PATH)
    args = parser.parse_args()

    run_image_to_video(args.image_path)


if __name__ == "__main__":
    main()
