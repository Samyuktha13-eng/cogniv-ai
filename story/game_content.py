"""Public content-layer factories for the Lakshmi story and reminders."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .scene_store import SceneStore

_ROOT = Path(__file__).resolve().parent.parent


def create_scene_store() -> SceneStore:
    return SceneStore()


def load_reminder_visuals(path: str | Path = _ROOT / "data" / "reminder_visuals.json") -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)["reminders"]
