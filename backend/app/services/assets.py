import os
from pathlib import Path
from urllib.parse import quote, urlparse

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STORY_IMAGE_ROOT = PROJECT_ROOT / "Patient story image"
load_dotenv(PROJECT_ROOT / ".env", override=True)


class AssetPublishError(RuntimeError):
    """Raised when a story asset cannot be exposed to the provider."""


class UnsupportedAssetError(AssetPublishError):
    pass


class StoryAssetService:
    supported_extensions = {".jpg", ".jpeg", ".png"}

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.getenv("COGNIV_ASSET_BASE_URL", "")).rstrip("/")

    def publish_image(self, local_path: Path) -> str:
        """Return the HTTPS URL where the configured asset host serves this image."""
        try:
            resolved_path = local_path.resolve()
            relative_path = resolved_path.relative_to(STORY_IMAGE_ROOT.resolve())
        except ValueError as error:
            raise AssetPublishError("Source image is outside the story asset directory.") from error

        if not resolved_path.is_file():
            raise AssetPublishError("Source image file not found.")
        if resolved_path.suffix.lower() not in self.supported_extensions:
            raise UnsupportedAssetError("Source image must be a JPEG or PNG file.")

        parsed_url = urlparse(self.base_url)
        if parsed_url.scheme != "https" or not parsed_url.netloc:
            raise AssetPublishError(
                "COGNIV_ASSET_BASE_URL must be an HTTPS URL serving the story image directory."
            )

        encoded_path = "/".join(quote(part) for part in relative_path.parts)
        return f"{self.base_url}/{encoded_path}"

    def validate_public_image_url(self, image_url: str) -> None:
        try:
            response = requests.get(
                image_url,
                headers={"User-Agent": "CognivAI-AssetValidator/1.0"},
                stream=True,
                timeout=15,
            )
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
            if not content_type.startswith("image/"):
                raise AssetPublishError("Public asset URL does not serve an image.")
        except requests.RequestException as error:
            status = getattr(error.response, "status_code", "timeout")
            raise AssetPublishError(
                f"Public asset URL could not be reached ({status}): {image_url}. "
                "Configure COGNIV_ASSET_BASE_URL with a stable public HTTPS host."
            ) from error
        finally:
            if "response" in locals():
                response.close()
