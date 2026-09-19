"""Temporary in-memory reminder tool for Phase 1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from threading import Lock
from typing import Any
from uuid import uuid4


@dataclass
class Reminder:
    id: str
    task: str
    time: str | None
    date: str | None = None
    reminder_type: str | None = None
    recurrence: str | None = None
    status: str = "pending"
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ReminderStore:
    def __init__(self) -> None:
        self._items: dict[str, Reminder] = {}
        self._lock = Lock()

    def create_reminder(
        self,
        task: str,
        time: str | None = None,
        date: str | None = None,
        reminder_type: str | None = None,
        recurrence: str | None = None,
    ) -> dict[str, Any]:
        if not task or not task.strip():
            return {"status": "error", "message": "Reminder task cannot be empty."}
        reminder = Reminder(
            f"rem_{uuid4().hex}", task.strip(), time.strip() if time else None,
            date.strip() if date else None, reminder_type, recurrence,
            created_at=datetime.now().isoformat(),
        )
        with self._lock:
            self._items[reminder.id] = reminder
        return {
            **reminder.to_dict(),
            "status": "success",
            "success": True,
            "reminder_id": reminder.id,
            "reminder": reminder.to_dict(),
        }

    def get_reminders(self) -> list[dict[str, Any]]:
        with self._lock:
            return [item.to_dict() for item in self._items.values()]

    def query_reminder(self, reminder_id: str | None = None) -> dict[str, Any]:
        with self._lock:
            if reminder_id:
                reminder = self._items.get(reminder_id)
                if reminder is None:
                    return {"status": "error", "success": False, "error": "reminder_not_found"}
                return {"status": "success", "success": True, "reminders": [reminder.to_dict()]}
            return {"status": "success", "success": True, "reminders": [item.to_dict() for item in self._items.values()]}

    def cancel_reminder(self, reminder_id: str) -> dict[str, Any]:
        return self._set_status(reminder_id, "cancelled")

    def complete_reminder(self, reminder_id: str) -> dict[str, Any]:
        return self._set_status(reminder_id, "completed")

    def _set_status(self, reminder_id: str, status: str) -> dict[str, Any]:
        with self._lock:
            reminder = self._items.get(reminder_id)
            if reminder is None:
                return {"status": "error", "success": False, "error": "reminder_not_found", "message": "Reminder not found."}
            reminder.status = status
            return {"status": "success", "success": True, "reminder": reminder.to_dict()}
