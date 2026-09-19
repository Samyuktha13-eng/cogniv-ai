"""Deterministic routing decisions for validated semantic intents."""

from __future__ import annotations

from typing import Any

from voice.semantic_validation import validate_semantic_result
from .reminders import ReminderStore


_ROUTE_ACTIONS = {
    "create_reminder": ("reminder", "create"),
    "cancel_reminder": ("reminder", "cancel"),
    "query_reminder": ("reminder", "query"),
    "complete_reminder": ("reminder", "complete"),
    "query_memory": ("memory", "query"),
    "save_memory": ("memory", "save"),
    "start_game": ("game", "start"),
    "answer_game": ("game", "answer"),
    "general_conversation": ("conversation", "respond"),
    "unknown": ("unknown", "reject"),
}

_REMINDER_FIELDS = ("task", "time", "date", "reminder_type", "recurrence")


def route_semantic_intent(semantic: dict[str, Any]) -> dict[str, Any]:
    """Convert one canonical semantic object into a side-effect-free route."""
    try:
        validate_semantic_result(semantic)
    except (TypeError, ValueError) as exc:
        return {
            "route": "unknown",
            "action": "reject",
            "payload": {},
            "error": f"Invalid semantic intent: {exc}",
        }

    if semantic["needs_clarification"]:
        return {
            "route": "clarification",
            "action": "ask",
            "payload": {"question": semantic["clarification_question"]},
        }

    intent = semantic["intent"]
    route, action = _ROUTE_ACTIONS[intent]
    entities = semantic["entities"]
    if intent in {"create_reminder", "cancel_reminder", "query_reminder", "complete_reminder"}:
        payload = {field: entities[field] for field in _REMINDER_FIELDS}
        payload["reminder_id"] = entities["memory_id"]
    elif intent in {"query_memory", "save_memory"}:
        payload = {field: entities[field] for field in ("query", "memory_id", "person", "task") if entities.get(field) is not None}
    elif intent in {"start_game", "answer_game"}:
        payload = {"game": entities["game"]}
    else:
        payload = {}
    return {"route": route, "action": action, "payload": payload}


class ToolRouter:
    """Object interface for dependency injection and future tool dispatch."""

    def __init__(self, reminder_tool: Any | None = None, memory_tool: Any | None = None) -> None:
        self.reminder_tool = reminder_tool or ReminderStore()
        self.memory_tool = memory_tool

    def route(self, semantic: dict[str, Any]) -> dict[str, Any]:
        return route_semantic_intent(semantic)

    def execute(self, semantic: dict[str, Any], patient_id: str | None = None) -> dict[str, Any]:
        """Delegate reminder or memory routes through injected application tools."""
        decision = self.route(semantic)
        if decision["route"] == "clarification":
            return decision
        if decision["route"] != "reminder":
            if decision["route"] == "memory" and self.memory_tool is not None:
                try:
                    payload = decision["payload"]
                    if decision["action"] == "query":
                        result = self.memory_tool.query(patient_id or "", payload.get("query") or payload.get("person") or payload.get("task") or "")
                    elif decision["action"] == "save":
                        result = self.memory_tool.save(payload)
                    else:
                        return decision
                    return {**decision, "tool_result": result}
                except Exception as exc:
                    return {**decision, "tool_result": {"success": False, "error": "memory_execution_failed", "detail": str(exc)}}
            return decision
        payload = decision["payload"]
        try:
            action = decision["action"]
            method_name = {
                "create": "create_reminder",
                "cancel": "cancel_reminder",
                "query": "query_reminder",
                "complete": "complete_reminder",
            }[action]
            method = getattr(self.reminder_tool, method_name)
            if action == "create":
                result = method(payload["task"], payload["time"], payload["date"], payload["reminder_type"], payload["recurrence"])
            elif action == "query":
                result = method(payload.get("reminder_id"))
            else:
                result = method(payload.get("reminder_id") or payload.get("task", ""))
            return {**decision, "tool_result": result}
        except Exception as exc:
            return {**decision, "tool_result": {"success": False, "error": "reminder_execution_failed", "detail": str(exc)}}
