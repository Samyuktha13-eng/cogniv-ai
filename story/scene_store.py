"""In-memory navigation over deterministic story scene metadata."""

from __future__ import annotations

from pathlib import Path

from .models import Question, StoryScene
from .scene_loader import load_scenes


class SceneStore:
    def __init__(self, scenes: list[StoryScene] | None = None, path: str | Path | None = None) -> None:
        loaded = scenes if scenes is not None else load_scenes(path) if path else load_scenes()
        self._scenes = {scene.scene_id: scene for scene in loaded}
        self._questions = {
            question.question_id: question
            for scene in loaded
            for question in scene.questions
        }

    def get_scene(self, scene_id: str) -> StoryScene | None:
        return self._scenes.get(scene_id)

    def list_scenes(self) -> list[StoryScene]:
        return list(self._scenes.values())

    def list_chapter(self, chapter_id: str) -> list[StoryScene]:
        return sorted(
            (scene for scene in self._scenes.values() if scene.chapter_id == chapter_id),
            key=lambda scene: scene.sequence,
        )

    def get_next_scene(self, scene_id: str) -> StoryScene | None:
        scene = self.get_scene(scene_id)
        return self.get_scene(scene.next_scene_id) if scene and scene.next_scene_id else None

    def get_previous_scene(self, scene_id: str) -> StoryScene | None:
        scene = self.get_scene(scene_id)
        return self.get_scene(scene.previous_scene_id) if scene and scene.previous_scene_id else None

    def get_questions(self, scene_id: str) -> list[Question]:
        scene = self.get_scene(scene_id)
        return list(scene.questions) if scene else []

    def get_question(self, question_id: str) -> Question | None:
        return self._questions.get(question_id)
