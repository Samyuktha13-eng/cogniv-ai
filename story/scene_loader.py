"""Load story scene metadata from JSON without connecting to game systems."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import StoryScene

_DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "lakshmi_story_scenes.json"


def load_scene_data(path: str | Path = _DEFAULT_PATH) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def load_scenes(path: str | Path = _DEFAULT_PATH) -> list[StoryScene]:
    data = load_scene_data(path)
    return [StoryScene.from_dict(item) for item in data["scenes"]]
