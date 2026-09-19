"""Graceful reminder interruption and reminiscence resumption."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .models import ReminderCue, TimelineState
from .reminder_scheduler import ReminderScheduler


class TimelineEngine:
    def __init__(self, scheduler: ReminderScheduler) -> None:
        self.scheduler = scheduler
        self.state = TimelineState()

    def begin_reminiscence(self, state: dict[str, Any]) -> None:
        self.state.active_reminiscence = True
        self.state.paused_state = state

    def check(self, now: datetime) -> ReminderCue | None:
        cue = self.scheduler.due(now)
        if cue:
            self.state.pending_reminder = cue.to_dict()
            if self.state.active_reminiscence:
                self.state.paused_state = self.state.paused_state or {}
                self.state.active_reminiscence = False
        return cue

    def complete_reminder(self) -> dict[str, Any] | None:
        pending = self.state.pending_reminder
        if pending and hasattr(self.scheduler.provider, "complete_reminder"):
            self.scheduler.provider.complete_reminder(pending["reminder_id"])
        paused = self.state.paused_state
        self.state.pending_reminder = None
        self.state.active_reminiscence = paused is not None
        return paused

    def snooze_or_skip(self) -> None:
        self.state.pending_reminder = None

    def to_dict(self) -> dict[str, Any]:
        return self.state.to_dict()
