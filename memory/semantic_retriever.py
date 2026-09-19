"""Hybrid structured and semantic autobiographical-memory retrieval."""

from __future__ import annotations

import math
from typing import Any

from reminiscence.memory_selector import MemoryCandidate, MemorySelector, _terms

from .semantic_embedder import SemanticEmbedder


class SemanticMemoryRetriever:
    def __init__(self, selector: MemorySelector, embedder: SemanticEmbedder, semantic_weight: float = 0.35) -> None:
        if not 0 <= semantic_weight <= 1:
            raise ValueError("semantic_weight must be between 0 and 1")
        self.selector = selector
        self.embedder = embedder
        self.semantic_weight = semantic_weight

    def retrieve(
        self,
        patient_id: str,
        utterance: str,
        meaning_result: dict[str, Any] | None = None,
        limit: int = 5,
        exclude_ids: set[str] | None = None,
    ) -> list[MemoryCandidate]:
        candidates = [candidate for source in self.selector.sources for candidate in source.candidates(patient_id)]
        excluded = exclude_ids or set()
        candidates = [candidate for candidate in candidates if candidate.memory_id not in excluded]
        if not candidates or limit <= 0:
            return []
        query = _semantic_query(utterance, meaning_result)
        texts = [_candidate_text(candidate) for candidate in candidates]
        vectors = self.embedder.embed([query, *texts])
        query_vector, candidate_vectors = vectors[0], vectors[1:]
        structured_scores = [_structured_score(query, candidate) for candidate in candidates]
        maximum = max(structured_scores, default=0.0)
        ranked = []
        for index, candidate in enumerate(candidates):
            structured = structured_scores[index] / maximum if maximum else 0.0
            semantic = _cosine(query_vector, candidate_vectors[index])
            score = (1 - self.semantic_weight) * structured + self.semantic_weight * semantic
            ranked.append((score, structured, -index, candidate))
        ranked.sort(key=lambda item: (-item[0], -item[1], item[2]))
        return [item[3] for item in ranked[:limit]]


def _semantic_query(utterance: str, meaning_result: dict[str, Any] | None) -> str:
    parts = [utterance]
    entities = (meaning_result or {}).get("entities", {})
    for key in ("person", "place", "object", "activity", "concepts"):
        value = entities.get(key)
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif value:
            parts.append(str(value))
    return " ".join(parts)


def _candidate_text(candidate: MemoryCandidate) -> str:
    fields = {
        "title": candidate.title,
        "topics": candidate.topics,
        "people": candidate.people,
        "places": candidate.places,
        "objects": candidate.objects,
        "activities": candidate.activities,
        "sensory_cues": candidate.sensory_cues,
    }
    return " ".join(_flatten(value) for value in fields.values())


def _structured_score(query: str, candidate: MemoryCandidate) -> float:
    wanted = _terms({"query": query})
    return (
        3 * len(wanted & _terms({"topics": candidate.topics}))
        + 4 * len(wanted & _terms({"people": candidate.people}))
        + 3 * len(wanted & _terms({"places": candidate.places}))
        + 2 * len(wanted & _terms({"objects": candidate.objects}))
        + 2 * len(wanted & _terms({"activities": candidate.activities}))
        + len(wanted & _terms({"sensory_cues": candidate.sensory_cues}))
    )


def _cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("embedding dimensions must match")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


def _flatten(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(_flatten(item) for item in value)
    return str(value or "")
