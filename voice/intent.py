"""Structured intent routing with a replaceable provider boundary."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class Intent:
    intent: str
    task: str | None = None
    time: str | None = None
    query: str | None = None
    game: str | None = None
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}


class IntentProvider(Protocol):
    def classify(self, text: str) -> Intent: ...


class DeterministicIntentProvider:
    """Small offline fallback for tests and environments without an LLM."""

    _reminder = re.compile(r"(?:remind me to|reminder to)\s+(.+?)(?:\s+at\s+(.+))?$", re.I)
    _game = re.compile(r"(?:start|play)\s+(?:a\s+)?(?:memory\s+)?game", re.I)

    def classify(self, text: str) -> Intent:
        message = " ".join(text.split()).strip()
        if not message:
            return Intent("unknown", message="")
        reminder = self._reminder.search(message)
        if reminder:
            task = reminder.group(1).strip().rstrip(".,!?;:")
            reminder_time = reminder.group(2)
            if reminder_time:
                reminder_time = reminder_time.strip().rstrip(".,!?;:")
            return Intent("create_reminder", task=task, time=reminder_time)
        if self._game.search(message):
            return Intent("start_game", game="memory")
        if re.search(r"\b(who|what|when|where|remember|daughter|son|family)\b", message, re.I):
            return Intent("query_memory", query=message)
        if re.search(r"\b(hello|hi|good morning|good evening|how are you|thank you)\b", message, re.I):
            return Intent("general_conversation", message=message)
        return Intent("unknown", message=message)


class IntentRouter:
    def __init__(self, provider: IntentProvider | None = None) -> None:
        self.provider = provider or DeterministicIntentProvider()

    def route(self, text: str) -> dict[str, Any]:
        try:
            result = self.provider.classify(text)
        except Exception as exc:
            return {"intent": "unknown", "error": f"Intent classification failed: {exc}"}
        if result.intent not in {"create_reminder", "query_memory", "start_game", "general_conversation", "unknown"}:
            return {"intent": "unknown", "error": "Intent provider returned an unsupported intent."}
        return result.to_dict()
