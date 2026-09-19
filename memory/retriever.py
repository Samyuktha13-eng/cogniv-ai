"""Deterministic patient-scoped memory retrieval."""

from __future__ import annotations

import re
from typing import Any

from .store import MemoryStore


_STOPWORDS = {"a", "about", "at", "before", "did", "do", "every", "her", "me", "tell", "the", "what", "with", "your"}


def _tokens(value: str) -> set[str]:
    tokens = set(re.findall(r"[\w]+", value.casefold().replace("'s", ""))) - _STOPWORDS
    normalized = set(tokens)
    for token in tokens:
        if token == "made":
            normalized.add("make")
        elif token.endswith("ies"):
            normalized.add(token[:-3] + "y")
        elif token.endswith("s") and len(token) > 4:
            normalized.add(token[:-1])
    return normalized


class MemoryRetriever:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def search_memories(self, patient_id: str, query: str, language: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
        query_tokens = _tokens(query)
        if not query_tokens:
            return []
        ranked = []
        for memory in self.store.list_memories(patient_id):
            if language and memory["language"] != language:
                continue
            title_tokens = _tokens(memory["title"])
            tag_tokens = _tokens(" ".join(memory["people"] + memory["relationships"] + memory["objects"] + memory["tags"]))
            body_tokens = _tokens(" ".join([memory["story"], memory.get("place") or "", memory.get("time") or "", memory.get("activity") or "", memory.get("emotion") or ""]))
            matched = query_tokens & (title_tokens | tag_tokens | body_tokens)
            if not matched:
                continue
            score = sum((3 if token in title_tokens else 2 if token in tag_tokens else 1) for token in matched) / (3 * len(query_tokens))
            ranked.append({"memory_id": memory["memory_id"], "title": memory["title"], "relevance": round(score, 4), "source": memory["source"], "confidence": memory["confidence"], "sensitive": memory["sensitive"], "memory": memory})
        ranked.sort(key=lambda item: (-item["relevance"], item["memory"].get("sequence") or 0))
        return ranked[:limit]
