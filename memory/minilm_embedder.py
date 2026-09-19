"""Lazy sentence-transformers MiniLM adapter."""

from __future__ import annotations

from typing import Any


class MiniLMUnavailableError(RuntimeError):
    """Raised when MiniLM is requested without its optional dependency."""


class MiniLMEmbedder:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2", model: Any | None = None) -> None:
        self.model_name = model_name
        self._model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise MiniLMUnavailableError(
                    "MiniLM requires the optional sentence-transformers package; it was not installed."
                ) from exc
            self._model = SentenceTransformer(self.model_name)
        if not texts:
            return []
        values = self._model.encode(texts, convert_to_numpy=True)
        return [vector.tolist() for vector in values]
