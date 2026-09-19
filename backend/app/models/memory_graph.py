"""
MemoryGraph
===========
Links a patient's stored assets (story documents, images, voice) to the
canonical story beats that have been grounded and generated.

This is the source-of-truth record that answers:
  "Which patient material was used to produce this video?"

Every generated video must trace back to:
  patient_id → story_id → beat_id → source_documents + reference_images
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class VideoOrigin(str, Enum):
    AI_RECONSTRUCTION = "ai_reconstruction"   # generated from story + images
    HISTORICAL_PHOTO   = "historical_photo"    # actual patient photograph
    CAREGIVER_UPLOAD   = "caregiver_upload"    # uploaded by caregiver


class MemoryNode(BaseModel):
    """One grounded beat that has been (or is being) generated."""
    beat_id: str
    story_id: str
    patient_id: str

    # Evidence used
    source_documents: list[str] = Field(default_factory=list)   # relative paths
    reference_images: list[str] = Field(default_factory=list)   # relative paths
    grounding_source: str = ""                                   # e.g. "story:jasmine_morning/beat:jasmine_04"

    # Output
    video_job_id: str | None = None
    video_path: str | None = None
    video_origin: VideoOrigin = VideoOrigin.AI_RECONSTRUCTION

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryGraph(BaseModel):
    """All grounded memory nodes for one patient."""
    patient_id: str
    nodes: list[MemoryNode] = Field(default_factory=list)

    def add(self, node: MemoryNode) -> None:
        # Replace existing node for the same beat, or append
        for i, existing in enumerate(self.nodes):
            if existing.beat_id == node.beat_id and existing.story_id == node.story_id:
                self.nodes[i] = node
                return
        self.nodes.append(node)

    def get(self, story_id: str, beat_id: str) -> MemoryNode | None:
        return next(
            (n for n in self.nodes if n.story_id == story_id and n.beat_id == beat_id),
            None,
        )

    def nodes_for_story(self, story_id: str) -> list[MemoryNode]:
        return [n for n in self.nodes if n.story_id == story_id]
