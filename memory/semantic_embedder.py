"""Provider-neutral semantic embedding contract."""

from __future__ import annotations

from typing import Protocol


class SemanticEmbedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one deterministic-length embedding for each input text."""
