"""Future memory retrieval boundary; RAG is intentionally out of scope."""

from __future__ import annotations

from typing import Any

from memory.retriever import MemoryRetriever
from memory.store import MemoryStore


def memory_search(query: str) -> dict[str, str]:
    if not query or not query.strip():
        return {"status": "error", "message": "Memory query cannot be empty."}
    return {"status": "not_connected", "message": "Personal memory retrieval is not connected yet."}


class MemoryTool:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store
        self.retriever = MemoryRetriever(store)

    def save(self, memory: dict[str, Any]) -> dict[str, Any]:
        saved = self.store.save_memory(memory)
        return {"success": True, "operation": "save", "memory_id": saved["memory_id"]}

    def query(self, patient_id: str, query: str, language: str | None = None) -> dict[str, Any]:
        return {"success": True, "operation": "query", "results": self.retriever.search_memories(patient_id, query, language)}

    def get(self, patient_id: str, memory_id: str) -> dict[str, Any]:
        memory = self.store.get_memory(memory_id, patient_id)
        return {"success": memory is not None, "operation": "get", "memory": memory}
