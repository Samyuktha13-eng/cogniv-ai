"""Transport models for reminder interruption and resumption."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ReminderCue:
    reminder_id: str
    reminder_type: str | None
    task: str
    visual_asset: str | None
    voice_style: str | None
    priority: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TimelineState:
    active_reminiscence: bool = False
    paused_state: dict[str, Any] | None = None
    pending_reminder: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
