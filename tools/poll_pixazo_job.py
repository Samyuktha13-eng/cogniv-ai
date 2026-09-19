import argparse
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("request_id")
    args = parser.parse_args()

    api_key = os.getenv("PIXAZO_API_KEY")
    if not api_key:
        raise RuntimeError("PIXAZO_API_KEY is not configured.")

    status_url = f"https://gateway.pixazo.ai/v2/requests/status/{args.request_id}"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    terminal_statuses = {"COMPLETED", "FAILED", "ERROR"}

    for _ in range(90):
        response = requests.get(status_url, headers=headers, timeout=60)
        response.raise_for_status()
        result = response.json()
        status = result.get("status")
        print("STATUS", status, flush=True)

        if status in terminal_statuses:
            if status != "COMPLETED":
                print("FINAL_RESPONSE", result, flush=True)
                raise SystemExit(2)

            media_url = (result.get("output") or {}).get("media_url")
            if isinstance(media_url, list):
                media_url = media_url[0] if media_url else None
            if not media_url:
                raise RuntimeError("Pixazo completed without a media URL.")

            output_path = PROJECT_ROOT / "outputs" / "jasmine_01.mp4"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            media_response = requests.get(media_url, timeout=180)
            media_response.raise_for_status()
            output_path.write_bytes(media_response.content)
            print("OUTPUT_PATH", output_path, flush=True)
            print("OUTPUT_BYTES", output_path.stat().st_size, flush=True)
            return

        time.sleep(10)

    raise TimeoutError("Pixazo generation did not finish within 15 minutes.")


if __name__ == "__main__":
    main()