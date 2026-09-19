"""Time-of-day context without inventing a patient routine."""

from __future__ import annotations

from datetime import datetime


class DailySchedule:
    @staticmethod
    def time_of_day(now: datetime) -> str:
        if now.hour < 12:
            return "morning"
        if now.hour < 17:
            return "afternoon"
        if now.hour < 21:
            return "evening"
        return "night"
