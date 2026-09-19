"""Adapter-based due reminder selection using existing reminder records."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from story.game_content import load_reminder_visuals

from .models import ReminderCue


class ReminderProvider(Protocol):
    def get_reminders(self) -> list[dict[str, Any]]: ...


_PRIORITY = {"safety": 1, "medication": 2, "appointment": 3, "routine": 4}
_VISUAL_ALIASES = {"medication": "medicine", "hydration": "water", "activity": "walk"}


class ReminderScheduler:
    def __init__(self, provider: ReminderProvider, visuals: list[dict[str, Any]] | None = None) -> None:
        self.provider = provider
        self.visuals = {item["reminder_type"]: item for item in (visuals or load_reminder_visuals())}

    def due(self, now: datetime) -> ReminderCue | None:
        current_time = now.strftime("%H:%M")
        due_items = []
        for reminder in self.provider.get_reminders():
            if reminder.get("status") != "pending" or not reminder.get("time") or reminder["time"] > current_time:
                continue
            reminder_date = reminder.get("date")
            if reminder_date not in (None, "", "today"):
                continue
            kind = reminder.get("reminder_type") or "routine"
            visual = self.visuals.get(_VISUAL_ALIASES.get(kind, kind))
            due_items.append(ReminderCue(reminder["id"], reminder.get("reminder_type"), reminder["task"], visual.get("image_asset") if visual else None, visual.get("suggested_voice_style") if visual else None, _PRIORITY.get(kind, 4)))
        return min(due_items, key=lambda cue: (cue.priority, cue.reminder_id)) if due_items else None
